"""语音识别相关的 HTTP 接口定义。"""

from __future__ import annotations

import logging
import uuid
from api.utils import utc_now_iso, build_error, ensure_max_length
from api.schemas import SpeechRecognizeResponse
from api.message_payload import build_message_payload
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from api.dependencies import get_speech_recognition_service
from services.speech_recognition import (
    SpeechRecognitionError,
    SpeechRecognitionService,
)

router = APIRouter(prefix="/api/v1", tags=["Speech"])
logger = logging.getLogger("app.api.routes.speech")


# 移除旧 shim：直接使用 utc_now_iso()


@router.post("/speech/recognize", response_model=SpeechRecognizeResponse)
async def recognize_speech(
    conversation_id: int = Form(...),
    audio_file: UploadFile = File(...),
    service: SpeechRecognitionService = Depends(get_speech_recognition_service),
) -> Dict[str, Any]:
    """处理语音识别上传请求。"""

    audio_bytes = await audio_file.read()
    if not audio_bytes:
        logger.warning("Uploaded audio file is empty", extra={"conversation_id": conversation_id})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=build_error(code="EMPTY_AUDIO", message="Audio file must not be empty."))

    try:
        result = service.transcribe(
            audio_bytes,
            language="zh-CN",
            conversation_id=conversation_id,
        )
    except SpeechRecognitionError as exc:
        logger.warning("Speech recognition failed", extra={"conversation_id": conversation_id, "reason": str(exc)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=build_error(code="TRANSCRIPTION_FAILED", message=ensure_max_length(str(exc), max_length=120, field_name="error"))) from exc

    logger.info(
        "Speech recognition succeeded",
        extra={
            "conversation_id": conversation_id,
            "processing_time_ms": result.processing_time_ms,
            "confidence": result.confidence,
        },
    )

    message_payload = build_message_payload(
        conversation_id=conversation_id,
        sender_type="user",
        content_type="audio",
        text_content=result.text,
        processing_time=result.processing_time_ms,
        metadata={"language": result.language, "confidence": result.confidence},
    )

    return SpeechRecognizeResponse(
        text=result.text,
        confidence=result.confidence,
        processing_time=result.processing_time_ms,
        message=message_payload,
    )
