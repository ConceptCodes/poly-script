import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from poly_core.services.auth import AuthService
from poly_core.services.settings import SettingsService
from src.dependencies import get_auth_service, get_current_user, get_db_session
from src.schemas.settings import (
    UpdateEmailRequest,
    UpdatePasswordRequest,
    UpdateUserNotificationsRequest,
    UpdateUserPreferencesRequest,
    UpdateUserProfileRequest,
    UserSettingsResponse,
)

router = APIRouter(prefix="/v1/user", tags=["User"])
users_router = APIRouter(prefix="/v1/users", tags=["User"])


def get_settings_service(db: Session = Depends(get_db_session)) -> SettingsService:
    return SettingsService(db)


def _require_self_account(user_id: uuid.UUID, current_user: dict) -> None:
    if str(current_user["id"]) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage your own account",
        )


@router.get("", response_model=UserSettingsResponse)
def get_user_settings(
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
):
    """Get current user's profile and settings."""
    try:
        settings = settings_service.get_user_settings(current_user["id"])
        return UserSettingsResponse(**settings)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.patch("", response_model=UserSettingsResponse)
def update_user_profile(
    request: UpdateUserProfileRequest,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
):
    """Update user profile (name, avatar)."""
    try:
        user = settings_service.update_user_profile(
            user_id=current_user["id"],
            full_name=request.full_name,
            avatar_url=request.avatar_url,
        )
        # Return full settings after update
        settings = settings_service.get_user_settings(user.id)
        return UserSettingsResponse(**settings)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch("/preferences", response_model=dict)
def update_user_preferences(
    request: UpdateUserPreferencesRequest,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
):
    """Update user preferences (language, theme)."""
    try:
        return settings_service.update_user_preferences(
            user_id=current_user["id"],
            host_language=request.host_language,
            theme=request.theme,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.patch("/notifications", response_model=dict)
def update_user_notifications(
    request: UpdateUserNotificationsRequest,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
):
    """Update user notification settings."""
    try:
        return settings_service.update_user_notifications(
            user_id=current_user["id"],
            notifications=request.notifications,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/email", status_code=status.HTTP_204_NO_CONTENT)
def update_user_email(
    request: UpdateEmailRequest,
    settings_service: SettingsService = Depends(get_settings_service),
    auth_service: AuthService = Depends(get_auth_service),
    current_user: dict = Depends(get_current_user),
):
    """Update user email (requires re-verification)."""
    try:
        settings_service.update_user_email(
            user_id=current_user["id"],
            new_email=request.new_email,
            auth_service=auth_service,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def update_user_password(
    request: UpdatePasswordRequest,
    settings_service: SettingsService = Depends(get_settings_service),
    auth_service: AuthService = Depends(get_auth_service),
    current_user: dict = Depends(get_current_user),
):
    """Update user password."""
    try:
        settings_service.update_user_password(
            user_id=current_user["id"],
            current_password=request.current_password,
            new_password=request.new_password,
            auth_service=auth_service,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """Delete user account."""
    from poly_db.models.users import User
    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()


@users_router.get("/{user_id}/settings", response_model=UserSettingsResponse)
def get_user_settings_by_id(
    user_id: uuid.UUID,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
):
    """Get a user's profile and settings via the canonical /v1/users route."""
    _require_self_account(user_id, current_user)
    try:
        settings = settings_service.get_user_settings(user_id)
        return UserSettingsResponse(**settings)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@users_router.patch("/{user_id}/settings", response_model=UserSettingsResponse)
def update_user_settings_by_id(
    user_id: uuid.UUID,
    request: UpdateUserPreferencesRequest,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
):
    """Update user preferences via the canonical /v1/users route."""
    _require_self_account(user_id, current_user)
    try:
        settings_service.update_user_preferences(
            user_id=user_id,
            host_language=request.host_language,
            theme=request.theme,
        )
        settings = settings_service.get_user_settings(user_id)
        return UserSettingsResponse(**settings)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account_by_id(
    user_id: uuid.UUID,
    db: Session = Depends(get_db_session),
    current_user: dict = Depends(get_current_user),
):
    """Delete the authenticated user's account via the canonical /v1/users route."""
    _require_self_account(user_id, current_user)
    from poly_db.models.users import User

    user = db.query(User).filter(User.id == current_user["id"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()

user_router = router
