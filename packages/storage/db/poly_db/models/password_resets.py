from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class PasswordReset(Base, TimestampMixin):
    __tablename__ = "password_resets"
    __table_args__ = (
        Index("ix_password_resets_user_id", "user_id"),
        Index("ix_password_resets_expires_at", "expires_at"),
        Index("ix_password_resets_used_at", "used_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<PasswordReset(user_id={self.user_id}, token={self.token})>"
