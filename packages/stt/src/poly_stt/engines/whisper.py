from typing import Optional, List
from faster_whisper import WhisperModel
import os

from ..interface import STTEngine, TranscriptionResult, Segment, EngineCapabilities
from ..normalizer import normalize_result, normalize_language_code


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
        print(f"[Whisper] Loaded model '{model_size}' on device: {self._device}")
    
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
        language: Optional[str] = None,
        timestamps: bool = True,
        diarization: bool = False,
        options: Optional[dict] = None,
    ) -> TranscriptionResult:
        """Transcribe audio file using faster-whisper."""
        
        # Normalize language code for faster-whisper
        whisper_lang = self._convert_language(language) if language else None
        
        # Transcribe with faster-whisper
        segments_generator, info = self._model.transcribe(
            audio_path,
            language=whisper_lang,
            word_timestamps=timestamps,
            vad_filter=True,  # Enable voice activity detection
        )
        
        # Collect segments
        segments: List[Segment] = []
        full_text = []
        
        for seg in segments_generator:
            text = seg.text.strip()
            if text:
                segments.append(Segment(
                    start_ms=int(seg.start * 1000),
                    end_ms=int(seg.end * 1000),
                    text=text,
                    speaker=None,  # Whisper doesn't support diarization
                ))
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
        
        return normalize_result(transcription_result)
    
    def _detect_device(self) -> str:
        """Detect available device for Whisper model."""
        # Check for CUDA
        try:
            import torch
            if torch.cuda.is_available():
                print("[Whisper] CUDA available")
                return "cuda"
        except ImportError:
            pass
        
        # Check for MPS (Apple Silicon)
        if hasattr(os, 'uname'):
            try:
                import torch
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    print("[Whisper] MPS (Apple Silicon) available")
                    return "mps"
            except ImportError:
                pass
        
        print("[Whisper] Using CPU")
        return "cpu"
    
    def _use_fp16(self) -> bool:
        """Check if FP16 precision is supported."""
        return self._device in ("cuda", "mps")
    
    def _convert_language(self, code: Optional[str]) -> Optional[str]:
        """Convert BCP-47 language code to faster-whisper format."""
        if not code:
            return None
        # faster-whisper uses 2-letter codes
        return code.split("-")[0].lower()
    
    def _convert_language_back(self, code: str) -> str:
        """Convert faster-whisper language code to BCP-47 format."""
        return normalize_language_code(code)
