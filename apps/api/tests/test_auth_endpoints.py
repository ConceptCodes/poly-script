import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from apps.api.src.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    db = Mock(spec=Session)
    return db


class TestAuthEndpoints:
    def test_signup_success(self, client, mock_db):
        with patch("apps.api.src.routes.auth.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.auth.AuthService") as mock_auth_service:
                mock_service = Mock()
                mock_auth_service.return_value = mock_service

                mock_user = Mock()
                mock_user.id = "user-id"
                mock_user.email = "test@example.com"
                mock_user.is_verified = False
                mock_service.signup.return_value = mock_user

                response = client.post(
                    "/v1/auth/signup",
                    json={
                        "email": "test@example.com",
                        "password": "password_123",
                        "full_name": "John Doe",
                        "language": "en"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["user"]["id"] == "user-id"
                assert data["user"]["email"] == "test@example.com"
                assert data["user"]["is_verified"] is False

    def test_signup_invalid_email(self, client, mock_db):
        with patch("apps.api.src.routes.auth.get_db", return_value=mock_db):
            response = client.post(
                "/v1/auth/signup",
                json={
                    "email": "invalid-email",
                    "password": "password_123",
                    "full_name": "John Doe",
                    "language": "en"
                }
            )

            assert response.status_code == 422

    def test_login_success(self, client, mock_db):
        with patch("apps.api.src.routes.auth.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.auth.AuthService") as mock_auth_service:
                mock_service = Mock()
                mock_auth_service.return_value = mock_service

                mock_user = Mock()
                mock_user.id = "user-id"
                mock_user.is_verified = True
                mock_user.is_active = True
                mock_service.login.return_value = mock_user

                with patch("apps.api.src.routes.auth.AuthService._create_access_token") as mock_token:
                    mock_token.return_value = "access-token"

                    response = client.post(
                        "/v1/auth/login",
                        json={
                            "email": "test@example.com",
                            "password": "password_123"
                        }
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert "access_token" in data
                    assert data["user"]["id"] == "user-id"

    def test_login_invalid_credentials(self, client, mock_db):
        with patch("apps.api.src.routes.auth.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.auth.AuthService") as mock_auth_service:
                mock_service = Mock()
                mock_auth_service.return_value = mock_service

                mock_service.login.side_effect = AuthError("Invalid credentials")

                response = client.post(
                    "/v1/auth/login",
                    json={
                        "email": "test@example.com",
                        "password": "wrong_password"
                    }
                )

                assert response.status_code == 401

    def test_verify_email_success(self, client, mock_db):
        with patch("apps.api.src.routes.auth.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.auth.AuthService") as mock_auth_service:
                mock_service = Mock()
                mock_auth_service.return_value = mock_service

                mock_user = Mock()
                mock_user.id = "user-id"
                mock_service.verify_email.return_value = mock_user

                response = client.post(
                    "/v1/auth/verify-email",
                    json={"token": "valid-token"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["user"]["id"] == "user-id"

    def test_verify_email_invalid_token(self, client, mock_db):
        with patch("apps.api.src.routes.auth.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.auth.AuthService") as mock_auth_service:
                mock_service = Mock()
                mock_auth_service.return_value = mock_service

                mock_service.verify_email.side_effect = EmailVerificationError("Invalid token")

                response = client.post(
                    "/v1/auth/verify-email",
                    json={"token": "invalid-token"}
                )

                assert response.status_code == 400

    def test_me_authenticated(self, client, mock_db):
        with patch("apps.api.src.routes.auth.get_db", return_value=mock_db):
            mock_user = Mock()
            mock_user.id = "user-id"
            mock_user.email = "test@example.com"

            response = client.get(
                "/v1/auth/me",
                headers={"Authorization": "Bearer valid-token"}
            )

            assert response.status_code == 200

    def test_me_unauthenticated(self, client):
        response = client.get("/v1/auth/me")

        assert response.status_code == 401

    def test_logout_success(self, client, mock_db):
        with patch("apps.api.src.routes.auth.get_db", return_value=mock_db):
            with patch("apps.api.src.routes.auth.AuthService") as mock_auth_service:
                mock_service = Mock()
                mock_auth_service.return_value = mock_service

                response = client.post(
                    "/v1/auth/logout",
                    headers={"Authorization": "Bearer valid-token"},
                    json={"refresh_token": "refresh-token"}
                )

                assert response.status_code == 204
                mock_service.logout.assert_called_once()

    def test_oauth_google_url(self, client):
        response = client.get("/v1/auth/oauth/google")

        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "google.com" in data["authorization_url"]
