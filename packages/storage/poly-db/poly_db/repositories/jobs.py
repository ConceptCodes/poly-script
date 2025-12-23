from .base import BaseRepository
from ..models.transcription_jobs import TranscriptionJob, JobStatus
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

    def get_by_status(self, status: JobStatus) -> List[TranscriptionJob]:
        stmt = select(TranscriptionJob).where(TranscriptionJob.status == status)
        return self.session.execute(stmt).scalars().all()

    def get_by_team_and_status(self, team_id: uuid.UUID, status: JobStatus) -> List[TranscriptionJob]:
        stmt = select(TranscriptionJob).where(
            TranscriptionJob.team_id == team_id,
            TranscriptionJob.status == status
        )
        return self.session.execute(stmt).scalars().all()

class AudioAssetRepository(BaseRepository[AudioAsset]):
    def __init__(self, session):
        super().__init__(AudioAsset, session)
        
    def get_by_job_id(self, job_id: uuid.UUID) -> Optional[AudioAsset]:
        stmt = select(AudioAsset).where(AudioAsset.job_id == job_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_storage_uri(self, storage_uri: str) -> Optional[AudioAsset]:
        stmt = select(AudioAsset).where(AudioAsset.storage_uri == storage_uri)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_team_id(self, team_id: uuid.UUID) -> List[AudioAsset]:
        stmt = (
            select(AudioAsset)
            .join(TranscriptionJob, AudioAsset.job_id == TranscriptionJob.id)
            .where(TranscriptionJob.team_id == team_id)
        )
        return self.session.execute(stmt).scalars().all()
