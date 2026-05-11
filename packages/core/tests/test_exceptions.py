"""
Tests for standardized exception handling system.
"""

from typing import ClassVar

import pytest
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from poly_core.exceptions.base import (
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    ErrorSeverity,
)
from poly_core.exceptions.common import (
    BadRequestError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)
from poly_core.exceptions.handlers import (
    get_locale_from_request,
    localize_error_message,
    setup_exception_handlers,
)
from poly_core.exceptions.utils import convert_http_exception


class TestErrorSchemas:
    """Test error response schemas and models."""

    def test_error_response_schema(self):
        """Test ErrorResponse Pydantic model."""
        error_response = ErrorResponse(
            error={
                "code": "TEST_ERROR",
                "message": "Test error message",
                "details": None,
                "severity": "error",
                "request_id": "req_123",
                "documentation_url": "https://example.com/errors/TEST_ERROR",
            }
        )

        assert error_response.error["code"] == "TEST_ERROR"
        assert error_response.error["message"] == "Test error message"
        assert error_response.error["severity"] == "error"
        assert error_response.error["request_id"] == "req_123"

    def test_error_detail_schema(self):
        """Test ErrorDetail Pydantic model."""
        error_detail = ErrorDetail(
            field="email",
            message="Invalid email format",
            code="email_invalid",
            value="invalid-email",
        )

        assert error_detail.field == "email"
        assert error_detail.message == "Invalid email format"
        assert error_detail.code == "email_invalid"
        assert error_detail.value == "invalid-email"

    def test_api_exception_to_dict(self):
        """Test APIException.to_dict() method."""
        exception = BadRequestError(
            message="Test error",
            code=ErrorCode.VALIDATION_INVALID_INPUT,
            request_id="req_123",
        )

        error_dict = exception.to_dict()

        assert error_dict["code"] == "VALIDATION_INVALID_INPUT"
        assert error_dict["message"] == "Test error"
        assert error_dict["severity"] == "error"
        assert error_dict["request_id"] == "req_123"


class TestExceptionClasses:
    """Test exception class hierarchy and behavior."""

    def test_bad_request_error(self):
        """Test BadRequestError properties."""
        error = BadRequestError(
            message="Invalid request",
            code=ErrorCode.VALIDATION_INVALID_INPUT,
        )

        assert error.status_code == 400
        assert error.code == ErrorCode.VALIDATION_INVALID_INPUT
        assert error.severity == ErrorSeverity.ERROR

    def test_not_found_error(self):
        """Test NotFoundError properties."""
        error = NotFoundError(message="Resource not found")

        assert error.status_code == 404
        assert error.code == ErrorCode.RESOURCE_NOT_FOUND

    def test_validation_error_with_details(self):
        """Test ValidationError with field details."""
        details = [
            ErrorDetail(field="email", message="Invalid email"),
            ErrorDetail(field="password", message="Too short"),
        ]

        error = ValidationError(
            message="Validation failed",
            details=details,
        )

        assert error.status_code == 422
        assert len(error.details) == 2
        assert error.details[0].field == "email"

    def test_internal_server_error(self):
        """Test InternalServerError properties."""
        error = InternalServerError(message="Unexpected error")

        assert error.status_code == 500
        assert error.code == ErrorCode.SYSTEM_INTERNAL_ERROR
        assert error.severity == ErrorSeverity.CRITICAL


class TestUtilityFunctions:
    """Test utility functions for error handling."""

    def test_convert_http_exception_400(self):
        """Test converting HTTPException 400 to BadRequestError."""
        http_exc = HTTPException(status_code=400, detail="Bad request")

        api_exc = convert_http_exception(http_exc)

        assert isinstance(api_exc, BadRequestError)
        assert api_exc.status_code == 400
        assert api_exc.message == "Bad request"

    def test_convert_http_exception_404(self):
        """Test converting HTTPException 404 to NotFoundError."""
        http_exc = HTTPException(status_code=404, detail="Not found")

        api_exc = convert_http_exception(http_exc)

        assert isinstance(api_exc, NotFoundError)
        assert api_exc.status_code == 404

    def test_convert_http_exception_with_custom_code(self):
        """Test converting with custom error code."""
        http_exc = HTTPException(status_code=400, detail="Invalid credentials")

        api_exc = convert_http_exception(
            http_exc,
            default_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            request_id="req_123",
        )

        assert api_exc.code == ErrorCode.AUTH_INVALID_CREDENTIALS
        assert api_exc.request_id == "req_123"


