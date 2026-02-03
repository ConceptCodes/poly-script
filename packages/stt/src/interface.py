from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Segment:
    """A segment of transcript with timing and optional speaker."""

    start_ms: float
    end_ms: float
    text: str
    speaker: str | None = None


@dataclass
class TranscriptionResult:
    """The normalized output from any STT engine."""

    text: str
    language: str
    segments: list[Segment]
    confidence: float | None = None
    engine: str = "base"


@dataclass
class EngineCapabilities:
    """Engine capabilities flags."""

    supports_timestamps: bool = True
    supports_diarization: bool = False
    supported_languages: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.supported_languages is None:
            self.supported_languages = ["en-US", "en-GB", "es-ES", "fr-FR"]


class STTEngine(ABC):
    """Abstract base class for all speech-to-text engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the engine identifier."""

    @property
    @abstractmethod
    def capabilities(self) -> EngineCapabilities:
        """Return the engine's capabilities."""

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
        timestamps: bool = True,
        diarization: bool = False,
        options: dict[str, Any] | None = None,
    ) -> TranscriptionResult:
        """Transcribe audio and return normalized result.

        Args:
            audio_path: Path to audio file to transcribe
            language: Optional BCP-47 language code for forced transcription
            timestamps: Whether to include timestamps in segments
            diarization: Whether to attempt diarization (if supported)
            options: Optional engine-specific options

        Returns:
            Normalized TranscriptionResult

        Raises:
            NotImplementedError: If engine cannot transcribe
        """
