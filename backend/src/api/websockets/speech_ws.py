"""语音识别流式 WebSocket 处理逻辑。"""

from __future__ import annotations

import base64
import binascii
import logging
from api.utils import utc_now_iso, ensure_max_length
from typing import Any, Dict

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from api.dependencies import get_speech_recognition_service
from services.speech_recognition import (
    SpeechRecognitionError,
    SpeechRecognitionService,
)

router = APIRouter()
logger = logging.getLogger("app.api.websockets.speech")


# 直接使用 utc_now_iso()


async def _send_error(
    websocket: WebSocket,
    *,
    code: str,
    message: str,
    recoverable: bool = True,
    details: Dict[str, Any] | None = None,
) -> None:
    """向客户端发送错误消息，统一格式。"""

    await websocket.send_json(
        {
            "type": "error",
            "data": {
                "error_code": code,
                "message": message,
                "details": details or {},
                "recoverable": recoverable,
            },
                "timestamp": utc_now_iso(),
            "id": f"error_{code.lower()}",
        }
    )


@router.websocket("/ws/conversations/{conversation_id}")
async def speech_stream(
    websocket: WebSocket,
    conversation_id: int,
    service: SpeechRecognitionService = Depends(get_speech_recognition_service),
) -> None:
    """处理实时语音识别的 WebSocket 数据流。"""

    await websocket.accept()
    await websocket.send_json(
        {
            "type": "connection_ack",
            "data": {"conversation_id": conversation_id},
                "timestamp": utc_now_iso(),
            "id": f"ack_{conversation_id}",
        }
    )

    audio_buffer = bytearray()

    try:
        while True:
            message = await websocket.receive_json()
            message_type = message.get("type")

            if message_type == "ping":
                # 心跳保持连接
                await websocket.send_json(
                    {
                        "type": "pong",
                        "data": {},
                            "timestamp": utc_now_iso(),
                        "id": message.get("id", "pong"),
                    }
                )
                continue

            if message_type == "start_recording":
                # 客户端开始发送音频，重置缓冲
                audio_buffer.clear()
                await websocket.send_json(
                    {
                        "type": "status_update",
                        "data": {
                            "status": "listening",
                            "message": "开始语音识别",
                        },
                            "timestamp": utc_now_iso(),
                        "id": "status_listening",
                    }
                )
                continue

            if message_type == "stop_recording":
                # 客户端显式结束录制
                audio_buffer.clear()
                await websocket.send_json(
                    {
                        "type": "status_update",
                        "data": {
                            "status": "idle",
                            "message": "语音识别结束",
                        },
                            "timestamp": utc_now_iso(),
                        "id": "status_idle",
                    }
                )
                continue

            if message_type != "audio_chunk":
                logger.warning(
                    "Unsupported WebSocket message type", extra={"type": message_type}
                )
                await _send_error(
                    websocket,
                    code="UNSUPPORTED_MESSAGE",
                    message=f"Unsupported message type: {message_type}",
                    details={"received_type": message_type},
                )
                continue

            chunk = message.get("data") or {}
            base64_audio = chunk.get("audio_data")
            if not base64_audio:
                await _send_error(
                    websocket,
                    code="EMPTY_AUDIO_CHUNK",
                    message="Audio chunk is missing audio_data payload.",
                )
                continue

            try:
                audio_bytes = base64.b64decode(base64_audio)
            except (binascii.Error, ValueError) as exc:
                logger.warning("Failed to decode audio chunk", exc_info=exc)
                await _send_error(
                    websocket,
                    code="INVALID_AUDIO_CHUNK",
                    message="Audio chunk could not be decoded.",
                    details={"error": ensure_max_length(str(exc), max_length=80, field_name="decode_error")},
                )
                continue

            audio_buffer.extend(audio_bytes)

            try:
                result = service.transcribe(
                    bytes(audio_buffer), conversation_id=conversation_id
                )
            except SpeechRecognitionError as exc:
                logger.warning(
                    "Speech recognition error", extra={"conversation_id": conversation_id}
                )
                await _send_error(
                    websocket,
                    code="TRANSCRIPTION_FAILED",
                    message=ensure_max_length(str(exc), max_length=120, field_name="transcription_error"),
                )
                audio_buffer.clear()
                continue

            # 将识别结果实时回传给客户端
            await websocket.send_json(
                {
                    "type": "speech_recognition",
                    "data": {
                        "text": result.text,
                        "confidence": result.confidence,
                        "processing_time": result.processing_time_ms,
                        "chunk_id": chunk.get("chunk_id"),
                        "is_final": bool(chunk.get("is_final")),
                    },
                        "timestamp": utc_now_iso(),
                    "id": f"recognition_{chunk.get('chunk_id', 'na')}",
                }
            )

            if chunk.get("is_final"):
                audio_buffer.clear()

    except WebSocketDisconnect:
        logger.info(
            "Speech WebSocket disconnected", extra={"conversation_id": conversation_id}
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected WebSocket error", exc_info=exc)
        await _send_error(
            websocket,
            code="INTERNAL_ERROR",
            message="Unexpected error while processing speech stream.",
            recoverable=False,
        )
        await websocket.close(code=1011)
