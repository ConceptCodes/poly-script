"""TranslateGemma translation engine.

TranslateGemma is a translation model from Google that supports 55 languages.
This engine implements translation (not ASR) for post-processing transcripts.
"""

import logging

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from poly_stt.interface import EngineCapabilities, Segment, TranscriptionResult
from poly_stt.normalizer import normalize_language_code

logger = logging.getLogger(__name__)


class TranslateGemmaEngine:
    """TranslateGemma translation engine.

    This engine translates text from one language to another.
    It follows the same interface as STTEngine but for translation.

    Model: google/translategemma-4b-it
    - 55 languages supported
    - 2k token input limit
    - Requires strict chat template
    """

    MODEL_NAME = "google/translategemma-4b-it"
    MAX_TOKENS = 2048

    def __init__(self):
        self._model_name = self.MODEL_NAME
        self._device = self._detect_device()
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
        self._model = AutoModelForCausalLM.from_pretrained(
            self._model_name,
            torch_dtype=torch.float16 if self._use_fp16() else torch.float32,
            device_map="auto",
        )
        logger.info("Loaded model '%s' on device: %s", self._model_name, self._device)

    @property
    def name(self) -> str:
        return f"{self._model_name}"

    @property
    def capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supports_timestamps=True,
            supports_diarization=False,
            supported_languages=self._get_supported_languages(),
        )

    def translate(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None,
    ) -> TranscriptionResult:
        """Translate text to target language.

        Args:
            text: Source text to translate.
            target_language: Target language code (e.g., 'es', 'fr').
            source_language: Source language code (optional, auto-detect if None).

        Returns:
            TranscriptionResult with translated text and metadata.
        """
        target_lang = normalize_language_code(target_language)
        source_lang = normalize_language_code(source_language) if source_language else None

        if self._should_chunk(text):
            return self._translate_chunked(text, target_lang, source_lang)

        translated_text = self._translate_single(text, target_lang, source_lang)

        return TranscriptionResult(
            text=translated_text,
            language=target_lang,
            segments=[Segment(start_ms=0, end_ms=0, text=translated_text)],
            engine=self.name,
            confidence=None,
        )

    def translate_segments(
        self,
        segments: list[Segment],
        target_language: str,
        source_language: str | None = None,
    ) -> TranscriptionResult:
        """Translate transcript segments to target language.

        Preserves segment timing information while translating text.

        Args:
            segments: List of segments with text and timing.
            target_language: Target language code.
            source_language: Source language code (optional).

        Returns:
            TranscriptionResult with translated segments.
        """
        target_lang = normalize_language_code(target_language)
        source_lang = normalize_language_code(source_language) if source_language else None

        full_text = " ".join(seg.text for seg in segments)

        if self._should_chunk(full_text):
            translated_segments = self._translate_segments_chunked(
                segments, target_lang, source_lang
            )
        else:
            translated_segments = self._translate_segments_single(
                segments, target_lang, source_lang
            )

        translated_text = " ".join(seg.text for seg in translated_segments)

        return TranscriptionResult(
            text=translated_text,
            language=target_lang,
            segments=translated_segments,
            engine=self.name,
            confidence=None,
        )

    def _translate_single(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None,
    ) -> str:
        """Translate a single chunk of text."""
        prompt = self._build_translation_prompt(text, target_language, source_language)

        inputs = self._tokenizer(prompt, return_tensors="pt", truncation=True).to(self._device)

        outputs = self._generate_with_fallback(inputs)

        decoded = self._tokenizer.decode(outputs[0], skip_special_tokens=True)

        translation = self._extract_translation(decoded)

        return translation.strip()

    def _generate_with_fallback(self, inputs):
        try:
            with torch.no_grad():
                return self._model.generate(
                    **inputs,
                    max_new_tokens=self.MAX_TOKENS,
                    do_sample=False,
                    temperature=1.0,
                )
        except RuntimeError as e:
            if self._is_accelerator_error(e) and self._device != "cpu":
                logger.warning(
                    "TranslateGemma accelerator error on %s: %s. Falling back to CPU.",
                    self._device,
                    e,
                )
                self._switch_to_cpu()
                cpu_inputs = inputs.to(self._device)
                with torch.no_grad():
                    return self._model.generate(
                        **cpu_inputs,
                        max_new_tokens=self.MAX_TOKENS,
                        do_sample=False,
                        temperature=1.0,
                    )
            raise

    def _translate_chunked(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None,
    ) -> TranscriptionResult:
        """Translate large text by chunking."""
        chunks = self._chunk_text(text)

        translated_chunks = []
        for chunk in chunks:
            translated = self._translate_single(chunk, target_language, source_language)
            translated_chunks.append(translated)

        full_translation = " ".join(translated_chunks)

        return TranscriptionResult(
            text=full_translation,
            language=target_language,
            segments=[Segment(start_ms=0, end_ms=0, text=full_translation)],
            engine=self.name,
            confidence=None,
        )

    def _translate_segments_single(
        self,
        segments: list[Segment],
        target_language: str,
        source_language: str | None = None,
    ) -> list[Segment]:
        """Translate segments in batch."""
        full_text = " ".join(seg.text for seg in segments)

        translated = self._translate_single(full_text, target_language, source_language)

        translated_segments = []
        translated_words = translated.split()

        word_idx = 0
        for seg in segments:
            original_word_count = len(seg.text.split())
            segment_words = translated_words[word_idx : word_idx + original_word_count]
            segment_text = " ".join(segment_words)

            translated_segments.append(
                Segment(
                    start_ms=seg.start_ms,
                    end_ms=seg.end_ms,
                    text=segment_text.strip(),
                )
            )
            word_idx += original_word_count

        return translated_segments

    def _translate_segments_chunked(
        self,
        segments: list[Segment],
        target_language: str,
        source_language: str | None = None,
    ) -> list[Segment]:
        """Translate segments by chunking."""
        translated_segments = []
        current_chunk = []
        current_text = ""

        for seg in segments:
            new_text = current_text + " " + seg.text if current_text else seg.text

            if self._should_chunk(new_text):
                if current_chunk:
                    translated = self._translate_segments_single(
                        current_chunk, target_language, source_language
                    )
                    translated_segments.extend(translated)

                current_chunk = [seg]
                current_text = seg.text
            else:
                current_chunk.append(seg)
                current_text = new_text

        if current_chunk:
            translated = self._translate_segments_single(
                current_chunk, target_language, source_language
            )
            translated_segments.extend(translated)

        return translated_segments

    def _build_translation_prompt(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None,
    ) -> str:
        """Build translation prompt with strict chat template."""
        if source_language:
            prompt = (
                f"Translate the following text from {source_language} to {target_language}: {text}"
            )
        else:
            prompt = f"Translate the following text to {target_language}: {text}"

        messages = [{"role": "user", "content": prompt}]

        return self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

    def _extract_translation(self, response: str) -> str:
        """Extract translation from model response."""
        lines = response.split("\n")

        translation_lines = []
        in_translation = False

        for line in lines:
            line = line.strip()
            if line.startswith(("model>", "Model:")):
                in_translation = True
                line = line.split(">", 1)[-1].split(":", 1)[-1].strip()
            elif line and line.startswith(("user>", "User:")):
                in_translation = False
            elif in_translation and line:
                translation_lines.append(line)

        if translation_lines:
            return " ".join(translation_lines)

        for line in reversed(lines):
            if line.strip() and not any(
                marker in line.lower() for marker in ["user>", "model>", "user:", "model:"]
            ):
                return line.strip()

        return response.strip()

    def _should_chunk(self, text: str) -> bool:
        """Check if text should be chunked based on token count."""
        tokens = self._tokenizer(text, return_tensors=None)
        token_count = len(tokens["input_ids"])
        return token_count > self.MAX_TOKENS

    def _chunk_text(self, text: str) -> list[str]:
        """Split text into chunks that fit within token limit."""
        sentences = text.split(". ")
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            tokens = self._tokenizer(sentence, return_tensors=None)
            token_count = len(tokens["input_ids"])

            if current_length + token_count > self.MAX_TOKENS:
                if current_chunk:
                    chunks.append(". ".join(current_chunk) + ".")
                current_chunk = [sentence]
                current_length = token_count
            else:
                current_chunk.append(sentence)
                current_length += token_count

        if current_chunk:
            chunks.append(". ".join(current_chunk) + ".")

        return chunks

    def _get_supported_languages(self) -> list[str]:
        """Return list of supported language codes.

        TranslateGemma supports 55 languages. This is a representative subset.
        Full list should be checked from HuggingFace model card.
        """
        return [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ru",
            "zh",
            "ja",
            "ko",
            "nl",
            "pl",
            "tr",
            "sv",
            "da",
            "no",
            "fi",
            "cs",
            "el",
            "hu",
            "ar",
            "hi",
            "th",
            "vi",
            "id",
            "ms",
            "uk",
            "he",
            "ro",
            "bg",
        ]

    def _detect_device(self) -> str:
        """Detect available device for inference."""
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _use_fp16(self) -> bool:
        """Check if fp16 precision should be used."""
        return self._device in ("cuda", "mps")

    def _switch_to_cpu(self) -> None:
        self._device = "cpu"
        self._model = AutoModelForCausalLM.from_pretrained(
            self._model_name,
            torch_dtype=torch.float32,
            device_map="cpu",
        )

    def _is_accelerator_error(self, error: Exception) -> bool:
        message = str(error).lower()
        return any(
            marker in message
            for marker in (
                "cuda",
                "cudnn",
                "cublas",
                "out of memory",
                "mps",
                "metal",
            )
        )
