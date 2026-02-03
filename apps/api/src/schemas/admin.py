import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    admin_id: uuid.UUID
    admin_email: EmailStr
    admin_full_name: str
    admin_role: str


class AdminActionRequest(BaseModel):
    reason: str | None = None


class AdminCounts(BaseModel):
    users: int
    teams: int
    jobs: int
    administrators: int


class AdminDashboardResponse(BaseModel):
    counts: AdminCounts


class AdminHealthResponse(BaseModel):
    api: str
    queue_depth: int
    worker_status: str


class AdminUserDetailResponse(AdminUserListItem):
    suspended_at: datetime | None = None
    suspended_by: uuid.UUID | None = None
    suspension_reason: str | None = None
    created_at: datetime | None = None


class AdminTeamDetailResponse(AdminTeamListItem):
    is_suspended: bool
    suspended_at: datetime | None = None
    suspended_by: uuid.UUID | None = None
    created_at: datetime | None = None


class AdminJobDetailResponse(AdminJobListItem):
    progress_stage: str | None = None
    attempts: int = 0
    error_message: str | None = None
    created_at: datetime | None = None
    finished_at: datetime | None = None


class AdminUserListItem(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None = None
    is_active: bool
    is_verified: bool
    is_suspended: bool = False


class AdminTeamListItem(BaseModel):
    id: uuid.UUID
    name: str
    host_language: str
    plan: str | None = None
    monthly_upload_count: int
    is_suspended: bool = False


class AdminJobListItem(BaseModel):
    id: uuid.UUID
    team_id: uuid.UUID | None = None
    status: str
    progress: int
    engine: str | None = None


class AdminUsersResponse(BaseModel):
    items: list[AdminUserListItem]
    total: int


class AdminTeamsResponse(BaseModel):
    items: list[AdminTeamListItem]
    total: int


class AdminJobsResponse(BaseModel):
    items: list[AdminJobListItem]
    total: int


class AdminAnalyticsResponse(BaseModel):
    users: int
    teams: int
    jobs: int
    successful_jobs: int


class AdminErrorAnalyticsResponse(BaseModel):
    total_errors: int
    failed_jobs: int
    canceled_jobs: int


class AdminSettingsResponse(BaseModel):
    administrators: list[dict[str, Any]]
    system: dict[str, Any]


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")


class AuditLogFilters(BaseModel):
    admin_user_id: uuid.UUID | None = None
    action: str | None = None
    target_type: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ImpersonationRequest(BaseModel):
    user_id: uuid.UUID


class ImpersonationResponse(BaseModel):
    impersonation_token: str
    user_id: uuid.UUID


class AdminJobVolumeResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    timeframe: dict[str, str]


class AdminSettingsUpdate(BaseModel):
    plan_limits: dict[str, Any] | None = None
    retention_windows: dict[str, int] | None = None
    feature_flags: dict[str, bool] | None = None


class AuditLogListItem(BaseModel):
    id: uuid.UUID
    admin_user_id: uuid.UUID | None = None
    target_type: str
    target_id: str
    action: str
    previous_state: dict[str, Any] | None = None
    new_state: dict[str, Any] | None = None
    reason: str | None = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogListItem]
    total: int
