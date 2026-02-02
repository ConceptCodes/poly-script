from .base import BaseRepository
from ..models.translation_artifacts import TranslationArtifact
from ..models.transcription_jobs import TranscriptionJob
from sqlalchemy import select
import uuid
from typing import Optional, List


class TranslationArtifactRepository(BaseRepository[TranslationArtifact]):
    def __init__(self, session):
        super().__init__(TranslationArtifact, session)

    def get_by_job_id(
        self, team_id: uuid.UUID, job_id: uuid.UUID
    ) -> Optional[TranslationArtifact]:
        """Get translation artifact by job ID with team scoping."""
        stmt = (
            select(TranslationArtifact)
            .join(TranscriptionJob, TranslationArtifact.job_id == TranscriptionJob.id)
            .where(
                TranslationArtifact.job_id == job_id,
                TranscriptionJob.team_id == team_id,
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_team(
        self, team_id: uuid.UUID, target_language: Optional[str] = None
    ) -> List[TranslationArtifact]:
        """List all translation artifacts for a team, optionally filtered by language."""
        stmt = (
            select(TranslationArtifact)
            .join(TranscriptionJob, TranslationArtifact.job_id == TranscriptionJob.id)
            .where(TranscriptionJob.team_id == team_id)
        )
        
        if target_language:
            stmt = stmt.where(TranslationArtifact.target_language == target_language)
        
        stmt = stmt.order_by(TranslationArtifact.created_at.desc())
        
        return self.session.execute(stmt).scalars().all()

    def list_recent(self, team_id: uuid.UUID, limit: int = 50) -> List[TranslationArtifact]:
        """List recent translation artifacts for a team."""
        stmt = (
            select(TranslationArtifact)
            .join(TranscriptionJob, TranslationArtifact.job_id == TranscriptionJob.id)
            .where(TranscriptionJob.team_id == team_id)
            .order_by(TranslationArtifact.created_at.desc())
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()
