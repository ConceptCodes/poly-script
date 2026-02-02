from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

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
    reason: Optional[str] = None


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
    suspended_at: Optional[datetime] = None
    suspended_by: Optional[uuid.UUID] = None
    suspension_reason: Optional[str] = None
    created_at: Optional[datetime] = None


class AdminTeamDetailResponse(AdminTeamListItem):
    is_suspended: bool
    suspended_at: Optional[datetime] = None
    suspended_by: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None


class AdminJobDetailResponse(AdminJobListItem):
    progress_stage: Optional[str] = None
    attempts: int = 0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class AdminUserListItem(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_suspended: bool = False


class AdminTeamListItem(BaseModel):
    id: uuid.UUID
    name: str
    host_language: str
    plan: Optional[str] = None
    monthly_upload_count: int
    is_suspended: bool = False


class AdminJobListItem(BaseModel):
    id: uuid.UUID
    team_id: Optional[uuid.UUID] = None
    status: str
    progress: int
    engine: Optional[str] = None


class AdminUsersResponse(BaseModel):
    items: List[AdminUserListItem]
    total: int


class AdminTeamsResponse(BaseModel):
    items: List[AdminTeamListItem]
    total: int


class AdminJobsResponse(BaseModel):
    items: List[AdminJobListItem]
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
    administrators: List[Dict[str, Any]]
    system: Dict[str, Any]


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")


class AuditLogFilters(BaseModel):
    admin_user_id: Optional[uuid.UUID] = None
    action: Optional[str] = None
    target_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ImpersonationRequest(BaseModel):
    user_id: uuid.UUID


class ImpersonationResponse(BaseModel):
    impersonation_token: str
    user_id: uuid.UUID


class AdminJobVolumeResponse(BaseModel):
    total: int
    by_status: Dict[str, int]
    timeframe: Dict[str, str]


class AdminSettingsUpdate(BaseModel):
    plan_limits: Optional[Dict[str, Any]] = None
    retention_windows: Optional[Dict[str, int]] = None
    feature_flags: Optional[Dict[str, bool]] = None


class AuditLogListItem(BaseModel):
    id: uuid.UUID
    admin_user_id: Optional[uuid.UUID] = None
    target_type: str
    target_id: str
    action: str
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogListItem]
    total: int
