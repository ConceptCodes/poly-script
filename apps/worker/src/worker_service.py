import json
import threading
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Try to import dependencies, with graceful fallback
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis not available. Install with: pip install redis")

try:
    from poly_storage.redis.queue import TranscriptionQueue, TranscriptionWorkItem
    QUEUE_AVAILABLE = True
except ImportError:
    QUEUE_AVAILABLE = False
    print("Warning: Queue package not available")

try:
    from poly_stt import EngineRegistry
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False
    print("Warning: STT package not available")

try:
    from poly_core.services.transcript import TranscriptService
    TRANSCRIPT_SERVICE_AVAILABLE = True
except ImportError:
    TRANSCRIPT_SERVICE_AVAILABLE = False
    print("Warning: Transcript service not available")


class SimpleWorker:
    
    def __init__(self):
        self._shutdown = threading.Event()
        self._setup_redis()
        self._setup_queue()
    
    def _setup_redis(self):
        if REDIS_AVAILABLE:
            self._redis_client = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)
        else:
            self._redis_client = None
            print("Redis not available - worker will run in mock mode")
    
    def _setup_queue(self):
        if QUEUE_AVAILABLE and REDIS_AVAILABLE:
            self._queue = TranscriptionQueue(self._redis_client)
        else:
            self._queue = None
            print("Queue not available - worker will run in mock mode")
    
    def start(self):
        threading.Thread(target=self._run, daemon=True).start()
        print("[Worker] Started transcription worker thread")
    
    def stop(self):
        self._shutdown.set()
        print("[Worker] Shutdown signal received")
    
    def _run(self):
        while not self._shutdown.is_set():
            try:
                work_item = self._get_work_item()
                if work_item:
                    self._process_job(work_item)
            except Exception as e:
                print(f"[Worker] Error in main loop: {e}")
                time.sleep(1)
    
    def _get_work_item(self):
        if self._queue:
            return self._queue.dequeue(timeout=1)
        return None
    
    def _process_job(self, work_item: Optional[Dict[str, Any]]):
        if not work_item:
            return
        
        job_id = work_item.get("job_id", "unknown")
        print(f"[Worker] Processing job {job_id}")
        
        try:
            self._publish_progress(job_id, 0, "downloading")
            time.sleep(1)
            
            if STT_AVAILABLE:
                result = self._transcribe_with_stt(work_item)
            else:
                result = self._mock_transcription(work_item)
            
            if TRANSCRIPT_SERVICE_AVAILABLE:
                self._save_transcript(job_id, result)
            else:
                print(f"Mock: Would save transcript for job {job_id}")
            
            self._publish_progress(job_id, 100, "completed")
            print(f"[Worker] Completed job {job_id}")
            
        except Exception as e:
            print(f"[Worker] Job {job_id} failed: {e}")
            self._publish_progress(job_id, 0, "failed")
    
    def _transcribe_with_stt(self, work_item: Dict[str, Any]):
        if not STT_AVAILABLE:
            raise RuntimeError("STT not available")
        
        self._publish_progress(work_item["job_id"], 20, "transcribing")
        time.sleep(1)
        
        engine = EngineRegistry.get(work_item.get("engine"))
        
        audio_path = work_item.get("audio_ref", "")
        if not audio_path or not audio_path.startswith(("/", "http")):
            audio_path = "/tmp/mock_audio.mp3"
        
        result = engine.transcribe(
            audio_path=audio_path,
            language=work_item.get("requested_language"),
            timestamps=work_item.get("options", {}).get("timestamps", True),
            diarization=work_item.get("options", {}).get("diarization", False),
        )
        
        return result
    
    def _mock_transcription(self, work_item: Dict[str, Any]):
        self._publish_progress(work_item["job_id"], 20, "transcribing")
        time.sleep(2)
        
        from poly_stt import TranscriptionResult, Segment
        
        return TranscriptionResult(
            text=f"Mock transcription for {work_item.get('job_id', 'unknown')}",
            language="en-US",
            segments=[
                Segment(start_ms=0, end_ms=2000, text="Hello world"),
                Segment(start_ms=2000, end_ms=4000, text="This is a test"),
            ],
            engine="mock-engine",
        )
    
    def _save_transcript(self, job_id: str, result):
        if not TRANSCRIPT_SERVICE_AVAILABLE:
            print(f"Mock: Would save transcript for job {job_id}")
            return
        
        from poly_db.database import get_db_session
        
        with get_db_session() as session:
            transcript_service = TranscriptService(session)
            transcript_service.save_transcript(job_id, result)
    
    def _publish_progress(self, job_id: str, progress: int, stage: str):
        if not REDIS_AVAILABLE:
            print(f"Mock progress: {job_id} - {progress}% - {stage}")
            return
        
        message = {
            "job_id": job_id,
            "status": "RUNNING" if progress < 100 else "SUCCEEDED",
            "progress_pct": progress,
            "progress_stage": stage,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self._redis_client.publish(f"job:{job_id}:progress", json.dumps(message))