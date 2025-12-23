from typing import Optional
from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin
from datetime import datetime
import uuid


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    stripe_invoice_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    amount_due: Mapped[int] = mapped_column(Integer)  # in cents
    amount_paid: Mapped[int] = mapped_column(Integer)  # in cents
    currency: Mapped[str] = mapped_column(String(3), default="usd")
    status: Mapped[str] = mapped_column(String(50))  # paid, open, void, uncollectible
    invoice_pdf: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    hosted_invoice_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    def __repr__(self):
        return (
            f"<Invoice(team_id={self.team_id}, amount_due={self.amount_due}, status={self.status})>"
        )
