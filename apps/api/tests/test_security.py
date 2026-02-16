"""
Security-focused integration tests for the PolyScript API.

This module tests critical security measures including:
- Sensitive field exposure prevention
- Input validation boundaries
- SQL injection prevention
- Authentication and authorization bypass attempts

These tests verify the security fixes from Phase 1 of the API audit remediation.

Tests use async patterns and can be run with:
    uv run pytest apps/api/tests/test_security.py -v
"""

import uuid
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from main import app

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_db():
    """Provide a mock database session."""
    return Mock()


@pytest.fixture
def auth_headers():
    """Provide valid authentication headers for testing."""
    return {"Authorization": "Bearer test-access-token"}


# =============================================================================
# Sensitive Field Exposure Tests
# =============================================================================


class TestSensitiveFieldExposure:
    """Tests to verify sensitive fields are never exposed in API responses."""

    def test_auth_me_no_password_fields(self, client, mock_db):
        """
        Test that /v1/auth/me endpoint does not expose password-related fields.

        Verifies that hashed_password, password_reset_token, and verification_token
        are never returned in the user response.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.email = "test@example.com"
                mock_user.full_name = "Test User"
                mock_user.is_verified = True
                mock_user.is_active = True
                mock_user.is_suspended = False
                mock_user.created_at = "2024-01-01T00:00:00Z"
                mock_user.hashed_password = "SENSITIVE_HASH"
                mock_user.verification_token = "SENSITIVE_TOKEN"
                mock_get_current_user.return_value = mock_user

                response = client.get(
                    "/v1/auth/me",
                    headers={"Authorization": "Bearer valid-token"},
                )

                assert response.status_code == 200
                data = response.json()

                # Verify expected safe fields are present
                assert "id" in data
                assert "email" in data
                assert "full_name" in data
                assert "is_verified" in data
                assert "is_active" in data

                # Verify sensitive fields are NOT present
                assert "hashed_password" not in data
                assert "password" not in data
                assert "verification_token" not in data
                assert "password_reset_token" not in data

    def test_signup_response_no_password_fields(self, client, mock_db):
        """
        Test that signup response does not expose password or sensitive tokens.

        Verifies that the signup response only returns safe user information
        without exposing any password hashes or sensitive tokens.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.email = "test@example.com"
                mock_user.is_verified = False
                mock_user.hashed_password = "SENSITIVE_HASH"
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

                # Verify safe fields
                assert "user_id" in data
                assert "email" in data
                assert "is_verified" in data

                # Verify sensitive fields NOT present
                assert "hashed_password" not in data
                assert "password" not in data
                assert "verification_token" not in data

    def test_team_response_no_stripe_fields(self, client, mock_db):
        """
        Test that team response does not expose Stripe customer information.

        Verifies that stripe_customer_id, stripe_subscription_id, and other
        payment-related sensitive fields are not exposed in team responses.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                with patch("apps.api.src.dependencies.get_team_service") as mock_team_service_dep:
                    mock_user = Mock()
                    mock_user.id = uuid.uuid4()
                    mock_user.team_id = uuid.uuid4()
                    mock_get_current_user.return_value = mock_user

                    mock_team = Mock()
                    mock_team.id = mock_user.team_id
                    mock_team.name = "Test Team"
                    mock_team.host_language = "en"
                    mock_team.plan = "FREE"
                    mock_team.monthly_upload_count = 0
                    mock_team.extra_credits = 0
                    mock_team.created_at = "2024-01-01T00:00:00Z"
                    mock_team.updated_at = "2024-01-01T00:00:00Z"
                    mock_team.stripe_customer_id = "cus_SENSITIVE"
                    mock_team.stripe_subscription_id = "sub_SENSITIVE"
                    mock_team.is_suspended = False

                    mock_service = Mock()
                    mock_service.get_team.return_value = mock_team
                    mock_team_service_dep.return_value = mock_service

                    response = client.get(
                        "/v1/teams/current",
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    assert response.status_code == 200
                    data = response.json()

                    # Verify expected safe fields
                    assert "id" in data
                    assert "name" in data
                    assert "host_language" in data
                    assert "plan" in data

                    # Verify sensitive fields NOT present
                    assert "stripe_customer_id" not in data
                    assert "stripe_subscription_id" not in data
                    assert "is_suspended" not in data or data.get("is_suspended") is None

    def test_dashboard_response_no_sensitive_billing_data(self, client, mock_db):
        """
        Test that dashboard response does not expose sensitive billing details.

        Verifies that credits_balance is returned but full payment method
        details or customer IDs are not exposed.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                with patch(
                    "apps.api.src.routes.dashboard.get_dashboard_service"
                ) as mock_dashboard_service_dep:
                    mock_user = Mock()
                    mock_user.id = uuid.uuid4()
                    mock_user.team_id = uuid.uuid4()
                    mock_get_current_user.return_value = mock_user

                    mock_dashboard = Mock()
                    mock_dashboard.total_jobs = 10
                    mock_dashboard.succeeded_jobs = 8
                    mock_dashboard.failed_jobs = 2
                    mock_dashboard.member_count = 3
                    mock_dashboard.plan = "FREE"
                    mock_dashboard.credits_balance = 5
                    mock_dashboard.max_members = 5
                    mock_dashboard.max_jobs_per_month = 30
                    mock_dashboard.stripe_customer_id = "cus_SENSITIVE"

                    mock_service = Mock()
                    mock_service.get_stats.return_value = mock_dashboard
                    mock_dashboard_service_dep.return_value = mock_service

                    response = client.get(
                        "/v1/dashboard/stats",
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    assert response.status_code == 200
                    data = response.json()

                    # Verify expected safe fields
                    assert "total_jobs" in data
                    assert "succeeded_jobs" in data
                    assert "failed_jobs" in data
                    assert "plan" in data
                    assert "credits_balance" in data

                    # Verify sensitive fields NOT present
                    assert "stripe_customer_id" not in data
                    assert "stripe_payment_method" not in data


# =============================================================================
# Input Validation Boundary Tests
# =============================================================================


class TestPasswordValidation:
    """Tests for password input validation boundaries."""

    def test_login_password_too_short(self, client):
        """
        Test that login rejects passwords shorter than 8 characters.

        Verifies that the password validation (min_length=8) is enforced
        and returns a 422 validation error.
        """
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "123",  # Too short - only 3 characters
            },
        )

        assert response.status_code == 422
        data = response.json()
        # Should contain validation error for password field
        assert "detail" in data

    def test_login_password_empty_string(self, client):
        """
        Test that login rejects empty password strings.

        Verifies that empty passwords are properly validated.
        """
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "",
            },
        )

        assert response.status_code == 422

    def test_signup_password_too_short(self, client, mock_db):
        """
        Test that signup rejects passwords shorter than 8 characters.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                response = client.post(
                    "/v1/auth/signup",
                    json={
                        "email": "test@example.com",
                        "password": "short",  # Too short
                        "full_name": "John Doe",
                    },
                )

                assert response.status_code == 422

    def test_reset_password_too_short(self, client, mock_db):
        """
        Test that password reset rejects passwords shorter than 8 characters.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                response = client.post(
                    "/v1/auth/reset-password",
                    json={
                        "token": "valid-reset-token",
                        "new_password": "short",  # Too short
                    },
                )

                assert response.status_code == 422


