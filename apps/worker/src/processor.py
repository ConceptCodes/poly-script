"""
Job Processor

Processes transcription jobs through a 5-stage pipeline:
1. Download/Load Audio (0-10%)
2. Decode & Validate (10-20%)
3. Transcribe with STT (20-90%)
4. Format & Normalize (90-95%)
5. Save to Database (95-100%)
"""
import logging
import os
import tempfile
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from poly_db.models.transcription_jobs import TranscriptionJob, JobStatus
from poly_db.models.audio_assets import AudioAsset
from poly_db.models.transcripts import Transcript
from poly_db.models.translation_artifacts import TranslationArtifact, TranslationStatus
from poly_db.repositories import (
    TranscriptionJobRepository,
    AudioAssetRepository,
    TranscriptRepository,
    TranslationArtifactRepository,
    TranscriptionJobRepository,
    AudioAssetRepository,
    TranscriptRepository,
)
from poly_stt.registry import EngineRegistry
from poly_stt.engines.translategemma import TranslateGemmaEngine
from poly_stt.interface import TranscriptionResult
from .progress import ProgressPublisher
from poly_core.logging_context import set_job_context, clear_job_context
from .enums import ProgressStage

logger = logging.getLogger(__name__)


class JobProcessor:
    """Processes a single transcription job through the pipeline."""

    def __init__(
        self,
        session: Session,
        storage_backend,
        progress_publisher: ProgressPublisher,
    ):
        self.session = session
        self.storage_backend = storage_backend
        self.progress_publisher = progress_publisher

        self.job_repo = TranscriptionJobRepository(session)
        self.audio_repo = AudioAssetRepository(session)
        self.transcript_repo = TranscriptRepository(session)
        self.translation_repo = TranslationArtifactRepository(session)

    def process_job(self, job_id: str) -> bool:
        """
        Process a job end-to-end.

        Args:
            job_id: Job UUID

        Returns:
            True if successful, False if failed.
        """
        # Fetch job
        job = self.job_repo.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return False

        set_job_context(str(job.id), str(job.team_id))

        # Check for cancellation
        if self._check_cancellation(job_id):
            logger.info(f"Job {job_id} canceled before processing")
            self._mark_canceled(job)
            return True

        # Mark as RUNNING
        job = self.job_repo.update(
            job_id,
            status=JobStatus.RUNNING,
            attempts=job.attempts + 1,
            started_at=datetime.now(timezone.utc),
        )

        self.progress_publisher.publish_progress(
            job_id=job_id,
            team_id=str(job.team_id),
            progress_pct=0,
            progress_stage="starting",
            status="RUNNING",
        )
        self._set_progress(job_id, "starting")

        audio_path: Optional[str] = None

        try:
            # Stage 1: Download/Load Audio (0-10%)
            audio_path = self._prepare_audio(job)
            self.progress_publisher.publish_stage_complete(
                job_id=job_id,
                team_id=str(job.team_id),
                stage="downloading",
            )
            self._set_progress(job_id, "downloading")

            # Stage 2: Decode & Validate (10-20%)
            duration_ms = self._validate_audio(audio_path)
            self.progress_publisher.publish_stage_complete(
                job_id=job_id,
                team_id=str(job.team_id),
                stage="decoding",
            )
            self._set_progress(job_id, "decoding")

            # Stage 3: Transcribe with STT (20-90%)
            result = self._transcribe_audio(job, audio_path)
            self.progress_publisher.publish_stage_complete(
                job_id=job_id,
                team_id=str(job.team_id),
                stage="transcribing",
            )
            self._set_progress(job_id, "transcribing")

            # Stage 4: Format & Normalize (90-95%)
            transcript = self._format_transcript(job, result, duration_ms)
            self.progress_publisher.publish_stage_complete(
                job_id=job_id,
                team_id=str(job.team_id),
                stage="formatting",
            )
            self._set_progress(job_id, "formatting")

            # Stage 5: Translate (95-98%) - if target_language specified
            if job.target_language:
                self._translate_transcript(job, transcript, result)
                self.progress_publisher.publish_stage_complete(
                    job_id=job_id,
                    team_id=str(job.team_id),
                    stage="translating",
                )
                self._set_progress(job_id, "translating")

            # Stage 6: Save to DB (98-100%)
            self._save_transcript(transcript)
            self.progress_publisher.publish_stage_complete(
                job_id=job_id,
                team_id=str(job.team_id),
                stage="saving",
            )
            self._set_progress(job_id, "saving")

            # Mark SUCCEEDED
            self._mark_succeeded(job, duration_ms)

            logger.info(f"Job {job_id} completed successfully")
            return True

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            self._mark_failed(job, str(e))
            return False
        finally:
            # Cleanup temp files
            if audio_path:
                self._cleanup_temp_files(audio_path)
            clear_job_context()

    def _prepare_audio(self, job: TranscriptionJob) -> str:
        """Download or prepare audio file for processing."""
        audio_asset = self.audio_repo.get_by_job_id(job.id)
        if not audio_asset:
            raise ValueError("Audio asset not found for job")

        # Check if URL job or upload
        if audio_asset.storage_uri.startswith(("http://", "https://")):
            # Download from URL
            return self._download_audio(audio_asset.storage_uri)
        else:
            # Get from local/S3 storage
            return self.storage_backend.get_local_path(audio_asset.storage_uri)

    def _download_audio(self, url: str) -> str:
        """Download audio from URL to temporary file."""
        import requests

        logger.info(f"Downloading audio from {url}")
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()

        # Determine extension
        ext = os.path.splitext(url)[1] or ".mp3"

        # Save to temp file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=ext,
        ) as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
            temp_path = f.name

        logger.info(f"Downloaded audio to {temp_path}")
        return temp_path

    def _validate_audio(self, audio_path: str) -> int:
        """Validate audio format and get duration in milliseconds."""
        import librosa
        import soundfile as sf

        logger.info(f"Validating audio: {audio_path}")

        try:
            # Try loading with librosa for duration
            y, sr = librosa.load(audio_path, sr=None)
            duration_seconds = len(y) / sr
            duration_ms = int(duration_seconds * 1000)

            # Validate with soundfile
            info = sf.info(audio_path)
            logger.info(f"Audio validated: {duration_ms}ms, {info.samplerate}Hz, {info.channels} channels")

            return duration_ms
        except Exception as e:
            raise ValueError(f"Invalid audio file: {e}")

    def _transcribe_audio(
        self, job: TranscriptionJob, audio_path: str
    ) -> TranscriptionResult:
        """Transcribe audio using configured STT engine."""
        # Get engine
        engine_name = job.engine or "whisper-local-base"

        try:
            engine = EngineRegistry.get(engine_name)
        except ValueError:
            logger.warning(f"Engine {engine_name} not found, using default")
            engine = EngineRegistry.get()

        # Get options
        options = job.options or {}
        timestamps = options.get("timestamps", True)
        diarization = options.get("diarization", False)
        requested_language = job.requested_language

        # Transcribe
        logger.info(f"Transcribing job {job.id} with {engine.name}")
        result = engine.transcribe(
            audio_path=audio_path,
            language=requested_language,
            timestamps=timestamps,
            diarization=diarization,
        )

        logger.info(f"Transcription complete: {len(result.segments)} segments")
        return result

    def _format_transcript(
        self, job: TranscriptionJob, result: TranscriptionResult, duration_ms: int
    ) -> Transcript:
        """Format transcription result into Transcript model."""
        # Convert segments to JSON
        segments_json = [
            {
                "start_ms": seg.start_ms,
                "end_ms": seg.end_ms,
                "text": seg.text,
                "speaker": seg.speaker,
            }
            for seg in result.segments
        ]

        logger.info(f"Formatted transcript: {len(segments_json)} segments, {len(result.text)} chars")

        return Transcript(
            job_id=job.id,
            text=result.text,
            language=result.language,
            segments=segments_json,
            engine_version=result.engine,
            audio_duration_ms=duration_ms,
        )


    def _translate_transcript(
        self, job: TranscriptionJob, transcript: Transcript, stt_result: TranscriptionResult
    ) -> None:
        """Translate transcript to target language.
        
        Translation failures do NOT mark the job as FAILED.
        The translation artifact is saved with appropriate status.
        """
        # Create pending translation artifact
        translation = TranslationArtifact(
            job_id=job.id,
            status=TranslationStatus.PENDING,
            target_language=job.target_language,
        )
        self.translation_repo.create(translation)
        self.session.commit()
        
        try:
            # Check plan limits before translating
            if not self._check_translation_limit(job):
                raise Exception("Translation limit exceeded for team")
            
            # Initialize translation engine
            translation_engine = TranslateGemmaEngine()
            
            # Translate with segments preserved
            from poly_stt.interface import Segment
            segments = [
                Segment(
                    start_ms=seg["start_ms"],
                    end_ms=seg["end_ms"],
                    text=seg["text"],
                    speaker=seg.get("speaker"),
                )
                for seg in transcript.segments
            ]
            
            translation_result = translation_engine.translate_segments(
                segments=segments,
                target_language=job.target_language,
                source_language=stt_result.language,
            )
            
            # Update translation artifact with result
            self.translation_repo.update(
                translation.id,
                status=TranslationStatus.SUCCEEDED,
                text=translation_result.text,
                segments=[
                    {
                        "start_ms": seg.start_ms,
                        "end_ms": seg.end_ms,
                        "text": seg.text,
                        "speaker": seg.speaker,
                    }
                    for seg in translation_result.segments
                ],
                engine=translation_result.engine,
                engine_version=translation_engine.name,
            )
            
            # Increment translation count
            self._increment_translation_count(job)
            
            self.session.commit()
            logger.info(f"Translation completed for job {job.id}: {job.target_language}")
            
        except Exception as e:
            # Mark translation as failed but don't fail the job
            logger.error(f"Translation failed for job {job.id}: {e}", exc_info=True)
            self.translation_repo.update(
                translation.id,
                status=TranslationStatus.FAILED,
                error_code="TRANSLATION_ERROR",
                error_message=str(e)[:1000],
            )
            self.session.commit()

    def _check_translation_limit(self, job: TranscriptionJob) -> bool:
        """Check if team has translation quota remaining."""
        from poly_db.models.teams import PlanType
        
        team = self.session.query(TranscriptionJob).filter_by(id=job.id).one().team
        
        if team.plan == PlanType.PRO:
            return True  # Unlimited for PRO
        
        if team.plan == PlanType.STANDARD:
            limit = 25
        else:  # FREE
            limit = 5
        
        return team.monthly_translation_count < limit

    def _increment_translation_count(self, job: TranscriptionJob) -> None:
        """Increment monthly translation count for team."""
        team = self.session.query(TranscriptionJob).filter_by(id=job.id).one().team
        team.monthly_translation_count += 1
        self.session.commit()


    def _save_transcript(self, transcript: Transcript) -> None:
        """Save transcript to database."""
        self.transcript_repo.create(transcript)
        self.session.commit()
        logger.info(f"Saved transcript for job {transcript.job_id}")

    def _mark_succeeded(
        self, job: TranscriptionJob, duration_ms: int
    ) -> None:
        """Mark job as SUCCEEDED."""
        self.job_repo.update(
            job.id,
            status=JobStatus.SUCCEEDED,
            progress=100,
            progress_stage="completed",
            finished_at=datetime.now(timezone.utc),
        )

        # Update audio duration
        audio = self.audio_repo.get_by_job_id(job.id)
        if audio:
            self.audio_repo.update(
                audio.id,
                duration_seconds=duration_ms / 1000,
            )

        self.session.commit()

        self.progress_publisher.publish_progress(
            job_id=job.id,
            team_id=str(job.team_id),
            progress_pct=100,
            progress_stage="completed",
            status="SUCCEEDED",
        )

        logger.info(f"Job {job.id} marked as SUCCEEDED")

    def _set_progress(self, job_id: str, stage: str) -> None:
        """Update job progress in DB based on stage."""
        progress_pct = self.progress_publisher._get_stage_progress(stage)
        self.job_repo.update(
            job_id,
            progress=progress_pct,
            progress_stage=stage,
        )
        self.session.commit()

    def _mark_failed(self, job: TranscriptionJob, error_message: str) -> None:
        """Mark job as FAILED."""
        self.job_repo.update(
            job.id,
            status=JobStatus.FAILED,
            progress=0,
            progress_stage="failed",
            error_message=error_message,
            finished_at=datetime.now(timezone.utc),
        )
        self.session.commit()

        self.progress_publisher.publish_progress(
            job_id=job.id,
            team_id=str(job.team_id),
            progress_pct=0,
            progress_stage="failed",
            status="FAILED",
            error_message=error_message,
        )

        logger.info(f"Job {job.id} marked as FAILED")

    def _mark_canceled(self, job: TranscriptionJob) -> None:
        """Mark job as CANCELED."""
        self.job_repo.update(
            job.id,
            status=JobStatus.CANCELED,
            progress=0,
            progress_stage="canceled",
            finished_at=datetime.now(timezone.utc),
        )
        self.session.commit()

        self.progress_publisher.publish_progress(
            job_id=job.id,
            team_id=str(job.team_id),
            progress_pct=0,
            progress_stage="canceled",
            status="CANCELED",
        )

        logger.info(f"Job {job.id} marked as CANCELED")

    def _check_cancellation(self, job_id: str) -> bool:
        """Check if job has been canceled."""
        from poly_redis.client import get_redis_client

        redis = get_redis_client()
        cancel_key = f"cancel:{job_id}"
        return redis.exists(cancel_key)

    def _cleanup_temp_files(self, audio_path: Optional[str]) -> None:
        """Clean up temporary audio files."""
        if audio_path and os.path.exists(audio_path):
            try:
                os.unlink(audio_path)
                logger.debug(f"Cleaned up temp file: {audio_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")
