"""Job-related request and response schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CreateJobOptions(BaseModel):
    language: str | None = None  # Source language for ASR
    target_language: str | None = Field(
        None, pattern=r"^[a-z]{2}(-[A-Z]{2})?$"
    )  # Target language for translation (e.g., es, fr, de)
    engine: str | None = None
    timestamps: bool = True
    diarization: bool = False


class CreateJobFromUrlRequest(BaseModel):
    url: HttpUrl = Field(..., min_length=1)
    options: CreateJobOptions = Field(default_factory=CreateJobOptions)


class CreateJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: uuid.UUID
    status: str
    message: str


class JobLimitError(BaseModel):
    error: dict[str, Any]


# Response schemas for job endpoints
class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str  # QUEUED|RUNNING|SUCCEEDED|FAILED|CANCELED
    filename: str
    language: str | None
    progress_pct: int
    progress_stage: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class JobListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    jobs: list[JobSummary]
    total: int
    page: int
    page_size: int


class JobDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    filename: str
    requested_language: str | None
    detected_language: str | None
    engine: str
    options: dict[str, Any]
    progress_pct: int
    progress_stage: str | None
    attempts: int
    error_code: str | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    audio_duration_seconds: float | None
    target_language: str | None  # Target language for translation


class SegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int  # segment index
    start_ms: int
    end_ms: int
    text: str
    speaker: str | None = None


class JobResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: uuid.UUID
    translation: dict[str, Any] | None = None  # Translation artifact if available
    transcript_id: uuid.UUID
    text: str
    language: str
    segments: list[SegmentResponse]
    engine: str


class CancelJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: str
