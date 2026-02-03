import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from poly_core.logging_context import clear_request_context, set_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        team_id = request.headers.get("X-Team-Id")
        set_request_context(request_id, team_id)

        try:
            response = await call_next(request)
        finally:
            clear_request_context()

        response.headers["X-Request-Id"] = request_id
        return response
