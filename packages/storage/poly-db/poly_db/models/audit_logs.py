from typing import Optional
from sqlalchemy import String, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin
import uuid

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    admin_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True)
    target_type: Mapped[str] = mapped_column(String(50)) # e.g., 'user', 'team', 'job'
    target_id: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(100)) # e.g., 'suspend_team'
    previous_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_state: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<AuditLog(action={self.action}, target_type={self.target_type})>"
