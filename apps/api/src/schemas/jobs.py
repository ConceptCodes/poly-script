"""Job-related request and response schemas."""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from pydantic import BaseModel, Field


class CreateJobOptions(BaseModel):
    language: Optional[str] = None
    engine: Optional[str] = None
    timestamps: bool = True
    diarization: bool = False

class CreateJobFromUrlRequest(BaseModel):
    url: str = Field(..., min_length=1)
    options: CreateJobOptions = Field(default_factory=CreateJobOptions)

class CreateJobResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    message: str

class JobLimitError(BaseModel):
    error: Dict[str, Any]


# Response schemas for job endpoints
class JobSummary(BaseModel):
    id: uuid.UUID
    status: str  # QUEUED|RUNNING|SUCCEEDED|FAILED|CANCELED
    filename: str
    language: Optional[str]
    progress_pct: int
    progress_stage: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]


class JobListResponse(BaseModel):
    jobs: List[JobSummary]
    total: int
    page: int
    page_size: int


class JobDetailResponse(BaseModel):
    id: uuid.UUID
    status: str
    filename: str
    requested_language: Optional[str]
    detected_language: Optional[str]
    engine: str
    options: Dict[str, Any]
    progress_pct: int
    progress_stage: Optional[str]
    attempts: int
    error_code: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    audio_duration_seconds: Optional[float]


class SegmentResponse(BaseModel):
    id: int  # segment index
    start_ms: int
    end_ms: int
    text: str
    speaker: Optional[str] = None


class JobResultResponse(BaseModel):
    job_id: uuid.UUID
    transcript_id: uuid.UUID
    text: str
    language: str
    segments: List[SegmentResponse]
    engine: str


class CancelJobResponse(BaseModel):
    message: str
