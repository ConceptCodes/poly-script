import uuid
from unittest.mock import Mock

import pytest

from poly_redis.queue import TranscriptionQueue, TranscriptionWorkItem


@pytest.fixture
def redis_client():
    """Mock Redis client for testing."""
    mock_redis = Mock()
    mock_redis.rpush = Mock(return_value=1)
    mock_redis.blpop = Mock(return_value=None)
    mock_redis.lindex = Mock(return_value=None)
    mock_redis.llen = Mock(return_value=0)
    return mock_redis


def test_create_work_item():
    """Test creating a TranscriptionWorkItem."""
    job_id = uuid.uuid4()
    item = TranscriptionWorkItem(
        job_id=job_id,
        audio_ref="local://audio/test.mp3",
        requested_language="en",
        engine="whisper",
        options={"timestamps": True},
    )

    assert item.job_id == job_id
    assert item.audio_ref == "local://audio/test.mp3"
    assert item.requested_language == "en"
    assert item.engine == "whisper"
    assert item.options["timestamps"] is True


def test_enqueue(redis_client):
    """Test enqueuing a work item."""
    queue = TranscriptionQueue(redis_client)
    item = TranscriptionWorkItem(job_id=uuid.uuid4(), audio_ref="local://audio/test.mp3")

    result = queue.enqueue(item)

    assert result == 1
    redis_client.rpush.assert_called_once()
    call_args = redis_client.rpush.call_args
    assert call_args[0][0] == "transcription:queue"


def test_queue_size(redis_client):
    """Test getting queue size."""
    queue = TranscriptionQueue(redis_client)
    redis_client.llen.return_value = 5

    size = queue.size()

    assert size == 5
    redis_client.llen.assert_called_once_with("transcription:queue")


def test_dequeue_empty_queue(redis_client):
    """Test dequeuing from an empty queue."""
    queue = TranscriptionQueue(redis_client)
    redis_client.blpop.return_value = None

    item = queue.dequeue(timeout=1)

    assert item is None
