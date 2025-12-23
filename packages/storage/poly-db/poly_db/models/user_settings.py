from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import uuid


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    host_language: Mapped[str] = mapped_column(String(10), default="en")
    notifications: Mapped[dict] = mapped_column(JSON, default=lambda: {"email": True})

    # Relationships
    user: Mapped["User"] = relationship(back_populates="settings")

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id})>"
