import uuid

from sqlalchemy import select

from poly_db.models.admin_users import AdminUser
from poly_db.models.audit_logs import AuditLog
from poly_db.repositories.base import BaseRepository


class AdminUserRepository(BaseRepository[AdminUser]):
    def __init__(self, session):
        super().__init__(AdminUser, session)

    def get_by_email(self, email: str) -> AdminUser | None:
        stmt = select(AdminUser).where(AdminUser.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_active(self) -> list[AdminUser]:
        stmt = select(AdminUser).where(AdminUser.is_active.is_(True))
        return self.session.execute(stmt).scalars().all()


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session):
        super().__init__(AuditLog, session)

    def list_by_admin_user(self, admin_user_id: uuid.UUID) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.admin_user_id == admin_user_id)
            .order_by(AuditLog.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()

    def list_by_target(self, target_type: str, target_id: str) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.target_type == target_type, AuditLog.target_id == target_id)
            .order_by(AuditLog.created_at.desc())
        )
        return self.session.execute(stmt).scalars().all()
