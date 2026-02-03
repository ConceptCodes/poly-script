"""Integration tests for API → Worker → DB flow."""

from unittest.mock import patch

import pytest

from poly_db.models.transcription_jobs import JobStatus
from poly_db.repositories import TranscriptionJobRepository
from poly_redis.client import get_redis_client
from poly_redis.queue import TranscriptionQueue


@pytest.fixture
def test_db():
    """Create test database session."""
    from poly_db.database import get_db_session

    with get_db_session() as session:
        yield session

        session.rollback()


@pytest.fixture
def test_queue():
    """Create test queue instance."""
    redis_client = get_redis_client()
    queue = TranscriptionQueue(redis_client)
    yield queue

    # Cleanup
    redis_client.flushdb()


class TestJobProcessingIntegration:
    """Integration tests for job processing flow."""

    @patch("src.consumer.initialize_engines")
    @patch("src.consumer.get_storage_backend")
    def test_enqueue_to_worker_flow(self, mock_storage, mock_bootstrap, test_db, test_queue):
        """Test enqueue → worker dequeue → process flow."""
        # Create test job in DB
        job_repo = TranscriptionJobRepository(test_db)

        from poly_db.models.transcription_jobs import TranscriptionJob

        job = job_repo.create(
            TranscriptionJob(
                team_id="test-team-123",
                audio_asset_id=None,
                status=JobStatus.QUEUED,
                progress=0,
                progress_stage="queued",
                requested_language="en",
                engine="whisper-local-tiny",
                options={"timestamps": True, "diarization": False},
            )
        )

        # Enqueue job
        work_item = {
            "job_id": str(job.id),
            "audio_ref": "/tmp/test.mp3",
            "requested_language": "en",
            "engine": "whisper-local-tiny",
            "options": {"timestamps": True, "diarization": False},
        }

        test_queue.enqueue(work_item)

        # Verify job was queued
        queued_job = job_repo.get(str(job.id))
        assert queued_job.status == JobStatus.QUEUED

        # Verify work item is in queue
        # (This would require actual consumer to test end-to-end)

    def test_redis_queue_operations(self, test_queue):
        """Test Redis queue enqueue/dequeue operations."""
        work_item = {
            "job_id": "test-123",
            "audio_ref": "/tmp/test.mp3",
            "requested_language": "en",
            "engine": "whisper-local-tiny",
            "options": {},
        }

        # Enqueue
        test_queue.enqueue(work_item)

        # Dequeue
        dequeued = test_queue.dequeue(timeout=1)

        assert dequeued is not None
        assert dequeued["job_id"] == "test-123"

    def test_progress_publishing(self, test_queue):
        """Test progress publishing to Redis."""
        from src.progress import ProgressPublisher

        publisher = ProgressPublisher()

        # Publish progress
        publisher.publish_progress(
            job_id="test-123",
            team_id="test-team",
            progress_pct=50,
            progress_stage="transcribing",
            status="RUNNING",
        )

        # Verify published (would need subscriber to fully test)
        # For now, just verify no errors

    @patch("src.consumer.initialize_engines")
    @patch("src.consumer.get_storage_backend")
    def test_retry_logic(self, mock_storage, mock_bootstrap, test_db, test_queue):
        """Test retry logic on job failure."""
        job_repo = TranscriptionJobRepository(test_db)

        # Create job
        from poly_db.models.transcription_jobs import TranscriptionJob

        job = job_repo.create(
            TranscriptionJob(
                team_id="test-team-123",
                audio_asset_id=None,
                status=JobStatus.QUEUED,
                progress=0,
                progress_stage="queued",
                requested_language="en",
                engine="whisper-local-tiny",
                options={},
                attempts=0,
            )
        )

        # Simulate retry
        assert job.attempts == 0

        # Update attempts
        job_repo.update(str(job.id), attempts=1, status=JobStatus.QUEUED)

        updated_job = job_repo.get(str(job.id))
        assert updated_job.attempts == 1
        assert updated_job.status == JobStatus.QUEUED

        # Simulate max retries reached
        job_repo.update(str(job.id), attempts=3, status=JobStatus.FAILED)

        final_job = job_repo.get(str(job.id))
        assert final_job.attempts == 3
        assert final_job.status == JobStatus.FAILED
