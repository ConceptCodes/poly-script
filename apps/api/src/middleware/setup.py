import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.middleware.rate_limit import RateLimitMiddleware, RedisRateLimiter
from src.middleware.request_context import RequestContextMiddleware


def setup_middleware(app: FastAPI) -> None:
    settings = get_settings()

    # Request context (request_id, team_id)
    app.add_middleware(RequestContextMiddleware)

    # Rate limiting (Redis-based with per-plan limits)
    # Skip under pytest so endpoint tests don't collide through shared counters.
    if "pytest" not in sys.modules and "PYTEST_CURRENT_TEST" not in os.environ:
        limiter = RedisRateLimiter()
        app.add_middleware(RateLimitMiddleware, limiter=limiter)

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add other middlewares as needed (e.g., logging, rate limiting)
