"""Job Manager service for creating and managing transcription jobs."""

import uuid
from typing import Any

import requests
from poly_redis.queue import TranscriptionQueue, TranscriptionWorkItem
from sqlalchemy.orm import Session

from poly_core.constants import PLAN_LIMITS, SUPPORTED_LANGUAGES, PlanType
from poly_core.services.storage_service import StorageBackend
from poly_db.models.teams import Team
from poly_db.models.transcription_jobs import JobStatus, TranscriptionJob
from poly_db.repositories import (
    AudioAssetRepository,
    TranscriptionJobRepository,
)


class JobManagerService:
    def __init__(
        self,
        session: Session,
        storage_backend: StorageBackend,
        billing_service,
        queue: TranscriptionQueue,
    ):
        self.session = session
        self.storage = storage_backend
        self.billing = billing_service
        self.job_repo = TranscriptionJobRepository(session)
        self.audio_repo = AudioAssetRepository(session)
        self.queue = queue

    def create_job_from_upload(  # noqa: PLR0913
        self,
        team_id: uuid.UUID,
        _user_id: uuid.UUID,
        file_content: bytes,
        filename: str,
        mime_type: str,
        file_size: int,
        options: dict[str, Any],
    ) -> TranscriptionJob:
        """Create transcription job from file upload.

        Args:
            team_id: Team ID
            user_id: User ID creating the job
            file_content: File bytes
            filename: Original filename
            mime_type: MIME type of file
            file_size: Size in bytes
            options: Transcription options (language, engine, timestamps, diarization)

        Returns:
            Created TranscriptionJob

        Raises:
            ValueError: If upload limit exceeded
        """
        can_upload, reason = self.billing.check_upload_limit(team_id)
        if not can_upload:
            raise ValueError(reason)

        requested_language = options.get("language")
        if not self._check_language_available(team_id, requested_language):
            raise ValueError("Requested language not available in plan")

        storage_uri = self.storage.save(file_content, filename, mime_type)

        job = self.job_repo.create(
            team_id=team_id,
            status=JobStatus.QUEUED,
            requested_language=requested_language,
            engine=options.get("engine"),
            options={
                "timestamps": options.get("timestamps", True),
                "diarization": options.get("diarization", False),
            },
        )

        self.audio_repo.create(
            job_id=job.id,
            storage_uri=storage_uri,
            filename=filename,
            mime_type=mime_type,
            file_size=file_size,
        )

        self.billing.increment_usage(team_id, job.id)

        work_item = TranscriptionWorkItem(
            job_id=job.id,
            audio_ref=storage_uri,
            requested_language=requested_language,
            engine=options.get("engine"),
            options=options,
        )
        self.queue.enqueue(work_item)

        return job

    def create_job_from_url(  # noqa: PLR0913
        self,
        team_id: uuid.UUID,
        _user_id: uuid.UUID,
        url: str,
        filename: str,
        options: dict[str, Any],
    ) -> TranscriptionJob:
        """Create transcription job from URL.

        Args:
            team_id: Team ID
            user_id: User ID creating the job
            url: URL to download audio from
            filename: Original filename
            options: Transcription options (language, engine, timestamps, diarization)

        Returns:
            Created TranscriptionJob

        Raises:
            ValueError: If upload limit exceeded or URL download fails
        """
        can_upload, reason = self.billing.check_upload_limit(team_id)
        if not can_upload:
            raise ValueError(reason)

        requested_language = options.get("language")
        if not self._check_language_available(team_id, requested_language):
            raise ValueError("Requested language not available in plan")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            file_content = response.content
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download file from URL: {e}") from e

        mime_type = response.headers.get("Content-Type", "audio/mpeg")
        file_size = len(file_content)

        storage_uri = self.storage.save(file_content, filename, mime_type)

        job = self.job_repo.create(
            team_id=team_id,
            status=JobStatus.QUEUED,
            requested_language=requested_language,
            engine=options.get("engine"),
            options={
                "timestamps": options.get("timestamps", True),
                "diarization": options.get("diarization", False),
            },
        )

        self.audio_repo.create(
            job_id=job.id,
            storage_uri=storage_uri,
            filename=filename,
            mime_type=mime_type,
            file_size=file_size,
        )

        self.billing.increment_usage(team_id, job.id)

        work_item = TranscriptionWorkItem(
            job_id=job.id,
            audio_ref=storage_uri,
            requested_language=requested_language,
            engine=options.get("engine"),
            options=options,
        )
        self.queue.enqueue(work_item)

        return job

    def _check_language_available(self, team_id: uuid.UUID, language: str | None) -> bool:
        """Check if language is available in team's plan.

        Args:
            team_id: Team ID
            language: Requested language code (None = auto-detect)

        Returns:
            True if language is available, False otherwise
        """
        if language is None:
            return True

        team = self.job_repo.session.query(Team).filter(Team.id == team_id).first()
        if not team:
            return False

        if language not in SUPPORTED_LANGUAGES:
            return False

        limits = PLAN_LIMITS.get(team.plan, PLAN_LIMITS[PlanType.FREE])
        max_languages = limits["languages"]

        if max_languages >= len(SUPPORTED_LANGUAGES):
            return True

        allowed = []
        if team.host_language in SUPPORTED_LANGUAGES:
            allowed.append(team.host_language)
        for lang in SUPPORTED_LANGUAGES:
            if lang not in allowed:
                allowed.append(lang)
            if len(allowed) >= max_languages:
                break

        return language in allowed
