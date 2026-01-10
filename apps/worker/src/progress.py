from typing import Optional
from .enums import ProgressStage, WorkerStatus

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis not available. Install with: pip install redis")


class ProgressPublisher:
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis package not available. Install with: pip install redis")
        self._redis_client = redis.from_url(redis_url, decode_responses=True)
    
    def publish_progress(
        self,
        job_id: str,
        status: WorkerStatus,
        progress_pct: int,
        progress_stage: Optional[ProgressStage] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        message: dict[str, object] = {
            "job_id": job_id,
            "status": status.value,
            "progress_pct": progress_pct,
            "progress_stage": progress_stage.value if progress_stage else None,
            "error_code": error_code,
            "error_message": error_message,
        }
        
        self._redis_client.publish(
            f"job:{job_id}:progress",
            str(message)
        )
    
    def publish_segment_update(
        self,
        job_id: str,
        segment: dict[str, object],
    ) -> None:
        message: dict[str, object] = {
            "job_id": job_id,
            "status": WorkerStatus.RUNNING.value,
            "segment": segment,
        }
        
        self._redis_client.publish(
            f"job:{job_id}:segments",
            str(message)
        )