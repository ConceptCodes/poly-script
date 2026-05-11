"""Security-focused API boundary tests."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from poly_db.database import get_db
from src.dependencies import (
    get_async_auth_service,
    get_current_team_id,
    get_current_user,
    get_team_context,
)
from src.routes.dashboard import get_dashboard_service
from src.routes.teams import get_team_service

from ..main import app
from . import setup_paths as _setup_paths

del _setup_paths


USER_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440010")
TEAM_ID = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")


@pytest.fixture
def client():
    original_overrides = app.dependency_overrides.copy()
    try:
        yield TestClient(app, raise_server_exceptions=False)
    finally:
        app.dependency_overrides = original_overrides


def auth_user(**overrides):
    values = {
        "id": USER_ID,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_verified": True,
        "is_active": True,
        "is_suspended": False,
        "created_at": "2026-01-01T00:00:00Z",
    }
    values.update(overrides)
    return values


def override_auth(**user_overrides):
    app.dependency_overrides[get_current_user] = lambda: auth_user(**user_overrides)
    app.dependency_overrides[get_current_team_id] = lambda: TEAM_ID
    app.dependency_overrides[get_team_context] = lambda: {"id": TEAM_ID, "role": "ADMIN"}


def team_response(**overrides):
    values = {
        "id": TEAM_ID,
        "name": "Test Team",
        "host_language": "en",
        "plan": "FREE",
        "monthly_upload_count": 0,
        "extra_credits": 0,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "stripe_customer_id": "cus_sensitive",
        "stripe_subscription_id": "sub_sensitive",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class TestSensitiveFieldExposure:
    """Verify sensitive fields are never exposed in API responses."""

    def test_auth_me_no_password_fields(self, client):
        override_auth(
            hashed_password="SENSITIVE_HASH",
            verification_token="SENSITIVE_TOKEN",
            password_reset_token="SENSITIVE_RESET_TOKEN",
        )
        app.dependency_overrides[get_db] = lambda: Mock()

        with patch("src.routes.auth.TeamMemberRepository") as member_repo_class:
            member_repo_class.return_value.list_by_user_id.return_value = []
            response = client.get("/v1/auth/me")

        assert response.status_code == 200
        data = response.json()["user"]
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data
        assert "password" not in data
        assert "verification_token" not in data
        assert "password_reset_token" not in data

    def test_signup_response_no_password_fields(self, client):
        auth_service = AsyncMock()
        auth_service.create_user.return_value = SimpleNamespace(
            id=USER_ID,
            email="test@example.com",
            full_name="John Doe",
            is_verified=False,
            hashed_password="SENSITIVE_HASH",
            verification_token="SENSITIVE_TOKEN",
        )
        app.dependency_overrides[get_async_auth_service] = lambda: auth_service

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
        assert data["user_id"] == str(USER_ID)
        assert "hashed_password" not in data
        assert "password" not in data
        assert "verification_token" not in data

    def test_team_response_no_stripe_fields(self, client):
        override_auth()
        service = Mock()
        service.get_team.return_value = team_response()
        app.dependency_overrides[get_team_service] = lambda: service

        response = client.get(f"/v1/teams/{TEAM_ID}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(TEAM_ID)
        assert "stripe_customer_id" not in data
        assert "stripe_subscription_id" not in data

    def test_dashboard_response_no_sensitive_billing_data(self, client):
        override_auth()
        service = Mock()
        service.get_dashboard_stats.return_value = {
            "total_jobs": 10,
            "succeeded_jobs": 8,
            "failed_jobs": 2,
            "member_count": 3,
            "plan": "FREE",
            "credits_balance": 5,
            "max_members": 5,
            "max_jobs_per_month": 30,
            "stripe_customer_id": "cus_sensitive",
        }
        app.dependency_overrides[get_dashboard_service] = lambda: service

        response = client.get("/v1/dashboard/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["credits_balance"] == 5
        assert "stripe_customer_id" not in data
        assert "stripe_payment_method" not in data


class TestPasswordValidation:
    """Tests for password input validation boundaries."""

    def test_login_password_too_short(self, client):
        response = client.post(
            "/v1/auth/login",
            json={"email": "test@example.com", "password": "123"},
        )

        assert response.status_code == 422

    def test_login_password_empty_string(self, client):
        response = client.post(
            "/v1/auth/login",
            json={"email": "test@example.com", "password": ""},
        )

        assert response.status_code == 422

    def test_signup_password_too_short(self, client):
        response = client.post(
            "/v1/auth/signup",
            json={"email": "test@example.com", "password": "short", "full_name": "John Doe"},
        )

        assert response.status_code == 422

    def test_reset_password_too_short(self, client):
        response = client.post(
            "/v1/auth/reset-password",
            json={"token": "valid-reset-token", "new_password": "short"},
        )

        assert response.status_code == 422


class TestURLValidation:
    """Tests for URL validation in job creation."""

    def test_create_job_from_url_invalid_url(self, client):
        override_auth()

        response = client.post("/v1/jobs/url", json={"url": "not-a-valid-url"})

        assert response.status_code == 422

    def test_create_job_from_url_missing_protocol(self, client):
        override_auth()

        response = client.post("/v1/jobs/url", json={"url": "example.com/audio.mp3"})

        assert response.status_code == 422


class TestMaxLengthConstraints:
    """Tests for max_length constraints on string fields."""

    def test_signup_full_name_too_long(self, client):
        response = client.post(
            "/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password_123",
                "full_name": "a" * 200,
            },
        )

        assert response.status_code == 422

    def test_create_team_name_too_long(self, client):
        override_auth()
        app.dependency_overrides[get_team_service] = lambda: Mock()

        response = client.post(
            "/v1/teams",
            json={"name": "a" * 200, "host_language": "en"},
        )

        assert response.status_code == 422

    def test_refresh_token_max_length(self, client):
        response = client.post("/v1/auth/refresh", json={"refresh_token": "a" * 1000})

        assert response.status_code == 422

    def test_verify_email_token_max_length(self, client):
        response = client.post("/v1/auth/verify-email", json={"token": "a" * 1000})

        assert response.status_code == 422


class TestSQLInjectionPrevention:
    """Tests to verify SQL injection prevention measures."""

    def test_team_lookup_sql_injection_in_name(self, client):
        override_auth()
        service = Mock()
        service.create_team.side_effect = ValueError("Invalid input")
        app.dependency_overrides[get_team_service] = lambda: service

        response = client.post(
            "/v1/teams",
            json={"name": "'; DROP TABLE teams; --", "host_language": "en"},
        )

        assert response.status_code in [400, 422, 500]

    def test_user_lookup_sql_injection_in_email(self, client):
        response = client.post(
            "/v1/auth/login",
            json={"email": "'; SELECT * FROM users; --@example.com", "password": "password_123"},
        )

        assert response.status_code in [400, 401, 422]

    def test_job_query_sql_injection_in_params(self, client):
        override_auth()

        with patch("src.routes.jobs.get_db_session") as db_session:
            db_session.return_value.__enter__.return_value = Mock()
            with patch("src.routes.jobs.TranscriptionJobRepository") as repo_class:
                repo_class.return_value.get_by_team_id.return_value = []
                response = client.get("/v1/jobs?status_filter='; DROP TABLE jobs; --")

        assert response.status_code in [200, 400, 422]


class TestAuthenticationBypass:
    """Tests to verify authentication bypass attempts are prevented."""

    def test_access_without_token(self, client):
        response = client.get("/v1/auth/me")
        assert response.status_code == 401

    def test_access_with_invalid_token(self, client):
        response = client.get("/v1/auth/me", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401

    def test_access_with_malformed_authorization_header(self, client):
        response = client.get("/v1/auth/me", headers={"Authorization": "some-token"})
        assert response.status_code == 401

        response = client.get("/v1/auth/me", headers={"Authorization": "Bearer "})
        assert response.status_code == 401

    def test_access_team_without_auth(self, client):
        response = client.get(f"/v1/teams/{TEAM_ID}")
        assert response.status_code == 401

    def test_access_jobs_without_auth(self, client):
        response = client.get("/v1/jobs")
        assert response.status_code == 401

    def test_access_dashboard_without_auth(self, client):
        response = client.get("/v1/dashboard/stats")
        assert response.status_code == 401

    def test_bearer_token_case_sensitivity(self, client):
        response = client.get("/v1/auth/me", headers={"Authorization": "bearer test-token"})
        assert response.status_code == 401


class TestAuthorizationBoundaries:
    """Tests for authorization boundaries between resources."""

    def test_cannot_access_other_team_data(self, client):
        override_auth()
        service = Mock()
        service.get_team.return_value = None
        app.dependency_overrides[get_team_service] = lambda: service

        response = client.get(f"/v1/teams/{uuid.uuid4()}")

        assert response.status_code in [403, 404]


class TestEmailValidation:
    """Tests for email format validation."""

    def test_signup_invalid_email_format(self, client):
        response = client.post(
            "/v1/auth/signup",
            json={"email": "not-an-email", "password": "password_123", "full_name": "John Doe"},
        )

        assert response.status_code == 422

    def test_signup_email_missing_at_symbol(self, client):
        response = client.post(
            "/v1/auth/signup",
            json={"email": "test.example.com", "password": "password_123", "full_name": "John Doe"},
        )

        assert response.status_code == 422

    def test_signup_email_missing_domain(self, client):
        response = client.post(
            "/v1/auth/signup",
            json={"email": "test@", "password": "password_123", "full_name": "John Doe"},
        )

        assert response.status_code == 422

    def test_login_invalid_email_format(self, client):
        response = client.post(
            "/v1/auth/login",
            json={"email": "invalid-email", "password": "password_123"},
        )

        assert response.status_code == 422


class TestDoSPrevention:
    """Tests for DoS prevention measures."""

    def test_empty_payload_rejected(self, client):
        response = client.post("/v1/auth/login", json={})

        assert response.status_code == 422

    def test_null_values_rejected(self, client):
        response = client.post(
            "/v1/auth/login",
            json={"email": None, "password": "password_123"},
        )

        assert response.status_code == 422

    def test_oversized_payload_detection(self, client):
        override_auth()
        app.dependency_overrides[get_team_service] = lambda: Mock()

        response = client.post(
            "/v1/teams",
            json={"name": "x" * 10000, "host_language": "en"},
        )

        assert response.status_code == 422
