"""应用工厂：集中注册中间件、路由与安全设置 - T030。"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.error_handlers import register_exception_handlers
from starlette.responses import Response
from api.middleware.rate_limit import RateLimitMiddleware
from api.logging_filters import register_sensitive_filter
from api.routes.speech import router as speech_router
from api.routes.messages import router as messages_router
from api.routes.appearance import router as appearance_router
from api.routes.voice import router as voice_router
from api.websockets.speech_ws import router as speech_ws_router


def create_app(allowed_origins: list[str] | None = None) -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):  # T030 安全头
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "microphone=()")  # 前端显式请求权限
        return response
    app.add_middleware(RateLimitMiddleware, max_requests=120, window_seconds=60)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins or ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(speech_router)
    app.include_router(messages_router)
    app.include_router(appearance_router)
    app.include_router(voice_router)
    app.include_router(speech_ws_router)
    # 注册日志脱敏过滤器 (T030)
    register_sensitive_filter([
        "app.api.routes.speech",
        "app.api.routes.messages",
        "app.api.websockets.speech",
        "app.services.speech_recognition",
    ])
    return app
