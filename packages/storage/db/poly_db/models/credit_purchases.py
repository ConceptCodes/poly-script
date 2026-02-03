from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class CreditPurchase(Base, TimestampMixin):
    __tablename__ = "credit_purchases"
    __table_args__ = (
        Index("ix_credit_purchases_team_id", "team_id"),
        Index("ix_credit_purchases_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    stripe_session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    amount: Mapped[int] = mapped_column(Integer)
    price_paid: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="usd")

    def __repr__(self):
        return f"<CreditPurchase(team_id={self.team_id}, amount={self.amount})>"
