"""Audit service for logging admin actions."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from poly_db.repositories import AuditLogRepository


@dataclass(frozen=True)
class AdminAuditAction:
    """Data required to persist an admin audit event."""

    admin_user_id: str
    action: str
    target_type: str
    target_id: str
    previous_state: dict[str, Any] | None = None
    new_state: dict[str, Any] | None = None
    reason: str | None = None


class AuditService:
    """Service for creating and managing audit logs."""

    def __init__(self, db_session):
        """Initialize with database session."""
        self.db_session = db_session
        self.audit_repo = AuditLogRepository(db_session)

    async def log_admin_action(
        self,
        audit_action: AdminAuditAction | None = None,
        **kwargs: Any,
    ) -> None:
        """Log an admin action to the audit log."""
        event = audit_action or AdminAuditAction(**kwargs)
        self.audit_repo.create(
            admin_user_id=event.admin_user_id,
            action=event.action,
            target_type=event.target_type,
            target_id=event.target_id,
            previous_state=event.previous_state,
            new_state=event.new_state,
            reason=event.reason,
            created_at=datetime.now(UTC),
        )
