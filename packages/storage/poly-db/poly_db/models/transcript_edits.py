from typing import Optional
from sqlalchemy import String, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import uuid


class TranscriptEdit(Base, TimestampMixin):
    __tablename__ = "transcript_edits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transcript_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # What was changed
    previous_text: Mapped[str] = mapped_column(Text)
    new_text: Mapped[str] = mapped_column(Text)
    previous_segments: Mapped[dict] = mapped_column(JSON)
    new_segments: Mapped[dict] = mapped_column(JSON)

    # Relationships
    transcript: Mapped["Transcript"] = relationship(back_populates="edits")

    def __repr__(self):
        return f"<TranscriptEdit(id={self.id}, transcript_id={self.transcript_id})>"
