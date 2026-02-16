"""Async version of AuthService for use with SQLAlchemy AsyncSession."""

import secrets
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from poly_core.constants import I18nKeys
from poly_core.services.notification import NotificationService
from poly_core.types import JWTTokenPayload, RefreshTokenResponse, TokenResponse
from poly_core.utils.token import generate_token
from poly_db.models.password_resets import PasswordReset
from poly_db.models.refresh_tokens import RefreshToken
from poly_db.models.team_members import TeamRole
from poly_db.models.users import User
from poly_db.repositories import TeamMemberRepository
from poly_db.repositories.auth_async import (
    OAuthAccountRepositoryAsync,
    PasswordResetRepositoryAsync,
    RefreshTokenRepositoryAsync,
)
from poly_db.repositories.users_async import UserRepositoryAsync


class AuthError(ValueError):
    """Base authentication error."""


class EmailVerificationError(AuthError):
    """Error during email verification."""


class PasswordResetError(AuthError):
    """Error during password reset."""


class AsyncAuthService:
    """Async authentication service using async repositories.

    This service provides the same functionality as AuthService but uses
    async repositories for compatibility with SQLAlchemy AsyncSession.
    """

    def __init__(  # noqa: PLR0913
        self,
        db_session: AsyncSession,
        jwt_secret: str | None = None,
        jwt_expiry_minutes: int = 15,
        notification_service: NotificationService | None = None,
        email_verification_expiry_hours: int = 24,
        password_reset_expiry_hours: int = 1,
    ):
        """Initialize the async auth service.

        Args:
            db_session: SQLAlchemy async session
            jwt_secret: Secret key for JWT token signing
            jwt_expiry_minutes: Access token expiry in minutes
            notification_service: Service for sending emails
            email_verification_expiry_hours: Email verification token expiry
            password_reset_expiry_hours: Password reset token expiry
        """
        self.db_session = db_session
        self.jwt_secret = jwt_secret or "test-secret"
        self.jwt_expiry_minutes = jwt_expiry_minutes
        self.notification_service = notification_service
        self.email_verification_expiry_hours = email_verification_expiry_hours
        self.password_reset_expiry_hours = password_reset_expiry_hours

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Initialize async repositories
        self.user_repo = UserRepositoryAsync(db_session)
        self.team_member_repo = TeamMemberRepository(db_session)
        self.oauth_repo = OAuthAccountRepositoryAsync(db_session)
        self.password_reset_repo = PasswordResetRepositoryAsync(db_session)
        self.refresh_token_repo = RefreshTokenRepositoryAsync(db_session)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            password: Plain text password
            hashed_password: Stored password hash

        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except ValueError:
            return False

    def _generate_email_verification_token(self, _user_id: str) -> str:
        """Generate an email verification token.

        Args:
            _user_id: User ID (unused, for interface compatibility)

        Returns:
            Random hex token
        """
        return secrets.token_hex(16)

    def _generate_password_reset_token(self, _user_id: str) -> str:
        """Generate a password reset token.

        Args:
            _user_id: User ID (unused, for interface compatibility)

        Returns:
            Random hex token
        """
        return secrets.token_hex(16)

    def _create_access_token(self, user_id: str | uuid.UUID) -> str:
        """Create a JWT access token.

        Args:
            user_id: User ID to encode in token

        Returns:
            Encoded JWT token
        """
        user_id_value = str(user_id)
        expire = datetime.now(UTC) + timedelta(minutes=self.jwt_expiry_minutes)
        exp_timestamp = int(expire.timestamp())

        payload: JWTTokenPayload = {
            "sub": user_id_value,
            "exp": exp_timestamp,
            "iat": int(datetime.now(UTC).timestamp()),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def _create_refresh_token(self, user_id: str | uuid.UUID) -> str:
        """Create a JWT refresh token.

        Args:
            user_id: User ID to encode in token

        Returns:
            Encoded JWT token
        """
        user_id_value = str(user_id)
        expire = datetime.now(UTC) + timedelta(days=30)
        payload: JWTTokenPayload = {
            "sub": user_id_value,
            "exp": int(expire.timestamp()),
            "iat": int(datetime.now(UTC).timestamp()),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    async def create_access_token(self, user_id: str | uuid.UUID) -> str:
        """Create a JWT access token.

        Args:
            user_id: User ID to encode in token

        Returns:
            Encoded JWT token
        """
        return self._create_access_token(user_id)

    async def create_refresh_token(
        self, user_id: uuid.UUID, expires_in_hours: int = 30 * 24
    ) -> str:
        """Create and store a refresh token for the user.

        Args:
            user_id: User ID to create token for
            expires_in_hours: Token expiry in hours

        Returns:
            The refresh token string
        """
        token = generate_token()
        expires_at = datetime.now(UTC) + timedelta(hours=expires_in_hours)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False,
        )
        await self.refresh_token_repo.create(refresh_token)
        return token

    def verify_access_token(self, token: str) -> JWTTokenPayload | None:
        """Verify a JWT access token.

        Args:
            token: JWT token to verify

        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except JWTError:
            return None

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> dict:
        """Create a new user account.

        Args:
            email: User email address
            password: User password
            full_name: Optional full name

        Returns:
            Created user data dict

        Raises:
            ValueError: If email already exists
        """
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError(I18nKeys.EMAIL_ALREADY_EXISTS.value)

        hashed_password = self.hash_password(password)
        verification_token = generate_token()
        verification_token_expires_at = datetime.now(UTC) + timedelta(
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

        created_user = await self.user_repo.create(user)
        await self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_verification_email(
                user_email=email, user_name=full_name or email, token=verification_token
            )

        return {
            "id": str(created_user.id),
            "email": created_user.email,
            "full_name": created_user.full_name,
            "is_verified": created_user.is_verified,
        }

    async def generate_verification_token(self, user_id: uuid.UUID) -> str:
        """Generate a new verification token for a user.

        Args:
            user_id: User ID

        Returns:
            Generated verification token

        Raises:
            ValueError: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        token = generate_token()
        user.verification_token = token
        user.verification_token_expires_at = datetime.now(UTC) + timedelta(
            hours=self.email_verification_expiry_hours
        )

        await self.user_repo.update(user)
        await self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_verification_email(
                user_email=user.email, user_name=user.full_name or user.email, token=token
            )

        return token

    async def verify_email(self, token: str) -> dict:
        """Verify a user's email with the provided token.

        Args:
            token: Email verification token

        Returns:
            Verified user data dict

        Raises:
            EmailVerificationError: If token is invalid, expired, or already verified
        """
        user = await self.user_repo.get_by_verification_token(token)

        if not user:
            raise EmailVerificationError(I18nKeys.INVALID_VERIFICATION_TOKEN.value)

        if user.is_verified:
            raise EmailVerificationError(I18nKeys.EMAIL_ALREADY_VERIFIED.value)

        verification_expires_at = getattr(user, "verification_token_expires_at", None)
        if isinstance(verification_expires_at, datetime) and verification_expires_at < datetime.now(
            UTC
        ):
            raise EmailVerificationError(I18nKeys.EXPIRED_VERIFICATION_TOKEN.value)

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires_at = None

        await self.user_repo.update(user)
        await self.db_session.commit()

        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
        }

    async def generate_password_reset_token(self, user_id: uuid.UUID) -> str:
        """Generate a password reset token for a user.

        Args:
            user_id: User ID

        Returns:
            Generated reset token

        Raises:
            ValueError: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        token = generate_token()
        expires_at = datetime.now(UTC) + timedelta(hours=self.password_reset_expiry_hours)

        password_reset = PasswordReset(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            used_at=None,
        )

        await self.password_reset_repo.create(password_reset)
        await self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_password_reset_email(
                user_email=user.email, user_name=user.full_name or user.email, token=token
            )

        return token

    async def reset_password(self, token: str, new_password: str) -> dict:
        """Reset a user's password using the reset token.

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            Updated user data dict

        Raises:
            PasswordResetError: If token is invalid, expired, or already used
            ValueError: If user not found
        """
        password_reset = await self.password_reset_repo.get_by_token(token)

        if not password_reset:
            raise PasswordResetError(I18nKeys.INVALID_PASSWORD_RESET_TOKEN.value)

        if password_reset.expires_at < datetime.now(UTC):
            raise PasswordResetError(I18nKeys.EXPIRED_PASSWORD_RESET_TOKEN.value)

        if password_reset.used_at:
            raise PasswordResetError(I18nKeys.ALREADY_USED_PASSWORD_RESET_TOKEN.value)

        user = await self.user_repo.get(password_reset.user_id)

        if not user:
            raise ValueError("User not found")

        hashed_password = self.hash_password(new_password)
        user.hashed_password = hashed_password

        await self.user_repo.update(user)

        password_reset.used_at = datetime.now(UTC)
        await self.password_reset_repo.update(password_reset)
        await self.db_session.commit()

        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
        }

    async def revoke_refresh_tokens(self, user_id: uuid.UUID) -> None:
        """Revoke all refresh tokens for a user.

        Args:
            user_id: User ID
        """
        tokens = await self.refresh_token_repo.get_by_user_id(user_id)
        for token in tokens:
            token.revoked = True
            await self.refresh_token_repo.update(token)

    async def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate a user and return tokens.

        Args:
            email: User email
            password: User password

        Returns:
            Access and refresh tokens

        Raises:
            ValueError: If credentials invalid or account issues
        """
        user = await self.user_repo.get_by_email(email)

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

        await self.revoke_refresh_tokens(user.id)

        access_token = self._create_access_token(user.id)
        refresh_token = await self.create_refresh_token(user.id)

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def logout(self, refresh_token: str) -> None:
        """Logout by revoking the refresh token.

        Args:
            refresh_token: Refresh token to revoke

        Raises:
            ValueError: If token invalid
        """
        token = await self.refresh_token_repo.get_by_token(refresh_token)

        if not token:
            raise ValueError(I18nKeys.INVALID_REFRESH_TOKEN.value)

        token.revoked = True
        await self.refresh_token_repo.update(token)
        await self.db_session.commit()

    async def refresh_access_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access and refresh tokens

        Raises:
            ValueError: If token invalid, expired, or revoked
        """
        token = await self.refresh_token_repo.get_by_token(refresh_token)

        if not token:
            raise ValueError(I18nKeys.INVALID_REFRESH_TOKEN.value)

        if token.revoked:
            raise ValueError(I18nKeys.INVALID_REFRESH_TOKEN.value)

        if token.expires_at < datetime.now(UTC):
            raise ValueError(I18nKeys.EXPIRED_REFRESH_TOKEN.value)

        user_id = token.user_id

        token.revoked = True
        await self.refresh_token_repo.update(token)

        new_access_token = self._create_access_token(user_id)
        new_refresh_token = await self.create_refresh_token(user_id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }

    async def resend_verification_email(self, email: str) -> None:
        """Resend verification email for unverified user.

        Args:
            email: User email

        Raises:
            ValueError: If user not found or already verified
        """
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise ValueError(I18nKeys.USER_NOT_FOUND.value)

        if user.is_verified:
            raise ValueError(I18nKeys.EMAIL_ALREADY_VERIFIED.value)

        await self.generate_verification_token(user.id)

    async def send_password_reset_email(self, email: str) -> None:
        """Send password reset email to user.

        Args:
            email: User email

        Raises:
            ValueError: If user not found
        """
        user = await self.user_repo.get_by_email(email)

        if not user:
            raise ValueError(I18nKeys.USER_NOT_FOUND.value)

        await self.generate_password_reset_token(user.id)

    async def send_verification_email(self, email: str, _locale: str) -> None:
        """Send verification email to user.

        Args:
            email: User email
            _locale: Locale (unused, for interface compatibility)

        Raises:
            AuthError: If user not found
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthError(I18nKeys.USER_NOT_FOUND.value)

        token = self._generate_email_verification_token(str(user.id))
        user.verification_token = token
        if hasattr(user, "verification_token_expires_at"):
            user.verification_token_expires_at = datetime.now(UTC) + timedelta(
                hours=self.email_verification_expiry_hours
            )

        await self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_verification_email(
                user_email=user.email,
                user_name=getattr(user, "full_name", None) or user.email,
                token=token,
            )

    async def request_password_reset(self, email: str, _locale: str) -> None:
        """Request a password reset for a user.

        Args:
            email: User email
            _locale: Locale (unused, for interface compatibility)

        Raises:
            AuthError: If user not found
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthError(I18nKeys.USER_NOT_FOUND.value)

        await self.password_reset_repo.delete_by_user(user.id)

        token = self._generate_password_reset_token(str(user.id))
        password_reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(UTC) + timedelta(hours=self.password_reset_expiry_hours),
            used_at=None,
        )
        await self.password_reset_repo.create(password_reset)
        await self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_password_reset_email(
                user_email=user.email,
                user_name=getattr(user, "full_name", None) or user.email,
                token=token,
            )

    async def signup(self, email: str, password: str, full_name: str, _locale: str) -> User:
        """Sign up a new user with team creation.

        Args:
            email: User email
            password: User password
            full_name: User full name
            _locale: Locale (unused, for interface compatibility)

        Returns:
            Created user

        Raises:
            AuthError: If email already exists
        """
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise AuthError(I18nKeys.EMAIL_ALREADY_EXISTS.value)

        hashed_password = self.hash_password(password)
        verification_token = self._generate_email_verification_token(email)
        verification_token_expires_at = datetime.now(UTC) + timedelta(
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

        created_user = await self.user_repo.create(user)

        team_name = full_name or email.split("@", 1)[0]
        team = TeamMemberRepository(self.db_session).create(name=team_name)
        self.team_member_repo.create(
            team_id=team.id,
            user_id=created_user.id,
            role=TeamRole.ADMIN,
        )

        await self.db_session.commit()

        if self.notification_service:
            self.notification_service.send_verification_email(
                user_email=created_user.email,
                user_name=created_user.full_name or created_user.email,
                token=verification_token,
            )

        return created_user


__all__ = ["AsyncAuthService"]
