"""
Unit tests for Consumer, Processor, and Progress Publisher.

Tests core worker functionality including job processing pipeline,
progress publishing, and consumer thread behavior.
"""

from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm import Session
from worker.src.consumer import TranscriptionConsumer
from worker.src.processor import JobProcessor
from worker.src.progress import ProgressPublisher

from poly_db.models.transcripts import Transcript

from . import setup_paths as _setup_paths

del _setup_paths


@pytest.fixture
def mock_session():
    """Mock database session."""
    return Mock(spec=Session)


@pytest.fixture
def mock_storage_backend():
    """Mock storage backend."""
    backend = Mock()
    backend.get_local_path.return_value = "/tmp/test.mp3"
    return backend


@pytest.fixture
def mock_queue():
    """Mock Redis queue."""
    queue = Mock()
    queue.dequeue.return_value = None  # No jobs
    return queue


@pytest.fixture
def mock_publisher():
    """Mock progress publisher."""
    publisher = Mock(spec=ProgressPublisher)
    return publisher


@pytest.fixture
def mock_transcription_result():
    """Mock STT transcription result."""
    from poly_stt.interface import Segment, TranscriptionResult

    return TranscriptionResult(
        text="Hello world",
        language="en",
        segments=[
            Segment(start_ms=0, end_ms=1000, text="Hello world"),
        ],
        engine="whisper-local-base",
    )
 
 
@pytest.fixture
def mock_processor(mock_session, mock_storage_backend, mock_publisher):
    """Mock job processor."""
    return JobProcessor(
        session=mock_session,
        storage_backend=mock_storage_backend,
        progress_publisher=mock_publisher,
    )


class TestProgressPublisher:
    """Tests for ProgressPublisher."""

    def test_publish_progress(self):
        """Test progress message is published to Redis."""
        with patch("worker.src.progress.get_redis_client") as mock_get_redis:
            mock_redis = Mock()
            mock_get_redis.return_value = mock_redis
            
            publisher = ProgressPublisher()
            publisher.publish_progress(
                job_id="test-job-123",
                team_id="test-team-456",
                progress_pct=50,
                progress_stage="transcribing",
                status="RUNNING",
            )
 
            # Verify publish was called
            mock_redis.publish.assert_called_once()
 
            # Verify channel format
            call_args = mock_redis.publish.call_args
            channel, message = call_args[0]
            assert channel == "job:test-job-123:progress"

    def test_get_stage_progress(self):
        """Test stage progress percentages."""
        assert ProgressPublisher._get_stage_progress("starting") == 0
        assert ProgressPublisher._get_stage_progress("downloading") == 10
        assert ProgressPublisher._get_stage_progress("decoding") == 20
        assert ProgressPublisher._get_stage_progress("transcribing") == 90
        assert ProgressPublisher._get_stage_progress("formatting") == 95
        assert ProgressPublisher._get_stage_progress("saving") == 100
        assert ProgressPublisher._get_stage_progress("completed") == 100
        assert ProgressPublisher._get_stage_progress("unknown") == 0


class TestJobProcessor:
    """Tests for JobProcessor."""

    def test_processor_initialization(self, mock_session, mock_storage_backend, mock_publisher):
        """Test processor initializes correctly."""
        processor = JobProcessor(
            session=mock_session,
            storage_backend=mock_storage_backend,
            progress_publisher=mock_publisher,
        )

        assert processor.session == mock_session
        assert processor.storage_backend == mock_storage_backend
        assert processor.progress_publisher == mock_publisher

    @patch("requests.get")
    def test_download_audio_from_url(self, mock_get, mock_processor):
        """Test downloading audio from URL."""
        # Setup mock response
        mock_response = Mock()
        mock_response.iter_content.return_value = [b"audio data"]
        mock_response.headers = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
 
        audio_path = mock_processor._download_audio("https://example.com/audio.mp3")
 
        # Verify download was called
        mock_get.assert_called_once()
        assert "https://example.com/audio.mp3" in mock_get.call_args[0]
 
        # Verify temp file was created
        assert audio_path.endswith(".mp3")

    @patch("librosa.load")
    @patch("soundfile.info")
    def test_validate_audio(self, mock_info, mock_load, mock_processor):
        """Test audio validation."""
        # Mock librosa to return audio
        import numpy as np
 
        mock_load.return_value = (np.zeros(1000), 16000)
 
        # Mock soundfile info
        mock_info.return_value = Mock(samplerate=16000, channels=1, format="WAV")
 
        duration_ms = mock_processor._validate_audio("/tmp/test.wav")
 
        # Verify duration calculation
        assert duration_ms == pytest.approx(62.5, rel=1e-2)  # ~1000/16

    def test_format_transcript(self, mock_processor, mock_transcription_result):
        """Test transcript formatting."""
        job = Mock()
        job.id = "job-123"

        transcript = mock_processor._format_transcript(job, mock_transcription_result, duration_ms=5000)

        # Verify transcript structure
        assert isinstance(transcript, Transcript)
        assert transcript.job_id == "job-123"
        assert transcript.text == "Hello world"
        assert transcript.language == "en"

        # Verify segments JSON format
        assert isinstance(transcript.segments, list)
        assert len(transcript.segments) == 1
        assert transcript.segments[0]["start_ms"] == 0
        assert transcript.segments[0]["end_ms"] == 1000
        assert transcript.segments[0]["text"] == "Hello world"


