from typing import List, Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from datetime import datetime
import uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_users_is_verified', 'is_verified'),
        Index('ix_users_is_active', 'is_active'),
        Index('ix_users_is_suspended', 'is_suspended'),
        Index('ix_users_deleted_at', 'deleted_at'),
        Index('ix_users_verification_token', 'verification_token'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    verification_token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    suspension_reason: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    suspended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )

    team_memberships: Mapped[List["TeamMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
