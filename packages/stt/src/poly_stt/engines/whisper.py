from typing import Optional, List
import torch
import whisper
import os
from ..interface import STTEngine, TranscriptionResult, Segment, EngineCapabilities
from ..normalizer import normalize_result, normalize_language_code

class WhisperLocalEngine(STTEngine):
    
    def __init__(self, model_size: str = "base"):
        self._model_size = model_size
        self._device = self._detect_device()
        self._model = whisper.load_model(model_size, device=self._device)
        print(f"[Whisper] Loaded model '{model_size}' on device: {self._device}")
    
    @property
    def name(self) -> str:
        return f"whisper-local-{self._model_size}"
    
    @property
    def capabilities(self) -> EngineCapabilities:
        return EngineCapabilities(
            supports_timestamps=True,
            supports_diarization=False,
            supported_languages=None,
        )
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        timestamps: bool = True,
        diarization: bool = False,
    ) -> TranscriptionResult:
        whisper_lang = self._convert_language(language) if language else None
        
        result = self._model.transcribe(
            audio_path,
            language=whisper_lang,
            word_timestamps=timestamps,
            fp16=self._use_fp16(),
        )
        
        segments: List[Segment] = []
        for seg in result.get("segments", []):
            segments.append(Segment(
                start_ms=int(seg["start"] * 1000),
                end_ms=int(seg["end"] *1000),
                text=seg["text"].strip(),
                speaker=None,
            ))
        
        transcription_result = TranscriptionResult(
            text=result["text"].strip(),
            language=self._convert_language_back(result.get("language", "en")),
            segments=segments,
            confidence=None,
            engine=self.name,
        )
        
        return normalize_result(transcription_result)
    
    def _detect_device(self) -> str:
        if torch.cuda.is_available():
            device = "cuda"
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"[Whisper] CUDA available: {gpu_count} GPU(s)")
            print(f"[Whisper] Using GPU: {gpu_name}")
            return device
        
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("[Whisper] MPS (Apple Silicon) available")
            return "mps"
        
        print("[Whisper] No GPU detected, using CPU")
        return "cpu"
    
    def _use_fp16(self) -> bool:
        return self._device in ("cuda", "mps")
    
    def _convert_language(self, code: Optional[str]) -> Optional[str]:
        if not code:
            return None
        return code.split("-")[0].lower()
    
    def _convert_language_back(self, code: str) -> str:
        return normalize_language_code(code)