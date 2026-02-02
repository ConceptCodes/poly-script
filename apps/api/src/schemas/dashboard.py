import uuid
from typing import List, Any, Optional

from pydantic import BaseModel, Field


class DashboardStatsResponse(BaseModel):
    total_jobs: int
    succeeded_jobs: int
    failed_jobs: int
    member_count: int
    plan: str
    credits_balance: int
    max_members: Optional[int] = None
    max_jobs_per_month: Optional[int] = None


class RecentJobItem(BaseModel):
    id: uuid.UUID
    file_name: str
    state: str
    created_at: str
    language: Optional[str] = None
    duration_seconds: Optional[int] = None


class ActivityItem(BaseModel):
    type: str
    display_name: str
    icon: str
    message: str
    timestamp: str


class UsageResponse(BaseModel):
    jobs_created: int
    jobs_succeeded: int
    jobs_failed: int
    month_start: str
