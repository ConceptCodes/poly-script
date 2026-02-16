"""Async version of Job repositories for use with SQLAlchemy AsyncSession."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from poly_db.models.audio_assets import AudioAsset
from poly_db.models.transcription_jobs import JobStatus, TranscriptionJob
from poly_db.repositories.base_async import BaseRepositoryAsync


class TranscriptionJobRepositoryAsync(BaseRepositoryAsync[TranscriptionJob]):
    """Async repository for TranscriptionJob operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(TranscriptionJob, session)

    async def get_by_team_id(self, team_id: uuid.UUID) -> list[TranscriptionJob]:
        """Get all transcription jobs for a specific team."""
        stmt = select(TranscriptionJob).where(TranscriptionJob.team_id == team_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, team_id: uuid.UUID, status: JobStatus) -> list[TranscriptionJob]:
        """Get all transcription jobs for a specific team with a given status."""
        stmt = select(TranscriptionJob).where(
            TranscriptionJob.team_id == team_id, TranscriptionJob.status == status
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_team_and_status(
        self, team_id: uuid.UUID, status: JobStatus
    ) -> list[TranscriptionJob]:
        """Get all transcription jobs for a specific team with a given status."""
        stmt = select(TranscriptionJob).where(
            TranscriptionJob.team_id == team_id, TranscriptionJob.status == status
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class AudioAssetRepositoryAsync(BaseRepositoryAsync[AudioAsset]):
    """Async repository for AudioAsset operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(AudioAsset, session)

    async def get_by_job_id(self, job_id: uuid.UUID) -> AudioAsset | None:
        """Get an audio asset by its associated job ID."""
        stmt = select(AudioAsset).where(AudioAsset.job_id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_storage_uri(self, team_id: uuid.UUID, storage_uri: str) -> AudioAsset | None:
        """Get an audio asset by its storage URI within a team."""
        stmt = (
            select(AudioAsset)
            .join(TranscriptionJob, AudioAsset.job_id == TranscriptionJob.id)
            .where(AudioAsset.storage_uri == storage_uri, TranscriptionJob.team_id == team_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_team_id(self, team_id: uuid.UUID) -> list[AudioAsset]:
        """List all audio assets for a specific team."""
        stmt = (
            select(AudioAsset)
            .join(TranscriptionJob, AudioAsset.job_id == TranscriptionJob.id)
            .where(TranscriptionJob.team_id == team_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


# Backward-compatible alias used by core services
JobRepositoryAsync = TranscriptionJobRepositoryAsync


__all__ = [
    "AudioAssetRepositoryAsync",
    "JobRepositoryAsync",
    "TranscriptionJobRepositoryAsync",
]
