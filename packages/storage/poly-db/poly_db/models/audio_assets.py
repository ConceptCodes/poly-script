from typing import Optional
from sqlalchemy import String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import uuid


class AudioAsset(Base, TimestampMixin):
    __tablename__ = "audio_assets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transcription_jobs.id", ondelete="CASCADE"), unique=True
    )
    storage_uri: Mapped[str] = mapped_column(String(1000))  # e.g., 'local://...', 's3://...'
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column(BigInteger)  # in bytes
    duration_seconds: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Relationships
    job: Mapped["TranscriptionJob"] = relationship(back_populates="audio_asset")

    def __repr__(self):
        return f"<AudioAsset(id={self.id}, filename={self.filename})>"
