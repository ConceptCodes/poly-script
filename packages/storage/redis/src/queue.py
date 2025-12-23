import json
import uuid
from typing import Optional, Any, Dict
from redis import Redis
from pydantic import BaseModel, Field

class TranscriptionWorkItem(BaseModel):
    job_id: uuid.UUID
    audio_ref: str
    requested_language: Optional[str] = None
    engine: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)

class TranscriptionQueue:
    QUEUE_KEY = "transcription:queue"

    def __init__(self, client: Redis):
        self.client = client

    def enqueue(self, item: TranscriptionWorkItem) -> int:
        return self.client.rpush(self.QUEUE_KEY, item.model_dump_json())

    def dequeue(self, timeout: int = 0) -> Optional[TranscriptionWorkItem]:
        # blpop returns (key, value)
        result = self.client.blpop(self.QUEUE_KEY, timeout=timeout)
        if result:
            _, data = result
            return TranscriptionWorkItem.model_validate_json(data)
        return None

    def peek(self) -> Optional[TranscriptionWorkItem]:
        data = self.client.lindex(self.QUEUE_KEY, 0)
        if data:
            return TranscriptionWorkItem.model_validate_json(data)
        return None

    def size(self) -> int:
        return self.client.llen(self.QUEUE_KEY)