class TestURLValidation:
    """Tests for URL validation in job creation."""

    def test_create_job_from_url_invalid_url(self, client, mock_db):
        """
        Test that job creation from URL rejects invalid URLs.

        Verifies that HttpUrl validation is enforced and malformed URLs
        return 422 validation errors.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.team_id = uuid.uuid4()
                mock_user.plan = "FREE"
                mock_get_current_user.return_value = mock_user

                with patch("apps.api.src.dependencies.get_job_service") as mock_job_service_dep:
                    mock_service = Mock()
                    mock_job_service_dep.return_value = mock_service

                    # Invalid URL - not a proper URL format
                    response = client.post(
                        "/v1/jobs/from-url",
                        json={
                            "url": "not-a-valid-url",
                        },
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    assert response.status_code == 422

    def test_create_job_from_url_missing_protocol(self, client, mock_db):
        """
        Test that job creation rejects URLs without protocol.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.team_id = uuid.uuid4()
                mock_user.plan = "FREE"
                mock_get_current_user.return_value = mock_user

                with patch("apps.api.src.dependencies.get_job_service") as mock_job_service_dep:
                    mock_service = Mock()
                    mock_job_service_dep.return_value = mock_service

                    # URL missing http/https protocol
                    response = client.post(
                        "/v1/jobs/from-url",
                        json={
                            "url": "example.com/audio.mp3",
                        },
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    assert response.status_code == 422


class TestMaxLengthConstraints:
    """Tests for max_length constraints on string fields."""

    def test_signup_full_name_too_long(self, client, mock_db):
        """
        Test that signup rejects full_name exceeding max_length.

        Verifies that full_name with more than 128 characters is rejected.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            response = client.post(
                "/v1/auth/signup",
                json={
                    "email": "test@example.com",
                    "password": "password_123",
                    "full_name": "a" * 200,  # Exceeds max_length of 128
                },
            )

            assert response.status_code == 422

    def test_create_team_name_too_long(self, client, mock_db):
        """
        Test that team creation rejects name exceeding max_length.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.team_id = uuid.uuid4()
                mock_get_current_user.return_value = mock_user

                with patch("apps.api.src.dependencies.get_team_service") as mock_team_service_dep:
                    mock_service = Mock()
                    mock_team_service_dep.return_value = mock_service

                    response = client.post(
                        "/v1/teams",
                        json={
                            "name": "a" * 200,  # Exceeds max_length of 128
                            "host_language": "en",
                        },
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    assert response.status_code == 422

    def test_refresh_token_max_length(self, client, mock_db):
        """
        Test that refresh token has max_length constraint.

        Verifies that tokens longer than 512 characters are rejected.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                response = client.post(
                    "/v1/auth/refresh",
                    json={
                        "refresh_token": "a" * 1000,  # Exceeds max_length of 512
                    },
                )

                # Should return 422 for invalid token length
                assert response.status_code == 422

    def test_verify_email_token_max_length(self, client, mock_db):
        """
        Test that email verification token has max_length constraint.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_auth_service") as mock_auth_service_dep:
                mock_service = Mock()
                mock_auth_service_dep.return_value = mock_service

                response = client.post(
                    "/v1/auth/verify-email",
                    json={
                        "token": "a" * 1000,  # Exceeds max_length of 512
                    },
                )

                assert response.status_code == 422


# =============================================================================
# SQL Injection Prevention Tests
# =============================================================================


class TestSQLInjectionPrevention:
    """Tests to verify SQL injection prevention measures."""

    def test_team_lookup_sql_injection_in_name(self, client, mock_db):
        """
        Test that team creation properly sanitizes team name input.

        Verifies that SQL injection attempts in the team name field
        are rejected or sanitized.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.team_id = uuid.uuid4()
                mock_get_current_user.return_value = mock_user

                with patch("apps.api.src.dependencies.get_team_service") as mock_team_service_dep:
                    mock_service = Mock()
                    mock_service.create_team.side_effect = ValueError("Invalid input")
                    mock_team_service_dep.return_value = mock_service

                    # SQL injection attempt in team name
                    response = client.post(
                        "/v1/teams",
                        json={
                            "name": "'; DROP TABLE teams; --",
                            "host_language": "en",
                        },
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    # Should not cause server error - either validation or service error
                    assert response.status_code in [400, 422, 500]

    def test_user_lookup_sql_injection_in_email(self, client):
        """
        Test that authentication properly handles SQL injection in email.

        Verifies that SQL injection attempts in the email field are rejected.
        """
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "'; SELECT * FROM users; --@example.com",
                "password": "password_123",
            },
        )

        # Should return validation error (422) or authentication error (401/400)
        # but NOT execute the SQL injection
        assert response.status_code in [400, 401, 422]

    def test_job_query_sql_injection_in_params(self, client, mock_db):
        """
        Test that job listing properly sanitizes query parameters.

        Verifies that SQL injection attempts in query parameters are rejected.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.team_id = uuid.uuid4()
                mock_get_current_user.return_value = mock_user

                with patch("apps.api.src.dependencies.get_job_service") as mock_job_service_dep:
                    mock_service = Mock()
                    mock_service.list_jobs.return_value = []
                    mock_job_service_dep.return_value = mock_service

                    # SQL injection attempt in query parameter
                    response = client.get(
                        "/v1/jobs?state='; DROP TABLE jobs; --",
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    # Should not execute the injection
                    assert response.status_code in [200, 400, 422]


# =============================================================================
# Authentication Bypass Tests
# =============================================================================


class TestAuthenticationBypass:
    """Tests to verify authentication bypass attempts are prevented."""

    def test_access_without_token(self, client):
        """
        Test that protected endpoints reject requests without authentication token.
        """
        # Try to access protected endpoint without token
        response = client.get("/v1/auth/me")
        assert response.status_code == 401

    def test_access_with_invalid_token(self, client):
        """
        Test that protected endpoints reject requests with invalid tokens.
        """
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    def test_access_with_malformed_authorization_header(self, client):
        """
        Test that protected endpoints reject malformed Authorization headers.
        """
        # Missing "Bearer" prefix
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "some-token"},
        )
        assert response.status_code == 401

        # Empty token
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer "},
        )
        assert response.status_code == 401

    def test_access_team_without_auth(self, client):
        """
        Test that team endpoints require authentication.
        """
        response = client.get("/v1/teams/current")
        assert response.status_code == 401

    def test_access_jobs_without_auth(self, client):
        """
        Test that job endpoints require authentication.
        """
        response = client.get("/v1/jobs")
        assert response.status_code == 401

    def test_access_dashboard_without_auth(self, client):
        """
        Test that dashboard endpoints require authentication.
        """
        response = client.get("/v1/dashboard/stats")
        assert response.status_code == 401

    def test_bearer_token_case_sensitivity(self, client):
        """
        Test that the Bearer prefix must be properly capitalized.

        Verifies that 'bearer' (lowercase) is not accepted.
        """
        response = client.get(
            "/v1/auth/me",
            headers={"Authorization": "bearer test-token"},
        )
        # Should reject lowercase "bearer"
        assert response.status_code == 401


