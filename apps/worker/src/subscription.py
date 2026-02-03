import json
from collections.abc import AsyncGenerator
from typing import Any

try:
    import redis
except ImportError:
    redis = None


class ProgressSubscriber:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._redis_client = redis.from_url(redis_url, decode_responses=True)
        self._pubsub = None

    async def subscribe_to_job(self, job_id: str) -> AsyncGenerator[dict[str, Any], None]:
        channel = f"job:{job_id}:progress"

        pubsub = self._redis_client.pubsub()
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])

                    yield data

                    if data.get("status") in ["SUCCEEDED", "FAILED", "CANCELED"]:
                        break
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    def publish_progress(
        self,
        job_id: str,
        status: str,
        progress_pct: int,
        progress_stage: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        message = {
            "job_id": job_id,
            "status": status,
            "progress_pct": progress_pct,
            "progress_stage": progress_stage,
            "error_code": error_code,
            "error_message": error_message,
        }

        self._redis_client.publish(f"job:{job_id}:progress", json.dumps(message))

    def publish_segment_update(
        self,
        job_id: str,
        segment: dict[str, Any],
    ) -> None:
        message = {
            "job_id": job_id,
            "status": "RUNNING",
            "segment": segment,
        }

        self._redis_client.publish(f"job:{job_id}:segments", json.dumps(message))
