from fastapi import Request
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

request_context: ContextVar[dict | None] = ContextVar("request_context", default=None)


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        request_token = request_context.set({"request_token": str(uuid.uuid4())})
        try:
            response = await call_next(request)
        finally:
            request_context.reset(request_token)
        return response
