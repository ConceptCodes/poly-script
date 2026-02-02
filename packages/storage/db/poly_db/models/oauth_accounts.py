from sqlalchemy import String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin
import uuid


class OAuthAccount(Base, TimestampMixin):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
        Index('ix_oauth_accounts_user_id', 'user_id'),
        Index('ix_oauth_accounts_provider', 'provider'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50))
    provider_user_id: Mapped[str] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")

    def __repr__(self):
        return f"<OAuthAccount(provider={self.provider}, user_id={self.user_id})>"
