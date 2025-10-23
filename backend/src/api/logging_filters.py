"""日志过滤与脱敏工具 - T030。"""

from __future__ import annotations

import logging
from typing import Iterable

SENSITIVE_KEYS: set[str] = {"audio_data", "text_content"}


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        if isinstance(record.args, dict):
            for k in list(record.args.keys()):
                if k in SENSITIVE_KEYS:
                    record.args[k] = "<redacted>"
        return True


def register_sensitive_filter(logger_names: Iterable[str]) -> None:
    for name in logger_names:
        logger = logging.getLogger(name)
        logger.addFilter(SensitiveDataFilter())
