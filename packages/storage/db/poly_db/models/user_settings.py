from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .users import User


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"
    __table_args__ = (Index("ix_user_settings_user_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    host_language: Mapped[str] = mapped_column(String(10), default="en")
    theme: Mapped[str] = mapped_column(String(20), default="system")
    notifications: Mapped[dict] = mapped_column(
        JSON, default=lambda: {"email": True, "job_completion": True, "in_app": True}
    )

    user: Mapped[User] = relationship(back_populates="settings")

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id})>"
