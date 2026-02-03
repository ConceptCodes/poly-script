import json
import logging
import threading
import time
from datetime import UTC, datetime

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SimpleWorker:
    def __init__(self):
        self._shutdown = threading.Event()
        if REDIS_AVAILABLE:
            self._redis_client = redis.Redis.from_url(
                "redis://localhost:6379/0", decode_responses=True
            )
        else:
            self._redis_client = None
            logger.warning("Redis not available - worker will run in mock mode")
        self._queue_key = "transcription:queue"

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()
        logger.info("Worker started transcription worker thread")

    def stop(self):
        self._shutdown.set()
        logger.info("Worker shutdown signal received")

    def _run(self):
        while not self._shutdown.is_set():
            try:
                result = self._redis_client.blpop(self._queue_key, timeout=1)
                if result:
                    _, data = result
                    work_item = json.loads(data)
                    self._process_job(work_item)
            except Exception as e:
                logger.exception("Worker error in main loop: %s", e)
                time.sleep(1)

    def _process_job(self, work_item: dict):
        try:
            job_id = work_item["job_id"]
            logger.info("Worker processing job %s", job_id)

            self._publish_progress(job_id, 0, "downloading")
            time.sleep(1)

            self._publish_progress(job_id, 20, "transcribing")
            time.sleep(2)

            self._publish_progress(job_id, 90, "saving")
            time.sleep(1)

            self._publish_progress(job_id, 100, "completed")

            logger.info("Worker completed job %s", job_id)

        except Exception as e:
            logger.exception(
                "Worker job %s failed: %s",
                work_item.get("job_id", "unknown"),
                e,
            )
            self._publish_progress(work_item.get("job_id", "unknown"), 0, "failed")

    def _publish_progress(self, job_id: str, progress: int, stage: str):
        message = {
            "job_id": job_id,
            "status": "RUNNING",
            "progress_pct": progress,
            "progress_stage": stage,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self._redis_client.publish(f"job:{job_id}:progress", json.dumps(message))
