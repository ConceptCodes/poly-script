from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin
import uuid


class PaymentMethod(Base, TimestampMixin):
    __tablename__ = "payment_methods"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    stripe_payment_method_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    brand: Mapped[str] = mapped_column(String(50))
    last4: Mapped[str] = mapped_column(String(4))
    exp_month: Mapped[int] = mapped_column()
    exp_year: Mapped[int] = mapped_column()
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f"<PaymentMethod(team_id={self.team_id}, brand={self.brand}, last4={self.last4})>"
