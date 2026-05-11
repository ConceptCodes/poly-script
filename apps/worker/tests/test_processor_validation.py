"""Tests for JobProcessor download and validation."""

from unittest.mock import Mock
import struct
import wave

import pytest

from apps.worker.src.config import Settings
from apps.worker.src.processor import (
    AudioDownloadError,
    AudioValidationError,
    JobProcessor,
)


class FakeResponse:
    def __init__(self, body: bytes, headers: dict[str, str] | None = None):
        self._body = body
        self.headers = headers or {}

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int = 8192):
        for idx in range(0, len(self._body), chunk_size):
            yield self._body[idx : idx + chunk_size]


@pytest.fixture
def processor():
    settings = Settings(
        DATABASE_URL="sqlite://",
        REDIS_URL="redis://localhost:6379/0",
        DOWNLOAD_MAX_RETRIES=1,
        DOWNLOAD_RETRY_BACKOFF=1,
        DOWNLOAD_TIMEOUT_SECONDS=1,
        DOWNLOAD_CHUNK_SIZE_BYTES=4,
        DOWNLOAD_MAX_BYTES=0,
    )
    return JobProcessor(
        session=Mock(),
        storage_backend=Mock(),
        progress_publisher=Mock(),
        settings=settings,
    )


def _write_wav(path, seconds: int = 1, sample_rate: int = 16000) -> None:
    with wave.open(str(path), "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack("h", 0) * sample_rate * seconds)


def test_validate_audio_success(processor, tmp_path):
    wav_path = tmp_path / "valid.wav"
    _write_wav(wav_path)

    duration_ms = processor._validate_audio(str(wav_path))

    assert duration_ms > 0


def test_validate_audio_codec_mismatch(processor, tmp_path):
    wav_path = tmp_path / "mismatch.mp3"
    _write_wav(wav_path)

    with pytest.raises(AudioValidationError, match="codec mismatch"):
        processor._validate_audio(str(wav_path))


def test_validate_audio_corrupt(processor, tmp_path):
    corrupt_path = tmp_path / "corrupt.wav"
    corrupt_path.write_bytes(b"not-audio")

    with pytest.raises(AudioValidationError):
        processor._validate_audio(str(corrupt_path))


def test_download_audio_content_length_mismatch(processor, monkeypatch):
    body = b"1234"
    response = FakeResponse(
        body, headers={"Content-Length": "10", "Content-Type": "audio/mpeg"}
    )

    def fake_get(*_args, **_kwargs):
        return response

    monkeypatch.setattr("requests.get", fake_get)

    with pytest.raises(AudioDownloadError, match="Incomplete download"):
        processor._download_audio("https://example.com/audio.mp3")
