from typing import Optional
import uuid
import requests
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

from poly_db.repositories.auth import OAuthAccountRepository
from poly_db.models.users import User
from poly_db.models.oauth_accounts import OAuthAccount
from poly_db.models.teams import Team
from poly_db.models.team_members import TeamMember

from .auth import AuthService
from ..constants import TeamRole, PlanType
from ..types import GoogleUserInfo


class OAuthService:
    def __init__(
        self,
        db_session: Session,
        google_client_id: str,
        google_client_secret: str,
        oauth_redirect_url: str,
        auth_service: AuthService,
    ):
        self.db_session = db_session
        self.google_client_id = google_client_id
        self.google_client_secret = google_client_secret
        self.oauth_redirect_url = oauth_redirect_url
        self.auth_service = auth_service

        self.oauth_repo = OAuthAccountRepository(db_session)

    def get_google_auth_url(
        self,
        redirect_url: Optional[str] = None,
        state: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
    ) -> str:
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
        self, code: str, state: Optional[str] = None, code_verifier: Optional[str] = None
    ) -> Optional[GoogleUserInfo]:
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

    def find_or_create_oauth_user(self, google_info: GoogleUserInfo) -> Optional[User]:
        existing_oauth = self.oauth_repo.get_by_provider_user_id(
            provider="google", provider_user_id=google_info["google_id"]
        )
        if existing_oauth:
            return self.db_session.query(User).filter(User.id == existing_oauth.user_id).first()

        existing_user = (
            self.db_session.query(User).filter(User.email == google_info["email"]).first()
        )
        if existing_user:
            oauth_account = OAuthAccount(
                user_id=existing_user.id,
                provider="google",
                provider_user_id=google_info["google_id"],
                access_token=google_info["access_token"],
                refresh_token=google_info["refresh_token"],
                expires_at=google_info["expires_at"],
            )
            self.oauth_repo.create(oauth_account)
            return existing_user

        user = User(
            email=google_info["email"],
            hashed_password="",
            full_name=google_info["full_name"],
            is_verified=True,
            verification_token=None,
            is_active=True,
            is_suspended=False,
        )
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        oauth_account = OAuthAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=google_info["google_id"],
            access_token=google_info["access_token"],
            refresh_token=google_info["refresh_token"],
            expires_at=google_info["expires_at"],
        )
        self.oauth_repo.create(oauth_account)
        return user

    def get_default_team_for_user(self, user_id: uuid.UUID) -> Optional[Team]:
        from poly_db.models.team_members import TeamMember
        from poly_db.models.teams import Team

        member = (
            self.db_session.query(TeamMember)
            .filter(TeamMember.user_id == user_id, TeamMember.role == TeamRole.ADMIN)
            .first()
        )
        if not member:
            return None

        return (
            self.db_session.query(Team)
            .filter(Team.id == member.team_id, Team.deleted_at.is_(None))
            .first()
        )

    def handle_google_oauth_callback(
        self, code: str, state: str | None = None, code_verifier: str | None = None
    ) -> dict:
        """Handle complete Google OAuth callback flow:
        - Exchange code for user info
        - Find or create user
        - Get default team (if any)
        - Return user data for JWT generation

        Returns:
            dict: User data including user_id, email, default_team_id
        """
        google_info = self.exchange_google_code(code=code, state=state, code_verifier=code_verifier)
        if not google_info:
            raise ValueError("Failed to exchange OAuth code")

        user = self.find_or_create_oauth_user(google_info)
        if not user:
            raise ValueError("Failed to create or find user")

        # Get default team for user
        default_team = self.get_default_team_for_user(user.id)

        return {
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "default_team_id": str(default_team.id) if default_team else None,
        }
