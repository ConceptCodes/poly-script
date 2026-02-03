"""
Worker Service

Manages the transcription consumer thread with graceful shutdown.
"""

import logging
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "storage" / "db"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "storage" / "poly-redis"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "stt"))

from src.config import get_settings
from src.consumer import TranscriptionConsumer

from poly_core.services.storage_service import get_storage_backend
from poly_redis.client import get_redis_client
from poly_redis.queue import TranscriptionQueue
from poly_stt.bootstrap import initialize_engines

logger = logging.getLogger(__name__)


class WorkerService:
    """Worker service that manages the consumer thread."""

    def __init__(self):
        settings = get_settings()

        # Initialize STT engines
        initialize_engines()

        # Initialize Redis client and queue
        self._redis_client = get_redis_client()
        self._queue = TranscriptionQueue(self._redis_client)

        # Initialize storage backend
        self._storage_backend = get_storage_backend()

        # Initialize consumer
        self._consumer = TranscriptionConsumer(
            queue=self._queue,
            storage_backend=self._storage_backend,
            max_retries=settings.QUEUE_MAX_RETRIES,
            retry_backoff=settings.QUEUE_RETRY_BACKOFF,
        )

    def start(self):
        """Start the worker service."""
        logger.info("Starting worker service...")
        self._consumer.start()
        logger.info("Worker service started")

    def stop(self):
        """Stop the worker service gracefully."""
        logger.info("Stopping worker service...")
        self._consumer.stop()
        logger.info("Worker service stopped")

    @property
    def is_running(self) -> bool:
        """Check if worker is running."""
        return self._consumer.is_running

    @property
    def current_job_id(self) -> str | None:
        """Get currently processing job ID."""
        return self._consumer.current_job_id
