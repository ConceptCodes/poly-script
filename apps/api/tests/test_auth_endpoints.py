import uuid
import sys
from pathlib import Path

# Add apps/api to path before other imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from unittest.mock import Mock, patch, AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from . import setup_paths as _setup_paths
from ..main import app

del _setup_paths
from src.dependencies import get_async_db, get_async_auth_service, get_current_user
from src.routes.auth import get_oauth_service


@pytest.fixture
def client():
    # Clear overrides before each test
    app.dependency_overrides = {}
    return TestClient(app)


@pytest.fixture
def mock_db():
    db = AsyncMock(spec=AsyncSession)
    return db


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_signup_success(self, client, mock_db):
        mock_service = AsyncMock()
        app.dependency_overrides[get_async_db] = lambda: mock_db
        app.dependency_overrides[get_async_auth_service] = lambda: mock_service

        mock_user = Mock()
        mock_user.id = uuid.uuid4()
        mock_user.email = "test@example.com"
        mock_user.full_name = "John Doe"
        mock_user.is_verified = False
        mock_service.create_user.return_value = mock_user

        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password_123",
                "full_name": "John Doe",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == str(mock_user.id)
        assert data["email"] == "test@example.com"
        assert data["is_verified"] is False

    def test_signup_invalid_email(self, client):
        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "invalid-email",
                "password": "password_123",
                "full_name": "John Doe",
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(self, client, mock_db):
        mock_service = AsyncMock()
        app.dependency_overrides[get_async_db] = lambda: mock_db
        app.dependency_overrides[get_async_auth_service] = lambda: mock_service

        mock_service.login.return_value = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
        }

        response = client.post(
            "/v1/auth/login",
            json={"email": "test@example.com", "password": "password_123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] == "test-access-token"
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, mock_db):
        mock_service = AsyncMock()
        app.dependency_overrides[get_async_db] = lambda: mock_db
        app.dependency_overrides[get_async_auth_service] = lambda: mock_service

        mock_service.login.side_effect = ValueError("Invalid credentials")

        response = client.post(
            "/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong_password"},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_verify_email_success(self, client, mock_db):
        mock_service = AsyncMock()
        app.dependency_overrides[get_async_db] = lambda: mock_db
        app.dependency_overrides[get_async_auth_service] = lambda: mock_service

        mock_user = Mock()
        mock_user.id = uuid.uuid4()
        mock_service.verify_email.return_value = mock_user

        response = client.post("/v1/auth/verify-email", json={"token": "valid-token"})

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_verify_email_invalid_token(self, client, mock_db):
        mock_service = AsyncMock()
        app.dependency_overrides[get_async_db] = lambda: mock_db
        app.dependency_overrides[get_async_auth_service] = lambda: mock_service

        mock_service.verify_email.side_effect = ValueError("Invalid token")

        response = client.post("/v1/auth/verify-email", json={"token": "invalid-token"})

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_me_authenticated(self, client, mock_db):
        app.dependency_overrides[get_async_db] = lambda: mock_db
        mock_user = {
            "id": uuid.uuid4(),
            "email": "test@example.com",
            "full_name": "Test User",
            "is_verified": True,
            "is_active": True,
            "is_suspended": False,
            "created_at": "2024-01-01T00:00:00",
        }
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer valid-token"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True

    def test_me_unauthenticated(self, client):
        response = client.get("/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_success(self, client, mock_db):
        mock_service = AsyncMock()
        app.dependency_overrides[get_async_db] = lambda: mock_db
        app.dependency_overrides[get_async_auth_service] = lambda: mock_service

        response = client.post(
            "/v1/auth/logout",
            headers={"Authorization": "Bearer valid-token"},
            json={"refresh_token": "refresh-token"},
        )

        assert response.status_code == 204
        mock_service.logout.assert_called_once()

    @pytest.mark.asyncio
    async def test_oauth_google_url(self, client):
        mock_service = AsyncMock()
        app.dependency_overrides[get_oauth_service] = lambda: mock_service

        mock_service.get_google_auth_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?..."
        )

        response = client.get("/v1/auth/oauth/google")

        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "google.com" in data["auth_url"]

    @pytest.mark.asyncio
    async def test_oauth_google_url_with_pkce(self, client):
        mock_service = AsyncMock()
        app.dependency_overrides[get_oauth_service] = lambda: mock_service

        mock_service.get_google_auth_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?..."
        )

        response = client.get(
            "/v1/auth/oauth/google",
            params={
                "code_challenge": "test_challenge",
                "code_challenge_method": "S256",
                "state": "test_state",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data

    @pytest.mark.asyncio
    async def test_oauth_callback_get_method(self, client, mock_db):
        mock_auth_service = AsyncMock()
        mock_oauth_service = AsyncMock()
        app.dependency_overrides[get_async_db] = lambda: mock_db
        app.dependency_overrides[get_async_auth_service] = lambda: mock_auth_service
        app.dependency_overrides[get_oauth_service] = lambda: mock_oauth_service

        # Mock the complete OAuth flow
        user_id = uuid.uuid4()
        mock_oauth_service.handle_google_oauth_callback.return_value = {
            "user_id": str(user_id),
            "email": "test@example.com",
            "full_name": "Test User",
            "is_verified": True,
            "default_team_id": None,
        }
        mock_auth_service.create_access_token.return_value = "test-access-token"
        mock_auth_service.create_refresh_token.return_value = "test-refresh-token"

        response = client.get(
            "/v1/auth/oauth/google/callback",
            params={"code": "test_code", "state": "test_state"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
