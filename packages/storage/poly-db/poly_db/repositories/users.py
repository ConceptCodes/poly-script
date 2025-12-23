from .base import BaseRepository
from ..models.user_settings import UserSettings
from sqlalchemy import select
import uuid
from typing import Optional

class UserSettingsRepository(BaseRepository[UserSettings]):
    def __init__(self, session):
        super().__init__(UserSettings, session)
    
    def get_by_user_id(self, user_id: uuid.UUID) -> Optional[UserSettings]:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()
