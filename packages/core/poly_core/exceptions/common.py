"""
Common exception types for different error categories.
"""


from .base import APIErrorOptions, APIException, ErrorCode, ErrorDetail, ErrorSeverity


class BadRequestError(APIException):
    """400 Bad Request - Client sent invalid request."""

    def __init__(
        self,
        message: str = "Bad request",
        code: ErrorCode = ErrorCode.GENERIC_BAD_REQUEST,
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            options=APIErrorOptions(documentation_url=documentation_url, request_id=request_id),
        )


class AuthenticationError(APIException):
    """401 Unauthorized - Authentication required or failed."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: ErrorCode = ErrorCode.AUTH_INVALID_CREDENTIALS,
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=401,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )


class AuthorizationError(APIException):
    """403 Forbidden - Authenticated but not authorized."""

    def __init__(
        self,
        message: str = "Forbidden",
        code: ErrorCode = ErrorCode.AUTHZ_INSUFFICIENT_PERMISSIONS,
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=403,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )


class ForbiddenError(APIException):
    """403 Forbidden - Alias for AuthorizationError."""

    def __init__(
        self,
        message: str = "Forbidden",
        code: ErrorCode = ErrorCode.GENERIC_FORBIDDEN,
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=403,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )


class NotFoundError(APIException):
    """404 Not Found - Resource not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=404,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )


class ConflictError(APIException):
    """409 Conflict - Resource conflict (e.g., duplicate entry)."""

    def __init__(
        self,
        message: str = "Conflict",
        code: ErrorCode = ErrorCode.RESOURCE_CONFLICT,
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=code,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=409,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )


class ValidationError(APIException):
    """422 Unprocessable Entity - Validation failed."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=ErrorCode.VALIDATION_INVALID_INPUT,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=422,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )


class RateLimitError(APIException):
    """429 Too Many Requests - Rate limit exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=429,
                severity=ErrorSeverity.WARNING,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )
        self.retry_after = retry_after


class InternalServerError(APIException):
    """500 Internal Server Error - Unexpected server error."""

    def __init__(
        self,
        message: str = "Internal server error",
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=ErrorCode.SYSTEM_INTERNAL_ERROR,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )


class ServiceUnavailableError(APIException):
    """503 Service Unavailable - Service temporarily unavailable."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: list[ErrorDetail] | None = None,
        documentation_url: str | None = None,
        request_id: str | None = None,
    ):
        super().__init__(
            code=ErrorCode.EXTERNAL_SERVICE_UNAVAILABLE,
            message=message,
            details=details,
            options=APIErrorOptions(
                status_code=503,
                severity=ErrorSeverity.CRITICAL,
                documentation_url=documentation_url,
                request_id=request_id,
            ),
        )