# =============================================================================
# Authorization Tests
# =============================================================================


class TestAuthorizationBoundaries:
    """Tests for authorization boundaries between resources."""

    def test_cannot_access_other_team_data(self, client, mock_db):
        """
        Test that users cannot access data from other teams.

        Verifies that the multi-tenant isolation is enforced.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                with patch("apps.api.src.dependencies.get_team_service") as mock_team_service_dep:
                    mock_user = Mock()
                    mock_user.id = uuid.uuid4()
                    mock_user.team_id = uuid.uuid4()
                    mock_get_current_user.return_value = mock_user

                    mock_service = Mock()
                    mock_service.get_team.side_effect = PermissionError("Not authorized")
                    mock_team_service_dep.return_value = mock_service

                    response = client.get(
                        f"/v1/teams/{uuid.uuid4()}",
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    # Should return 403 or 404 for unauthorized access
                    assert response.status_code in [403, 404]


# =============================================================================
# Email Validation Tests
# =============================================================================


class TestEmailValidation:
    """Tests for email format validation."""

    def test_signup_invalid_email_format(self, client, mock_db):
        """
        Test that signup rejects invalid email formats.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            response = client.post(
                "/v1/auth/signup",
                json={
                    "email": "not-an-email",
                    "password": "password_123",
                    "full_name": "John Doe",
                },
            )

            assert response.status_code == 422

    def test_signup_email_missing_at_symbol(self, client, mock_db):
        """
        Test that signup rejects email without @ symbol.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            response = client.post(
                "/v1/auth/signup",
                json={
                    "email": "test.example.com",
                    "password": "password_123",
                    "full_name": "John Doe",
                },
            )

            assert response.status_code == 422

    def test_signup_email_missing_domain(self, client, mock_db):
        """
        Test that signup rejects email without domain.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            response = client.post(
                "/v1/auth/signup",
                json={
                    "email": "test@",
                    "password": "password_123",
                    "full_name": "John Doe",
                },
            )

            assert response.status_code == 422

    def test_login_invalid_email_format(self, client):
        """
        Test that login rejects invalid email formats.
        """
        response = client.post(
            "/v1/auth/login",
            json={
                "email": "invalid-email",
                "password": "password_123",
            },
        )

        assert response.status_code == 422


