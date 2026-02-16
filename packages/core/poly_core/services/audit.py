"""Audit service for logging admin actions."""

from datetime import UTC, datetime
from typing import Any

from poly_db.repositories import AuditLogRepository


class AuditService:
    """Service for creating and managing audit logs."""

    def __init__(self, db_session):
        """Initialize with database session."""
        self.db_session = db_session
        self.audit_repo = AuditLogRepository(db_session)

    async def log_admin_action(
        self,
        admin_user_id: str,
        action: str,
        target_type: str,
        target_id: str,
        previous_state: dict[str, Any] | None = None,
        new_state: dict[str, Any] | None = None,
        reason: str | None = None,
    ) -> None:
        """Log an admin action to the audit log."""
        self.audit_repo.create(
            admin_user_id=admin_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
            created_at=datetime.now(UTC),
        )
