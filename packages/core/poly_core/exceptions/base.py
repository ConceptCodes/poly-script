"""
Base exception classes and error response schemas for standardized API error handling.
"""

from enum import Enum, StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorSeverity(StrEnum):
    """Severity levels for API errors."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCode(StrEnum):
    """
    Standardized error codes for API responses.
    
    Format: DOMAIN_CATEGORY_DESCRIPTION
    Example: AUTH_INVALID_CREDENTIALS, TEAM_NOT_FOUND, BILLING_PLAN_LIMIT_REACHED
    """
    
    # Authentication errors (1xxx)
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID = "AUTH_TOKEN_INVALID"
    AUTH_TOKEN_MISSING = "AUTH_TOKEN_MISSING"
    AUTH_USER_NOT_FOUND = "AUTH_USER_NOT_FOUND"
    AUTH_EMAIL_NOT_VERIFIED = "AUTH_EMAIL_NOT_VERIFIED"
    AUTH_ACCOUNT_SUSPENDED = "AUTH_ACCOUNT_SUSPENDED"
    AUTH_INVALID_REFRESH_TOKEN = "AUTH_INVALID_REFRESH_TOKEN"
    
    # Authorization errors (2xxx)
    AUTHZ_INSUFFICIENT_PERMISSIONS = "AUTHZ_INSUFFICIENT_PERMISSIONS"
    AUTHZ_FORBIDDEN_RESOURCE = "AUTHZ_FORBIDDEN_RESOURCE"
    AUTHZ_TEAM_ACCESS_DENIED = "AUTHZ_TEAM_ACCESS_DENIED"
    AUTHZ_ADMIN_REQUIRED = "AUTHZ_ADMIN_REQUIRED"
    
    # Validation errors (3xxx)
    VALIDATION_INVALID_INPUT = "VALIDATION_INVALID_INPUT"
    VALIDATION_MISSING_FIELD = "VALIDATION_MISSING_FIELD"
    VALIDATION_INVALID_FORMAT = "VALIDATION_INVALID_FORMAT"
    VALIDATION_OUT_OF_RANGE = "VALIDATION_OUT_OF_RANGE"
    VALIDATION_UNIQUE_CONSTRAINT = "VALIDATION_UNIQUE_CONSTRAINT"
    
    # Resource errors (4xxx)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RESOURCE_LIMIT_REACHED = "RESOURCE_LIMIT_REACHED"
    
    # Business logic errors (5xxx)
    BUSINESS_INVALID_STATE = "BUSINESS_INVALID_STATE"
    BUSINESS_PLAN_LIMIT_REACHED = "BUSINESS_PLAN_LIMIT_REACHED"
    BUSINESS_INSUFFICIENT_CREDITS = "BUSINESS_INSUFFICIENT_CREDITS"
    BUSINESS_JOB_QUEUE_FULL = "BUSINESS_JOB_QUEUE_FULL"
    
    # External service errors (6xxx)
    EXTERNAL_SERVICE_UNAVAILABLE = "EXTERNAL_SERVICE_UNAVAILABLE"
    EXTERNAL_SERVICE_TIMEOUT = "EXTERNAL_SERVICE_TIMEOUT"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # System errors (7xxx)
    SYSTEM_INTERNAL_ERROR = "SYSTEM_INTERNAL_ERROR"
    SYSTEM_DATABASE_ERROR = "SYSTEM_DATABASE_ERROR"
    SYSTEM_QUEUE_ERROR = "SYSTEM_QUEUE_ERROR"
    SYSTEM_CONFIGURATION_ERROR = "SYSTEM_CONFIGURATION_ERROR"
    
    # Rate limiting (8xxx)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # Generic errors (9xxx)
    GENERIC_BAD_REQUEST = "GENERIC_BAD_REQUEST"
    GENERIC_NOT_FOUND = "GENERIC_NOT_FOUND"
    GENERIC_FORBIDDEN = "GENERIC_FORBIDDEN"
    GENERIC_INTERNAL_ERROR = "GENERIC_INTERNAL_ERROR"


class ErrorDetail(BaseModel):
    """Detailed error information for validation errors."""
    
    field: Optional[str] = Field(None, description="Field name that caused the error")
    message: str = Field(..., description="Error message for this field")
    code: Optional[str] = Field(None, description="Field-specific error code")
    value: Optional[Any] = Field(None, description="Invalid value that caused the error")


class ErrorResponse(BaseModel):
    """
    Standardized error response format for all API errors.
    
    This format ensures consistent error handling across all endpoints
    and provides machine-readable error codes for client applications.
    """
    
    error: Dict[str, Any] = Field(
        ...,
        description="Error object containing standardized error information",
        example={
            "code": "AUTH_INVALID_CREDENTIALS",
            "message": "Invalid email or password",
            "details": None,
            "severity": "error",
            "request_id": "req_1234567890abcdef",
            "documentation_url": "https://docs.polyscript.com/errors/AUTH_INVALID_CREDENTIALS"
        }
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "AUTH_INVALID_CREDENTIALS",
                    "message": "Invalid email or password",
                    "details": None,
                    "severity": "error",
                    "request_id": "req_1234567890abcdef",
                    "documentation_url": "https://docs.polyscript.com/errors/AUTH_INVALID_CREDENTIALS"
                }
            }
        }


class APIException(Exception):
    """
    Base exception class for all API errors.
    
    This exception is caught by global exception handlers and transformed
    into a standardized ErrorResponse.
    """
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        details: Optional[List[ErrorDetail]] = None,
        documentation_url: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.severity = severity
        self.details = details or []
        self.documentation_url = documentation_url
        self.request_id = request_id
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "code": self.code.value,
            "message": self.message,
            "details": [detail.dict(exclude_none=True) for detail in self.details] if self.details else None,
            "severity": self.severity.value,
            "request_id": self.request_id,
            "documentation_url": self.documentation_url,
        }
    
    def to_response(self) -> ErrorResponse:
        """Convert exception to standardized error response."""
        return ErrorResponse(error=self.to_dict())
