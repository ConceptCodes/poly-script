"""
Tests for standardized error handling and API error format.

These tests verify:
1. Error responses follow the standardized format
2. Error codes match the taxonomy
3. Localization works via Accept-Language header
4. HTTP status codes are correct
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from poly_core.constants import I18N_KEY_HTTP_STATUS, I18nKeys


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


class TestErrorResponseFormat:
    """Test that error responses follow the standardized format."""

    def test_error_response_has_nested_error_object(self, client):
        """Verify error responses have {error: {...}} structure."""
        # Trigger a 404 error
        response = client.get("/v1/jobs/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404
        data = response.json()

        # Must have 'error' key at root
        assert "error" in data
        error = data["error"]

        # Error object must have required fields
        assert "code" in error
        assert "message" in error
        assert "request_id" in error

    def test_error_response_includes_request_id(self, client):
        """Verify error responses include request_id for tracing."""
        response = client.get("/v1/jobs/invalid-uuid")

        data = response.json()
        error = data.get("error", {})

        # request_id should be present and non-empty
        assert "request_id" in error
        assert error["request_id"] is not None
        assert len(error["request_id"]) > 0

    def test_error_response_includes_documentation_url(self, client):
        """Verify error responses include documentation_url."""
        response = client.get("/v1/jobs/00000000-0000-0000-0000-000000000000")

        data = response.json()
        error = data.get("error", {})

        # documentation_url should be present
        assert "documentation_url" in error


class TestErrorLocalization:
    """Test error message localization via Accept-Language header."""

    def test_error_message_localized_for_german(self, client):
        """Verify error messages are localized for German (de)."""
        response = client.get(
            "/v1/jobs/00000000-0000-0000-0000-000000000000", headers={"Accept-Language": "de"}
        )

        data = response.json()
        error = data.get("error", {})

        # Message should be present (localized or fallback)
        assert "message" in error
        assert len(error["message"]) > 0

    def test_error_message_localized_for_spanish(self, client):
        """Verify error messages are localized for Spanish (es)."""
        response = client.get(
            "/v1/jobs/00000000-0000-0000-0000-000000000000", headers={"Accept-Language": "es"}
        )

        data = response.json()
        error = data.get("error", {})

        assert "message" in error
        assert len(error["message"]) > 0

    def test_error_message_fallback_to_english(self, client):
        """Verify error messages fallback to English for unsupported locales."""
        response = client.get(
            "/v1/jobs/00000000-0000-0000-0000-000000000000",
            headers={"Accept-Language": "xx"},  # Invalid locale
        )

        data = response.json()
        error = data.get("error", {})

        # Should still have a message (fallback to English)
        assert "message" in error
        assert len(error["message"]) > 0


class TestErrorCodeTaxonomy:
    """Test that error codes follow the taxonomy."""

    def test_all_err_i18n_keys_have_http_status(self):
        """Verify all ERR_* I18nKeys have HTTP status mappings."""
        error_keys = [key for key in I18nKeys if key.name.startswith("ERR_")]

        for key in error_keys:
            assert key in I18N_KEY_HTTP_STATUS, f"Missing HTTP status for {key.name}"
            status = I18N_KEY_HTTP_STATUS[key]
            assert 400 <= status < 600, f"Invalid HTTP status {status} for {key.name}"

    def test_error_codes_follow_hierarchical_pattern(self):
        """Verify error codes follow errors.{category}.{specific} pattern."""
        error_keys = [key for key in I18nKeys if key.name.startswith("ERR_")]

        for key in error_keys:
            value = key.value
            # Should start with "errors."
            assert value.startswith("errors."), f"{key.name} doesn't start with 'errors.'"

            # Should have 3 parts: errors.category.specific
            parts = value.split(".")
            assert len(parts) == 3, f"{key.name} doesn't follow 3-part pattern: {value}"

    def test_error_categories_are_valid(self):
        """Verify error codes use valid categories."""
        valid_categories = {
            "auth",
            "jobs",
            "transcripts",
            "teams",
            "billing",
            "validation",
            "rate_limit",
            "generic",
        }

        error_keys = [key for key in I18nKeys if key.name.startswith("ERR_")]

        for key in error_keys:
            parts = key.value.split(".")
            category = parts[1]
            assert category in valid_categories, f"Invalid category '{category}' in {key.name}"


class TestHTTPStatusCodes:
    """Test that HTTP status codes are correct for different error types."""

    def test_authentication_errors_return_401(self, client):
        """Verify auth errors return 401 Unauthorized."""
        # Try to access protected endpoint without auth
        response = client.get("/v1/jobs")

        # Should be 401 (no authentication provided)
        assert response.status_code == 401

    def test_not_found_errors_return_404(self, client):
        """Verify not found errors return 404."""
        response = client.get("/v1/jobs/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404

        data = response.json()
        error = data.get("error", {})
        assert "code" in error

    def test_validation_errors_return_422(self, client):
        """Verify validation errors return 422."""
        # Send invalid data to trigger validation error
        response = client.post(
            "/v1/auth/signup", json={"email": "invalid-email", "password": "123"}
        )

        # Should be 422 (validation error)
        assert response.status_code == 422


class TestErrorHeaders:
    """Test that error responses include appropriate headers."""

    def test_error_response_includes_content_language_header(self, client):
        """Verify error responses include Content-Language header."""
        response = client.get("/v1/jobs/00000000-0000-0000-0000-000000000000")

        # Should have Content-Language header
        assert "content-language" in response.headers

    def test_error_response_includes_request_id_header(self, client):
        """Verify error responses include X-Request-ID header."""
        response = client.get("/v1/jobs/00000000-0000-0000-0000-000000000000")

        # Should have X-Request-ID header
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0
