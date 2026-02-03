from __future__ import annotations

import uuid

from sqlalchemy import JSON, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_admin_user_id", "admin_user_id"),
        Index("ix_audit_logs_target_type", "target_type"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_target", "target_type", "target_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"), nullable=True
    )
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[str] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(100))
    previous_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<AuditLog(action={self.action}, target_type={self.target_type})>"
