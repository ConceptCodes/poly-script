from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dependencies import get_current_user
from poly_core.constants import I18nKeys
from poly_core.services.team import TeamService
from poly_db.database import get_db_session
from schemas.onboarding import CompleteOnboardingRequest, OnboardingResponse

router = APIRouter(prefix="/v1/onboarding", tags=["Onboarding"])


def get_team_service(db: Session = Depends(get_db_session)) -> TeamService:
    return TeamService(db)


@router.post("/complete", response_model=OnboardingResponse)
def complete_onboarding(
    request: CompleteOnboardingRequest,
    team_service: TeamService = Depends(get_team_service),
    current_user: dict = Depends(get_current_user),
):
    team = team_service.create_team(
        user_id=current_user["id"],
        name=request.team_name,
        host_language=request.host_language,
    )
    if not team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=I18nKeys.USER_NOT_FOUND.value,
        )
    return OnboardingResponse(
        team_id=team.id,
        name=team.name,
        host_language=team.host_language,
        plan=team.plan,
    )
