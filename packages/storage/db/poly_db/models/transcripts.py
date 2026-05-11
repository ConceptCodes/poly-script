from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .transcript_edits import TranscriptEdit
    from .transcription_jobs import TranscriptionJob


class Transcript(Base, TimestampMixin):
    __tablename__ = "transcripts"
    __table_args__ = (
        Index("ix_transcripts_job_id", "job_id"),
        Index("ix_transcripts_language", "language"),
        Index("ix_transcripts_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transcription_jobs.id", ondelete="CASCADE"), unique=True
    )
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10))
    segments: Mapped[dict] = mapped_column(JSON)
    format_versions: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    engine_version: Mapped[str] = mapped_column(String(50))

    job: Mapped[TranscriptionJob] = relationship(back_populates="transcript")
    edits: Mapped[list[TranscriptEdit]] = relationship(
        back_populates="transcript", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Transcript(id={self.id}, job_id={self.job_id})>"
