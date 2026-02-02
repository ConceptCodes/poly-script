from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_current_user, get_auth_service, get_team_context
from poly_core.services.settings import SettingsService
from poly_core.services.auth import AuthService
from poly_db.database import get_db_session
from schemas.settings import (
    UserSettingsResponse,
    UpdateUserProfileRequest,
    UpdateEmailRequest,
    UpdatePasswordRequest,
    TeamSettingsResponse,
    UpdateTeamSettingsRequest,
    TeamMemberItem,
    BillingInfoResponse,
)

router = APIRouter(prefix="/v1/settings", tags=["Settings"])


def get_settings_service(db: Session = Depends(get_db_session)) -> SettingsService:
    return SettingsService(db)


# User Settings

@router.get("/user", response_model=UserSettingsResponse)
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


@router.patch("/user", response_model=UserSettingsResponse)
def update_user_profile(
    request: UpdateUserProfileRequest,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
):
    """Update user profile."""
    try:
        user = settings_service.update_user_profile(
            user_id=current_user["id"],
            full_name=request.full_name,
            avatar_url=request.avatar_url,
        )
        return UserSettingsResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post("/user/email", status_code=status.HTTP_204_NO_CONTENT)
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


@router.post("/user/password", status_code=status.HTTP_204_NO_CONTENT)
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


# Team Settings

@router.get("/team", response_model=TeamSettingsResponse)
def get_team_settings(
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
    team_context: dict = Depends(get_team_context),
):
    """Get team settings."""
    try:
        settings = settings_service.get_team_settings(
            team_id=team_context["id"],
            user_id=current_user["id"],
        )
        return TeamSettingsResponse(**settings)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.patch("/team", response_model=TeamSettingsResponse)
def update_team_settings(
    request: UpdateTeamSettingsRequest,
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
    team_context: dict = Depends(get_team_context),
):
    """Update team settings (admin only)."""
    try:
        team = settings_service.update_team_settings(
            team_id=team_context["id"],
            user_id=current_user["id"],
            name=request.name,
            host_language=request.host_language,
        )
        return TeamSettingsResponse(
            id=team.id,
            name=team.name,
            host_language=team.host_language,
            plan=team.plan.value,
            credits_balance=team.credits_balance or 0,
            created_at=team.created_at.isoformat(),
            members_count=len(settings_service.member_repo.list_by_team_id(team.id)),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get("/team/members", response_model=list[TeamMemberItem])
def get_team_members(
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
    team_context: dict = Depends(get_team_context),
):
    """Get team members list."""
    try:
        members = settings_service.get_team_members(
            team_id=team_context["id"],
            user_id=current_user["id"],
        )
        return [TeamMemberItem(**member) for member in members]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


# Billing Settings

@router.get("/billing", response_model=BillingInfoResponse)
def get_billing_info(
    settings_service: SettingsService = Depends(get_settings_service),
    current_user: dict = Depends(get_current_user),
    team_context: dict = Depends(get_team_context),
):
    """Get billing information."""
    try:
        billing = settings_service.get_billing_info(
            team_id=team_context["id"],
            user_id=current_user["id"],
        )
        return BillingInfoResponse(**billing)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
