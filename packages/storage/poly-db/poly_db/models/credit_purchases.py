from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin
import uuid


class CreditPurchase(Base, TimestampMixin):
    __tablename__ = "credit_purchases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    stripe_session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    amount: Mapped[int] = mapped_column(Integer)  # number of credits
    price_paid: Mapped[int] = mapped_column(Integer)  # in cents
    currency: Mapped[str] = mapped_column(String(3), default="usd")

    def __repr__(self):
        return f"<CreditPurchase(team_id={self.team_id}, amount={self.amount})>"
