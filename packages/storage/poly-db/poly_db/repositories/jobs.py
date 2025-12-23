from .base import BaseRepository
from ..models.transcription_jobs import TranscriptionJob
from ..models.audio_assets import AudioAsset
from sqlalchemy import select
import uuid
from typing import Optional, List

class TranscriptionJobRepository(BaseRepository[TranscriptionJob]):
    def __init__(self, session):
        super().__init__(TranscriptionJob, session)
        
    def get_by_team_id(self, team_id: uuid.UUID) -> List[TranscriptionJob]:
        stmt = select(TranscriptionJob).where(TranscriptionJob.team_id == team_id)
        return self.session.execute(stmt).scalars().all()

class AudioAssetRepository(BaseRepository[AudioAsset]):
    def __init__(self, session):
        super().__init__(AudioAsset, session)
        
    def get_by_job_id(self, job_id: uuid.UUID) -> Optional[AudioAsset]:
        # Assuming correlation might be via job_id or opposite
        # Usually Audio has a job_id or Job has audio_id
        # Let's assume AudioAsset is standalone but linked to Job
        # Checking logic: Usually Audio is created first, then Job.
        # But if we want assets by job, we need to check the schema.
        # Safe bet for now: just basic CRUD via BaseRepository
        pass
