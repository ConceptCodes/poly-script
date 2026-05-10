"""Transcript-related request and response schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SegmentResponse(BaseModel):
    """Response model for a transcript segment."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    start_ms: int
    end_ms: int
    text: str
    speaker: str | None = None


class TranscriptResponse(BaseModel):
    """Response model for a complete transcript."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    text: str
    language: str
    segments: list[SegmentResponse]
    engine_version: str
    created_at: datetime
    updated_at: datetime | None = None


class TranscriptListItem(BaseModel):
    """Summary model for transcript list items."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    job_filename: str | None = None
    text_preview: str = ""
    language: str
    created_at: datetime
    updated_at: datetime | None = None


class TranscriptListResponse(BaseModel):
    """Response model for listing transcripts."""

    model_config = ConfigDict(from_attributes=True)

    transcripts: list[TranscriptListItem]
    total: int
    page: int
    page_size: int


class SegmentsResponse(BaseModel):
    """Response model for transcript segments."""

    model_config = ConfigDict(from_attributes=True)

    segments: list[SegmentResponse]


class UpdateTranscriptRequest(BaseModel):
    """Request model for updating full transcript text."""

    text: str = Field(..., min_length=1, max_length=100000)


class UpdateSegmentRequest(BaseModel):
    """Request model for updating a single segment."""

    text: str = Field(..., min_length=1, max_length=10000)


class EditEntry(BaseModel):
    """Model for a single edit entry in history."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None = None
    user_email: str | None = None
    field_edited: str  # "full_text" | "segment"
    segment_id: int | None = None
    previous_text: str
    new_text: str
    created_at: datetime


class EditHistoryResponse(BaseModel):
    """Response model for transcript edit history."""

    model_config = ConfigDict(from_attributes=True)

    edits: list[EditEntry]
    total: int


class RevertTranscriptRequest(BaseModel):
    """Request model for reverting transcript to original."""

    confirm: bool = Field(..., description="Must be true to confirm revert")


class RevertTranscriptResponse(BaseModel):
    """Response model for transcript revert."""

    model_config = ConfigDict(from_attributes=True)

    message: str
    transcript_id: uuid.UUID


class ExportFormat(BaseModel):
    """Supported export formats."""

    format: str = Field(..., pattern="^(txt|json|srt|vtt)$")


class ExportResponse(BaseModel):
    """Response model for export request."""

    model_config = ConfigDict(from_attributes=True)

    message: str
    format: str
    content_length: int


class SplitSegmentRequest(BaseModel):
    """Request model for splitting a segment at a timestamp."""

    split_at_ms: int = Field(
        ...,
        description="Timestamp in milliseconds to split at (must be within segment range)",
        gt=0,
    )


class SplitSegmentResponse(BaseModel):
    """Response model for split segment operation."""

    model_config = ConfigDict(from_attributes=True)

    message: str
    original_segment_id: int
    new_segment_ids: list[int] = Field(..., min_items=2, max_items=2)


class MergeSegmentsRequest(BaseModel):
    """Request model for merging consecutive segments."""

    segment_ids: list[int] = Field(
        ..., min_length=2, description="List of consecutive segment IDs to merge"
    )


class MergeSegmentsResponse(BaseModel):
    """Response model for merge segments operation."""

    model_config = ConfigDict(from_attributes=True)

    message: str
    merged_segment_id: int
    removed_segment_ids: list[int]


class UpdateSegmentTimestampsRequest(BaseModel):
    """Request model for updating segment timestamps."""

    start_ms: int = Field(..., gt=0, description="New start time in milliseconds")
    end_ms: int = Field(..., gt=0, description="New end time in milliseconds")


class UpdateSegmentTimestampsResponse(BaseModel):
    """Response model for updating segment timestamps."""

    model_config = ConfigDict(from_attributes=True)

    message: str
    segment: SegmentResponse


class TranscriptError(BaseModel):
    """Error response model for transcript operations."""

    error: str
    code: str
    details: dict[str, Any] | None = None


class BulkDeleteTranscriptsRequest(BaseModel):
    """Request model for deleting multiple transcripts."""

    transcript_ids: list[uuid.UUID] = Field(..., min_length=1)


class BulkDeleteTranscriptsResponse(BaseModel):
    """Response model for deleting multiple transcripts."""

    model_config = ConfigDict(from_attributes=True)

    deleted_count: int
