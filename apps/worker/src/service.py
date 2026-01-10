import json
import threading
import time
from datetime import datetime, timezone
from typing import Optional

from poly_storage.redis.client import get_redis_client
from poly_storage.redis.queue import TranscriptionQueue, TranscriptionWorkItem
from poly_stt import EngineRegistry
from poly_core.services.transcript import TranscriptService


class WorkerService:
    
    def __init__(self):
        self._shutdown = threading.Event()
        self._redis_client = get_redis_client()
        self._queue = TranscriptionQueue(self._redis_client)
    
    def start(self):
        threading.Thread(target=self._run, daemon=True).start()
        print("[Worker] Started transcription worker thread")
    
    def stop(self):
        self._shutdown.set()
        print("[Worker] Shutdown signal received")
    
    def _run(self):
        while not self._shutdown.is_set():
            try:
                work_item = self._queue.dequeue(timeout=1)
                if work_item:
                    self._process_job(work_item)
            except Exception as e:
                print(f"[Worker] Error in main loop: {e}")
                time.sleep(1)
    
    def _process_job(self, work_item: TranscriptionWorkItem):
        try:
            print(f"[Worker] Processing job {work_item.job_id}")
            
            self._publish_progress(work_item.job_id, 0, "downloading")
            
            result = self._transcribe_audio(work_item)
            
            self._save_transcript(work_item.job_id, result)
            
            self._publish_progress(work_item.job_id, 100, "completed")
            
            print(f"[Worker] Completed job {work_item.job_id}")
            
        except Exception as e:
            print(f"[Worker] Job {work_item.job_id} failed: {e}")
            self._publish_progress(work_item.job_id, 0, "failed")
    
    def _transcribe_audio(self, work_item: TranscriptionWorkItem):
        self._publish_progress(work_item.job_id, 20, "transcribing")
        
        engine = EngineRegistry.get(work_item.engine)
        
        result = engine.transcribe(
            audio_path=work_item.audio_ref,
            language=work_item.requested_language,
            timestamps=work_item.options.get("timestamps", True),
            diarization=work_item.options.get("diarization", False),
        )
        
        return result
    
    def _save_transcript(self, job_id: str, result):
        self._publish_progress(job_id, 90, "saving")
        
        from poly_db.database import get_db_session
        
        with get_db_session() as session:
            transcript_service = TranscriptService(session)
            transcript_service.save_transcript(job_id, result)
    
    def _publish_progress(self, job_id: str, progress: int, stage: str):
        message = {
            "job_id": job_id,
            "status": "RUNNING",
            "progress_pct": progress,
            "progress_stage": stage,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self._redis_client.publish(f"job:{job_id}:progress", json.dumps(message))