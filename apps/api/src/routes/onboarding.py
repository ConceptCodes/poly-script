from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from poly_core.constants import PlanType
from poly_core.services.onboarding import OnboardingService
from poly_core.services.team import TeamService
from poly_db.database import get_db_session
from src.dependencies import get_current_user
from src.schemas.onboarding import CompleteOnboardingRequest, OnboardingResponse

router = APIRouter(prefix="/v1/onboarding", tags=["Onboarding"])


def get_team_service(db: Session = Depends(get_db_session)) -> TeamService:
    return TeamService(db)


def get_onboarding_service(db: Session = Depends(get_db_session)) -> OnboardingService:
    return OnboardingService(db)


@router.post("/complete", response_model=OnboardingResponse)
def complete_onboarding(
    request: CompleteOnboardingRequest,
    onboarding_service: OnboardingService = Depends(get_onboarding_service),
    current_user: dict = Depends(get_current_user),
):
    try:
        # Determine plan (default to FREE if not specified)
        plan = PlanType.FREE
        if request.plan:
            try:
                plan = PlanType(request.plan)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid plan: {request.plan}",
                )

        team = onboarding_service.complete_onboarding(
            user_id=current_user["id"],
            team_name=request.team_name,
            host_language=request.host_language,
            plan=plan,
            invite_emails=request.invite_emails,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return OnboardingResponse(
        team_id=team.id,
        name=team.name,
        host_language=team.host_language,
        plan=team.plan.value,
    )


onboarding_router = router
onboarding_router = router
