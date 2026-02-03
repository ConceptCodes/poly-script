from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from redis import Redis, from_url


class RedisSettings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return RedisSettings()


def get_redis_client() -> Redis:
    settings = get_settings()
    return from_url(settings.REDIS_URL, decode_responses=True)
