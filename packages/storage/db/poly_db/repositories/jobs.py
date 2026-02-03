import uuid

from sqlalchemy import select

from poly_db.models.audio_assets import AudioAsset
from poly_db.models.transcription_jobs import JobStatus, TranscriptionJob
from poly_db.repositories.base import BaseRepository


class TranscriptionJobRepository(BaseRepository[TranscriptionJob]):
    def __init__(self, session):
        super().__init__(TranscriptionJob, session)

    def get_by_team_id(self, team_id: uuid.UUID) -> list[TranscriptionJob]:
        stmt = select(TranscriptionJob).where(TranscriptionJob.team_id == team_id)
        return self.session.execute(stmt).scalars().all()

    def get_by_status(self, team_id: uuid.UUID, status: JobStatus) -> list[TranscriptionJob]:
        stmt = select(TranscriptionJob).where(
            TranscriptionJob.team_id == team_id, TranscriptionJob.status == status
        )
        return self.session.execute(stmt).scalars().all()

    def get_by_team_and_status(
        self, team_id: uuid.UUID, status: JobStatus
    ) -> list[TranscriptionJob]:
        stmt = select(TranscriptionJob).where(
            TranscriptionJob.team_id == team_id, TranscriptionJob.status == status
        )
        return self.session.execute(stmt).scalars().all()


class AudioAssetRepository(BaseRepository[AudioAsset]):
    def __init__(self, session):
        super().__init__(AudioAsset, session)

    def get_by_job_id(self, job_id: uuid.UUID) -> AudioAsset | None:
        stmt = select(AudioAsset).where(AudioAsset.job_id == job_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_storage_uri(self, team_id: uuid.UUID, storage_uri: str) -> AudioAsset | None:
        stmt = (
            select(AudioAsset)
            .join(TranscriptionJob, AudioAsset.job_id == TranscriptionJob.id)
            .where(AudioAsset.storage_uri == storage_uri, TranscriptionJob.team_id == team_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_team_id(self, team_id: uuid.UUID) -> list[AudioAsset]:
        stmt = (
            select(AudioAsset)
            .join(TranscriptionJob, AudioAsset.job_id == TranscriptionJob.id)
            .where(TranscriptionJob.team_id == team_id)
        )
        return self.session.execute(stmt).scalars().all()


# Backward-compatible alias used by core services
JobRepository = TranscriptionJobRepository
