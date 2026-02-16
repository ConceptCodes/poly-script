"""
Utilities for migrating existing error handling to standardized format.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from .base import ErrorCode
from .common import (
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)


def convert_http_exception(
    http_exc: HTTPException,
    default_code: Optional[ErrorCode] = None,
    request_id: Optional[str] = None,
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
    
    # Map status codes to appropriate exception types
    if status_code == status.HTTP_400_BAD_REQUEST:
        code = default_code or ErrorCode.GENERIC_BAD_REQUEST
        return BadRequestError(
            message=detail,
            code=code,
            request_id=request_id,
        )
    elif status_code == status.HTTP_401_UNAUTHORIZED:
        code = default_code or ErrorCode.AUTH_INVALID_CREDENTIALS
        return AuthenticationError(
            message=detail,
            code=code,
            request_id=request_id,
        )
    elif status_code == status.HTTP_403_FORBIDDEN:
        code = default_code or ErrorCode.GENERIC_FORBIDDEN
        return ForbiddenError(
            message=detail,
            code=code,
            request_id=request_id,
        )
    elif status_code == status.HTTP_404_NOT_FOUND:
        code = default_code or ErrorCode.RESOURCE_NOT_FOUND
        return NotFoundError(
            message=detail,
            code=code,
            request_id=request_id,
        )
    elif status_code == status.HTTP_409_CONFLICT:
        code = default_code or ErrorCode.RESOURCE_CONFLICT
        return ConflictError(
            message=detail,
            code=code,
            request_id=request_id,
        )
    elif status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        return ValidationError(
            message=detail,
            request_id=request_id,
        )
    elif status_code == status.HTTP_429_TOO_MANY_REQUENTS:
        code = default_code or ErrorCode.RATE_LIMIT_EXCEEDED
        return BadRequestError(
            message=detail,
            code=code,
            request_id=request_id,
        )
    elif status_code >= 500:
        return InternalServerError(
            message=detail,
            request_id=request_id,
        )
    else:
        return BadRequestError(
            message=detail,
            code=default_code or ErrorCode.GENERIC_BAD_REQUEST,
            request_id=request_id,
        )


def create_error_response(
    code: ErrorCode,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
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
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
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
    from .common import (
        AuthenticationError,
        AuthorizationError,
        BadRequestError,
        ConflictError,
        ForbiddenError,
        InternalServerError,
        NotFoundError,
        ValidationError,
    )
    
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
    elif status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        exc_class = ValidationError
    elif status_code >= 500:
        exc_class = InternalServerError
    else:
        exc_class = BadRequestError
    
    raise exc_class(
        message=message,
        code=code,
        request_id=request_id,
    )
