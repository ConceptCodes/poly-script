from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from dependencies import get_current_user, get_team_context
from poly_core.services.dashboard import DashboardService
from poly_db.database import get_db_session
from schemas.dashboard import (
    DashboardStatsResponse,
    RecentJobItem,
    ActivityItem,
    UsageResponse,
)

router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])


def get_dashboard_service(db: Session = Depends(get_db_session)) -> DashboardService:
    return DashboardService(db)


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    team_service: DashboardService = Depends(get_dashboard_service),
    current_user: dict = Depends(get_current_user),
    team_context: dict = Depends(get_team_context),
):
    """Get dashboard statistics for the current team."""
    try:
        team_id = team_context["id"]
        user_id = current_user["id"]
        stats = team_service.get_dashboard_stats(team_id, user_id)
        return DashboardStatsResponse(**stats)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get("/recent-jobs", response_model=list[RecentJobItem])
def get_recent_jobs(
    limit: int = Query(10, ge=1, le=50),
    team_service: DashboardService = Depends(get_dashboard_service),
    current_user: dict = Depends(get_current_user),
    team_context: dict = Depends(get_team_context),
):
    """Get recent jobs for the current team."""
    try:
        team_id = team_context["id"]
        user_id = current_user["id"]
        jobs = team_service.get_recent_jobs(team_id, user_id, limit)
        return [RecentJobItem(**job) for job in jobs]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get("/activity", response_model=list[ActivityItem])
def get_team_activity(
    limit: int = Query(50, ge=1, le=100),
    team_service: DashboardService = Depends(get_dashboard_service),
    current_user: dict = Depends(get_current_user),
    team_context: dict = Depends(get_team_context),
):
    """Get team activity feed."""
    try:
        team_id = team_context["id"]
        user_id = current_user["id"]
        activities = team_service.get_team_activity(team_id, user_id, limit)
        return [ActivityItem(**activity) for activity in activities]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@router.get("/usage", response_model=UsageResponse)
def get_usage(
    team_service: DashboardService = Depends(get_dashboard_service),
    current_user: dict = Depends(get_current_user),
    team_context: dict = Depends(get_team_context),
):
    """Get usage statistics for the current month."""
    try:
        team_id = team_context["id"]
        user_id = current_user["id"]
        usage = team_service.get_usage_this_month(team_id, user_id)
        return UsageResponse(**usage)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )
