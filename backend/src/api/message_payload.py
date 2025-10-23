"""统一消息载荷构造工具 - T028。"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from api.utils import utc_now_iso


def build_message_payload(
    *,
    conversation_id: int,
    sender_type: str,
    content_type: str,
    text_content: str,
    processing_time: int,
    audio_url: Optional[str] = None,
    audio_duration: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """构造统一的消息载荷字典。"""
    return {
        "id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "sender_type": sender_type,
        "content_type": content_type,
        "text_content": text_content,
        "audio_url": audio_url,
        "audio_duration": audio_duration,
        "processing_time": processing_time,
        "created_at": utc_now_iso(),
        "metadata": metadata or {},
    }
