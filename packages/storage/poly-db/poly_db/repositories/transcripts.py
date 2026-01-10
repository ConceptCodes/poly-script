from .base import BaseRepository
from ..models.transcripts import Transcript
from ..models.transcript_edits import TranscriptEdit
from ..models.transcription_jobs import TranscriptionJob
from sqlalchemy import select
import uuid
from typing import Optional, List


class TranscriptRepository(BaseRepository[Transcript]):
    def __init__(self, session):
        super().__init__(Transcript, session)

    def get_by_job_id(self, team_id: uuid.UUID, job_id: uuid.UUID) -> Optional[Transcript]:
        stmt = (
            select(Transcript)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(Transcript.job_id == job_id, TranscriptionJob.team_id == team_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_language(self, team_id: uuid.UUID, language: str) -> List[Transcript]:
        stmt = (
            select(Transcript)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(Transcript.language == language, TranscriptionJob.team_id == team_id)
        )
        return self.session.execute(stmt).scalars().all()

    def list_recent(self, team_id: uuid.UUID, limit: int = 50) -> List[Transcript]:
        stmt = (
            select(Transcript)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(TranscriptionJob.team_id == team_id)
            .order_by(Transcript.created_at.desc())
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()


class TranscriptEditRepository(BaseRepository[TranscriptEdit]):
    def __init__(self, session):
        super().__init__(TranscriptEdit, session)

    def get_history_by_transcript_id(
        self, team_id: uuid.UUID, transcript_id: uuid.UUID
    ) -> List[TranscriptEdit]:
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
        return self.session.execute(stmt).scalars().all()

    def list_by_user_id(self, team_id: uuid.UUID, user_id: uuid.UUID) -> List[TranscriptEdit]:
        stmt = (
            select(TranscriptEdit)
            .join(Transcript, TranscriptEdit.transcript_id == Transcript.id)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(TranscriptEdit.user_id == user_id, TranscriptionJob.team_id == team_id)
            .order_by(TranscriptEdit.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()
