import uuid
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    db = Mock(spec=Session)
    return db


class TestAuthEndpoints:
    def test_signup_success(self, client, mock_db):
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.email = "test@example.com"
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

    def test_login_success(self, client, mock_db):
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

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

    def test_login_invalid_credentials(self, client, mock_db):
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                mock_service.login.side_effect = ValueError("Invalid credentials")

                response = client.post(
                    "/v1/auth/login",
                    json={"email": "test@example.com", "password": "wrong_password"},
                )

                assert response.status_code == 400

    def test_verify_email_success(self, client, mock_db):
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_service.verify_email.return_value = mock_user

                response = client.post("/v1/auth/verify-email", json={"token": "valid-token"})

                assert response.status_code == 204

    def test_verify_email_invalid_token(self, client, mock_db):
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                mock_service.verify_email.side_effect = ValueError("Invalid token")

                response = client.post("/v1/auth/verify-email", json={"token": "invalid-token"})

                assert response.status_code == 400

    def test_me_authenticated(self, client, mock_db):
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.email = "test@example.com"
                mock_get_current_user.return_value = mock_user

                response = client.get(
                    "/v1/auth/me",
                    headers={"Authorization": "Bearer valid-token"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["email"] == "test@example.com"

    def test_me_unauthenticated(self, client):
        response = client.get("/v1/auth/me")
        assert response.status_code == 401

    def test_logout_success(self, client, mock_db):
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                response = client.post(
                    "/v1/auth/logout",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"refresh_token": "refresh-token"},
                )

                assert response.status_code == 204
                mock_service.logout.assert_called_once()

    def test_oauth_google_url(self, client):
        with patch("apps.api.src.routes.auth.get_oauth_service") as mock_oauth_service_dep:
            mock_service = Mock()
            mock_oauth_service_dep.return_value = mock_service

            mock_service.get_google_auth_url.return_value = "https://accounts.google.com/o/oauth2/auth?..."

            response = client.get("/v1/auth/oauth/google")

            assert response.status_code == 200
            data = response.json()
            assert "auth_url" in data
            assert "google.com" in data["auth_url"]

    def test_oauth_google_url_with_pkce(self, client):
        with patch("apps.api.src.routes.auth.get_oauth_service") as mock_oauth_service_dep:
            mock_service = Mock()
            mock_oauth_service_dep.return_value = mock_service

            mock_service.get_google_auth_url.return_value = "https://accounts.google.com/o/oauth2/auth?..."

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

    def test_oauth_callback_get_method(self, client, mock_db):
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                with patch("apps.api.src.routes.auth.get_oauth_service") as mock_oauth_service_dep:
                    mock_auth_service = Mock()
                    mock_auth_service_dep.return_value = mock_auth_service

                    mock_oauth_service = Mock()
                    mock_oauth_service_dep.return_value = mock_oauth_service

                    # Mock the complete OAuth flow
                    mock_oauth_service.handle_google_oauth_callback.return_value = {
                        "user_id": str(uuid.uuid4()),
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
