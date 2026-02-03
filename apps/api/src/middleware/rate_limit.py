from __future__ import annotations

import time
from typing import TYPE_CHECKING

from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from poly_redis.client import get_redis_client
from src.config import get_settings

if TYPE_CHECKING:
    from fastapi import Request
    from redis import Redis


# Per-plan rate limits (requests per minute)
PLAN_RATE_LIMITS = {
    "FREE": 30,
    "STANDARD": 60,
    "PRO": 120,
}

DEFAULT_RATE_LIMIT = 60  # Default for unknown plans/IP-based


class RedisRateLimiter:
    """Redis-based rate limiter using sorted sets for sliding window algorithm.

    This provides:
    - Proper distributed rate limiting across API workers
    - Sliding window for smooth rate limiting
    - Automatic cleanup of old entries
    """

    def __init__(self, redis_client: Redis | None = None):
        self.redis = redis_client or get_redis_client()

    def _get_key(self, key: str) -> str:
        """Get the Redis key for rate limiting."""
        return f"ratelimit:{key}"

    def allow(
        self, key: str, max_requests: int = DEFAULT_RATE_LIMIT, window_seconds: int = 60
    ) -> tuple[bool, int, int]:
        """Check if a request is allowed and record it.

        Uses Redis sorted sets for efficient sliding window rate limiting.

        Args:
            key: The rate limit key (e.g., "team:uuid" or "user:uuid" or "ip:x.x.x.x")
            max_requests: Maximum requests allowed in the window
            window_seconds: The time window in seconds

        Returns:
            Tuple of (allowed, remaining, reset_time)
            - allowed: True if request is within rate limit
            - remaining: Number of requests remaining in window
            - reset_time: Unix timestamp when the window resets
        """
        now = time.time()
        window_start = now - window_seconds
        rate_key = self._get_key(key)

        # Use a pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Remove old entries outside the window
        pipe.zremrangebyscore(rate_key, 0, window_start)

        # Count current entries in window
        pipe.zcard(rate_key)

        # Add current request with timestamp as score
        pipe.zadd(rate_key, {f"{now}": now})

        # Set TTL on the key to auto-cleanup
        pipe.expire(rate_key, window_seconds + 1)

        results = pipe.execute()
        current_count = results[1]

        if current_count >= max_requests:
            # Rate limit exceeded - rollback the add
            self.redis.zrem(rate_key, f"{now}")
            # Get the oldest entry to calculate reset time
            oldest = self.redis.zrange(rate_key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1] + window_seconds) if oldest else int(now + window_seconds)
            remaining = 0
            allowed = False
        else:
            remaining = max_requests - current_count - 1
            reset_time = int(now + window_seconds)
            allowed = True

        return allowed, remaining, reset_time

    def get_usage(self, key: str, window_seconds: int = 60) -> int:
        """Get current request count for a key."""
        now = time.time()
        window_start = now - window_seconds
        rate_key = self._get_key(key)
        return self.redis.zcount(rate_key, window_start, now)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: RedisRateLimiter | None = None):
        super().__init__(app)
        self.limiter = limiter or RedisRateLimiter()
        self.settings = get_settings()

    def _get_rate_limit_for_plan(self, plan: str | None) -> int:
        """Get rate limit based on plan."""
        if plan and plan in PLAN_RATE_LIMITS:
            return PLAN_RATE_LIMITS[plan]
        return PLAN_RATE_LIMITS["FREE"]  # Conservative default for unknown

    def _key_from_request(self, request: Request) -> tuple[str | None, str | None]:
        """Extract rate limit key and optional plan from request.

        Returns:
            Tuple of (key, plan)
            - key: The rate limit key
            - plan: The team plan (if available from header)
        """
        team_id = request.headers.get("X-Team-Id")
        plan = request.headers.get("X-Team-Plan")

        if team_id:
            return f"team:{team_id}", plan

        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ", 1)[1].strip()
            try:
                payload = jwt.decode(token, self.settings.JWT_SECRET, algorithms=["HS256"])
                if "sub" in payload:
                    return f"user:{payload['sub']}", plan
            except JWTError:
                pass

        client = request.client
        if client:
            return f"ip:{client.host}", plan
        return None, plan

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for non-API endpoints and health checks
        if not request.url.path.startswith("/v1"):
            return await call_next(request)
        if request.url.path.startswith("/v1/health"):
            return await call_next(request)

        key, plan = self._key_from_request(request)

        if key:
            max_requests = self._get_rate_limit_for_plan(plan)
            allowed, remaining, reset_time = self.limiter.allow(key, max_requests=max_requests)

            # Add rate limit headers to request for potential use downstream
            request.state.rate_limit_remaining = remaining
            request.state.rate_limit_reset = reset_time
            request.state.rate_limit_max = max_requests

            if not allowed:
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "rate_limited",
                            "message": "Rate limit exceeded. Please try again later.",
                        }
                    },
                )
                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = "0"
                response.headers["X-RateLimit-Reset"] = str(reset_time)
                response.headers["Retry-After"] = str(reset_time - int(time.time()))
                return response

        response = await call_next(request)

        # Add rate limit headers to successful responses
        if key and hasattr(request.state, "rate_limit_remaining"):
            response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_max)
            response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
            response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)

        return response
