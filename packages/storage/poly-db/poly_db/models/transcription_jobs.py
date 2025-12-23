from typing import List, Optional
from sqlalchemy import String, ForeignKey, Integer, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import enum
import uuid


class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class TranscriptionJob(Base, TimestampMixin):
    __tablename__ = "transcription_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus), default=JobStatus.QUEUED)
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100

    # Processing options
    requested_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    engine: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    options: Mapped[dict] = mapped_column(JSON, default=dict)

    # Error info
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    team: Mapped["Team"] = relationship(back_populates="jobs")
    audio_asset: Mapped["AudioAsset"] = relationship(
        back_populates="job", uselist=False, cascade="all, delete-orphan"
    )
    transcript: Mapped["Transcript"] = relationship(
        back_populates="job", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TranscriptionJob(id={self.id}, status={self.status}, team_id={self.team_id})>"
