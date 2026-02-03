from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from poly_core.services.settings import SettingsService
from poly_db.database import get_db_session
from src.dependencies import get_current_user, get_team_context
from src.schemas.settings import (
    BillingInfoResponse,
    TeamMemberItem,
    TeamSettingsResponse,
    UpdateTeamSettingsRequest,
)

router = APIRouter(prefix="/v1/settings", tags=["Settings"])


def get_settings_service(db: Session = Depends(get_db_session)) -> SettingsService:
    return SettingsService(db)


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

settings_router = router