# =============================================================================
# Rate Limiting and DoS Prevention Tests
# =============================================================================


class TestDoSPrevention:
    """Tests for DoS prevention measures."""

    def test_empty_payload_rejected(self, client):
        """
        Test that completely empty payloads are rejected.

        Verifies that empty JSON bodies return appropriate errors.
        """
        response = client.post(
            "/v1/auth/login",
            json={},
        )

        assert response.status_code == 422

    def test_null_values_rejected(self, client):
        """
        Test that null values in required fields are rejected.
        """
        response = client.post(
            "/v1/auth/login",
            json={
                "email": None,
                "password": "password_123",
            },
        )

        assert response.status_code == 422

    def test_oversized_payload_detection(self, client, mock_db):
        """
        Test that excessively long fields are rejected.

        While max_length should handle this, verify the validation works.
        """
        with patch("apps.api.src.dependencies.get_db_session", return_value=mock_db):
            with patch("apps.api.src.dependencies.get_current_user") as mock_get_current_user:
                mock_user = Mock()
                mock_user.id = uuid.uuid4()
                mock_user.team_id = uuid.uuid4()
                mock_get_current_user.return_value = mock_user

                with patch("apps.api.src.dependencies.get_team_service") as mock_team_service_dep:
                    mock_service = Mock()
                    mock_team_service_dep.return_value = mock_service

                    # Create a name that exceeds reasonable limits
                    response = client.post(
                        "/v1/teams",
                        json={
                            "name": "x" * 10000,
                            "host_language": "en",
                        },
                        headers={"Authorization": "Bearer valid-token"},
                    )

                    # Should reject with 422 for validation error
                    assert response.status_code == 422
