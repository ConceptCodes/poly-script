from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class PlanType(str, enum.Enum):
    FREE = "FREE"
    STANDARD = "STANDARD"
    PRO = "PRO"


class Team(Base, TimestampMixin):
    __tablename__ = "teams"
    __table_args__ = (
        Index("ix_teams_plan", "plan"),
        Index("ix_teams_is_suspended", "is_suspended"),
        Index("ix_teams_stripe_customer_id", "stripe_customer_id"),
        Index("ix_teams_stripe_subscription_id", "stripe_subscription_id"),
        Index("ix_teams_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    host_language: Mapped[str] = mapped_column(String(10), default="en")

    plan: Mapped[PlanType] = mapped_column(SQLEnum(PlanType), default=PlanType.FREE)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )

    monthly_upload_count: Mapped[int] = mapped_column(Integer, default=0)
    monthly_translation_count: Mapped[int] = mapped_column(Integer, default=0)
    extra_credits: Mapped[int] = mapped_column(Integer, default=0)

    members: Mapped[list["TeamMember"]] = relationship(
        back_populates="team", cascade="all, delete-orphan"
    )
    invitations: Mapped[list["TeamInvitation"]] = relationship(
        back_populates="team", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["TranscriptionJob"]] = relationship(back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name}, plan={self.plan})>"
