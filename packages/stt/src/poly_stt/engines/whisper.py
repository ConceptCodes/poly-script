import logging
import os

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency for GPU detection
    torch = None

from faster_whisper import WhisperModel

from poly_stt.interface import EngineCapabilities, Segment, STTEngine, TranscriptionResult
from poly_stt.normalizer import normalize_language_code, normalize_result

logger = logging.getLogger(__name__)


class WhisperLocalEngine(STTEngine):
    """Whisper engine using faster-whisper for faster transcription."""

    def __init__(self, model_size: str = "medium"):
        self._model_size = model_size
        self._device = self._detect_device()
        self._model = WhisperModel(
            model_size,
            device=self._device,
            compute_type="float16" if self._use_fp16() else "int8",
        )
        logger.info("Loaded model '%s' on device: %s", model_size, self._device)

    @property
    def name(self) -> str:
        return f"whisper-local-{self._model_size}"

    @property
    def capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supports_timestamps=True,
            supports_diarization=False,
            supported_languages=None,  # faster-whisper supports all
        )

    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
        timestamps: bool = True,
        _diarization: bool = False,
        _options: dict | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio file using faster-whisper."""

        # Normalize language code for faster-whisper
        whisper_lang = self._convert_language(language) if language else None

        # Transcribe with faster-whisper
        segments_generator, info = self._transcribe_with_fallback(
            audio_path=audio_path,
            language=whisper_lang,
            timestamps=timestamps,
        )

        # Collect segments
        segments: list[Segment] = []
        full_text = []

        total_speech_ms = 0
        for seg in segments_generator:
            text = seg.text.strip()
            if text:
                total_speech_ms += int((seg.end - seg.start) * 1000)
                segments.append(
                    Segment(
                        start_ms=int(seg.start * 1000),
                        end_ms=int(seg.end * 1000),
                        text=text,
                        speaker=None,  # Whisper doesn't support diarization
                    )
                )
                full_text.append(text)

        # Get detected or final language
        detected_lang = info.language if info.language else "en"
        final_language = language if language else normalize_language_code(detected_lang)

        transcription_result = TranscriptionResult(
            text=" ".join(full_text).strip(),
            language=final_language,
            segments=segments,
            confidence=None,  # faster-whisper doesn't provide confidence
            engine=self.name,
        )

        self._log_vad_stats(info, total_speech_ms)

        return normalize_result(transcription_result)

    def _transcribe_with_fallback(
        self,
        audio_path: str,
        language: str | None,
        timestamps: bool,
    ):
        try:
            return self._model.transcribe(
                audio_path,
                language=language,
                word_timestamps=timestamps,
                vad_filter=True,  # Enable voice activity detection
            )
        except RuntimeError as e:
            if self._is_accelerator_error(e) and self._device != "cpu":
                logger.warning(
                    "Whisper accelerator error on %s: %s. Falling back to CPU.",
                    self._device,
                    e,
                )
                self._switch_to_cpu()
                return self._model.transcribe(
                    audio_path,
                    language=language,
                    word_timestamps=timestamps,
                    vad_filter=True,
                )
            raise

    def _switch_to_cpu(self) -> None:
        self._device = "cpu"
        self._model = WhisperModel(
            self._model_size,
            device="cpu",
            compute_type="int8",
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

    def _log_vad_stats(self, info, total_speech_ms: int) -> None:
        total_duration = getattr(info, "duration", None)
        if not total_duration or total_duration <= 0:
            if total_speech_ms == 0:
                logger.warning("VAD produced no segments and audio duration unavailable")
            return

        total_ms = int(total_duration * 1000)
        if total_ms <= 0:
            return

        speech_ratio = total_speech_ms / total_ms
        if speech_ratio < 0.1:
            logger.warning(
                "VAD filtered most of the audio (speech_ms=%s, total_ms=%s, ratio=%.2f)",
                total_speech_ms,
                total_ms,
                speech_ratio,
            )

    def _detect_device(self) -> str:
        """Detect available device for Whisper model."""
        # Check for CUDA
        if torch and torch.cuda.is_available():
            logger.info("CUDA available")
            return "cuda"

        # Check for MPS (Apple Silicon)
        if (
            torch
            and hasattr(os, "uname")
            and hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            logger.info("MPS (Apple Silicon) available")
            return "mps"

        logger.info("Using CPU")
        return "cpu"

    def _use_fp16(self) -> bool:
        """Check if FP16 precision is supported."""
        return self._device in ("cuda", "mps")

    def _convert_language(self, code: str | None) -> str | None:
        """Convert BCP-47 language code to faster-whisper format."""
        if not code:
            return None
        # faster-whisper uses 2-letter codes
        return code.split("-")[0].lower()

    def _convert_language_back(self, code: str) -> str:
        """Convert faster-whisper language code to BCP-47 format."""
        return normalize_language_code(code)
