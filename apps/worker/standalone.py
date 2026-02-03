#!/usr/bin/env python3
"""Standalone worker entry point for Railway deployment."""
import os
import signal
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import concurrent consumer
from src.consumer_pool import ConcurrentConsumer  # noqa: E402


def run_worker():
    """Run concurrent worker with thread pool."""
    # Import configuration
    from src.config import get_settings
    settings = get_settings()
    
    # Get Redis client
    from poly_redis.client import get_redis_client
    redis = get_redis_client()
    
    # Get storage backend
    from poly_core.services.storage_service import get_storage_backend
    storage_backend = get_storage_backend(
        backend_type=settings.STORAGE_BACKEND,
        storage_path=settings.STORAGE_PATH,
        min_free_bytes=settings.STORAGE_MIN_FREE_BYTES,
        bucket=settings.AWS_S3_BUCKET,
        region=settings.AWS_REGION,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    
    # Initialize concurrent consumer
    max_workers = int(os.getenv("MAX_WORKERS", "4"))
    consumer = ConcurrentConsumer(
        redis=redis,
        storage_backend=storage_backend,
        max_workers=max_workers,
    )
    
    # Setup shutdown handler
    def signal_handler(sig, _frame):
        logger.info("Received signal %s, shutting down...", sig)
        consumer.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGUSR1, signal_handler)
    
    logger.info("Starting concurrent worker...")
    try:
        consumer.start()
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
        consumer.stop()
    except Exception as e:
        logger.exception("Worker error: %s", e)
        consumer.stop()
        raise
    
    logger.info("Worker shutdown complete")

if __name__ == "__main__":
    run_worker()
