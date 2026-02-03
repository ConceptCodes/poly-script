from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"
    __table_args__ = (
        Index("ix_subscriptions_team_id", "team_id"),
        Index("ix_subscriptions_status", "status"),
        Index("ix_subscriptions_plan_id", "plan_id"),
        Index("ix_subscriptions_current_period_start", "current_period_start"),
        Index("ix_subscriptions_current_period_end", "current_period_end"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), unique=True
    )
    stripe_subscription_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50))
    plan_id: Mapped[str] = mapped_column(String(255))
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cancel_at_period_end: Mapped[bool] = mapped_column(default=False)

    stripe_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self):
        return f"<Subscription(team_id={self.team_id}, status={self.status})>"
