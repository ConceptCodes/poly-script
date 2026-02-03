"""Tests for WhisperLocalEngine with faster-whisper."""

import struct
import wave

import pytest

from poly_stt.engines import WhisperLocalEngine
from poly_stt.interface import TranscriptionResult
from poly_stt.registry import EngineRegistry


@pytest.fixture
def tiny_engine():
    """Create a tiny Whisper engine for testing."""
    # Use tiny model for fast tests
    return WhisperLocalEngine(model_size="tiny")


@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a minimal WAV audio file for testing."""
    # Generate a silent 1-second WAV file
    wav_path = tmp_path / "test_audio.wav"

    with wave.open(str(wav_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # Write 1 second of silence
        wav_file.writeframes(struct.pack("h", 0) * 16000)

    return str(wav_path)


class TestWhisperEngine:
    """Tests for WhisperLocalEngine."""

    def test_engine_name(self, tiny_engine):
        """Test engine name property."""
        assert "whisper-local-tiny" in tiny_engine.name

    def test_capabilities(self, tiny_engine):
        """Test engine capabilities."""
        caps = tiny_engine.capabilities
        assert caps.supports_timestamps is True
        assert caps.supports_diarization is False

    def test_transcribe_basic(self, tiny_engine, sample_audio_file):
        """Test basic transcription."""
        result = tiny_engine.transcribe(
            audio_path=sample_audio_file,
            language=None,  # Auto-detect
            timestamps=True,
            diarization=False,
        )

        assert isinstance(result, TranscriptionResult)
        assert isinstance(result.text, str)
        assert isinstance(result.language, str)
        assert isinstance(result.segments, list)
        assert result.engine is not None

    def test_transcribe_with_language(self, tiny_engine, sample_audio_file):
        """Test transcription with requested language."""
        result = tiny_engine.transcribe(
            audio_path=sample_audio_file,
            language="en",
            timestamps=True,
            diarization=False,
        )

        assert result.language.startswith("en")

    def test_transcribe_without_timestamps(self, tiny_engine, sample_audio_file):
        """Test transcription without timestamps."""
        result = tiny_engine.transcribe(
            audio_path=sample_audio_file,
            language=None,
            timestamps=False,
            diarization=False,
        )

        # Segments may still exist but without detailed timestamps
        assert isinstance(result.segments, list)

    def test_transcribe_diarization_ignored(self, tiny_engine, sample_audio_file):
        """Test that diarization=True is safely ignored."""
        # Should not raise error even though not supported
        result = tiny_engine.transcribe(
            audio_path=sample_audio_file,
            language=None,
            timestamps=True,
            diarization=True,  # Ignored
        )

        # All segments should have None speaker
        for seg in result.segments:
            assert seg.speaker is None


class TestEngineRegistry:
    """Tests for EngineRegistry."""

    def test_register_and_get(self):
        """Test registering and retrieving an engine."""
        engine = WhisperLocalEngine(model_size="tiny")
        EngineRegistry.register(engine)

        retrieved = EngineRegistry.get(engine.name)
        assert retrieved is engine

    def test_set_default(self):
        """Test setting default engine."""
        engine = WhisperLocalEngine(model_size="tiny")
        EngineRegistry.register(engine)
        EngineRegistry.set_default(engine.name)

        assert EngineRegistry.is_default_set()

    def test_list_engines(self):
        """Test listing available engines."""
        engine = WhisperLocalEngine(model_size="tiny")
        EngineRegistry.register(engine)

        engines = EngineRegistry.list_engines()
        assert len(engines) > 0
