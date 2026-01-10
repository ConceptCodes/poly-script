from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, TypedDict, Required, NotRequired

@dataclass
class Segment:
    start_ms: int
    end_ms: int
    text: str
    speaker: Optional[str] = None

@dataclass
class EngineCapabilities:
    supports_timestamps: bool = True
    supports_diarization: bool = False
    supported_languages: Optional[List[str]] = None

@dataclass
class TranscriptionResult:
    text: str
    language: str
    segments: List[Segment]
    engine: str
    confidence: Optional[float] = None

class STTEngine(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> EngineCapabilities:
        pass
    
    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        timestamps: bool = True,
        diarization: bool = False,
    ) -> TranscriptionResult:
        pass