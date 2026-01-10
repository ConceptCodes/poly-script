from typing import Optional
from sqlalchemy.orm import Session

from poly_db.models.transcripts import Transcript
from poly_db.repositories.transcripts import TranscriptRepository
from poly_stt import TranscriptionResult


class TranscriptService:
    
    def __init__(self, db_session: Session):
        self.session = db_session
        self.repo = TranscriptRepository(db_session)
    
    def save_transcript(
        self,
        job_id: str,
        result: TranscriptionResult,
    ) -> Transcript:
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
        
        return self.repo.create(transcript)
    
    def get_transcript(
        self,
        transcript_id: str,
    ) -> Optional[Transcript]:
        return self.repo.get(transcript_id)
    
    def get_transcript_by_job(
        self,
        job_id: str,
    ) -> Optional[Transcript]:
        return self.repo.get_by_job_id(job_id)