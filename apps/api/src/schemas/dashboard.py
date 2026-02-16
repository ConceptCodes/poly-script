import uuid

from pydantic import BaseModel, ConfigDict


class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_jobs: int
    succeeded_jobs: int
    failed_jobs: int
    member_count: int
    plan: str
    credits_balance: int
    max_members: int | None = None
    max_jobs_per_month: int | None = None


class RecentJobItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_name: str
    state: str
    created_at: str
    language: str | None = None
    duration_seconds: int | None = None


class ActivityItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    display_name: str
    icon: str
    message: str
    timestamp: str


class UsageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobs_created: int
    jobs_succeeded: int
    jobs_failed: int
    month_start: str
