"""文本消息相关的 HTTP 接口定义。"""

from __future__ import annotations

import logging
import uuid
from api.utils import utc_now_iso, build_error, ensure_max_length
from api.schemas import TextMessageResponse
from api.message_payload import build_message_payload
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Form

from api.dependencies import get_text_generation_service, get_voice_synthesis_service
from services.text_generation import TextGenerationService
from services.voice_synthesis import VoiceSynthesisService

router = APIRouter(prefix="/api/v1", tags=["Messages"])
logger = logging.getLogger("app.api.routes.messages")


# 直接使用 utc_now_iso()


@router.post("/conversations/{conversation_id}/messages", response_model=TextMessageResponse)
async def send_text_message(
    conversation_id: int,
    text_content: str = Form(...),
    text_service: TextGenerationService = Depends(get_text_generation_service),
    voice_service: VoiceSynthesisService = Depends(get_voice_synthesis_service),
) -> Dict[str, Any]:
    """处理文本消息发送请求，并集成语音合成。"""
    if not text_content.strip():
        logger.warning("文本内容为空", extra={"conversation_id": conversation_id})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=build_error(code="EMPTY_TEXT", message="文本内容不能为空。"))
    # 生成数字人文本回复
    result = text_service.generate_reply(text_content, conversation_id=conversation_id)
    # 将回复文本转为语音
    voice_result = voice_service.synthesize(result.reply)
    message_payload = build_message_payload(
        conversation_id=conversation_id,
        sender_type="user",
        content_type="text",
        text_content=text_content,
        audio_url=voice_result.audio_url,
        audio_duration=voice_result.duration,
        processing_time=result.processing_time_ms + voice_result.processing_time_ms,
        metadata={
            "reply": result.reply,
            "confidence": result.confidence,
            "voice_synthesis": voice_result.metadata,
        },
    )
    return TextMessageResponse(
        reply=result.reply,
        confidence=result.confidence,
        audio_url=voice_result.audio_url,
        audio_duration=voice_result.duration,
        processing_time=result.processing_time_ms + voice_result.processing_time_ms,
        message=message_payload,
    )
