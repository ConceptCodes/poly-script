import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from datetime import datetime, timezone

from poly_db.database import get_db_session
from poly_db.repositories import (
    AuditLogRepository,
    UserRepository,
    TeamRepository,
    TranscriptionJobRepository,
    AudioAssetRepository,
)
from poly_db.models.transcription_jobs import JobStatus
from poly_core.services.admin import AdminService
from poly_core.services.admin_auth import AdminAuthService
from src.dependencies import get_admin_auth_service, get_current_admin
from fastapi import Query
from src.schemas.admin import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminDashboardResponse,
    AdminCounts,
    AdminUsersResponse,
    AdminTeamsResponse,
    AdminJobsResponse,
    AdminAnalyticsResponse,
    AdminSettingsResponse,
    AuditLogListResponse,
    AuditLogListItem,
    AdminUserListItem,
    AdminTeamListItem,
    AdminJobListItem,
    AdminJobDetailResponse,
    AdminActionRequest,
    AdminHealthResponse,
    AdminUserDetailResponse,
    AdminTeamDetailResponse,
    AdminErrorAnalyticsResponse,
)
from poly_redis.client import get_redis_client
from poly_redis.queue import TranscriptionQueue, TranscriptionWorkItem


router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/auth/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    auth_service: AdminAuthService = Depends(get_admin_auth_service),
):
    try:
        data = auth_service.login(request.email, request.password)
        return AdminLoginResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/dashboard/stats", response_model=AdminDashboardResponse)
