from .base import BaseRepository
from ..models.transcripts import Transcript
from ..models.transcript_edits import TranscriptEdit
from sqlalchemy import select
import uuid
from typing import Optional, List


class TranscriptRepository(BaseRepository[Transcript]):
    def __init__(self, session):
        super().__init__(Transcript, session)

    def get_by_job_id(self, job_id: uuid.UUID) -> Optional[Transcript]:
        stmt = select(Transcript).where(Transcript.job_id == job_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_language(self, language: str) -> List[Transcript]:
        stmt = select(Transcript).where(Transcript.language == language)
        return self.session.execute(stmt).scalars().all()

    def list_recent(self, limit: int = 50) -> List[Transcript]:
        stmt = select(Transcript).order_by(Transcript.created_at.desc()).limit(limit)
        return self.session.execute(stmt).scalars().all()


class TranscriptEditRepository(BaseRepository[TranscriptEdit]):
    def __init__(self, session):
        super().__init__(TranscriptEdit, session)

    def get_history_by_transcript_id(self, transcript_id: uuid.UUID) -> List[TranscriptEdit]:
        stmt = (
            select(TranscriptEdit)
            .where(TranscriptEdit.transcript_id == transcript_id)
            .order_by(TranscriptEdit.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def list_by_user_id(self, user_id: uuid.UUID) -> List[TranscriptEdit]:
        stmt = (
            select(TranscriptEdit)
            .where(TranscriptEdit.user_id == user_id)
            .order_by(TranscriptEdit.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()
