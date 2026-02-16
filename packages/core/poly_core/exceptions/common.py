"""
Common exception types for different error categories.
"""

from typing import Any, List, Optional

from .base import APIException, ErrorCode, ErrorDetail, ErrorSeverity


class BadRequestError(APIException):
    """400 Bad Request - Client sent invalid request."""
    
    def __init__(
        self,
        message: str = "Bad request",
        code: ErrorCode = ErrorCode.GENERIC_BAD_REQUEST,
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=400,
            severity=ErrorSeverity.ERROR,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )


class AuthenticationError(APIException):
    """401 Unauthorized - Authentication required or failed."""
    
    def __init__(
        self,
        message: str = "Authentication required",
        code: ErrorCode = ErrorCode.AUTH_INVALID_CREDENTIALS,
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=401,
            severity=ErrorSeverity.ERROR,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )


class AuthorizationError(APIException):
    """403 Forbidden - Authenticated but not authorized."""
    
    def __init__(
        self,
        message: str = "Forbidden",
        code: ErrorCode = ErrorCode.AUTHZ_INSUFFICIENT_PERMISSIONS,
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=403,
            severity=ErrorSeverity.ERROR,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )


class ForbiddenError(APIException):
    """403 Forbidden - Alias for AuthorizationError."""
    
    def __init__(
        self,
        message: str = "Forbidden",
        code: ErrorCode = ErrorCode.GENERIC_FORBIDDEN,
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=403,
            severity=ErrorSeverity.ERROR,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )


class NotFoundError(APIException):
    """404 Not Found - Resource not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=404,
            severity=ErrorSeverity.ERROR,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )


class ConflictError(APIException):
    """409 Conflict - Resource conflict (e.g., duplicate entry)."""
    
    def __init__(
        self,
        message: str = "Conflict",
        code: ErrorCode = ErrorCode.RESOURCE_CONFLICT,
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=409,
            severity=ErrorSeverity.ERROR,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )


class ValidationError(APIException):
    """422 Unprocessable Entity - Validation failed."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=ErrorCode.VALIDATION_INVALID_INPUT,
            message=message,
            status_code=422,
            severity=ErrorSeverity.ERROR,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )


class RateLimitError(APIException):
    """429 Too Many Requests - Rate limit exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            status_code=429,
            severity=ErrorSeverity.WARNING,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )
        self.retry_after = retry_after


class InternalServerError(APIException):
    """500 Internal Server Error - Unexpected server error."""
    
    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=ErrorCode.SYSTEM_INTERNAL_ERROR,
            message=message,
            status_code=500,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )


class ServiceUnavailableError(APIException):
    """503 Service Unavailable - Service temporarily unavailable."""
    
    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(
            code=ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            message=message,
            status_code=503,
            severity=ErrorSeverity.CRITICAL,
            details=details,
            documentation_url=documentation_url,
            request_id=request_id,
        )
