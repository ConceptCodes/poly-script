"""Transcript API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from poly_core.services.async_export_service import AsyncExportService
from poly_core.services.export_service import ExportService
from poly_core.services.transcript_service import TranscriptService
from poly_db.database import get_db_session
from poly_db.repositories import AudioAssetRepository, TranscriptRepository
from src.dependencies import get_current_team_id, get_current_user_id
from src.schemas.transcripts import (
    EditEntry,
    EditHistoryResponse,
    MergeSegmentsRequest,
    MergeSegmentsResponse,
    RevertTranscriptRequest,
    RevertTranscriptResponse,
    SegmentResponse,
    SegmentsResponse,
    SplitSegmentRequest,
    SplitSegmentResponse,
    TranscriptListItem,
    TranscriptListResponse,
    TranscriptResponse,
    UpdateSegmentRequest,
    UpdateSegmentTimestampsRequest,
    UpdateSegmentTimestampsResponse,
    UpdateTranscriptRequest,
)

router = APIRouter(prefix="/v1/transcripts", tags=["transcripts"])


def get_transcript_with_team_check(
    transcript_id: uuid.UUID,
    team_id: uuid.UUID,
    session: Session,
):
    """Get transcript and verify team access."""
    repo = TranscriptRepository(session)
    transcript = repo.get(transcript_id)

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found",
        )

    # Verify team access via job
    if transcript.job and transcript.job.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this transcript",
        )

    return transcript


@router.get("", response_model=TranscriptListResponse)
async def list_transcripts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    language: str | None = Query(None),
    search: str | None = Query(None),
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> TranscriptListResponse:
    """List all transcripts for the current team."""
    with get_db_session() as session:
        service = TranscriptService(session)
        transcripts, total = service.list_transcripts(
            team_id=str(team_id),
            language=language,
            search=search,
            page=page,
            page_size=page_size,
        )

        audio_repo = AudioAssetRepository(session)

        items = []
        for t in transcripts:
            audio = audio_repo.get_by_job_id(t.job_id)
            items.append(
                TranscriptListItem(
                    id=t.id,
                    job_id=t.job_id,
                    job_filename=audio.filename if audio else None,
                    text_preview=t.text[:200] + "..." if len(t.text) > 200 else t.text,
                    language=t.language,
                    created_at=t.created_at,
                    updated_at=t.updated_at,
                )
            )

        return TranscriptListResponse(
            transcripts=items,
            total=total,
            page=page,
            page_size=page_size,
        )


@router.get("/{transcript_id}", response_model=TranscriptResponse)
async def get_transcript(
    transcript_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> TranscriptResponse:
    """Get a specific transcript by ID."""
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        # Build segment responses
        segments = []
        for idx, seg in enumerate(transcript.segments or []):
            segments.append(
                {
                    "id": idx,
                    "start_ms": seg.get("start_ms", 0),
                    "end_ms": seg.get("end_ms", 0),
                    "text": seg.get("text", ""),
                    "speaker": seg.get("speaker"),
                }
            )

        return TranscriptResponse(
            id=transcript.id,
            job_id=transcript.job_id,
            text=transcript.text,
            language=transcript.language,
            segments=segments,
            engine_version=transcript.engine_version,
            created_at=transcript.created_at,
            updated_at=transcript.updated_at,
        )


@router.patch("/{transcript_id}", response_model=TranscriptResponse)
async def update_transcript_full_text(
    transcript_id: uuid.UUID,
    request: UpdateTranscriptRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    user_id: str = Depends(get_current_user_id),
) -> TranscriptResponse:
    """Update the full text of a transcript."""
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        service = TranscriptService(session)
        updated = service.update_full_text(
            str(transcript_id),
            user_id,
            request.text,
        )

        # Build segment responses
        segments = []
        for idx, seg in enumerate(updated.segments or []):
            segments.append(
                {
                    "id": idx,
                    "start_ms": seg.get("start_ms", 0),
                    "end_ms": seg.get("end_ms", 0),
                    "text": seg.get("text", ""),
                    "speaker": seg.get("speaker"),
                }
            )

        return TranscriptResponse(
            id=updated.id,
            job_id=updated.job_id,
            text=updated.text,
            language=updated.language,
            segments=segments,
            engine_version=updated.engine_version,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )


@router.get("/{transcript_id}/segments", response_model=SegmentsResponse)
async def get_transcript_segments(
    transcript_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
):
    """Get segments of a specific transcript."""
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        segments = []
        for idx, seg in enumerate(transcript.segments or []):
            segments.append(
                {
                    "id": idx,
                    "start_ms": seg.get("start_ms", 0),
                    "end_ms": seg.get("end_ms", 0),
                    "text": seg.get("text", ""),
                    "speaker": seg.get("speaker"),
                }
            )

        return SegmentsResponse(segments=segments)


@router.patch("/{transcript_id}/segments/{segment_id}", response_model=SegmentResponse)
async def update_transcript_segment(
    transcript_id: uuid.UUID,
    segment_id: int,
    request: UpdateSegmentRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    user_id: str = Depends(get_current_user_id),
):
    """Update a single segment of a transcript."""
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        service = TranscriptService(session)
        updated = service.update_segment(
            str(transcript_id),
            segment_id,
            user_id,
            request.text,
        )

        # Return updated segment
        if segment_id < len(updated.segments):
            seg = updated.segments[segment_id]
            return SegmentResponse(
                id=segment_id,
                start_ms=seg.get("start_ms", 0),
                end_ms=seg.get("end_ms", 0),
                text=seg.get("text", ""),
                speaker=seg.get("speaker"),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Segment not found",
            )


@router.get("/{transcript_id}/history", response_model=EditHistoryResponse)
async def get_transcript_history(
    transcript_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> EditHistoryResponse:
    """Get edit history for a transcript."""
    with get_db_session() as session:
        # First verify access
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        service = TranscriptService(session)
        edits = service.get_edit_history(str(team_id), str(transcript_id))

        entries = []
        for edit in edits:
            entries.append(
                EditEntry(
                    id=edit.id,
                    user_id=edit.user_id,
                    user_email=None,  # Would need to join with user table
                    field_edited="segment" if edit.previous_segments else "full_text",
                    segment_id=None,  # Would need to parse from previous_segments
                    previous_text=edit.previous_text or "",
                    new_text=edit.new_text,
                    created_at=edit.created_at,
                )
            )

        return EditHistoryResponse(edits=entries, total=len(entries))


@router.post("/{transcript_id}/revert", response_model=RevertTranscriptResponse)
async def revert_transcript(
    transcript_id: uuid.UUID,
    request: RevertTranscriptRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    user_id: str = Depends(get_current_user_id),
):
    """Revert transcript to its original state."""
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation required to revert transcript",
        )
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        service = TranscriptService(session)
        try:
            service.revert_to_original(str(team_id), str(transcript_id), user_id)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        return RevertTranscriptResponse(
            message="Transcript reverted to original state",
            transcript_id=transcript_id,
        )



@router.post("/{transcript_id}/segments/{segment_id}/split", response_model=SplitSegmentResponse)
async def split_segment(
    transcript_id: uuid.UUID,
    segment_id: int,
    request: SplitSegmentRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    user_id: str = Depends(get_current_user_id),
):
    """Split a segment at a specified timestamp."""
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        service = TranscriptService(session)
        try:
            updated, new_ids = service.split_segment(
                str(transcript_id),
                segment_id,
                user_id,
                request.split_at_ms,
            )
            return SplitSegmentResponse(
                message="Segment split successfully",
                original_segment_id=segment_id,
                new_segment_ids=new_ids,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )


@router.post("/{transcript_id}/segments/merge", response_model=MergeSegmentsResponse)
async def merge_segments(
    transcript_id: uuid.UUID,
    request: MergeSegmentsRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    user_id: str = Depends(get_current_user_id),
):
    """Merge consecutive segments into one."""
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        service = TranscriptService(session)
        try:
            updated, merged_id, removed_ids = service.merge_segments(
                str(transcript_id),
                list(request.segment_ids),
                user_id,
            )
            return MergeSegmentsResponse(
                message="Segments merged successfully",
                merged_segment_id=merged_id,
                removed_segment_ids=removed_ids,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )


@router.patch("/{transcript_id}/segments/{segment_id}/timestamps", response_model=UpdateSegmentTimestampsResponse)
async def update_segment_timestamps(
    transcript_id: uuid.UUID,
    segment_id: int,
    request: UpdateSegmentTimestampsRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    user_id: str = Depends(get_current_user_id),
):
    """Update timestamps of a segment."""
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        service = TranscriptService(session)
        try:
            updated = service.update_segment_timestamps(
                str(transcript_id),
                segment_id,
                user_id,
                request.start_ms,
                request.end_ms,
            )

            # Return updated segment
            if segment_id < len(updated.segments):
                seg = updated.segments[segment_id]
                return UpdateSegmentTimestampsResponse(
                    message="Segment timestamps updated successfully",
                    segment=SegmentResponse(
                        id=segment_id,
                        start_ms=seg.get("start_ms", 0),
                        end_ms=seg.get("end_ms", 0),
                        text=seg.get("text", ""),
                        speaker=seg.get("speaker"),
                    ),
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Segment not found",
                )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

@router.get("/{transcript_id}/export")
async def export_transcript(
    transcript_id: uuid.UUID,
    format: str = Query("txt", regex="^(txt|json|srt|vtt)$"),
    async_export: bool = Query(False, description="Use async export with caching"),
    team_id: uuid.UUID = Depends(get_current_team_id),
):
    """
    Export transcript in the specified format.
    
    For async_export=true, returns a presigned URL for large exports.
    Otherwise, returns the exported content directly.
    """
    with get_db_session() as session:
        transcript = get_transcript_with_team_check(transcript_id, team_id, session)

        # For async export with caching
        if async_export:
            from poly_core.services.storage_service import get_storage_backend
            from src.config import settings

            storage_backend = None
            if settings.STORAGE_TYPE == "s3":
                storage_backend = get_storage_backend(
                    "s3",
                    bucket=settings.S3_BUCKET,
                    region=settings.S3_REGION,
                    access_key=settings.AWS_ACCESS_KEY_ID,
                    secret_key=settings.AWS_SECRET_ACCESS_KEY,
                )

            async_service = AsyncExportService(session)

            # Check cache first
            cached = async_service.get_cached_export(transcript, format)
            if cached and cached.presigned_url:
                # Return redirect to presigned URL
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=cached.presigned_url, status_code=307)

            # Generate new export
            artifact = async_service.generate_and_cache_export(
                transcript,
                format,
                storage_backend,
            )

            if artifact.presigned_url:
                # Return redirect to presigned URL
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=artifact.presigned_url, status_code=307)
            else:
                # Return inline content
                content_type = ExportService.get_export_content_type(format)
                filename = ExportService.get_export_filename(transcript, format)
                return PlainTextResponse(
                    content=artifact.content,
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"',
                        "Content-Length": str(artifact.content_length),
                    },
                )

        # Synchronous export (backward compatible)
        content = ExportService.export_transcript(transcript, format)
        content_length = len(content.encode("utf-8"))

        # Determine response type and headers
        content_type = ExportService.get_export_content_type(format)
        filename = ExportService.get_export_filename(transcript, format)

        return PlainTextResponse(
            content=content,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(content_length),
            },
        )

transcripts_router = router
transcripts_router = router
