"""API 路由通用工具。"""

from __future__ import annotations

from datetime import datetime, timezone


"""API 通用工具: 时间、错误和响应构造 (T028 重构)。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional


def utc_now_iso() -> str:
    """返回当前 UTC 时间的 ISO8601 字符串 (不含微秒简化日志)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_error(
    *,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """构造统一错误响应载荷。

    结构:
    {
      "error": {"code": <CODE>, "message": <MSG>, "details": {...}}
    }
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "timestamp": utc_now_iso(),
        }
    }


def ensure_max_length(value: str, *, max_length: int, field_name: str) -> str:
    """裁剪过长字符串并返回 (保留前端展示友好)。"""
    if len(value) <= max_length:
        return value
    return value[: max_length - 3] + "..."
