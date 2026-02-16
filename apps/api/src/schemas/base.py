"""Shared base schema classes for API responses.

This module provides reusable base Pydantic models that can be extended
by other schema modules to ensure consistency across API responses.
"""

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

# Generic type variable for paginated responses
T = TypeVar("T")


class BaseResponse(BaseModel):
    """Base response model with common fields for all API responses.

    This class serves as the foundation for all response models in the API.
    It includes common audit fields (id, created_at, updated_at) that are
    optional since not all responses require them.

    All subclasses inherit:
        - model_config with from_attributes=True for ORM compatibility
        - Optional audit fields that can be included when needed

    Example:
        class UserResponse(BaseResponse):
            email: str
            name: str
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    """Optional unique identifier for the resource."""

    created_at: datetime | None = None
    """Optional timestamp when the resource was created."""

    updated_at: datetime | None = None
    """Optional timestamp when the resource was last updated."""


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model for list endpoints.

    This class provides a consistent structure for paginated API responses,
    allowing any item type to be paginated while maintaining a uniform
    response format across the API.

    Type Parameters:
        T: The type of items in the paginated list.

    Attributes:
        items: List of items for the current page.
        total: Total number of items across all pages.
        page: Current page number (1-indexed).
        page_size: Number of items per page.

    Example:
        # Usage in a specific endpoint
        class UserResponse(BaseModel):
            id: UUID
            email: str

        def list_users() -> PaginatedResponse[UserResponse]:
            return PaginatedResponse(
                items=[UserResponse(...)],
                total=100,
                page=1,
                page_size=20
            )
    """

    model_config = ConfigDict(from_attributes=True)

    items: list[T]
    """List of items for the current page."""

    total: int
    """Total number of items across all pages."""

    page: int
    """Current page number (1-indexed)."""

    page_size: int
    """Number of items per page."""


class SuccessResponse(BaseModel):
    """Simple success response model for operations that return a message.

    This class provides a standardized structure for returning success
    messages from API endpoints, ensuring consistency across the API.

    Attributes:
        message: Human-readable success message.
        status: Status indicator, defaults to "success".

    Example:
        @router.post("/users")
        def create_user() -> SuccessResponse:
            return SuccessResponse(message="User created successfully")
    """

    model_config = ConfigDict(from_attributes=True)

    message: str
    """Human-readable success message describing the operation result."""

    status: str = "success"
    """Status indicator, defaults to 'success'."""


# Export all base classes
__all__ = [
    "BaseResponse",
    "PaginatedResponse",
    "SuccessResponse",
]
