"""
Utilities for migrating existing error handling to standardized format.
"""

from typing import Any

from fastapi import HTTPException, status

from .base import APIException, ErrorCode, ErrorDetail
from .common import (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)


def convert_http_exception(
    http_exc: HTTPException,
    default_code: ErrorCode | None = None,
    request_id: str | None = None,
) -> "APIException":
    """
    Convert existing HTTPException to standardized APIException.

    This utility helps migrate existing code that uses HTTPException
    to the new standardized error format.

    Args:
        http_exc: Original HTTPException instance
        default_code: Optional ErrorCode to use if mapping not found
        request_id: Optional request ID for correlation

    Returns:
        Standardized APIException
    """
    status_code = http_exc.status_code or 500
    detail = str(http_exc.detail) if http_exc.detail else "Unknown error"

    if status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
        return ValidationError(
            message=detail,
            request_id=request_id,
        )

    if status_code >= 500:
        return InternalServerError(
            message=detail,
            request_id=request_id,
        )

    error_map = {
        status.HTTP_400_BAD_REQUEST: (
            BadRequestError,
            default_code or ErrorCode.GENERIC_BAD_REQUEST,
        ),
        status.HTTP_401_UNAUTHORIZED: (
            AuthenticationError,
            default_code or ErrorCode.AUTH_INVALID_CREDENTIALS,
        ),
        status.HTTP_403_FORBIDDEN: (ForbiddenError, default_code or ErrorCode.GENERIC_FORBIDDEN),
        status.HTTP_404_NOT_FOUND: (NotFoundError, default_code or ErrorCode.RESOURCE_NOT_FOUND),
        status.HTTP_409_CONFLICT: (ConflictError, default_code or ErrorCode.RESOURCE_CONFLICT),
        status.HTTP_429_TOO_MANY_REQUESTS: (
            BadRequestError,
            default_code or ErrorCode.RATE_LIMIT_EXCEEDED,
        ),
    }
    exc_class, code = error_map.get(
        status_code,
        (BadRequestError, default_code or ErrorCode.GENERIC_BAD_REQUEST),
    )
    return exc_class(message=detail, code=code, request_id=request_id)


def create_error_response(
    code: ErrorCode,
    message: str,
    status_code: int = 400,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Create standardized error response dictionary.

    This is a convenience function for creating error responses
    in the new format without raising exceptions.

    Args:
        code: ErrorCode enum value
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional error details
        request_id: Optional request ID for correlation

    Returns:
        Dictionary in standardized error response format
    """
    error_dict = {
        "code": code.value,
        "message": message,
        "status_code": status_code,
        "severity": "error",
        "request_id": request_id,
    }

    if details:
        error_dict["details"] = details

    return {"error": error_dict}


def raise_standardized_error(
    code: ErrorCode,
    message: str,
    status_code: int = 400,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> None:
    """
    Raise standardized APIException with given parameters.

    This is a convenience function for raising standardized errors
    in existing code during migration.

    Args:
        code: ErrorCode enum value
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional error details
        request_id: Optional request ID for correlation

    Raises:
        Appropriate APIException subclass based on status code
    """
    if status_code == status.HTTP_400_BAD_REQUEST:
        exc_class = BadRequestError
    elif status_code == status.HTTP_401_UNAUTHORIZED:
        exc_class = AuthenticationError
    elif status_code == status.HTTP_403_FORBIDDEN:
        exc_class = ForbiddenError
    elif status_code == status.HTTP_404_NOT_FOUND:
        exc_class = NotFoundError
    elif status_code == status.HTTP_409_CONFLICT:
        exc_class = ConflictError
    elif status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
        exc_class = ValidationError
    elif status_code >= 500:
        exc_class = InternalServerError
    else:
        exc_class = BadRequestError

    error_details = (
        [ErrorDetail(field=key, message=str(value)) for key, value in details.items()]
        if details
        else None
    )
    raise exc_class(
        message=message,
        code=code,
        details=error_details,
        request_id=request_id,
    )
