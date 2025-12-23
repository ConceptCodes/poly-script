from typing import Optional
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin
import uuid

class UsageLog(Base, TimestampMixin):
    __tablename__ = "usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("transcription_jobs.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(50)) # e.g., 'upload'
    amount: Mapped[int] = mapped_column(Integer, default=1)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return f"<UsageLog(team_id={self.team_id}, action={self.action}, amount={self.amount})>"