class TestTranscriptionConsumer:
    """Tests for TranscriptionConsumer."""

    def test_consumer_initialization(self, mock_queue):
        """Test consumer initializes correctly."""
        consumer = TranscriptionConsumer(
            queue=mock_queue, storage_backend=Mock(), max_retries=3, retry_backoff=2
        )

        assert consumer.queue == mock_queue
        assert consumer.max_retries == 3
        assert consumer.retry_backoff == 2
        assert consumer._thread is None
        assert not consumer._shutdown.is_set()

    def test_consumer_starts_thread(self, mock_queue):
        """Test consumer starts thread."""
        consumer = TranscriptionConsumer(queue=mock_queue, storage_backend=Mock())

        consumer.start()

        # Verify thread was created
        assert consumer._thread is not None
        assert consumer._thread.name == "TranscriptionConsumer"
        assert consumer._thread.is_alive()

        # Clean up
        consumer._shutdown.set()
        consumer._thread.join(timeout=1)

    def test_consumer_stops_gracefully(self, mock_queue):
        """Test consumer stops gracefully."""
        consumer = TranscriptionConsumer(queue=mock_queue, storage_backend=Mock())
        consumer.start()

        # Stop consumer
        consumer.stop()

        # Verify thread was stopped
        assert consumer._thread.is_alive() is False

    @patch("worker.src.consumer.TranscriptionJobRepository")
    def test_retry_logic(self, mock_repo_class, mock_queue):
        """Test retry logic with exponential backoff."""
 
        consumer = TranscriptionConsumer(
            queue=mock_queue, storage_backend=Mock(), max_retries=3, retry_backoff=2
        )
 
        # Mock session and job
        mock_session = Mock()
        job = Mock()
        job.id = "job-123"
        job.attempts = 0
 
        mock_repo = mock_repo_class.return_value
        mock_repo.get.return_value = job
        mock_repo.update = Mock() # Ensure update is mocked if called
 
        # Simulate failure handling
        work_item = {
            "job_id": "job-123",
            "audio_ref": "local://test.mp3",
            "engine": None,
            "options": {},
        }
 
        with patch("time.sleep") as mock_sleep:
            with patch("worker.src.consumer.get_db_session") as mock_get_session:
                # Mock the context manager
                mock_get_session.return_value.__enter__.return_value = mock_session
 
                consumer._handle_job_failure(
                    session=mock_session,
                    job_id="job-123",
                    work_item=work_item,
                )
 
                # Verify retry was attempted
                assert mock_queue.enqueue.call_count == 1
 
                # Verify sleep with backoff: 2^0 = 1s
                mock_sleep.assert_called_with(1)
 
    @patch("worker.src.consumer.TranscriptionJobRepository")
    def test_max_retries_exceeded(self, mock_repo_class, mock_queue):
        """Test job fails after max retries."""
        mock_session = Mock()
        job = Mock()
        job.id = "job-123"
        job.attempts = 3  # Already at max retries
 
        mock_repo = mock_repo_class.return_value
        mock_repo.get.return_value = job
        mock_repo.update = Mock() # Ensure update is mocked if called
 
        consumer = TranscriptionConsumer(
            queue=mock_queue, storage_backend=Mock(), max_retries=3, retry_backoff=2
        )
 
        work_item = {
            "job_id": "job-123",
            "audio_ref": "local://test.mp3",
            "engine": None,
            "options": {},
        }
 
        with patch("worker.src.consumer.get_db_session") as mock_get_session:
            # Mock the context manager
            mock_get_session.return_value.__enter__.return_value = mock_session
 
            consumer._handle_job_failure(
                session=mock_session,
                job_id="job-123",
                work_item=work_item,
            )
 
            # Verify job was NOT re-enqueued
            assert mock_queue.enqueue.call_count == 0

    def test_is_running_property(self, mock_queue):
        """Test is_running property."""
        consumer = TranscriptionConsumer(queue=mock_queue, storage_backend=Mock())

        assert consumer.is_running is False

        consumer.start()
        assert consumer.is_running is True

        # Clean up
        consumer._shutdown.set()
        consumer._thread.join(timeout=1)
