"""
Worker Service Entry Point

Standalone worker service that processes transcription jobs from Redis queue.
Runs with a dedicated consumer thread and its own event loop.
"""

import logging
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "storage" / "db"))
sys.path.insert(
    0, str(Path(__file__).parent.parent / "packages" / "storage" / "poly-redis")
)
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "stt"))

from src.config import get_settings
from src.worker_service import SimpleWorker

from poly_stt.bootstrap import initialize_engines

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def start_worker():
    """Start the transcription worker service."""
    logger.info("🚀 Starting PolyScript Worker Service...")

    # Load settings
    settings = get_settings()

    # Initialize STT engines
    initialize_engines()
    logger.info("✅ STT engines initialized")

    # Create and start worker
    worker = SimpleWorker()
    worker.start()
    logger.info("✅ Worker service started")

    return worker


if __name__ == "__main__":
    import signal

    worker = None

    def signal_handler(sig, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {sig}, shutting down...")
        if worker:
            worker.stop()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start worker
        worker = start_worker()

        # Keep main thread alive
        logger.info("Worker is running. Press Ctrl+C to stop.")

        # Main thread just keeps alive
        import time

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        if worker:
            worker.stop()
        logger.info("✅ Worker service stopped")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        if worker:
            worker.stop()
        sys.exit(1)
