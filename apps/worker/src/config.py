import sys
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Get the project root directory (go up from worker/src to project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_PATH: str = "./storage"
    STORAGE_MIN_FREE_BYTES: int = 0
    AWS_S3_BUCKET: str | None = None
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    # STT
    WHISPER_MODEL_SIZE: str = "medium"
    WHISPER_DEVICE: str = "auto"  # auto, cuda, cpu, mps

    # Queue
    QUEUE_MAX_RETRIES: int = 3
    QUEUE_RETRY_BACKOFF: int = 2
    QUEUE_TIMEOUT: int = 30

    # Worker
    WORKER_CONSUMER_THREADS: int = 1
    WORKER_SHUTDOWN_TIMEOUT: int = 30

    # Download validation
    DOWNLOAD_MAX_RETRIES: int = 3
    DOWNLOAD_RETRY_BACKOFF: int = 2
    DOWNLOAD_TIMEOUT_SECONDS: int = 60
    DOWNLOAD_CHUNK_SIZE_BYTES: int = 8192
    DOWNLOAD_MAX_BYTES: int = 0  # 0 disables max size checks

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")


@lru_cache
def get_settings():
    return Settings()
