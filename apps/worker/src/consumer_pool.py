import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from poly_redis.queue import TranscriptionQueue
from poly_db.models.transcription_jobs import JobStatus
from poly_db.repositories import TranscriptionJobRepository
from .processor import JobProcessor
from .progress import ProgressPublisher

logger = logging.getLogger(__name__)


class ConcurrentConsumer:
    """Thread pool consumer for parallel job processing.
    
    Handles multiple jobs concurrently using ThreadPoolExecutor.
    Each job gets its own database session and processor instance.
    Translation is CPU-bound, so parallel jobs prevent GPU conflicts.
    """
    
    def __init__(
        self,
        queue: TranscriptionQueue,
        storage_backend,
        max_workers: int = 4,  # Adjust based on your GPU
        max_retries: int = 3,
        retry_backoff: int = 2,
    ):
        """Initialize consumer.
        
        Args:
            queue: TranscriptionQueue instance
            max_workers: Number of concurrent jobs (default: 4)
            max_retries: Maximum retry attempts (default: 3)
            retry_backoff: Exponential backoff base (default: 2)
        """
        self.queue = queue
        self.storage_backend = storage_backend
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.progress_publisher = ProgressPublisher(queue.redis)
        self._shutdown = False
        self._active_jobs: Dict[str, Dict[str, Any]] = {}  # Track job processing state
    
    def start(self) -> None:
        """Start thread pool consumer."""
        if self.executor._shutdown:
            logger.warning("Consumer executor already shut down")
            return
        
        logger.info(f"Starting concurrent consumer with {self.max_workers} workers")
        self._shutdown.clear()
        
        try:
            while not self._shutdown.is_set():
                try:
                    # Dequeue with timeout to check shutdown flag
                    work_item = self.queue.dequeue(timeout=1.0)
                    
                    if work_item:
                        self._process_work_item(work_item)
                except Exception as e:
                    logger.error(f"Error in consumer loop: {e}")
                    time.sleep(0.1)  # Small sleep to prevent tight error loop
        except KeyboardInterrupt:
            logger.info("Consumer thread interrupted by user")
            self.stop()
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            self.stop()
            raise
        
        logger.info("Consumer loop exited")
    
    def stop(self) -> None:
        """Stop thread pool consumer."""
        logger.info("Stopping concurrent consumer...")
        self._shutdown.set()
        
        # Wait for active jobs to complete (max 30s)
        if self._active_jobs:
            logger.info(f"Waiting for {len(self._active_jobs)} active jobs to complete...")
            futures = [job_info.get("future") for job_info in self._active_jobs.values()]
            
            try:
                as_completed(futures, timeout=30.0)
                logger.info("All active jobs completed")
            except Exception as e:
                logger.warning(f"Shutdown timeout: {e}")
        
        # Cancel pending futures
        for job_id, job_info in list(self._active_jobs.items()):
            future = job_info.get("future")
            if future and not future.done():
                future.cancel()
                logger.debug(f"Cancelled job {job_id}")
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        logger.info("Concurrent consumer stopped")
    
    def _process_work_item(self, work_item: dict) -> None:
        """Process a work item from queue.
        
        Creates a dedicated processor for each job with its own session.
        Jobs are tracked and can complete in parallel.
        """
        job_id = work_item.get("job_id")
        audio_ref = work_item.get("audio_ref")
        requested_language = work_item.get("requested_language")
        target_language = work_item.get("target_language")
        engine = work_item.get("engine")
        options = work_item.get("options", {})
        
        # Check if job is already being processed (prevent duplicate work)
        if job_id in self._active_jobs:
            logger.warning(f"Job {job_id} already being processed, skipping duplicate")
            return
        
        try:
            # Import here to avoid circular dependencies
            from poly_db.database import get_db_session
            
            # Create processor for this specific job
            with get_db_session() as session:
                processor = JobProcessor(
                    session=session,
                    storage_backend=self.storage_backend,
                    progress_publisher=self.progress_publisher,
                )
                
                # Process job
                success = processor.process_job(
                    job_id=job_id,
                    audio_ref=audio_ref,
                    requested_language=requested_language,
                    target_language=target_language,
                    engine=engine,
                    options=options,
                )
                
                # Handle retry logic if failed
                if not success:
                    self._handle_job_failure(session, job_id, work_item)
        except Exception as e:
            logger.error(f"Unhandled error processing job {job_id}: {e}")
            # Mark job as failed
            self._mark_job_failed(job_id, str(e))
    
    def _handle_job_failure(self, session: Session, job_id: str, work_item: dict) -> None:
        """Handle job failure with retry logic.
        
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
            delay = self.retry_backoff ** job.attempts
            logger.info(
                f"Retrying job {job_id} "
                f"(attempt {job.attempts + 1}/{self.max_retries}) "
                f"in {delay}s"
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
            session.commit()\n        else:
            # Max retries reached - already marked as FAILED by processor
            logger.error(
                f"Job {job_id} failed after {job.attempts} attempts"
            )
    
    def _mark_job_failed(self, job_id: str, error_message: str) -> None:
        """Mark a job as failed (emergency fallback).
        """
        try:
            from poly_db.database import get_db_session
            from poly_db.repositories import TranscriptionJobRepository
            
            with get_db_session() as session:
                job_repo = TranscriptionJobRepository(session)
                job = job_repo.get(job_id)
                
                if job:
                    job_repo.update(
                        job_id,
                        status=JobStatus.FAILED,
                        progress=0,
                        progress_stage="failed",
                        error_message=error_message,
                        finished_at=datetime.now(timezone.utc),
                    )
                    session.commit()
        except Exception as e:
            logger.error(f"Failed to mark job {job_id} as failed: {e}")
    
    def _on_job_completed(self, job_id: str, future: 'as_completed') -> None:
        """Handle job completion callback.
        """
        # Remove from active jobs tracking
        if job_id in self._active_jobs:
            del self._active_jobs[job_id]
            logger.debug(f"Job {job_id} removed from active tracking")
