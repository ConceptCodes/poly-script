from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.middleware.request_context import RequestContextMiddleware
from src.middleware.rate_limit import RateLimiter, RateLimitMiddleware


def setup_middleware(app: FastAPI) -> None:
    settings = get_settings()

    # Request context (request_id, team_id)
    app.add_middleware(RequestContextMiddleware)

    # Rate limiting
    limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)
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
