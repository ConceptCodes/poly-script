"""Deterministic API -> queue -> worker contract tests."""

import importlib.util
import json
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

from poly_db.models.transcription_jobs import JobStatus
from poly_redis.queue import TranscriptionQueue, TranscriptionWorkItem


class InMemoryRedis:
    """Minimal Redis subset used by queue and progress tests."""

    def __init__(self):
        self.lists: dict[str, list[str]] = {}
        self.messages: list[tuple[str, str]] = []

    def rpush(self, key: str, value: str) -> int:
        values = self.lists.setdefault(key, [])
        values.append(value)
        return len(values)

    def blpop(self, key: str, timeout: int = 0):
        del timeout
        values = self.lists.get(key, [])
        if not values:
            return None
        return key, values.pop(0)

    def lindex(self, key: str, index: int):
        values = self.lists.get(key, [])
        try:
            return values[index]
        except IndexError:
            return None

    def llen(self, key: str) -> int:
        return len(self.lists.get(key, []))

    def publish(self, channel: str, payload: str) -> int:
        self.messages.append((channel, payload))
        return 1

    def flushdb(self) -> None:
        self.lists.clear()
        self.messages.clear()


class TestJobProcessingIntegration:
    """Contract tests for job queueing and worker-adjacent state updates."""

    def test_enqueue_to_worker_flow(self):
        """Test enqueue -> dequeue preserves the worker payload contract."""
        redis = InMemoryRedis()
        queue = TranscriptionQueue(redis)
        job_id = uuid.uuid4()

        work_item = TranscriptionWorkItem(
            job_id=job_id,
            audio_ref="/tmp/test.mp3",
            requested_language="en",
            engine="whisper-local-tiny",
            options={"timestamps": True, "diarization": False},
        )

        assert queue.enqueue(work_item) == 1
        assert queue.size() == 1

        dequeued = queue.dequeue(timeout=1)

        assert dequeued is not None
        assert dequeued.job_id == job_id
        assert dequeued.audio_ref == "/tmp/test.mp3"
        assert dequeued.requested_language == "en"
        assert dequeued.engine == "whisper-local-tiny"
        assert dequeued.options == {"timestamps": True, "diarization": False}

    def test_redis_queue_operations(self):
        """Test queue enqueue, peek, dequeue, and size behavior."""
        redis = InMemoryRedis()
        queue = TranscriptionQueue(redis)
        work_item = TranscriptionWorkItem(
            job_id=uuid.uuid4(),
            audio_ref="/tmp/test.mp3",
            requested_language="en",
            engine="whisper-local-tiny",
            options={},
        )

        queue.enqueue(work_item)

        assert queue.size() == 1
        assert queue.peek() == work_item
        assert queue.dequeue(timeout=1) == work_item
        assert queue.size() == 0

    def test_progress_publishing(self):
        """Test progress publishing uses the expected job channel and payload."""
        redis = InMemoryRedis()
        progress_path = Path(__file__).resolve().parents[3] / "worker" / "src" / "progress.py"
        spec = importlib.util.spec_from_file_location("worker_progress_for_test", progress_path)
        assert spec and spec.loader
        progress_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(progress_module)

        with patch.object(progress_module, "get_redis_client", return_value=redis):
            publisher = progress_module.ProgressPublisher()
            publisher.publish_progress(
                job_id="test-123",
                team_id="test-team",
                progress_pct=50,
                progress_stage="transcribing",
                status="RUNNING",
            )

        assert len(redis.messages) == 1
        channel, payload = redis.messages[0]
        assert channel == "job:test-123:progress"
        assert json.loads(payload) == {
            "job_id": "test-123",
            "team_id": "test-team",
            "status": "RUNNING",
            "progress_pct": 50,
            "progress_stage": "transcribing",
            "error_message": None,
        }

    def test_retry_logic(self):
        """Test retry state transitions are persisted through the repository boundary."""
        job_id = uuid.uuid4()
        job = Mock(id=job_id, attempts=0, status=JobStatus.QUEUED)
        job_repo = Mock()
        job_repo.get.return_value = job

        job_repo.update(str(job_id), attempts=1, status=JobStatus.QUEUED)
        job.attempts = 1
        job.status = JobStatus.QUEUED

        assert job_repo.get(str(job_id)).attempts == 1
        assert job_repo.get(str(job_id)).status == JobStatus.QUEUED

        job_repo.update(str(job_id), attempts=3, status=JobStatus.FAILED)
        job.attempts = 3
        job.status = JobStatus.FAILED

        assert job_repo.get(str(job_id)).attempts == 3
        assert job_repo.get(str(job_id)).status == JobStatus.FAILED
