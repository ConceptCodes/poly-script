"""Async version of OAuthService for use with SQLAlchemy AsyncSession."""

import uuid

import requests
from google_auth_oauthlib.flow import Flow
from sqlalchemy.ext.asyncio import AsyncSession

from poly_core.constants import TeamRole
from poly_core.services.auth_async import AsyncAuthService
from poly_core.types import GoogleUserInfo
from poly_db.models.oauth_accounts import OAuthAccount
from poly_db.models.teams import Team
from poly_db.models.users import User
from poly_db.repositories.auth_async import OAuthAccountRepositoryAsync
from poly_db.repositories.teams_async import TeamMemberRepositoryAsync
from poly_db.repositories.users_async import UserRepositoryAsync


class AsyncOAuthService:
    """Async OAuth service using async repositories for compatibility with SQLAlchemy AsyncSession.

    This service provides the same functionality as OAuthService but uses
    async repositories for compatibility with async FastAPI routes.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        google_client_id: str,
        google_client_secret: str,
        oauth_redirect_url: str,
        auth_service: AsyncAuthService,
    ):
        """Initialize the async OAuth service.

        Args:
            db_session: SQLAlchemy async session
            google_client_id: Google OAuth client ID
            google_client_secret: Google OAuth client secret
            oauth_redirect_url: Redirect URL for OAuth callback
            auth_service: AsyncAuthService instance for authentication operations
        """
        self.db_session = db_session
        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
        self.oauth_redirect_url = oauth_redirect_url
        self.auth_service = auth_service

        # Initialize async repositories
        self.oauth_repo = OAuthAccountRepositoryAsync(db_session)
        self.user_repo = UserRepositoryAsync(db_session)
        self.team_member_repo = TeamMemberRepositoryAsync(db_session)

    def get_google_auth_url(
        self,
        redirect_url: str | None = None,
        state: str | None = None,
        code_challenge: str | None = None,
        code_challenge_method: str | None = None,
    ) -> str:
        """Generate Google OAuth authorization URL with optional PKCE support.

        Args:
            redirect_url: Custom redirect URL (defaults to oauth_redirect_url)
            state: Optional state parameter for CSRF protection
            code_challenge: PKCE code challenge for enhanced security
            code_challenge_method: PKCE code challenge method (S256 or plain)

        Returns:
            Authorization URL for Google OAuth flow
        """
        redirect_uri = redirect_url or self.oauth_redirect_url
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.google_client_id,
                    "client_secret": self.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            },
            scopes=["openid", "email", "profile"],
        )
        flow.redirect_uri = redirect_uri

        # PKCE support: pass code_challenge and code_challenge_method
        authorization_url_params = {}
        if state:
            authorization_url_params["state"] = state
        if code_challenge:
            authorization_url_params["code_challenge"] = code_challenge
        if code_challenge_method:
            authorization_url_params["code_challenge_method"] = code_challenge_method

        if authorization_url_params:
            authorization_url, _ = flow.authorization_url(**authorization_url_params)
        else:
            authorization_url, _ = flow.authorization_url()

        return authorization_url

    def exchange_google_code(
        self, code: str, _state: str | None = None, code_verifier: str | None = None
    ) -> GoogleUserInfo | None:
        """Exchange Google OAuth authorization code for user info.

        Args:
            code: Authorization code from Google OAuth callback
            _state: State parameter (unused, for interface compatibility)
            code_verifier: PKCE code verifier for enhanced security

        Returns:
            GoogleUserInfo dict with user details, or None if exchange fails
        """
        try:
            flow = Flow.from_client_config(
                client_config={
                    "web": {
                        "client_id": self.google_client_id,
                        "client_secret": self.google_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.oauth_redirect_url],
                    }
                },
                scopes=["openid", "email", "profile"],
            )
            flow.redirect_uri = self.oauth_redirect_url

            # PKCE support: pass code_verifier if provided
            token_kwargs = {"code": code}
            if code_verifier:
                token_kwargs["code_verifier"] = code_verifier

            flow.fetch_token(**token_kwargs)
            credentials = flow.credentials

            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {credentials.token}"},
            )
            response.raise_for_status()
            user_info = response.json()

            result: GoogleUserInfo = {
                "google_id": user_info["id"],
                "email": user_info["email"],
                "full_name": user_info.get("name", ""),
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "expires_at": str(credentials.expiry) if credentials.expiry else None,
            }
            return result
        except Exception:
            return None

    async def find_or_create_oauth_user(self, google_info: GoogleUserInfo) -> dict | None:
        """Find existing OAuth user or create a new one.

        Args:
            google_info: Google user information from OAuth flow

        Returns:
            User data dict or None if operation fails
        """
        existing_oauth = await self.oauth_repo.get_by_provider_user_id(
            provider="google", provider_user_id=google_info["google_id"]
        )
        if existing_oauth:
            user = await self.user_repo.get(existing_oauth.user_id)
            if user:
                return {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_verified": user.is_verified,
                }

        existing_user = await self.user_repo.get_by_email(google_info["email"])
        if existing_user:
            oauth_account = OAuthAccount(
                user_id=existing_user.id,
                provider="google",
                provider_user_id=google_info["google_id"],
                access_token=google_info["access_token"],
                refresh_token=google_info["refresh_token"],
                expires_at=google_info["expires_at"],
            )
            await self.oauth_repo.create(oauth_account)
            await self.db_session.commit()
            return {
                "id": str(existing_user.id),
                "email": existing_user.email,
                "full_name": existing_user.full_name,
                "is_verified": existing_user.is_verified,
            }

        user = User(
            email=google_info["email"],
            hashed_password="",
            full_name=google_info["full_name"],
            is_verified=True,
            verification_token=None,
            is_active=True,
            is_suspended=False,
        )
        await self.user_repo.create(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)

        oauth_account = OAuthAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=google_info["google_id"],
            access_token=google_info["access_token"],
            refresh_token=google_info["refresh_token"],
            expires_at=google_info["expires_at"],
        )
        await self.oauth_repo.create(oauth_account)
        await self.db_session.commit()
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
        }

    async def get_default_team_for_user(self, user_id: uuid.UUID) -> Team | None:
        """Get the default team for a user (team where user is ADMIN).

        Args:
            user_id: User UUID

        Returns:
            Team instance or None if user is not admin of any team
        """
        members = await self.team_member_repo.list_by_user_id(user_id)
        admin_memberships = [m for m in members if m.role == TeamRole.ADMIN]

        if not admin_memberships:
            return None

        # Get the team from the first admin membership
        team = await self.db_session.get(Team, admin_memberships[0].team_id)
        if team and team.deleted_at is None:
            return team

        return None

    async def handle_google_oauth_callback(
        self, code: str, state: str | None = None, code_verifier: str | None = None
    ) -> dict:
        """Handle complete Google OAuth callback flow.

        This method:
        1. Exchanges the authorization code for user info
        2. Finds or creates the user in the database
        3. Retrieves the user's default team (if any)
        4. Returns user data for JWT token generation

        Args:
            code: Authorization code from Google OAuth callback
            state: State parameter (optional, for CSRF protection)
            code_verifier: PKCE code verifier (optional, for enhanced security)

        Returns:
            dict: User data including user_id, email, default_team_id

        Raises:
            ValueError: If OAuth code exchange or user creation fails
        """
        google_info = self.exchange_google_code(code=code, state=state, code_verifier=code_verifier)
        if not google_info:
            raise ValueError("Failed to exchange OAuth code")

        user = await self.find_or_create_oauth_user(google_info)
        if not user:
            raise ValueError("Failed to create or find user")

        # Get default team for user
        default_team = await self.get_default_team_for_user(uuid.UUID(user["id"]))

        return {
            "user_id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_verified": user["is_verified"],
            "default_team_id": str(default_team.id) if default_team else None,
        }


__all__ = ["AsyncOAuthService"]
