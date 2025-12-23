from typing import List
from sqlalchemy import String, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import uuid

class Transcript(Base, TimestampMixin):
    __tablename__ = "transcripts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("transcription_jobs.id", ondelete="CASCADE"), unique=True)
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10))
    segments: Mapped[dict] = mapped_column(JSON) # List of segments {start_ms, end_ms, text, speaker}
    engine_version: Mapped[str] = mapped_column(String(50))
    
    # Relationships
    job: Mapped["TranscriptionJob"] = relationship(back_populates="transcript")
    edits: Mapped[List["TranscriptEdit"]] = relationship(back_populates="transcript", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Transcript(id={self.id}, job_id={self.job_id})>"
