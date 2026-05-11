from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from poly_core.constants import I18nKeys
from poly_core.services.invitation import InvitationService
from poly_core.services.team import TeamService
from poly_db.database import get_db_session
from src.dependencies import get_current_user
from src.schemas.teams import (
    CreateInvitationRequest,
    CreateTeamRequest,
    InvitationResponse,
    TeamMemberResponse,
    TeamResponse,
    UpdateMemberRoleRequest,
    UpdateTeamRequest,
)

router = APIRouter(prefix="/v1/teams", tags=["Teams"])


def get_team_service(db: Session = Depends(get_db_session)) -> TeamService:
    return TeamService(db)


def get_invitation_service(db: Session = Depends(get_db_session)) -> InvitationService:
    from poly_core.services.notification import NotificationService
    from src.config import get_settings

    settings = get_settings()
    notification_service = NotificationService(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_password=settings.SMTP_PASSWORD,
        smtp_from=settings.SMTP_FROM,
        templates_dir=str(Path(__file__).resolve().parents[1] / "templates"),
        app_url=settings.APP_URL,
    )
    return InvitationService(db, notification_service)


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    request: CreateTeamRequest,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    team = team_service.create_team(
        user_id=current_user["id"],
        name=request.name,
        host_language=request.host_language,
    )
    if not team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=I18nKeys.USER_NOT_FOUND.value,
        )
    return team


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    team = team_service.get_team(
        team_id=team_id,
        user_id=current_user["id"],
    )
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=I18nKeys.TEAM_NOT_FOUND.value,
        )
    return team


@router.patch("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: str,
    request: UpdateTeamRequest,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    team = team_service.update_team(
        team_id=team_id,
        user_id=current_user["id"],
        name=request.name,
        host_language=request.host_language,
    )
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=I18nKeys.TEAM_NOT_FOUND.value,
        )
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    success = team_service.delete_team(team_id=team_id, user_id=current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=I18nKeys.TEAM_NOT_FOUND.value,
        )


@router.get("/{team_id}/members", response_model=list[TeamMemberResponse])
def get_team_members(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    members = team_service.get_members(
        team_id=team_id,
        user_id=current_user["id"],
    )
    return members


@router.patch("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
def update_member_role(
    team_id: str,
    member_id: str,
    request: UpdateMemberRoleRequest,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    member = team_service.update_member_role(
        team_id=team_id,
        requesting_user_id=current_user["id"],
        target_user_id=member_id,
        new_role=request.role,
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=I18nKeys.MEMBER_NOT_FOUND.value,
        )
    return member


@router.delete("/{team_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    team_id: str,
    member_id: str,
    current_user: dict = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
):
    success = team_service.remove_member(
        team_id=team_id,
        requesting_user_id=current_user["id"],
        target_user_id=member_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=I18nKeys.MEMBER_NOT_FOUND.value,
        )


@router.post(
    "/{team_id}/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED
)
def create_invitation(
    team_id: str,
    request: CreateInvitationRequest,
    current_user: dict = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    invitation = invitation_service.create_invitation(
        team_id=team_id,
        inviting_user_id=current_user["id"],
        email=request.email,
        role=request.role,
    )
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=I18nKeys.ERR_GENERIC_FORBIDDEN.value,
        )
    return invitation


@router.get("/{team_id}/invitations", response_model=list[InvitationResponse])
def get_team_invitations(
    team_id: str,
    current_user: dict = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    invitations = invitation_service.get_pending_invitations(
        team_id=team_id, user_id=current_user["id"]
    )
    return invitations


@router.delete("/{team_id}/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_invitation(
    team_id: str,
    invitation_id: str,
    current_user: dict = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    success = invitation_service.cancel_invitation(
        invitation_id=invitation_id, user_id=current_user["id"]
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=I18nKeys.INVITATION_NOT_FOUND.value,
        )


@router.post("/invitations/{token}/accept", status_code=status.HTTP_204_NO_CONTENT)
def accept_invitation(
    token: str,
    current_user: dict = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
):
    success = invitation_service.accept_invitation(
        token=token,
        user_id=current_user["id"],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=I18nKeys.INVALID_INVITATION_TOKEN.value,
        )


teams_router = router
