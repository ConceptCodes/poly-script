from .base import BaseRepository
from ..models.admin_users import AdminUser
from ..models.audit_logs import AuditLog
from sqlalchemy import select
import uuid
from typing import Optional, List


class AdminUserRepository(BaseRepository[AdminUser]):
    def __init__(self, session):
        super().__init__(AdminUser, session)

    def get_by_email(self, email: str) -> Optional[AdminUser]:
        stmt = select(AdminUser).where(AdminUser.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_active(self) -> List[AdminUser]:
        stmt = select(AdminUser).where(AdminUser.is_active.is_(True))
        return self.session.execute(stmt).scalars().all()


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session):
        super().__init__(AuditLog, session)

    def list_by_admin_user(self, admin_user_id: uuid.UUID) -> List[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.admin_user_id == admin_user_id)
            .order_by(AuditLog.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def list_by_target(self, target_type: str, target_id: str) -> List[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.target_type == target_type, AuditLog.target_id == target_id)
            .order_by(AuditLog.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()
