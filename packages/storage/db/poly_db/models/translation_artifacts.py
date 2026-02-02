import enum
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Text, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import uuid


class TranslationStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class TranslationArtifact(Base, TimestampMixin):
    __tablename__ = "translation_artifacts"
    __table_args__ = (
        Index('ix_translation_artifacts_job_id', 'job_id'),
        Index('ix_translation_artifacts_status', 'status'),
        Index('ix_translation_artifacts_target_language', 'target_language'),
        Index('ix_translation_artifacts_created_at', 'created_at'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transcription_jobs.id", ondelete="CASCADE"), unique=True
    )
    status: Mapped[TranslationStatus] = mapped_column(
        SQLEnum(TranslationStatus), default=TranslationStatus.PENDING
    )
    target_language: Mapped[str] = mapped_column(String(10), nullable=False)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    segments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    engine: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    engine_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    job: Mapped["TranscriptionJob"] = relationship(back_populates="translation_artifact")

    def __repr__(self):
        return f"<TranslationArtifact(id={self.id}, job_id={self.job_id}, status={self.status})>"
