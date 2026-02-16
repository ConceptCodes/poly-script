import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from poly_db.models.transcript_edits import TranscriptEdit
from poly_db.models.transcription_jobs import TranscriptionJob
from poly_db.models.transcripts import Transcript
from poly_db.repositories.transcripts import TranscriptEditRepository, TranscriptRepository

if TYPE_CHECKING:
    from poly_stt import TranscriptionResult
else:
    TranscriptionResult = Any


class TranscriptService:
    def __init__(self, db_session: Session):
        self.session = db_session
        self.repo = TranscriptRepository(db_session)
        self.edit_repo = TranscriptEditRepository(db_session)

    def save_transcript(
        self,
        job_id: str,
        result: TranscriptionResult,
    ) -> dict[str, Any]:
        """Save a new transcript from STT result."""
        segments_json = [
            {
                "start_ms": seg.start_ms,
                "end_ms": seg.end_ms,
                "text": seg.text,
                "speaker": seg.speaker,
            }
            for seg in result.segments
        ]

        transcript = Transcript(
            job_id=job_id,
            text=result.text,
            language=result.language,
            segments=segments_json,
            engine_version=result.engine,
        )

        created = self.repo.create(transcript)
        return {
            "id": created.id,
            "job_id": created.job_id,
            "text": created.text,
            "language": created.language,
            "segments": created.segments,
            "engine_version": created.engine_version,
            "created_at": created.created_at,
            "updated_at": created.updated_at,
        }

    def get_transcript(
        self,
        transcript_id: str,
    ) -> dict[str, Any] | None:
        """Get transcript by ID."""
        transcript = self.repo.get(transcript_id)
        if transcript is None:
            return None
        return {
            "id": transcript.id,
            "job_id": transcript.job_id,
            "text": transcript.text,
            "language": transcript.language,
            "segments": transcript.segments,
            "engine_version": transcript.engine_version,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    def get_transcript_by_job(
        self,
        job_id: str,
    ) -> dict[str, Any] | None:
        """Get transcript by job ID."""
        transcript = self.repo.get_by_job_id(job_id)
        if transcript is None:
            return None
        return {
            "id": transcript.id,
            "job_id": transcript.job_id,
            "text": transcript.text,
            "language": transcript.language,
            "segments": transcript.segments,
            "engine_version": transcript.engine_version,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    def get_transcript_with_team_check(
        self,
        transcript_id: str,
        team_id: str,
    ) -> dict[str, Any] | None:
        """
        Get transcript with team isolation check.

        Args:
            transcript_id: The transcript UUID
            team_id: The team UUID to verify access for

        Returns:
            Transcript dictionary if found and team has access, None otherwise
        """
        transcript = self.repo.get(transcript_id)

        if not transcript:
            return None

        # Verify team access via job
        if transcript.job and transcript.job.team_id != uuid.UUID(team_id):
            return None

        return {
            "id": transcript.id,
            "job_id": transcript.job_id,
            "text": transcript.text,
            "language": transcript.language,
            "segments": transcript.segments,
            "engine_version": transcript.engine_version,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    def update_full_text(
        self,
        transcript_id: str,
        user_id: str,
        new_text: str,
    ) -> dict[str, Any]:
        """
        Update the full text of a transcript and log the edit.

        Args:
            transcript_id: The transcript UUID
            user_id: The user making the edit
            new_text: The new full transcript text

        Returns:
            Updated Transcript as dictionary

        Raises:
            ValueError: If transcript not found
        """
        transcript = self.repo.get(transcript_id)
        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")

        # Store previous state for edit history
        previous_text = transcript.text

        # Update transcript
        transcript.text = new_text
        self.session.flush()

        # Log edit
        edit = TranscriptEdit(
            transcript_id=transcript_id,
            user_id=uuid.UUID(user_id) if user_id else None,
            previous_text=previous_text,
            new_text=new_text,
            previous_segments=transcript.segments,
            new_segments=transcript.segments,
        )
        self.edit_repo.create(edit)
        self.session.flush()

        return {
            "id": transcript.id,
            "job_id": transcript.job_id,
            "text": transcript.text,
            "language": transcript.language,
            "segments": transcript.segments,
            "engine_version": transcript.engine_version,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    def update_segment(
        self,
        transcript_id: str,
        segment_id: int,
        user_id: str,
        new_text: str,
    ) -> dict[str, Any]:
        """
        Update a single segment of a transcript and log the edit.

        Args:
            transcript_id: The transcript UUID
            segment_id: The index of the segment to update
            user_id: The user making the edit
            new_text: The new segment text

        Returns:
            Updated Transcript as dictionary

        Raises:
            ValueError: If transcript not found or segment_id invalid
        """
        transcript = self.repo.get(transcript_id)
        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")

        segments = transcript.segments
        if segment_id < 0 or segment_id >= len(segments):
            raise ValueError(f"Invalid segment_id: {segment_id}")

        # Store previous state
        previous_segments = list(segments)
        previous_text = segments[segment_id].get("text", "")

        # Update segment
        segments[segment_id]["text"] = new_text
        transcript.segments = segments
        self.session.flush()

        # Log edit
        edit = TranscriptEdit(
            transcript_id=transcript_id,
            user_id=uuid.UUID(user_id) if user_id else None,
            previous_text=previous_text,
            new_text=new_text,
            previous_segments={"0": previous_segments},
            new_segments={"0": segments},
        )
        self.edit_repo.create(edit)
        self.session.flush()

        return {
            "id": transcript.id,
            "job_id": transcript.job_id,
            "text": transcript.text,
            "language": transcript.language,
            "segments": transcript.segments,
            "engine_version": transcript.engine_version,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    def get_edit_history(
        self,
        team_id: str,
        transcript_id: str,
    ) -> list[TranscriptEdit]:
        """
        Get the edit history for a transcript.

        Args:
            transcript_id: The transcript UUID

        Returns:
            List of TranscriptEdit records, ordered by creation date descending
        """
        return self.edit_repo.get_history_by_transcript_id(
            uuid.UUID(team_id),
            uuid.UUID(transcript_id),
        )

    def revert_to_original(
        self,
        team_id: str,
        transcript_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """
        Revert transcript to its original state (first version).

        Args:
            team_id: The team UUID
            transcript_id: The transcript UUID
            user_id: The user making the revert

        Returns:
            Reverted Transcript as dictionary

        Raises:
            ValueError: If transcript not found or no edits exist
        """
        transcript = self.repo.get(transcript_id)
        if not transcript:
            raise ValueError(f"Transcript {transcript_id} not found")

        # Get the earliest edit to restore from
        edits = self.edit_repo.get_history_by_transcript_id(
            uuid.UUID(team_id),
            uuid.UUID(transcript_id),
        )

        if edits:
            # Revert to the state before the first edit
            original_text = edits[-1].previous_text if edits[-1].previous_text else transcript.text
            original_segments = (
                edits[-1].previous_segments if edits[-1].previous_segments else transcript.segments
            )
        else:
            # No edits to revert from
            raise ValueError(f"No edits to revert for transcript {transcript_id}")

        # Store current state before revert
        previous_text = transcript.text
        previous_segments = transcript.segments

        # Revert
        transcript.text = original_text
        transcript.segments = original_segments
        self.session.flush()

        # Log the revert as an edit
        edit = TranscriptEdit(
            transcript_id=transcript_id,
            user_id=uuid.UUID(user_id) if user_id else None,
            previous_text=previous_text,
            new_text=original_text,
            previous_segments=previous_segments,
            new_segments=original_segments,
        )
        self.edit_repo.create(edit)
        self.session.flush()

        return {
            "id": transcript.id,
            "job_id": transcript.job_id,
            "text": transcript.text,
            "language": transcript.language,
            "segments": transcript.segments,
            "engine_version": transcript.engine_version,
            "created_at": transcript.created_at,
            "updated_at": transcript.updated_at,
        }

    def list_transcripts(
        self,
        team_id: str,
        language: str | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        List transcripts for a team with filtering and pagination.

        Args:
            team_id: The team UUID
            language: Optional language filter
            search: Optional text search in transcript text
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Tuple of (transcripts list as dicts, total count)
        """
        # Build query with joins
        stmt = (
            select(Transcript)
            .join(TranscriptionJob, Transcript.job_id == TranscriptionJob.id)
            .where(TranscriptionJob.team_id == uuid.UUID(team_id))
        )

        if language:
            stmt = stmt.where(Transcript.language == language)

        if search:
            stmt = stmt.where(Transcript.text.ilike(f"%{search}%"))

        # Get total count
        count_stmt = select(Transcript.id).select_from(stmt.subquery())

        def _extract_all(exec_result):
            if hasattr(exec_result, "scalars"):
                return exec_result.scalars().all()
            if hasattr(exec_result, "all"):
                return exec_result.all()
            return list(exec_result)

        total = len(_extract_all(self.session.execute(count_stmt)))

        # Apply pagination
        stmt = stmt.order_by(Transcript.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        transcripts = _extract_all(self.session.execute(stmt))

        return [
            {
                "id": t.id,
                "job_id": t.job_id,
                "text": t.text,
                "language": t.language,
                "segments": t.segments,
                "engine_version": t.engine_version,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
            }
            for t in transcripts
        ], total
