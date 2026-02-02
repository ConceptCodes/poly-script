from sqlalchemy import String, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
from datetime import datetime
import uuid


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index('ix_refresh_tokens_user_id', 'user_id'),
        Index('ix_refresh_tokens_expires_at', 'expires_at'),
        Index('ix_refresh_tokens_revoked', 'revoked'),
        Index('ix_refresh_tokens_created_at', 'created_at'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(user_id={self.user_id}, token={self.token})>"
