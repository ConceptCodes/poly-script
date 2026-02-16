"""
Global exception handlers for FastAPI application.

This module provides:
1. Global exception handlers for standardized error responses
2. Localization support via Accept-Language header
3. OpenAPI documentation integration
4. Request ID correlation
"""

import logging
import traceback
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from poly_core.constants import I18nKeys
from poly_core.services.i18n import I18nService

from .base import APIException, ErrorCode, ErrorDetail, ErrorResponse, ErrorSeverity
from .common import (
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def get_locale_from_request(request: Request) -> str:
    """
    Extract locale from Accept-Language header.
    
    Defaults to 'en' if no valid locale found.
    """
    accept_language = request.headers.get("accept-language", "en")
    # Parse Accept-Language header (e.g., "en-US,en;q=0.9,fr;q=0.8")
    if "," in accept_language:
        # Take the first language code
        locale = accept_language.split(",")[0].split(";")[0].strip()
    else:
        locale = accept_language.split(";")[0].strip()
    
    # Normalize locale (e.g., "en-US" -> "en")
    if "-" in locale:
        locale = locale.split("-")[0]
    
    # Validate against supported locales
    supported_locales = ["en", "de", "es", "fr", "jp"]
    if locale not in supported_locales:
        locale = "en"
    
    return locale


def localize_error_message(
    i18n_service: Optional[I18nService],
    error_key: str,
    locale: str,
    default_message: str,
    **kwargs: Any,
) -> str:
    """
    Localize error message using I18nService.
    
    Args:
        i18n_service: I18nService instance (may be None)
        error_key: I18nKeys enum value or translation key
        locale: Target locale
        default_message: Fallback message if translation fails
        **kwargs: Format arguments for the message
    
    Returns:
        Localized error message
    """
    if i18n_service is None:
        return default_message
    
    try:
        # Check if error_key is an I18nKeys enum
        if hasattr(I18nKeys, error_key):
            key_value = getattr(I18nKeys, error_key).value
        else:
            key_value = error_key
        
        localized = i18n_service.t(key_value, locale=locale, **kwargs)
        if localized != key_value:  # Translation succeeded
            return localized
    except Exception as e:
        logger.warning(f"Failed to localize error message: {e}")
    
    return default_message


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handle APIException instances with localization support.
    
    This handler:
    1. Adds request_id from request context
    2. Localizes error message based on Accept-Language header
    3. Returns standardized error response
    """
    # Get locale from request
    locale = get_locale_from_request(request)
    
    # Get i18n service from app state
    i18n_service = getattr(request.app.state, "i18n_service", None)
    
    # Localize error message
    localized_message = localize_error_message(
        i18n_service=i18n_service,
        error_key=exc.code.value,
        locale=locale,
        default_message=exc.message,
    )
    
    # Get request_id from request headers or context
    request_id = request.headers.get("X-Request-ID") or exc.request_id
    
    # Create error response
    error_response = ErrorResponse(
        error={
            "code": exc.code.value,
            "message": localized_message,
            "details": [detail.dict(exclude_none=True) for detail in exc.details] if exc.details else None,
            "severity": exc.severity.value,
            "request_id": request_id,
            "documentation_url": exc.documentation_url,
        }
    )
    
    # Log error (excluding validation errors from user input)
    if exc.status_code >= 500:
        logger.error(
            f"APIException {exc.code.value}: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
            },
        )
    elif exc.status_code >= 400 and exc.code != ErrorCode.VALIDATION_INVALID_INPUT:
        logger.warning(
            f"APIException {exc.code.value}: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
            },
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict(),
        headers={"Content-Language": locale},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle Starlette/FastAPI HTTPException instances.
    
    Converts HTTPException to standardized APIException format.
    """
    # Map HTTP status codes to appropriate APIException types
    status_code = exc.status_code or 500
    
    if status_code == status.HTTP_400_BAD_REQUEST:
        api_exc = BadRequestError(message=str(exc.detail))
    elif status_code == status.HTTP_401_UNAUTHORIZED:
        api_exc = AuthenticationError(message=str(exc.detail))
    elif status_code == status.HTTP_403_FORBIDDEN:
        api_exc = AuthorizationError(message=str(exc.detail))
    elif status_code == status.HTTP_404_NOT_FOUND:
        api_exc = NotFoundError(message=str(exc.detail))
    elif status_code == status.HTTP_409_CONFLICT:
        api_exc = BadRequestError(message=str(exc.detail), code=ErrorCode.RESOURCE_CONFLICT)
    elif status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        # This should be handled by validation_error_handler
        api_exc = ValidationError(message=str(exc.detail))
    elif status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        api_exc = BadRequestError(message=str(exc.detail), code=ErrorCode.RATE_LIMIT_EXCEEDED)
    else:
        api_exc = BadRequestError(message=str(exc.detail))
    
    # Set status code
    api_exc.status_code = status_code
    
    # Use the API exception handler
    return await api_exception_handler(request, api_exc)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors (422 Unprocessable Entity).
    
    Converts FastAPI's RequestValidationError to standardized ValidationError.
    """
    # Extract validation error details
    error_details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        if field.startswith("body."):
            field = field[5:]  # Remove "body." prefix
        
        error_details.append(
            ErrorDetail(
                field=field if field else None,
                message=error.get("msg", "Validation error"),
                code=error.get("type"),
                value=error.get("input"),
            )
        )
    
    # Get locale for localization
    locale = get_locale_from_request(request)
    
    # Create validation error
    validation_error = ValidationError(
        message="Validation failed",
        details=error_details,
        request_id=request.headers.get("X-Request-ID"),
    )
    
    # Use the API exception handler
    return await api_exception_handler(request, validation_error)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unhandled exceptions.
    
    This handler ensures no internal server errors leak stack traces to clients.
    """
    # Log the full exception with traceback
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "request_id": request.headers.get("X-Request-ID"),
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        },
        exc_info=True,
    )
    
    # Create internal server error
    internal_error = InternalServerError(
        message="An unexpected error occurred",
        request_id=request.headers.get("X-Request-ID"),
    )
    
    # Use the API exception handler
    return await api_exception_handler(request, internal_error)


def setup_exception_handlers(app: FastAPI, i18n_service: Optional[I18nService] = None) -> None:
    """
    Register global exception handlers for FastAPI application.
    
    Args:
        app: FastAPI application instance
        i18n_service: Optional I18nService for error message localization
    """
    # Store i18n service in app state for handlers to access
    if i18n_service:
        app.state.i18n_service = i18n_service
    
    # Register exception handlers in order of specificity
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Global exception handlers registered")
