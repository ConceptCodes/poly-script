"""
Standardized exception handling for PolyScript API.

This module provides:
1. Base APIException class with error code taxonomy
2. Standardized error response schemas
3. Common exception types for different error categories
4. Utilities for error localization
"""

from .base import APIException, ErrorCode, ErrorResponse, ErrorSeverity
from .common import (
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)
from .handlers import setup_exception_handlers
from .mappings import ERROR_CODE_TO_I18N_KEY, get_i18n_key_for_error_code

__all__ = [
    "APIException",
    "ErrorCode",
    "ErrorResponse",
    "ErrorSeverity",
    "AuthenticationError",
    "AuthorizationError",
    "BadRequestError",
    "ConflictError",
    "ForbiddenError",
    "InternalServerError",
    "NotFoundError",
    "RateLimitError",
    "ServiceUnavailableError",
    "ValidationError",
    "setup_exception_handlers",
    "ERROR_CODE_TO_I18N_KEY",
    "get_i18n_key_for_error_code",
]
