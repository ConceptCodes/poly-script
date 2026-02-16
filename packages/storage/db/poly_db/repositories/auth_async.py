"""Async version of Auth repositories for use with SQLAlchemy AsyncSession."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from poly_db.models.oauth_accounts import OAuthAccount
from poly_db.models.password_resets import PasswordReset
from poly_db.models.refresh_tokens import RefreshToken
from poly_db.repositories.base_async import BaseRepositoryAsync


class OAuthAccountRepositoryAsync(BaseRepositoryAsync[OAuthAccount]):
    """Async repository for OAuthAccount operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(OAuthAccount, session)

    async def get_by_provider(self, provider: str, provider_account_id: str) -> OAuthAccount | None:
        """Get an OAuth account by provider and provider account ID."""
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider, OAuthAccount.provider_user_id == provider_account_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_provider_user_id(
        self, provider: str, provider_user_id: str
    ) -> OAuthAccount | None:
        """Get an OAuth account by provider and provider user ID."""
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider, OAuthAccount.provider_user_id == provider_user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[OAuthAccount]:
        """Get all OAuth accounts for a specific user."""
        stmt = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class PasswordResetRepositoryAsync(BaseRepositoryAsync[PasswordReset]):
    """Async repository for PasswordReset operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(PasswordReset, session)

    async def get_by_token(self, token: str) -> PasswordReset | None:
        """Get a password reset by token."""
        stmt = select(PasswordReset).where(PasswordReset.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_token(self, token: str) -> PasswordReset | None:
        """Get an active (unused and not expired) password reset by token."""
        now = datetime.now(UTC)
        stmt = select(PasswordReset).where(
            PasswordReset.token == token,
            PasswordReset.used_at.is_(None),
            PasswordReset.expires_at > now,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_expired(self) -> list[PasswordReset]:
        """Delete all expired password resets and return them."""
        now = datetime.now(UTC)
        stmt = select(PasswordReset).where(PasswordReset.expires_at < now)
        result = await self.session.execute(stmt)
        expired = list(result.scalars().all())

        for reset in expired:
            await self.session.delete(reset)

        await self.session.flush()
        return expired


class RefreshTokenRepositoryAsync(BaseRepositoryAsync[RefreshToken]):
    """Async repository for RefreshToken operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Get a refresh token by token string."""
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_token(self, token: str) -> RefreshToken | None:
        """Get an active (not revoked and not expired) refresh token by token string."""
        now = datetime.now(UTC)
        stmt = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.revoked.is_(False),
            RefreshToken.expires_at > now,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user_id(self, user_id: uuid.UUID) -> list[RefreshToken]:
        """List all refresh tokens for a specific user."""
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[RefreshToken]:
        """Get all refresh tokens for a specific user (alias for list_by_user_id)."""
        return await self.list_by_user_id(user_id)

    async def delete_revoked(self) -> list[RefreshToken]:
        """Delete all revoked refresh tokens and return them."""
        stmt = select(RefreshToken).where(RefreshToken.revoked.is_(True))
        result = await self.session.execute(stmt)
        revoked = list(result.scalars().all())

        for token in revoked:
            await self.session.delete(token)

        await self.session.flush()
        return revoked


__all__ = [
    "OAuthAccountRepositoryAsync",
    "PasswordResetRepositoryAsync",
    "RefreshTokenRepositoryAsync",
]
