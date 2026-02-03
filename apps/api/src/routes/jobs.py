import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from poly_core.services.billing import BillingService
from poly_core.services.job_manager import JobManagerService
from poly_core.services.storage_service import get_storage_backend
from poly_db.database import get_db_session
from poly_db.models.transcription_jobs import JobStatus
from poly_db.repositories import (
    AudioAssetRepository,
    TranscriptionJobRepository,
    TranscriptRepository,
)
from poly_redis.client import get_redis_client
from poly_redis.queue import TranscriptionQueue
from src.config import get_settings
from src.dependencies import get_current_team_id, get_current_user_id
from src.schemas.jobs import (
    CancelJobResponse,
    CreateJobFromUrlRequest,
    CreateJobResponse,
    JobDetailResponse,
    JobListResponse,
    JobResultResponse,
    JobSummary,
)

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


async def job_progress_streamer(
    job_id: uuid.UUID,
    team_id: uuid.UUID,
    cancel_flag: str | None = None,
) -> AsyncGenerator[dict, None]:
    redis_client = get_redis_client()
    channel = f"job:{job_id}:progress"
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)

    try:
        while True:
            message = await asyncio.to_thread(
                pubsub.get_message, ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message.get("data"):
                data = json.loads(message["data"])

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
    finally:
        pubsub.close()


@router.get("/{job_id}/live")
async def stream_job_progress(
    job_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
    cancel_token: str | None = None,
):
    from poly_db.database import get_db_session
    from poly_db.repositories import TranscriptionJobRepository

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


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(
        None, description="Filter by status: queued, running, succeeded, failed, canceled"
    ),
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


@router.get("/pending", response_model=JobListResponse)
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


@router.get("/completed", response_model=JobListResponse)
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
            page=page,
            page_size=page_size,
        )


@router.get("/{job_id}", response_model=JobDetailResponse)
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


@router.get("/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(
    job_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
) -> JobResultResponse:
    with get_db_session() as session:
        job_repo = TranscriptionJobRepository(session)
        transcript_repo = TranscriptRepository(session)
        translation_repo = TranslationArtifactRepository(session)

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
        translation_repo = TranslationArtifactRepository(session)
        translation = translation_repo.get_by_job_id(team_id, job_id)

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

        translation_data = None
        if translation and translation.status.value == "SUCCEEDED":
            translation_data = {
                "target_language": translation.target_language,
                "text": translation.text,
                "segments": translation.segments,
                "engine": translation.engine,
                "engine_version": translation.engine_version,
            }

        return JobResultResponse(
            job_id=job.id,
            transcript_id=transcript.id,
            text=transcript.text,
            language=transcript.language,
            segments=segments,
            engine=transcript.engine_version,
            translation=translation_data,
        )


@router.post("/{job_id}/cancel", response_model=CancelJobResponse)
async def cancel_job(
    job_id: uuid.UUID,
    team_id: uuid.UUID = Depends(get_current_team_id),
):
    from poly_db.database import get_db_session
    from poly_db.models.transcription_jobs import JobStatus
    from poly_db.repositories import TranscriptionJobRepository
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


def _build_job_manager(session: Session) -> JobManagerService:
    settings = get_settings()
    storage_backend = get_storage_backend(
        backend_type=settings.STORAGE_BACKEND,
        storage_path=settings.STORAGE_PATH,
        min_free_bytes=settings.STORAGE_MIN_FREE_BYTES,
        bucket=settings.AWS_S3_BUCKET,
        region=settings.AWS_REGION,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    billing_service = BillingService(session, settings.STRIPE_SECRET_KEY)
    queue = TranscriptionQueue(get_redis_client())
    return JobManagerService(
        session=session,
        storage_backend=storage_backend,
        billing_service=billing_service,
        queue=queue,
    )


def _filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = parsed.path.split("/")[-1]
    return name or "audio"


@router.post("", response_model=CreateJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_from_upload(
    file: UploadFile = File(...),
    language: str | None = Form(None),
    engine: str | None = Form(None),
    timestamps: bool = Form(True),
    diarization: bool = Form(False),
    target_language: str | None = Form(None),
    team_id: uuid.UUID = Depends(get_current_team_id),
    user_id: str = Depends(get_current_user_id),
):
    settings = get_settings()
    file_content = await file.read()
    file_size = len(file_content)

    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Upload exceeds maximum size",
        )

    # Validate MIME type
    allowed_mime_types = {
        "audio/mpeg",
        "audio/mp4",
        "audio/mp3",
        "audio/wav",
        "audio/x-wav",
        "audio/ogg",
        "audio/webm",
        "audio/m4a",
        "audio/flac",
        "audio/amr",
        "audio/amr-wb",
        "audio/aac",
    }
    content_type = file.content_type or ""
    if content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported audio format: {content_type}. "
                "Allowed: MP3, WAV, M4A, AAC, FLAC, AMR, AMR-WB, OGG, WEBM, MP4"
            ),
        )

    with get_db_session() as session:
        manager = _build_job_manager(session)
        try:
            job = manager.create_job_from_upload(
                team_id=team_id,
                user_id=uuid.UUID(user_id),
                file_content=file_content,
                filename=file.filename or "audio",
                mime_type=file.content_type or "audio/mpeg",
                file_size=file_size,
                options={
                    "language": language,
                    "engine": engine,
                    "timestamps": timestamps,
                    "diarization": diarization,
                    "target_language": target_language,
                },
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e),
            )
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    return CreateJobResponse(
        job_id=job.id,
        status=job.status.value,
        message="Job created",
    )


@router.post("/url", response_model=CreateJobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_from_url(
    request: CreateJobFromUrlRequest,
    team_id: uuid.UUID = Depends(get_current_team_id),
    user_id: str = Depends(get_current_user_id),
):
    with get_db_session() as session:
        manager = _build_job_manager(session)
        try:
            job = manager.create_job_from_url(
                team_id=team_id,
                user_id=uuid.UUID(user_id),
                url=request.url,
                filename=_filename_from_url(request.url),
                options=request.options.model_dump(),
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(e),
            )
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    return CreateJobResponse(
        job_id=job.id,
        status=job.status.value,
        message="Job created",
    )


jobs_router = router
jobs_router = router
