"""
Progress Publisher for Job Processing

Publishes job progress updates to Redis Pub/Sub for real-time UI updates.
"""
import json
import logging
from typing import Optional

from poly_redis.client import get_redis_client
from .enums import ProgressStage, WorkerStatus

logger = logging.getLogger(__name__)


class ProgressPublisher:
    """Publishes job progress updates to Redis Pub/Sub."""

    def __init__(self):
        self.redis_client = get_redis_client()

    def publish_progress(
        self,
        job_id: str,
        team_id: str,
        progress_pct: int,
        progress_stage: str,
        status: str = "RUNNING",
        error_message: Optional[str] = None,
    ) -> None:
        """
        Publish progress update to Redis Pub/Sub channel.

        Args:
            job_id: Job identifier
            team_id: Team identifier for job
            progress_pct: Progress percentage (0-100)
            progress_stage: Current processing stage
            status: Job status (QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELED)
            error_message: Error message if failed
        """
        channel = f"job:{job_id}:progress"

        payload = {
            "job_id": job_id,
            "team_id": team_id,
            "status": status,
            "progress_pct": progress_pct,
            "progress_stage": progress_stage,
            "error_message": error_message,
        }

        try:
            self.redis_client.publish(channel, json.dumps(payload))
            logger.debug(
                f"[Progress] Job {job_id}: {progress_pct}% ({progress_stage})"
            )
        except Exception as e:
            logger.error(f"[Progress] Failed to publish for job {job_id}: {e}")

    def publish_stage_complete(
        self,
        job_id: str,
        team_id: str,
        stage: str,
        next_stage: Optional[str] = None,
    ) -> None:
        """
        Publish completion of a processing stage.

        Args:
            job_id: Job identifier
            team_id: Team identifier
            stage: Completed stage name
            next_stage: Next stage (for logging)
        """
        progress_pct = self._get_stage_progress(stage)

        self.publish_progress(
            job_id=job_id,
            team_id=team_id,
            progress_pct=progress_pct,
            progress_stage=stage,
            status="RUNNING",
        )

        logger.info(
            f"[Progress] Job {job_id} completed stage '{stage}' ({progress_pct}%)"
        )

    @staticmethod
    def _get_stage_progress(stage: str) -> int:
        """
        Get progress percentage for a given stage.

        Args:
            stage: Processing stage name

        Returns:
            Progress percentage (0-100)
        """
        stage_progress = {
            "starting": 0,
            "downloading": 10,
            "decoding": 20,
            "transcribing": 90,
            "formatting": 95,
            "saving": 100,
            "completed": 100,
            "failed": 0,
            "canceled": 0,
        }
        return stage_progress.get(stage, 0)