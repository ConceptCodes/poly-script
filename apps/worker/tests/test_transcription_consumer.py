"""Tests for TranscriptionConsumer."""

import time
from unittest.mock import Mock, patch

import pytest
from apps.worker.src.consumer import TranscriptionConsumer


@pytest.fixture
def mock_queue():
    """Mock TranscriptionQueue."""
    queue = Mock()
    queue.dequeue.return_value = None
    return queue


@pytest.fixture
def mock_storage():
    """Mock storage backend."""
    return Mock()


@pytest.fixture
def consumer(mock_queue, mock_storage):
    """Create a TranscriptionConsumer instance."""
    return TranscriptionConsumer(
        queue=mock_queue,
        storage_backend=mock_storage,
        max_retries=2,
        retry_backoff=2,
    )


class TestTranscriptionConsumer:
    """Tests for TranscriptionConsumer."""

    def test_consumer_initialization(self, consumer, mock_queue):
        """Test consumer initializes correctly."""
        assert consumer.queue == mock_queue
        assert consumer.storage_backend is not None
        assert consumer.max_retries == 2
        assert consumer.retry_backoff == 2
        assert not consumer.is_running

        assert consumer.current_job_id is None

    def test_consumer_start(self, consumer):
        """Test consumer starts a thread."""
        consumer.start()
        time.sleep(0.1)  # Give thread time to start

        assert consumer.is_running
        assert consumer._thread is not None

        consumer.stop()

    def test_consumer_stop(self, consumer):
        """Test consumer stops gracefully."""
        consumer.start()
        time.sleep(0.1)

        assert consumer.is_running

        consumer.stop()
        time.sleep(0.1)  # Give thread time to stop

        assert not consumer.is_running

    @patch("apps.worker.src.consumer.get_db_session")
    @patch("apps.worker.src.consumer.JobProcessor")
    def test_process_work_item_success(
        self, mock_processor_class, mock_db_session, consumer, mock_queue
    ):
        """Test processing a work item successfully."""
        work_item = {
            "job_id": "test-job-123",
            "audio_ref": "/tmp/test.mp3",
            "requested_language": "en",
            "engine": "whisper-local-tiny",
            "options": {"timestamps": True, "diarization": False},
        }

        mock_queue.dequeue.return_value = work_item
        mock_session = Mock()
        mock_db_session.return_value.__enter__.return_value = mock_session

        mock_processor = mock_processor_class.return_value
        mock_processor.process_job.return_value = True

        consumer._process_work_item(work_item)

        mock_processor.process_job.assert_called_once_with("test-job-123")
