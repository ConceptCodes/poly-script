from contextlib import contextmanager
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/polyscript"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return DatabaseSettings()


def get_engine():
    settings = get_settings()
    return create_engine(settings.DATABASE_URL)


def get_session_factory():
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Raw generator for database sessions, suitable for FastAPI Depends."""
    factory = get_session_factory()
    with factory() as session:
        yield session


@contextmanager
def get_db_session() -> Session:
    """Context manager for database sessions, for manual 'with' usage."""
    factory = get_session_factory()
    with factory() as session:
        yield session
