import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter: 100 requests/60 seconds per client IP.
    For production use Redis-backed rate limiting instead.
    """

    LIMIT = 100
    WINDOW_SECONDS = 60

    def __init__(self, app):
        super().__init__(app)
        self._counters: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.WINDOW_SECONDS

        # Prune timestamps older than the window
        self._counters[client_ip] = [
            t for t in self._counters[client_ip] if t > window_start
        ]

        if len(self._counters[client_ip]) >= self.LIMIT:
            return JSONResponse(
                status_code=429,
                content={"error": "rate_limit_exceeded", "detail": "Too many requests. Please slow down."},
            )

        self._counters[client_ip].append(now)
        return await call_next(request)
