from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import uuid
import secrets
import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from poly_db.repositories import UserRepository, TeamRepository, TeamMemberRepository
from poly_db.repositories.auth import (
    OAuthAccountRepository,
    PasswordResetRepository,
    RefreshTokenRepository,
)
from poly_db.repositories.users import UserSettingsRepository
from poly_db.models.users import User
from poly_db.models.team_members import TeamRole
from poly_db.models.password_resets import PasswordReset
from poly_db.models.refresh_tokens import RefreshToken
from poly_db.models.oauth_accounts import OAuthAccount

from ..constants import I18nKeys
from ..types import JWTTokenPayload, TokenResponse, RefreshTokenResponse
from ..utils.token import generate_token
from .notification import NotificationService


class AuthError(ValueError):
    pass


class EmailVerificationError(AuthError):
    pass


class PasswordResetError(AuthError):
    pass


class AuthService:
    def __init__(
        self,
        db_session: Session,
        jwt_secret: Optional[str] = None,
        jwt_expiry_minutes: int = 15,
        notification_service: Optional[NotificationService] = None,
        email_verification_expiry_hours: int = 24,
        password_reset_expiry_hours: int = 1,
    ):
        self.db_session = db_session
        self.jwt_secret = jwt_secret or "test-secret"
        self.jwt_expiry_minutes = jwt_expiry_minutes
        self.notification_service = notification_service
        self.email_verification_expiry_hours = email_verification_expiry_hours
        self.password_reset_expiry_hours = password_reset_expiry_hours

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        self.user_repo = UserRepository(db_session)
        self.team_repo = TeamRepository(db_session)
        self.team_member_repo = TeamMemberRepository(db_session)
        self.oauth_repo = OAuthAccountRepository(db_session)
        self.password_reset_repo = PasswordResetRepository(db_session)
        self.refresh_token_repo = RefreshTokenRepository(db_session)
        self.user_settings_repo = UserSettingsRepository(db_session)

    def hash_password(self, password: str) -> str:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except ValueError:
            return False

    def _generate_email_verification_token(self, user_id: str) -> str:
        return secrets.token_hex(16)

    def _generate_password_reset_token(self, user_id: str) -> str:
        return secrets.token_hex(16)

    def _create_access_token(self, user_id: Union[str, uuid.UUID]) -> str:
        user_id_value = str(user_id)
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.jwt_expiry_minutes)
        exp_timestamp = int(expire.timestamp())

        payload: JWTTokenPayload = {
            "sub": user_id_value,
            "exp": exp_timestamp,
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def _create_refresh_token(self, user_id: Union[str, uuid.UUID]) -> str:
        user_id_value = str(user_id)
        expire = datetime.now(timezone.utc) + timedelta(days=30)
        payload: JWTTokenPayload = {
            "sub": user_id_value,
            "exp": int(expire.timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def create_access_token(self, user_id: Union[str, uuid.UUID]) -> str:
        user_id_value = str(user_id)
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.jwt_expiry_minutes)
        exp_timestamp = int(expire.timestamp())

        payload: JWTTokenPayload = {
            "sub": user_id_value,
            "exp": exp_timestamp,
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def create_refresh_token(self, user_id: uuid.UUID, expires_in_hours: int = 30 * 24) -> str:
        token = generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False,
        )
        self.refresh_token_repo.create(refresh_token)
        return token

    def verify_access_token(self, token: str) -> Optional[JWTTokenPayload]:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except JWTError:
            return None

    def create_user(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError(I18nKeys.EMAIL_ALREADY_EXISTS.value)

        hashed_password = self.hash_password(password)
        verification_token = generate_token()
        verification_token_expires_at = datetime.now(timezone.utc) + timedelta(
            hours=self.email_verification_expiry_hours
        )

        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_verified=False,
            verification_token=verification_token,
            verification_token_expires_at=verification_token_expires_at,
            is_active=True,
            is_suspended=False,
        )

        created_user = self.user_repo.create(user)

        if self.notification_service:
            self.notification_service.send_verification_email(
                user_email=email, user_name=full_name or email, token=verification_token
            )

        return created_user

    def generate_verification_token(self, user_id: uuid.UUID) -> str:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        token = generate_token()
        user.verification_token = token
        user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(
            hours=self.email_verification_expiry_hours
        )

        self.user_repo.update(user)

        if self.notification_service:
            self.notification_service.send_verification_email(
                user_email=user.email, user_name=user.full_name or user.email, token=token
            )

        return token

    def verify_email(self, token: str) -> User:
        user = self.user_repo.get_by_verification_token(token)

        if not user:
            raise EmailVerificationError(I18nKeys.INVALID_VERIFICATION_TOKEN.value)

        if user.is_verified:
            raise EmailVerificationError(I18nKeys.EMAIL_ALREADY_VERIFIED.value)

        verification_expires_at = getattr(user, "verification_token_expires_at", None)
        if isinstance(verification_expires_at, datetime):
            if verification_expires_at < datetime.now(timezone.utc):
                raise EmailVerificationError(I18nKeys.EXPIRED_VERIFICATION_TOKEN.value)

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires_at = None

        self.user_repo.update(user)
        self.db_session.add(user)
        self.db_session.commit()

        return user

    def generate_password_reset_token(self, user_id: uuid.UUID) -> str:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        token = generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self.password_reset_expiry_hours)

        password_reset = PasswordReset(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            used_at=None,
        )

        self.password_reset_repo.create(password_reset)

        if self.notification_service:
            self.notification_service.send_password_reset_email(
                user_email=user.email, user_name=user.full_name or user.email, token=token
            )

        return token

    def reset_password(self, token: str, new_password: str) -> User:
        password_reset = self.password_reset_repo.get_by_token(token)

        if not password_reset:
            raise PasswordResetError(I18nKeys.INVALID_PASSWORD_RESET_TOKEN.value)

        if password_reset.expires_at < datetime.utcnow():
            raise PasswordResetError(I18nKeys.EXPIRED_PASSWORD_RESET_TOKEN.value)

        if password_reset.used_at:
            raise PasswordResetError(I18nKeys.ALREADY_USED_PASSWORD_RESET_TOKEN.value)

        user = self.user_repo.get(password_reset.user_id)

        if not user:
            raise ValueError("User not found")

        hashed_password = self.hash_password(new_password)
        user.hashed_password = hashed_password
        self.user_repo.update(user)

        password_reset.used_at = datetime.utcnow()
        self.password_reset_repo.update(password_reset)
        self.db_session.add(user)
        self.db_session.add(password_reset)
        self.db_session.commit()

        return user

    def revoke_refresh_tokens(self, user_id: uuid.UUID) -> None:
        tokens = self.refresh_token_repo.get_by_user_id(user_id)
        for token in tokens:
            token.revoked = True
            self.refresh_token_repo.update(token)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repo.get_by_email(email)

        if not user:
            raise ValueError(I18nKeys.INVALID_CREDENTIALS.value)

        if not self.verify_password(password, user.hashed_password):
            raise ValueError(I18nKeys.INVALID_CREDENTIALS.value)

        if not user.is_verified:
            raise ValueError(I18nKeys.EMAIL_NOT_VERIFIED.value)

        if not user.is_active:
            raise ValueError(I18nKeys.ACCOUNT_INACTIVE.value)

        if user.is_suspended:
            raise ValueError(I18nKeys.ACCOUNT_SUSPENDED.value)

        self.revoke_refresh_tokens(user.id)

        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)

        return {"access_token": access_token, "refresh_token": refresh_token}

    def logout(self, refresh_token: str) -> None:
        token = self.refresh_token_repo.get_by_token(refresh_token)

        if not token:
            raise ValueError(I18nKeys.INVALID_REFRESH_TOKEN.value)

        token.revoked = True
        self.refresh_token_repo.update(token)

    def refresh_access_token(self, refresh_token: str) -> RefreshTokenResponse:
        token = self.refresh_token_repo.get_by_token(refresh_token)

        if not token:
            raise ValueError(I18nKeys.INVALID_REFRESH_TOKEN.value)

        if token.revoked:
            raise ValueError(I18nKeys.INVALID_REFRESH_TOKEN.value)

        if token.expires_at < datetime.now(timezone.utc):
            raise ValueError(I18nKeys.EXPIRED_REFRESH_TOKEN.value)

        user_id = token.user_id

        token.revoked = True
        self.refresh_token_repo.update(token)

        new_access_token = self.create_access_token(user_id)
        new_refresh_token = self.create_refresh_token(user_id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }

    def resend_verification_email(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)

        if not user:
            raise ValueError(I18nKeys.USER_NOT_FOUND.value)

        if user.is_verified:
            raise ValueError(I18nKeys.EMAIL_ALREADY_VERIFIED.value)

        token = self.generate_verification_token(user.id)

    def send_password_reset_email(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)

        if not user:
            raise ValueError(I18nKeys.USER_NOT_FOUND.value)

        self.generate_password_reset_token(user.id)

    def send_verification_email(self, email: str, locale: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise AuthError(I18nKeys.USER_NOT_FOUND.value)

        token = self._generate_email_verification_token(str(user.id))
        user.verification_token = token
        if hasattr(user, "verification_token_expires_at"):
            user.verification_token_expires_at = datetime.utcnow() + timedelta(
                hours=self.email_verification_expiry_hours
            )

        self.db_session.add(user)
        self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_verification_email(
                user_email=user.email,
                user_name=getattr(user, "full_name", None) or user.email,
                token=token,
            )

    def request_password_reset(self, email: str, locale: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise AuthError(I18nKeys.USER_NOT_FOUND.value)

        self.password_reset_repo.delete_by_user(user.id)

        token = self._generate_password_reset_token(str(user.id))
        password_reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=self.password_reset_expiry_hours),
            used_at=None,
        )
        self.password_reset_repo.create(password_reset)
        self.db_session.add(password_reset)
        self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_password_reset_email(
                user_email=user.email,
                user_name=getattr(user, "full_name", None) or user.email,
                token=token,
            )

    def signup(self, email: str, password: str, full_name: str, locale: str) -> User:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise AuthError(I18nKeys.EMAIL_ALREADY_EXISTS.value)

        hashed_password = self.hash_password(password)
        verification_token = self._generate_email_verification_token(email)
        verification_token_expires_at = datetime.utcnow() + timedelta(
            hours=self.email_verification_expiry_hours
        )

        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_verified=False,
            verification_token=verification_token,
            verification_token_expires_at=verification_token_expires_at,
            is_active=True,
            is_suspended=False,
        )

        created_user = self.user_repo.create(user)

        team_name = full_name or email.split("@", 1)[0]
        team = self.team_repo.create(name=team_name)
        self.team_member_repo.create(
            team_id=team.id,
            user_id=created_user.id,
            role=TeamRole.ADMIN,
        )

        self.db_session.add(created_user)
        self.db_session.add(team)
        self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_verification_email(
                user_email=created_user.email,
                user_name=created_user.full_name or created_user.email,
                token=verification_token,
            )

        return created_user
