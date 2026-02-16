"""Async version of User repositories for use with SQLAlchemy AsyncSession."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from poly_db.models.user_settings import UserSettings
from poly_db.models.users import User
from poly_db.repositories.base_async import BaseRepositoryAsync


class UserRepositoryAsync(BaseRepositoryAsync[User]):
    """Async repository for User operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by their email address."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str) -> User | None:
        """Get a user by their verification token."""
        stmt = select(User).where(User.verification_token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class UserSettingsRepositoryAsync(BaseRepositoryAsync[UserSettings]):
    """Async repository for UserSettings operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(UserSettings, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSettings | None:
        """Get user settings for a specific user."""
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_language(self, host_language: str) -> list[UserSettings]:
        """List all user settings with a specific host language."""
        stmt = select(UserSettings).where(UserSettings.host_language == host_language)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


__all__ = ["UserRepositoryAsync", "UserSettingsRepositoryAsync"]
