from contextlib import asynccontextmanager
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/polyscript"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> DatabaseSettings:
    return DatabaseSettings()


def get_async_engine():
    """Create async SQLAlchemy engine with asyncpg driver."""
    settings = get_settings()
    sync_url = settings.DATABASE_URL
    async_url = sync_url.replace("postgresql://", "postgresql+asyncpg://")
    return create_async_engine(async_url, echo=True, future=True)


def get_async_session_factory():
    """Create async session factory."""
    engine = get_async_engine()
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@asynccontextmanager
async def get_async_db_session() -> AsyncSession:
    """
    Async context manager for database sessions.

    Usage:
        async with get_async_db_session() as session:
            await session.execute(select(User))
    """
    factory = get_async_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
