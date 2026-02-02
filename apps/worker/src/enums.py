from typing import Optional
from enum import StrEnum


class ProgressStage(StrEnum):
    STARTING = "starting"
    DOWNLOADING = "downloading"
    DECODING = "decoding"
    TRANSCRIBING = "transcribing"
    TRANSLATING = "translating"
    FORMATTING = "formatting"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class WorkerStatus(StrEnum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"