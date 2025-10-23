"""请求与响应 Pydantic 模型 (T030)。"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class SpeechRecognizeResponse(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time: int = Field(ge=0)
    message: Optional[Dict[str, Any]] = None  # 保留原有扩展载荷兼容既有前端与测试


class TextMessageResponse(BaseModel):
    reply: str
    confidence: float = Field(ge=0.0, le=1.0)
    audio_url: str
    audio_duration: int = Field(ge=0)
    processing_time: int = Field(ge=0)
    message: Optional[Dict[str, Any]] = None
