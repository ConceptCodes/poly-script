from typing import Optional
from sqlalchemy import String, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import uuid


class TranscriptEdit(Base, TimestampMixin):
    __tablename__ = "transcript_edits"
    __table_args__ = (
        Index('ix_transcript_edits_transcript_id', 'transcript_id'),
        Index('ix_transcript_edits_user_id', 'user_id'),
        Index('ix_transcript_edits_created_at', 'created_at'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transcript_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    previous_text: Mapped[str] = mapped_column(Text)
    new_text: Mapped[str] = mapped_column(Text)
    previous_segments: Mapped[dict] = mapped_column(JSON)
    new_segments: Mapped[dict] = mapped_column(JSON)

    transcript: Mapped["Transcript"] = relationship(back_populates="edits")

    def __repr__(self):
        return f"<TranscriptEdit(id={self.id}, transcript_id={self.transcript_id})>"
