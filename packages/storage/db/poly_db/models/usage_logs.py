from typing import Optional
from sqlalchemy import String, ForeignKey, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin
import uuid


class UsageLog(Base, TimestampMixin):
    __tablename__ = "usage_logs"
    __table_args__ = (
        Index('ix_usage_logs_team_id', 'team_id'),
        Index('ix_usage_logs_job_id', 'job_id'),
        Index('ix_usage_logs_action', 'action'),
        Index('ix_usage_logs_created_at', 'created_at'),
        Index('ix_usage_logs_team_action_created', 'team_id', 'action', 'created_at'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("transcription_jobs.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50))
    amount: Mapped[int] = mapped_column(Integer, default=1)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self):
        return f"<UsageLog(team_id={self.team_id}, action={self.action}, amount={self.amount})>"
