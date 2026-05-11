"""Tests for WhisperLocalEngine with faster-whisper."""

import struct
import wave
from unittest.mock import MagicMock, patch

import pytest

from poly_stt.engines import WhisperLocalEngine
from poly_stt.interface import TranscriptionResult
from poly_stt.registry import EngineRegistry


@pytest.fixture
def tiny_engine():
    """Create a tiny Whisper engine for testing."""
    return WhisperLocalEngine(model_size="tiny")


@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a minimal WAV audio file for testing."""
    wav_path = tmp_path / "test_audio.wav"

    with wave.open(str(wav_path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
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

    @patch("poly_stt.engines.whisper.WhisperLocalEngine._transcribe_with_fallback")
    def test_transcribe_basic(self, mock_transcribe, tiny_engine, sample_audio_file):
        """Test basic transcription."""
        mock_segments = iter(
            [
                MagicMock(start=0.0, end=1.0, text="Hello"),
                MagicMock(start=1.0, end=2.0, text="world"),
            ]
        )
        mock_info = MagicMock(language="en", language_probability=0.9, duration=2.0)
        mock_transcribe.return_value = (mock_segments, mock_info)

        result = tiny_engine.transcribe(
            audio_path=sample_audio_file,
            language=None,
            timestamps=True,
        )

        assert isinstance(result, TranscriptionResult)
        assert isinstance(result.text, str)
        assert isinstance(result.language, str)
        assert isinstance(result.segments, list)
        assert result.engine is not None

    @patch("poly_stt.engines.whisper.WhisperLocalEngine._transcribe_with_fallback")
    def test_transcribe_with_language(self, mock_transcribe, tiny_engine, sample_audio_file):
        """Test transcription with requested language."""
        mock_segments = iter([MagicMock(start=0.0, end=1.0, text="Hello")])
        mock_info = MagicMock(language="en", language_probability=0.9, duration=1.0)
        mock_transcribe.return_value = (mock_segments, mock_info)

        result = tiny_engine.transcribe(
            audio_path=sample_audio_file,
            language="en",
            timestamps=True,
        )

        assert result.language.startswith("en")

    @patch("poly_stt.engines.whisper.WhisperLocalEngine._transcribe_with_fallback")
    def test_transcribe_without_timestamps(self, mock_transcribe, tiny_engine, sample_audio_file):
        """Test transcription without timestamps."""
        mock_segments = iter([MagicMock(start=0.0, end=1.0, text="Hello")])
        mock_info = MagicMock(language="en", language_probability=0.9, duration=1.0)
        mock_transcribe.return_value = (mock_segments, mock_info)

        result = tiny_engine.transcribe(
            audio_path=sample_audio_file,
            language=None,
            timestamps=False,
        )

        assert isinstance(result.segments, list)

    def test_transcribe_diarization_not_supported(self, tiny_engine):
        """Test that diarization is not supported."""
        caps = tiny_engine.capabilities
        assert caps.supports_diarization is False


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
