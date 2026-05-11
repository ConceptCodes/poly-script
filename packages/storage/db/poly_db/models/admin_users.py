from __future__ import annotations

import uuid
from enum import Enum

from sqlalchemy import Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class AdminUserRole(str, Enum):
    """Admin user role enum."""

    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class AdminUser(Base, TimestampMixin):
    __tablename__ = "admin_users"
    __table_args__ = (
        Index("ix_admin_users_is_active", "is_active"),
        Index("ix_admin_users_is_suspended", "is_suspended"),
        Index("ix_admin_users_role", "role"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(50), default="ADMIN")

    def __repr__(self):
        return f"<AdminUser(email={self.email}, role={self.role})>"
