import uuid
import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from poly_db.repositories import TranscriptionJobRepository, TranscriptRepository, AudioAssetRepository
from poly_db.models.transcription_jobs import JobStatus
from poly_db.database import get_db_session
from src.dependencies import get_current_team_id
from src.schemas.jobs import JobSummary, JobListResponse, JobDetailResponse, JobResultResponse, CancelJobResponse
from poly_redis.client import get_redis_client

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


async def job_progress_streamer(
    job_id: uuid.UUID,
    team_id: uuid.UUID,
    cancel_flag: str | None = None,
) -> AsyncGenerator[dict, None]:
    redis_client = get_redis_client()
    channel = f"job:{job_id}:progress"

    try:
        while True:
            message = redis_client.blpop(channel, timeout=5)
            if message:
                data = json.loads(message)

                if cancel_flag and data.get("job_id") == str(job_id):
                    return

                if data.get("job_id") == str(job_id):
                    yield {
                        "event": "progress",
                        "data": data,
                    }
            else:
                yield {
                    "event": "keepalive",
                    "data": {"timestamp": asyncio.get_event_loop().time()},
                }
    except Exception as e:
        yield {
            "event": "error",
            "data": {"error": str(e)},
        }


@router.get("/{job_id}/live")
async def stream_job_progress(
    job_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
    cancel_token: str | None = None,
):
    from poly_db.repositories import TranscriptionJobRepository
    from poly_db.database import get_db_session

    with get_db_session() as session:
        job_repo = TranscriptionJobRepository(session)
        job = job_repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        if job.team_id != team_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this job",
            )

    async def event_stream():
        async for event in job_progress_streamer(job_id, team_id, cancel_token):
            yield event

    return EventSourceResponse(event_stream())


