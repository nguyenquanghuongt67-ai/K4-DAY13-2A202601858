from __future__ import annotations

import re
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

# Upstream callers may pass their own id, but we only trust it if it is a short,
# log-safe token; anything else gets replaced so every record stays greppable.
SAFE_CORRELATION_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")


def new_correlation_id() -> str:
    return f"req-{uuid.uuid4().hex[:8]}"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Each request starts from a clean context so ids never leak across requests
        # that happen to be served by the same worker task.
        clear_contextvars()

        inbound = (request.headers.get("x-request-id") or "").strip()
        correlation_id = inbound if SAFE_CORRELATION_ID.match(inbound) else new_correlation_id()

        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{elapsed_ms:.1f}"

        return response
