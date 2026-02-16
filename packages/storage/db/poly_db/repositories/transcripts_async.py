"""Async version of Transcript repositories for use with SQLAlchemy AsyncSession."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from poly_db.models.transcript_edits import TranscriptEdit
from poly_db.models.transcription_jobs import TranscriptionJob
from poly_db.models.transcripts import Transcript
from poly_db.repositories.base_async import BaseRepositoryAsync


class TranscriptRepositoryAsync(BaseRepositoryAsync[Transcript]):
    """Async repository for Transcript operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Transcript, session)

    async def get_by_job_id(self, team_id: uuid.UUID, job_id: uuid.UUID) -> Transcript | None:
        """Get a transcript by its associated job ID within a team."""
        stmt = (
            select(Transcript)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(Transcript.job_id == job_id, TranscriptionJob.team_id == team_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_language(self, team_id: uuid.UUID, language: str) -> list[Transcript]:
        """List all transcripts for a specific team with a given language."""
        stmt = (
            select(Transcript)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(Transcript.language == language, TranscriptionJob.team_id == team_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent(self, team_id: uuid.UUID, limit: int = 50) -> list[Transcript]:
        """List the most recent transcripts for a specific team."""
        stmt = (
            select(Transcript)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(TranscriptionJob.team_id == team_id)
            .order_by(Transcript.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class TranscriptEditRepositoryAsync(BaseRepositoryAsync[TranscriptEdit]):
    """Async repository for TranscriptEdit operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(TranscriptEdit, session)

    async def get_history_by_transcript_id(
        self, team_id: uuid.UUID, transcript_id: uuid.UUID
    ) -> list[TranscriptEdit]:
        """Get the edit history for a specific transcript within a team."""
        stmt = (
            select(TranscriptEdit)
            .join(Transcript, TranscriptEdit.transcript_id == Transcript.id)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(
                TranscriptEdit.transcript_id == transcript_id,
                TranscriptionJob.team_id == team_id,
            )
            .order_by(TranscriptEdit.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_user_id(self, team_id: uuid.UUID, user_id: uuid.UUID) -> list[TranscriptEdit]:
        """List all transcript edits made by a specific user within a team."""
        stmt = (
            select(TranscriptEdit)
            .join(Transcript, TranscriptEdit.transcript_id == Transcript.id)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(TranscriptEdit.user_id == user_id, TranscriptionJob.team_id == team_id)
            .order_by(TranscriptEdit.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


__all__ = [
    "TranscriptEditRepositoryAsync",
    "TranscriptRepositoryAsync",
]
