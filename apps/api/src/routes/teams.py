from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from poly_db.database import get_db_session
from poly_core.services.team import TeamService
from poly_core.services.invitation import InvitationService
from poly_core.constants import I18nKeys
from schemas.teams import (
    CreateTeamRequest,
    UpdateTeamRequest,
    TeamResponse,
    TeamMemberResponse,
    UpdateMemberRoleRequest,
    CreateInvitationRequest,
    InvitationResponse,
    AcceptInvitationRequest,
)
from dependencies import get_current_user


router = APIRouter(prefix="/v1/teams", tags=["Teams"])


def get_team_service(db: Session = Depends(get_db_session)) -> TeamService:
    return TeamService(db)


def get_invitation_service(db: Session = Depends(get_db_session)) -> InvitationService:
    return InvitationService(db)


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    request: CreateTeamRequest,
    team_service: TeamService = Depends(get_team_service),
    current_user: dict = Depends(get_current_user),
):
    team = team_service.create_team(
        user_id=current_user["id"],
        name=request.name,
        host_language=request.host_language,
    )
    return team


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: str,
    team_service: TeamService = Depends(get_team_service),
    current_user: dict = Depends(get_current_user),
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
    team_service: TeamService = Depends(get_team_service),
    current_user: dict = Depends(get_current_user),
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
    team_service: TeamService = Depends(get_team_service),
    current_user: dict = Depends(get_current_user),
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
    team_service: TeamService = Depends(get_team_service),
    current_user: dict = Depends(get_current_user),
):
    members = team_service.get_team_members(
        team_id=team_id,
        user_id=current_user["id"],
    )
    return members


@router.patch("/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
def update_member_role(
    team_id: str,
    member_id: str,
    request: UpdateMemberRoleRequest,
    team_service: TeamService = Depends(get_team_service),
    current_user: dict = Depends(get_current_user),
):
    member = team_service.update_member_role(
        team_id=team_id,
        member_id=member_id,
        user_id=current_user["id"],
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
    team_service: TeamService = Depends(get_team_service),
    current_user: dict = Depends(get_current_user),
):
    success = team_service.remove_member(
        team_id=team_id,
        member_id=member_id,
        user_id=current_user["id"],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=I18nKeys.MEMBER_NOT_FOUND.value,
        )


@router.post("/{team_id}/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def create_invitation(
    team_id: str,
    request: CreateInvitationRequest,
    invitation_service: InvitationService = Depends(get_invitation_service),
    current_user: dict = Depends(get_current_user),
):
    invitation = invitation_service.create_invitation(
        team_id=team_id,
        email=request.email,
        role=request.role,
        inviting_user_id=current_user["id"],
    )
    return invitation


@router.get("/{team_id}/invitations", response_model=list[InvitationResponse])
def get_team_invitations(
    team_id: str,
    invitation_service: InvitationService = Depends(get_invitation_service),
    current_user: dict = Depends(get_current_user),
):
    invitations = invitation_service.get_team_invitations(
        team_id=team_id,
        user_id=current_user["id"],
    )
    return invitations


@router.delete("/{team_id}/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_invitation(
    team_id: str,
    invitation_id: str,
    invitation_service: InvitationService = Depends(get_invitation_service),
    current_user: dict = Depends(get_current_user),
):
    success = invitation_service.cancel_invitation(
        team_id=team_id,
        invitation_id=invitation_id,
        user_id=current_user["id"],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=I18nKeys.INVITATION_NOT_FOUND.value,
        )


@router.post("/invitations/accept", status_code=status.HTTP_204_NO_CONTENT)
def accept_invitation(
    request: AcceptInvitationRequest,
    invitation_service: InvitationService = Depends(get_invitation_service),
    current_user: dict = Depends(get_current_user),
):
    success = invitation_service.accept_invitation(
        token=request.token,
        user_id=current_user["id"],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=I18nKeys.INVALID_INVITATION_TOKEN.value,
        )
