from .base import BaseRepository
from ..models.oauth_accounts import OAuthAccount
from ..models.password_resets import PasswordReset
from ..models.refresh_tokens import RefreshToken
from sqlalchemy import select
import uuid
from typing import Optional, List


class OAuthAccountRepository(BaseRepository[OAuthAccount]):
    def __init__(self, session):
        super().__init__(OAuthAccount, session)

    def get_by_provider(self, provider: str, provider_account_id: str) -> Optional[OAuthAccount]:
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider, OAuthAccount.provider_user_id == provider_account_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_provider_user_id(
        self, provider: str, provider_user_id: str
    ) -> Optional[OAuthAccount]:
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider, OAuthAccount.provider_user_id == provider_user_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_user_id(self, user_id: uuid.UUID) -> List[OAuthAccount]:
        stmt = select(OAuthAccount).where(OAuthAccount.user_id == user_id)
        return self.session.execute(stmt).scalars().all()


class PasswordResetRepository(BaseRepository[PasswordReset]):
    def __init__(self, session):
        super().__init__(PasswordReset, session)

    def get_by_token(self, token: str) -> Optional[PasswordReset]:
        stmt = select(PasswordReset).where(PasswordReset.token == token)
        # Assuming there is a token field
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active_by_token(self, token: str) -> Optional[PasswordReset]:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        stmt = select(PasswordReset).where(
            PasswordReset.token == token,
            PasswordReset.used_at.is_(None),
            PasswordReset.expires_at > now,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def delete_expired(self) -> List[PasswordReset]:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        stmt = select(PasswordReset).where(PasswordReset.expires_at < now)
        expired = self.session.execute(stmt).scalars().all()
        for reset in expired:
            self.session.delete(reset)
        self.session.flush()
        return expired


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session):
        super().__init__(RefreshToken, session)

    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active_by_token(self, token: str) -> Optional[RefreshToken]:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.revoked.is_(False),
            RefreshToken.expires_at > now,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_user_id(self, user_id: uuid.UUID) -> List[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        return self.session.execute(stmt).scalars().all()

    def get_by_user_id(self, user_id: uuid.UUID) -> List[RefreshToken]:
        return self.list_by_user_id(user_id)

    def delete_revoked(self) -> List[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.revoked.is_(True))
        revoked = self.session.execute(stmt).scalars().all()
        for token in revoked:
            self.session.delete(token)
        self.session.flush()
        return revoked
