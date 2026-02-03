from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_PATH: str = "./storage"
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()
