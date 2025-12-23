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

class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session):
        super().__init__(AuditLog, session)
