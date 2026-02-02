from __future__ import annotations

import time
from typing import Dict, Tuple, Optional

from jose import JWTError, jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from src.config import get_settings


class RateLimiter:
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self._buckets: Dict[str, Tuple[float, int]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        window_start, count = self._buckets.get(key, (now, 0))

        if now - window_start >= 60:
            self._buckets[key] = (now, 1)
            return True

        if count >= self.max_per_minute:
            return False

        self._buckets[key] = (window_start, count + 1)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limiter: RateLimiter):
        super().__init__(app)
        self.limiter = limiter
        self.settings = get_settings()

    def _key_from_request(self, request: Request) -> Optional[str]:
        team_id = request.headers.get("X-Team-Id")
        if team_id:
            return f"team:{team_id}"

        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ", 1)[1].strip()
            try:
                payload = jwt.decode(token, self.settings.JWT_SECRET, algorithms=["HS256"])
                if "sub" in payload:
                    return f"user:{payload['sub']}"
            except JWTError:
                pass

        client = request.client
        if client:
            return f"ip:{client.host}"
        return None

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith("/v1"):
            return await call_next(request)
        if request.url.path.startswith("/v1/health"):
            return await call_next(request)

        key = self._key_from_request(request)
        if key and not self.limiter.allow(key):
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limited", "message": "Rate limit exceeded"}},
            )

        return await call_next(request)