@router.get("")
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, description="Filter by status: queued, running, succeeded, failed, canceled"),
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> JobListResponse:
    with get_db_session() as session:
        job_repo = TranscriptionJobRepository(session)
        audio_repo = AudioAssetRepository(session)

        all_jobs = job_repo.get_by_team_id(team_id)

        if status_filter:
            try:
                status_enum = JobStatus(status_filter.upper())
                all_jobs = [j for j in all_jobs if j.status == status_enum]
            except ValueError:
                pass

        all_jobs = sorted(all_jobs, key=lambda j: j.created_at, reverse=True)

        total = len(all_jobs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_jobs = all_jobs[start_idx:end_idx]

        job_summaries = []
        for job in paginated_jobs:
            audio = audio_repo.get_by_job_id(job.id)
            job_summaries.append(
                JobSummary(
                    id=job.id,
                    status=job.status.value,
                    filename=audio.filename if audio else "unknown",
                    language=job.requested_language,
                    progress_pct=job.progress or 0,
                    progress_stage=job.progress_stage,
                    created_at=job.created_at,
                    started_at=getattr(job, "started_at", None),
                    finished_at=getattr(job, "finished_at", None),
                )
            )

        return JobListResponse(
            jobs=job_summaries,
            total=total,
            page=page,
            page_size=page_size,
        )


@router.get("/pending")
async def list_pending_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> JobListResponse:
    with get_db_session() as session:
        job_repo = TranscriptionJobRepository(session)
        audio_repo = AudioAssetRepository(session)

        queued_jobs = job_repo.get_by_status(team_id, JobStatus.QUEUED)
        running_jobs = job_repo.get_by_status(team_id, JobStatus.RUNNING)

        all_jobs = sorted(
            queued_jobs + running_jobs,
            key=lambda j: j.created_at,
            reverse=True,
        )

        total = len(all_jobs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_jobs = all_jobs[start_idx:end_idx]

        job_summaries = []
        for job in paginated_jobs:
            audio = audio_repo.get_by_job_id(job.id)
            job_summaries.append(
                JobSummary(
                    id=job.id,
                    status=job.status.value,
                    filename=audio.filename if audio else "unknown",
                    language=job.requested_language,
                    progress_pct=job.progress or 0,
                    progress_stage=job.progress_stage,
                    created_at=job.created_at,
                    started_at=getattr(job, "started_at", None),
                    finished_at=getattr(job, "finished_at", None),
                )
            )

        return JobListResponse(
            jobs=job_summaries,
            total=total,
            page=page,
            page_size=page_size,
        )


@router.get("/completed")
async def list_completed_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> JobListResponse:
    with get_db_session() as session:
        job_repo = TranscriptionJobRepository(session)
        audio_repo = AudioAssetRepository(session)

        succeeded_jobs = job_repo.get_by_status(team_id, JobStatus.SUCCEEDED)
        failed_jobs = job_repo.get_by_status(team_id, JobStatus.FAILED)
        canceled_jobs = job_repo.get_by_status(team_id, JobStatus.CANCELED)

        all_jobs = sorted(
            succeeded_jobs + failed_jobs + canceled_jobs,
            key=lambda j: j.created_at,
            reverse=True,
        )

        total = len(all_jobs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_jobs = all_jobs[start_idx:end_idx]

        job_summaries = []
        for job in paginated_jobs:
            audio = audio_repo.get_by_job_id(job.id)
            job_summaries.append(
                JobSummary(
                    id=job.id,
                    status=job.status.value,
                    filename=audio.filename if audio else "unknown",
                    language=job.requested_language,
                    progress_pct=job.progress or 0,
                    progress_stage=job.progress_stage,
                    created_at=job.created_at,
                    started_at=getattr(job, "started_at", None),
                    finished_at=getattr(job, "finished_at", None),
                )
            )

        return JobListResponse(
            jobs=job_summaries,
            total=total,
            page=page_size,
            page=page_size,
        )


@router.get("/{job_id}")
async def get_job_detail(
    job_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> JobDetailResponse:
    with get_db_session() as session:
        job_repo = TranscriptionJobRepository(session)
        audio_repo = AudioAssetRepository(session)

        job = job_repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        if job.team_id != team_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this job",
            )

        audio = audio_repo.get_by_job_id(job_id)

        return JobDetailResponse(
            id=job.id,
            status=job.status.value,
            filename=audio.filename if audio else "unknown",
            requested_language=job.requested_language,
            detected_language=None,
            engine=job.engine or "default",
            options=job.options or {},
            progress_pct=job.progress or 0,
            progress_stage=job.progress_stage,
            attempts=job.attempts,
            error_code=job.error_code,
            error_message=job.error_message,
            created_at=job.created_at,
            started_at=getattr(job, "started_at", None),
            finished_at=getattr(job, "finished_at", None),
            audio_duration_seconds=audio.duration_seconds if audio else None,
        )


@router.get("/{job_id}/result")
async def get_job_result(
    job_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> JobResultResponse:
    with get_db_session() as session:
        job_repo = TranscriptionJobRepository(session)
        transcript_repo = TranscriptRepository(session)

        job = job_repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        if job.team_id != team_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this job",
            )

        if job.status != JobStatus.SUCCEEDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job has not completed successfully yet",
            )

        transcript = transcript_repo.get_by_job_id(team_id, job_id)

        if not transcript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcript not found for this job",
            )

        segments_data = transcript.segments or []

        segments = [
            {
                "id": idx,
                "start_ms": seg.get("start_ms", 0),
                "end_ms": seg.get("end_ms", 0),
                "text": seg.get("text", ""),
                "speaker": seg.get("speaker"),
            }
            for idx, seg in enumerate(segments_data)
        ]

        return JobResultResponse(
            job_id=job.id,
            transcript_id=transcript.id,
            text=transcript.text,
            language=transcript.language,
            segments=segments,
            engine=transcript.engine_version,
        )


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
):
    from poly_db.repositories import TranscriptionJobRepository
    from poly_db.models.transcription_jobs import JobStatus
    from poly_db.database import get_db_session
    from poly_redis.client import get_redis_client

    with get_db_session() as session:
        job_repo = TranscriptionJobRepository(session)
        job = job_repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
            )

        if job.team_id != team_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this job",
            )

        if job.status in [JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel a job that is completed, failed, or canceled",
            )

        redis_client = get_redis_client()
        cancel_key = f"cancel:{job_id}"
        redis_client.setex(cancel_key, 60, "1")

        job_repo.update(job_id, status=JobStatus.CANCELED)

        return CancelJobResponse(message="Job cancellation requested")
