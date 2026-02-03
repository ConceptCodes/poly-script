import logging
import threading

from apps.worker.src.consumer import TranscriptionConsumer

from poly_core.services.storage_service import get_storage_backend
from poly_redis.client import get_redis_client
from poly_redis.queue import TranscriptionQueue
from src.config import get_settings

logger = logging.getLogger(__name__)


class WorkerService:
    """Manages background worker for transcription jobs."""

    def __init__(self):
        self._consumer: TranscriptionConsumer | None = None
        self._shutdown = threading.Event()
        self._settings = get_settings()

    def start(self) -> None:
        """Start transcription worker."""
        if self._consumer:
            logger.warning("Worker already running")
            return

        logger.info("Starting transcription worker...")

        # Get configuration
        max_retries = getattr(self._settings, "QUEUE_MAX_RETRIES", 3)
        retry_backoff = getattr(self._settings, "QUEUE_RETRY_BACKOFF", 2)

        # Initialize queue
        redis_client = get_redis_client()
        queue = TranscriptionQueue(redis_client)

        # Initialize storage backend
        storage_backend = get_storage_backend(
            backend_type=self._settings.STORAGE_BACKEND,
            storage_path=self._settings.STORAGE_PATH,
            min_free_bytes=self._settings.STORAGE_MIN_FREE_BYTES,
            bucket=self._settings.AWS_S3_BUCKET,
            region=self._settings.AWS_REGION,
            access_key=self._settings.AWS_ACCESS_KEY_ID,
            secret_key=self._settings.AWS_SECRET_ACCESS_KEY,
        )

        # Create and start consumer
        self._consumer = TranscriptionConsumer(
            queue=queue,
            storage_backend=storage_backend,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
        )

        self._consumer.start()
        logger.info("Transcription worker started")

    def stop(self) -> None:
        """Stop transcription worker."""
        if not self._consumer:
            logger.warning("Worker not running")
            return

        logger.info("Stopping transcription worker...")
        self._consumer.stop()
        self._consumer = None
        self._shutdown.set()
        logger.info("Transcription worker stopped")

    @property
    def is_running(self) -> bool:
        """Check if worker is running."""
        return self._consumer is not None
