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
            OAuthAccount.oauth_name == provider,
            OAuthAccount.oauth_account_id == provider_account_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

class PasswordResetRepository(BaseRepository[PasswordReset]):
    def __init__(self, session):
        super().__init__(PasswordReset, session)
        
    def get_by_token(self, token: str) -> Optional[PasswordReset]:
        stmt = select(PasswordReset).where(PasswordReset.token == token)
        # Assuming there is a token field
        return self.session.execute(stmt).scalar_one_or_none()

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session):
        super().__init__(RefreshToken, session)
        
    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        return self.session.execute(stmt).scalar_one_or_none()
