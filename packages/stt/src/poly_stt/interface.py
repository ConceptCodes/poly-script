from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Segment:
    start_ms: int
    end_ms: int
    text: str
    speaker: str | None = None


@dataclass
class EngineCapabilities:
    supports_timestamps: bool = True
    supports_diarization: bool = False
    supported_languages: list[str] | None = None


@dataclass
class TranscriptionResult:
    text: str
    language: str
    segments: list[Segment]
    engine: str
    confidence: float | None = None


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
        language: str | None = None,
        timestamps: bool = True,
        diarization: bool = False,
    ) -> TranscriptionResult:
        pass
