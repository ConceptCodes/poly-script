from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_EXPIRY: str = "24h"
    ADMIN_JWT_SECRET: str
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
    ]

    # Storage
    STORAGE_BACKEND: str = "local"  # local|s3
    STORAGE_PATH: str = "./storage"
    AWS_S3_BUCKET: str | None = None
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None

    # Email
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "noreply@polyscript.io"

    # Application
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: list[str] = ["en", "de", "es", "fr", "jp"]
    MAX_UPLOAD_SIZE_MB: int = 100
    QUEUE_MAX_RETRIES: int = 3
    QUEUE_RETRY_BACKOFF: int = 2

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_ID_STANDARD: str
    STRIPE_PRICE_ID_PRO: str
    CREDIT_PRICE_PER_UPLOAD: int = 100

    # OAuth
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    OAUTH_REDIRECT_URL: str

    # URLs
    APP_URL: str
    ADMIN_URL: str

    # Expiry
    EMAIL_VERIFICATION_EXPIRY: int = 24
    PASSWORD_RESET_EXPIRY: int = 1
    INVITATION_EXPIRY: int = 7

    # Deletion Policy
    DELETION_GRACE_PERIOD_DAYS: int = 30
    ORPHANED_CONTENT_RETENTION_DAYS: int = 90

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()