class TestLocalizationUtilities:
    """Test localization-related utility functions."""

    def test_get_locale_from_request_simple(self):
        """Test extracting locale from simple Accept-Language header."""

        class MockRequest:
            headers: ClassVar[dict[str, str]] = {"accept-language": "en"}

        request = MockRequest()
        locale = get_locale_from_request(request)

        assert locale == "en"

    def test_get_locale_from_request_complex(self):
        """Test extracting locale from complex Accept-Language header."""

        class MockRequest:
            headers: ClassVar[dict[str, str]] = {"accept-language": "en-US,en;q=0.9,fr;q=0.8"}

        request = MockRequest()
        locale = get_locale_from_request(request)

        assert locale == "en"

    def test_get_locale_from_request_fallback(self):
        """Test locale fallback to English."""

        class MockRequest:
            headers: ClassVar[dict[str, str]] = {"accept-language": "xx-YY"}

        request = MockRequest()
        locale = get_locale_from_request(request)

        assert locale == "en"

    def test_get_locale_from_request_missing_header(self):
        """Test locale extraction when header is missing."""

        class MockRequest:
            headers: ClassVar[dict[str, str]] = {}

        request = MockRequest()
        locale = get_locale_from_request(request)

        assert locale == "en"

    def test_localize_error_message_without_service(self):
        """Test localization without I18nService (returns default)."""
        message = localize_error_message(
            i18n_service=None,
            error_key="TEST_ERROR",
            locale="en",
            default_message="Default message",
        )

        assert message == "Default message"


# Test FastAPI integration
app = FastAPI()


@app.get("/test/bad-request")
def raise_bad_request():
    raise BadRequestError(message="Test bad request")


@app.get("/test/not-found")
def raise_not_found():
    raise NotFoundError(message="Test not found")


@app.get("/test/validation")
def raise_validation():
    raise ValidationError(
        message="Test validation", details=[ErrorDetail(field="test", message="Field error")]
    )


@app.get("/test/http-exception")
def raise_http_exception():
    raise HTTPException(status_code=400, detail="HTTP Exception")


@app.get("/test/unhandled")
def raise_unhandled():
    raise ValueError("Unhandled exception")


class TestFastAPIIntegration:
    """Test integration with FastAPI application."""

    @pytest.fixture
    def client(self):
        """Create test client with exception handlers."""
        setup_exception_handlers(app, i18n_service=None)
        return TestClient(app, raise_server_exceptions=False)

    def test_bad_request_endpoint(self, client):
        """Test endpoint raising BadRequestError."""
        response = client.get("/test/bad-request")

        assert response.status_code == 400
        data = response.json()

        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert data["error"]["message"] == "Test bad request"

    def test_not_found_endpoint(self, client):
        """Test endpoint raising NotFoundError."""
        response = client.get("/test/not-found")

        assert response.status_code == 404
        data = response.json()

        assert data["error"]["code"] == "RESOURCE_NOT_FOUND"

    def test_validation_endpoint(self, client):
        """Test endpoint raising ValidationError."""
        response = client.get("/test/validation")

        assert response.status_code == 422
        data = response.json()

        assert "details" in data["error"]
        assert len(data["error"]["details"]) == 1
        assert data["error"]["details"][0]["field"] == "test"

    def test_http_exception_endpoint(self, client):
        """Test endpoint raising HTTPException (legacy)."""
        response = client.get("/test/http-exception")

        assert response.status_code == 400
        data = response.json()

        # Should be converted to standardized format
        assert "error" in data
        assert "code" in data["error"]

    def test_unhandled_exception_endpoint(self, client):
        """Test endpoint raising unhandled exception."""
        response = client.get("/test/unhandled")

        assert response.status_code == 500
        data = response.json()

        # Should be converted to InternalServerError
        assert data["error"]["code"] == "SYSTEM_INTERNAL_ERROR"
        # Should not leak internal error message
        assert data["error"]["message"] == "An unexpected error occurred"