async def admin_dashboard(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    service = AdminService(db)
    data = service.dashboard()
    return AdminDashboardResponse(
        counts=AdminCounts(
            users=data.get("users", 0),
            teams=data.get("teams", 0),
            jobs=data.get("jobs", 0),
            administrators=data.get("administrators", 0),
        )
    )


@router.get("/system/health", response_model=AdminHealthResponse)
async def admin_system_health(
    admin: dict = Depends(get_current_admin),
):
    redis_client = get_redis_client()
    queue_depth = 0
    try:
        queue_depth = TranscriptionQueue(redis_client).size()
    except Exception:
        queue_depth = 0
    return AdminHealthResponse(
        api="ok",
        queue_depth=queue_depth,
        worker_status="unknown",
    )


@router.get("/users", response_model=AdminUsersResponse)
async def admin_users(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
    q: str | None = Query(None),
):
    service = AdminService(db)
    users = service.users()
    if q:
        q_lower = q.lower()
        users = [
            u
            for u in users
            if q_lower in (u.get("email", "").lower())
            or q_lower in (u.get("full_name") or "").lower()
        ]
    items = [
        AdminUserListItem(
            id=uuid.UUID(u["id"]),
            email=u["email"],
            full_name=u.get("full_name"),
            is_active=u.get("is_active", False),
            is_verified=u.get("is_verified", False),
            is_suspended=u.get("is_suspended", False),
        )
        for u in users
    ]
    return AdminUsersResponse(items=items, total=len(items))


@router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
async def admin_user_detail(
    user_id: uuid.UUID,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AdminUserDetailResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_suspended=user.is_suspended,
        suspended_at=user.suspended_at,
        suspended_by=user.suspended_by,
        suspension_reason=user.suspension_reason,
        created_at=user.created_at,
    )


@router.post("/users/{user_id}/suspend")
async def admin_suspend_user(
    user_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    previous = {"is_suspended": user.is_suspended, "suspension_reason": user.suspension_reason}
    user_repo.update(
        user_id,
        is_suspended=True,
        suspended_at=datetime.now(timezone.utc),
        suspended_by=admin["id"],
        suspension_reason=request.reason,
    )
    AuditLogRepository(db).create(
        admin_user_id=admin["id"],
        target_type="user",
        target_id=str(user_id),
        action="suspend_user",
        previous_state=previous,
        new_state={"is_suspended": True, "suspension_reason": request.reason},
        reason=request.reason,
    )
    db.commit()
    return {"status": "success"}


@router.post("/users/{user_id}/unsuspend")
async def admin_unsuspend_user(
    user_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    previous = {"is_suspended": user.is_suspended, "suspension_reason": user.suspension_reason}
    user_repo.update(
        user_id,
        is_suspended=False,
        suspended_at=None,
        suspended_by=None,
        suspension_reason=None,
    )
    AuditLogRepository(db).create(
        admin_user_id=admin["id"],
        target_type="user",
        target_id=str(user_id),
        action="unsuspend_user",
        previous_state=previous,
        new_state={"is_suspended": False},
        reason=request.reason,
    )
    db.commit()
    return {"status": "success"}


@router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    previous = {"deleted_at": user.deleted_at}
    user_repo.update(user_id, deleted_at=datetime.now(timezone.utc))
    AuditLogRepository(db).create(
        admin_user_id=admin["id"],
        target_type="user",
        target_id=str(user_id),
        action="delete_user",
        previous_state=previous,
        new_state={"deleted_at": datetime.now(timezone.utc).isoformat()},
        reason=request.reason,
    )
    db.commit()
    return {"status": "success"}


@router.post("/users/{user_id}/impersonate")
async def admin_impersonate_user(
    user_id: uuid.UUID,
    admin: dict = Depends(get_current_admin),
):
    return {"token": f"impersonate:{user_id}"}


@router.get("/teams", response_model=AdminTeamsResponse)
async def admin_teams(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
    q: str | None = Query(None),
):
    service = AdminService(db)
    teams = service.teams()
    if q:
        q_lower = q.lower()
        teams = [t for t in teams if q_lower in t.get("name", "").lower()]
    items = [
        AdminTeamListItem(
            id=uuid.UUID(t["id"]),
            name=t["name"],
            host_language=t.get("host_language") or "en",
            plan=t.get("plan"),
            monthly_upload_count=t.get("monthly_upload_count", 0),
            is_suspended=t.get("is_suspended", False),
        )
        for t in teams
    ]
    return AdminTeamsResponse(items=items, total=len(items))


@router.get("/teams/{team_id}", response_model=AdminTeamDetailResponse)
async def admin_team_detail(
    team_id: uuid.UUID,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    team_repo = TeamRepository(db)
    team = team_repo.get(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return AdminTeamDetailResponse(
        id=team.id,
        name=team.name,
        host_language=team.host_language,
        plan=team.plan.name if team.plan else None,
        monthly_upload_count=team.monthly_upload_count,
        is_suspended=team.is_suspended,
        suspended_at=team.suspended_at,
        suspended_by=team.suspended_by,
        created_at=team.created_at,
    )


@router.post("/teams/{team_id}/suspend")
async def admin_suspend_team(
    team_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    team_repo = TeamRepository(db)
    team = team_repo.get(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    previous = {"is_suspended": team.is_suspended}
    team_repo.update(
        team_id,
        is_suspended=True,
        suspended_at=datetime.now(timezone.utc),
        suspended_by=admin["id"],
    )
    AuditLogRepository(db).create(
        admin_user_id=admin["id"],
        target_type="team",
        target_id=str(team_id),
        action="suspend_team",
        previous_state=previous,
        new_state={"is_suspended": True},
        reason=request.reason,
    )
    db.commit()
    return {"status": "success"}


@router.post("/teams/{team_id}/unsuspend")
async def admin_unsuspend_team(
    team_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    team_repo = TeamRepository(db)
    team = team_repo.get(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    previous = {"is_suspended": team.is_suspended}
    team_repo.update(
        team_id,
        is_suspended=False,
        suspended_at=None,
        suspended_by=None,
    )
    AuditLogRepository(db).create(
        admin_user_id=admin["id"],
        target_type="team",
        target_id=str(team_id),
        action="unsuspend_team",
        previous_state=previous,
        new_state={"is_suspended": False},
        reason=request.reason,
    )
    db.commit()
    return {"status": "success"}


@router.delete("/teams/{team_id}")
async def admin_delete_team(
    team_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    team_repo = TeamRepository(db)
    team = team_repo.get(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    previous = {"deleted_at": team.deleted_at if hasattr(team, "deleted_at") else None}
    team_repo.delete(team_id)
    AuditLogRepository(db).create(
        admin_user_id=admin["id"],
        target_type="team",
        target_id=str(team_id),
        action="delete_team",
        previous_state=previous,
        new_state={"deleted": True},
        reason=request.reason,
    )
    db.commit()
    return {"status": "success"}


@router.get("/jobs", response_model=AdminJobsResponse)
async def admin_jobs(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
    status: str | None = Query(None),
    team_id: str | None = Query(None),
):
    service = AdminService(db)
    jobs = service.jobs()
    if status:
        jobs = [j for j in jobs if j.get("status") == status]
    if team_id:
        jobs = [j for j in jobs if (j.get("team_id") or "").startswith(team_id)]
    items = [
        AdminJobListItem(
            id=uuid.UUID(j["id"]),
            team_id=uuid.UUID(j["team_id"]) if j.get("team_id") else None,
            status=j.get("status", "UNKNOWN"),
            progress=j.get("progress", 0),
            engine=j.get("engine"),
        )
        for j in jobs
    ]
    return AdminJobsResponse(items=items, total=len(items))


@router.get("/jobs/{job_id}", response_model=AdminJobDetailResponse)
async def admin_job_detail(
    job_id: uuid.UUID,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    job_repo = TranscriptionJobRepository(db)
    job = job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return AdminJobDetailResponse(
        id=job.id,
        team_id=job.team_id,
        status=job.status.value,
        progress=job.progress,
        engine=job.engine,
        progress_stage=job.progress_stage,
        attempts=job.attempts,
        error_message=job.error_message,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )


@router.post("/jobs/{job_id}/retry")
async def admin_retry_job(
    job_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    job_repo = TranscriptionJobRepository(db)
    audio_repo = AudioAssetRepository(db)
    job = job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    audio = audio_repo.get_by_job_id(job_id)
    if not audio:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio asset missing")

    job_repo.update(
        job_id,
        status=JobStatus.QUEUED,
        progress=0,
        progress_stage="queued",
    )
    queue = TranscriptionQueue(get_redis_client())
    queue.enqueue(
        TranscriptionWorkItem(
            job_id=job.id,
            audio_ref=audio.storage_uri,
            requested_language=job.requested_language,
            engine=job.engine,
            options=job.options or {},
        )
    )
    AuditLogRepository(db).create(
        admin_user_id=admin["id"],
        target_type="job",
        target_id=str(job_id),
        action="retry_job",
        previous_state={"status": job.status.value},
        new_state={"status": JobStatus.QUEUED.value},
        reason=request.reason,
    )
    db.commit()
    return {"status": "success"}


@router.post("/jobs/{job_id}/cancel")
async def admin_cancel_job(
    job_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    job_repo = TranscriptionJobRepository(db)
    job = job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    redis_client = get_redis_client()
    cancel_key = f"cancel:{job_id}"
    redis_client.setex(cancel_key, 60, "1")
    job_repo.update(job_id, status=JobStatus.CANCELED, progress_stage="canceled")
    AuditLogRepository(db).create(
        admin_user_id=admin["id"],
        target_type="job",
        target_id=str(job_id),
        action="cancel_job",
        previous_state={"status": job.status.value},
        new_state={"status": JobStatus.CANCELED.value},
        reason=request.reason,
    )
    db.commit()
    return {"status": "success"}


@router.get("/analytics/usage", response_model=dict)
async def admin_analytics(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    granularity: str = Query("day", regex="^(day|week|month)$"),
):
    """Get usage analytics with optional timeframe and granularity."""
    service = AdminService(db)
    
    # Parse dates if provided
    from datetime import datetime, timezone
    start = None
    end = None
    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            pass
    
    return service.analytics_with_timeframe(
        start_date=start,
        end_date=end,
        granularity=granularity,
    )


@router.get("/analytics/errors", response_model=AdminErrorAnalyticsResponse)
async def admin_error_analytics(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    job_repo = TranscriptionJobRepository(db)
    jobs = job_repo.list()
    failed_jobs = sum(1 for j in jobs if j.status == JobStatus.FAILED)
    canceled_jobs = sum(1 for j in jobs if j.status == JobStatus.CANCELED)
    return AdminErrorAnalyticsResponse(
        total_errors=failed_jobs + canceled_jobs,
        failed_jobs=failed_jobs,
        canceled_jobs=canceled_jobs,
    )


@router.get("/system/settings", response_model=dict)
async def admin_settings(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Get system settings."""
    service = AdminService(db)
    return service.get_system_settings()


@router.patch("/system/settings", response_model=dict)
async def admin_update_settings(
    payload: dict,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Update system settings (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can update settings")
    
    service = AdminService(db)
    try:
        return service.update_system_settings(
            settings_update=payload,
            admin_id=admin["id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))




@router.post("/admin-users", response_model=dict)
async def admin_create_admin_user(
    request: dict,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Create a new admin user (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can create admins")
    
    service = AdminService(db)
    try:
        result = service.create_admin_user(
            email=request.get("email"),
            password=request.get("password"),
            full_name=request.get("full_name"),
            role=request.get("role", "ADMIN"),
            created_by_admin_id=admin["id"],
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/admin-users/{admin_id}/suspend")
async def admin_suspend_admin_user(
    admin_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Suspend an admin user (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can suspend admins")
    
    service = AdminService(db)
    try:
        result = service.suspend_admin_user(
            admin_id=admin_id,
            suspended_by_admin_id=admin["id"],
            reason=request.reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/admin-users/{admin_id}/unsuspend")
async def admin_unsuspend_admin_user(
    admin_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Unsuspend an admin user (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can unsuspend admins")
    
    service = AdminService(db)
    try:
        result = service.unsuspend_admin_user(
            admin_id=admin_id,
            unsuspended_by_admin_id=admin["id"],
            reason=request.reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/admin-users/{admin_id}/role")
async def admin_change_admin_role(
    admin_id: uuid.UUID,
    request: dict,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Change admin role (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can change admin roles")
    
    service = AdminService(db)
    try:
        result = service.change_admin_role(
            admin_id=admin_id,
            new_role=request.get("role"),
            changed_by_admin_id=admin["id"],
            reason=request.get("reason"),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/admin-users/{admin_id}")
async def admin_delete_admin_user(
    admin_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Delete an admin user (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can delete admins")
    
    service = AdminService(db)
    try:
        result = service.delete_admin_user(
            admin_id=admin_id,
            deleted_by_admin_id=admin["id"],
            reason=request.reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/teams/{team_id}/suspend")
async def admin_suspend_team(
    team_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Suspend a team (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can suspend teams")
    
    service = AdminService(db)
    try:
        result = service.suspend_team(
            team_id=team_id,
            suspended_by_admin_id=admin["id"],
            reason=request.reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/teams/{team_id}/unsuspend")
async def admin_unsuspend_team(
    team_id: uuid.UUID,
    request: AdminActionRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Unsuspend a team (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can unsuspend teams")
    
    service = AdminService(db)
    try:
        result = service.unsuspend_team(
            team_id=team_id,
            unsuspended_by_admin_id=admin["id"],
            reason=request.reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/audit-logs", response_model=AuditLogListResponse)
async def admin_audit_logs(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    audit_repo = AuditLogRepository(db)
    logs = audit_repo.list()
    items = [
        AuditLogListItem(
            id=log.id,
            admin_user_id=log.admin_user_id,
            target_type=log.target_type,
            target_id=log.target_id,
            action=log.action,
            previous_state=log.previous_state,
            new_state=log.new_state,
            reason=log.reason,
            created_at=log.created_at,
        )
        for log in logs
    ]
    return AuditLogListResponse(logs=items, total=len(items))

@router.get("/audit-logs/{audit_id}", response_model=AuditLogListItem)
async def admin_audit_log_detail(
    audit_id: uuid.UUID,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Get a single audit log detail."""
    audit_repo = AuditLogRepository(db)
    log = audit_repo.get_by_id(audit_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    
    return AuditLogListItem(
        id=log.id,
        admin_user_id=log.admin_user_id,
        target_type=log.target_type,
        target_id=log.target_id,
        action=log.action,
        previous_state=log.previous_state,
        new_state=log.new_state,
        reason=log.reason,
        created_at=log.created_at,
    )


@router.post("/impersonation")
async def admin_create_impersonation_token(
    request: dict,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Create an impersonation token for a user (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can create impersonation tokens")
    
    user_id_str = request.get("user_id")
    if not user_id_str:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required")
    
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id")
    
    service = AdminService(db)
    try:
        result = service.create_impersonation_token(
            target_user_id=user_id,
            admin_id=admin["id"],
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/impersonation/{token_id}")
async def admin_revoke_impersonation_token(
    token_id: str,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """Revoke an impersonation token (SUPER_ADMIN only)."""
    if admin["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SUPER_ADMIN can revoke impersonation tokens")
    
    service = AdminService(db)
    result = service.revoke_impersonation_token(
        token_id=token_id,
        admin_id=admin["id"],
    )
    return result


@router.get("/analytics/jobs", response_model=dict)
async def admin_job_volume_analytics(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
):
    """Get job volume analytics by status."""
    service = AdminService(db)
    
    # Parse dates if provided
    from datetime import datetime, timezone
    start = None
    end = None
    if start_date:
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            pass
    
    return service.job_volume_analytics(start_date=start, end_date=end)

admin_router = router
