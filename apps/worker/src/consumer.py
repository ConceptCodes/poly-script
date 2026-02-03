"""
Transcription Consumer Thread

Consumer thread that processes transcription jobs from Redis queue.
Implements retry logic with exponential backoff and graceful shutdown.
"""

import asyncio
import logging
import threading
import time
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from poly_db.database import get_db_session
from poly_db.models.transcription_jobs import JobStatus
from poly_db.repositories import TranscriptionJobRepository
from poly_redis.queue import TranscriptionQueue

from .processor import JobProcessor
from .progress import ProgressPublisher

logger = logging.getLogger(__name__)


class TranscriptionConsumer:
    """Consumer thread that processes transcription jobs from Redis queue."""

    def __init__(
        self,
        queue: TranscriptionQueue,
        storage_backend,
        max_retries: int = 3,
        retry_backoff: int = 2,
    ):
        """
        Initialize consumer.

        Args:
            queue: TranscriptionQueue instance
            max_retries: Maximum retry attempts (default: 3)
            retry_backoff: Exponential backoff base (default: 2)
        """
        self.queue = queue
        self.storage_backend = storage_backend
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        self._thread: threading.Thread | None = None
        self._shutdown = threading.Event()
        self._current_job_id: str | None = None

        self.progress_publisher = ProgressPublisher()

    def start(self) -> None:
        """Start consumer thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Consumer thread already running")
            return

        self._shutdown.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="TranscriptionConsumer",
            daemon=True,
        )
        self._thread.start()
        logger.info("Consumer thread started")

    def stop(self) -> None:
        """Stop consumer thread gracefully."""
        if not self._thread or not self._thread.is_alive():
            logger.warning("Consumer thread not running")
            return

        logger.info("Stopping consumer thread...")
        self._shutdown.set()

        # Wait for thread to finish current job (max 30s)
        self._thread.join(timeout=30)

        if self._thread.is_alive():
            logger.warning("Consumer thread did not stop gracefully")
        else:
            logger.info("Consumer thread stopped")

    def _run(self) -> None:
        """Main consumer loop with dedicated event loop."""
        logger.info("Consumer loop started with dedicated event loop")

        # Create and run dedicated event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the consumer loop in the event loop
            loop.run_until_complete(self._run_with_event_loop())
        finally:
            # Clean up event loop
            loop.close()
            logger.info("Consumer event loop closed")

        logger.info("Consumer loop exited")

    async def _run_with_event_loop(self) -> None:
        """Async consumer loop running in dedicated event loop."""
        logger.info("Async consumer loop running")

        while not self._shutdown.is_set():
            try:
                # Run dequeue in thread pool to avoid blocking event loop
                work_item = await asyncio.to_thread(self.queue.dequeue, timeout=1)

                if work_item:
                    # Process work item
                    await asyncio.to_thread(self._process_work_item, work_item)

            except Exception as e:
                logger.error(f"Error in consumer loop: {e}", exc_info=True)
                # Sleep briefly to avoid tight error loop
                await asyncio.sleep(1)

    def _process_work_item(self, work_item: dict) -> None:
        """
        Process a single work item from queue.

        Args:
            work_item: Work item with job_id, audio_ref, options, etc.
        """
        job_id = work_item.get("job_id")
        audio_ref = work_item.get("audio_ref")
        requested_language = work_item.get("requested_language")
        engine = work_item.get("engine")
        options = work_item.get("options", {})

        self._current_job_id = job_id

        logger.info(f"Processing job {job_id} (engine={engine}, language={requested_language})")

        try:
            with get_db_session() as session:
                # Create processor
                processor = JobProcessor(
                    session=session,
                    storage_backend=self.storage_backend,
                    progress_publisher=self.progress_publisher,
                )

                # Process job
                success = processor.process_job(job_id)

                # Handle retry logic if failed
                if not success:
                    self._handle_job_failure(session, job_id, work_item)

        except Exception as e:
            logger.error(
                f"Unhandled error processing job {job_id}: {e}",
                exc_info=True,
            )
            # Mark as failed
            self._mark_job_failed_in_db(job_id, str(e))

        finally:
            self._current_job_id = None

    def _handle_job_failure(self, session: Session, job_id: str, work_item: dict) -> None:
        """
        Handle job failure with retry logic.

        Args:
            session: Database session
            job_id: Job UUID
            work_item: Original work item for re-enqueue
        """
        job_repo = TranscriptionJobRepository(session)
        job = job_repo.get(job_id)

        if not job:
            logger.error(f"Job {job_id} not found for retry handling")
            return

        # Check if we should retry
        if job.attempts < self.max_retries:
            # Calculate backoff delay
            delay = self.retry_backoff**job.attempts
            logger.info(
                f"Retrying job {job_id} (attempt {job.attempts + 1}/{self.max_retries}) in {delay}s"
            )

            # Re-enqueue with delay
            time.sleep(delay)
            self.queue.enqueue(work_item)

            # Update job status back to QUEUED
            job_repo.update(
                job_id,
                status=JobStatus.QUEUED,
                progress=0,
                progress_stage="queued",
            )
            session.commit()
        else:
            # Max retries reached - already marked as FAILED by processor
            logger.error(f"Job {job_id} failed after {job.attempts} attempts")

    def _mark_job_failed_in_db(self, job_id: str, error_message: str) -> None:
        """
        Mark a job as failed (emergency fallback).

        Args:
            job_id: Job UUID
            error_message: Error message to store
        """
        try:
            with get_db_session() as session:
                from poly_db.repositories import TranscriptionJobRepository

                job_repo = TranscriptionJobRepository(session)
                job_repo.update(
                    job_id,
                    status=JobStatus.FAILED,
                    progress=0,
                    progress_stage="failed",
                    error_message=error_message,
                    finished_at=datetime.now(UTC),
                )
                session.commit()
        except Exception as e:
            logger.error(f"Failed to mark job {job_id} as failed: {e}")

    @property
    def is_running(self) -> bool:
        """Check if consumer is running."""
        return self._thread is not None and self._thread.is_alive()

    @property
    def current_job_id(self) -> str | None:
        """Get currently processing job ID."""
        return self._current_job_id
