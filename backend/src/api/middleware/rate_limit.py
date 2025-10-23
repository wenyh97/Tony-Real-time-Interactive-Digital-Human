"""简易令牌桶速率限制中间件 (内存版)。"""

from __future__ import annotations

import time
from collections import deque
from typing import Deque, Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, Deque[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        q = self._requests.setdefault(key, deque())
        while q and now - q[0] > self.window_seconds:
            q.popleft()
        if len(q) >= self.max_requests:
            return False
        q.append(now)
        return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60, key_strategy: str = "ip") -> None:  # noqa: D401
        super().__init__(app)
        self._limiter = InMemoryRateLimiter(max_requests=max_requests, window_seconds=window_seconds)
        self.key_strategy = key_strategy  # ip | ip_path

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        client_ip = request.client.host if request.client else "unknown"
        if self.key_strategy == "ip_path":
            key = f"ip:{client_ip}:path:{request.url.path}"
        else:
            key = f"ip:{client_ip}"
        if not self._limiter.allow(key):
            resp = JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please slow down.",
                        "retry_after_seconds": self._limiter.window_seconds,
                        "scope": self.key_strategy,
                    }
                },
            )
            resp.headers["Retry-After"] = str(self._limiter.window_seconds)
            return resp
        return await call_next(request)
