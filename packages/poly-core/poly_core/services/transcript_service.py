from typing import Optional
from sqlalchemy.orm import Session

try:
    from poly_db.repositories.transcripts import TranscriptRepository
    from poly_db.models.transcripts import Transcript
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Error importing DB models: {e}")
    MODELS_AVAILABLE = False
    Transcript = None
    TranscriptRepository = None

try:
    from poly_stt import TranscriptionResult
    STT_AVAILABLE = True
except ImportError as e:
    print(f"Error importing STT: {e}")
    STT_AVAILABLE = False
    TranscriptionResult = None


class TranscriptService:
    
    def __init__(self, db_session: Session):
        if not MODELS_AVAILABLE:
            raise RuntimeError("DB models not available")
        self.session = db_session
        self.repo = TranscriptRepository(db_session)
    
    def save_transcript(
        self,
        job_id: str,
        result: Optional[TranscriptionResult],
    ) -> Optional[Transcript]:
        if not STT_AVAILABLE or result is None:
            print(f"Mock: Would save transcript for job {job_id}")
            return None
        
        if not MODELS_AVAILABLE:
            raise RuntimeError("DB models not available")
        
        segments_json: list[dict[str, object]] = [
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
        
        return self.repo.create(transcript)
    
    def get_transcript(
        self,
        transcript_id: str,
    ) -> Optional[Transcript]:
        if not MODELS_AVAILABLE:
            print(f"Mock: Would get transcript {transcript_id}")
            return None
        return self.repo.get(transcript_id)
    
    def get_transcript_by_job(
        self,
        job_id: str,
    ) -> Optional[Transcript]:
        if not MODELS_AVAILABLE:
            print(f"Mock: Would get transcript by job {job_id}")
            return None
        return self.repo.get_by_job_id(job_id)