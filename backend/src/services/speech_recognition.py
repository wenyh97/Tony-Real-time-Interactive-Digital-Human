"""后端通用的语音识别服务封装。"""

from __future__ import annotations

import logging
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger("app.services.speech_recognition")


class SpeechRecognitionError(RuntimeError):
    """语音识别处理失败时抛出的异常。"""


@dataclass(slots=True)
class SpeechRecognitionResult:
    """语音识别服务返回的结构化结果。"""

    text: str
    confidence: float
    processing_time_ms: int
    language: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SpeechRecognitionService:
    """可注入的语音识别服务，用于抽象真实识别引擎。

    默认实现提供一个轻量级的回退识别逻辑，便于在本地或测试环境中
    模拟真实的延迟与文本结果；生产环境可通过 ``transcriber`` 参数注入
    实际的语音识别模型。"""

    def __init__(
        self,
        *,
        transcriber: Optional[Callable[[bytes, str], Tuple[str, float]]] = None,
        latency_budget_ms: int = 200,
        min_audio_bytes: int = 256,
    ) -> None:
        self._transcriber = transcriber
        self.latency_budget_ms = latency_budget_ms
        self.min_audio_bytes = min_audio_bytes

    def transcribe(
        self,
        audio_bytes: bytes,
        *,
        language: str = "zh-CN",
        conversation_id: Optional[int] = None,
    ) -> SpeechRecognitionResult:
        """将音频数据转写为文本。"""

        if not audio_bytes:
            logger.error(
                "Received empty audio payload", extra={"conversation_id": conversation_id}
            )
            raise SpeechRecognitionError("Audio payload must not be empty.")

        if len(audio_bytes) < self.min_audio_bytes:
            logger.error(
                "Audio payload too short",
                extra={
                    "conversation_id": conversation_id,
                    "payload_bytes": len(audio_bytes),
                    "required_bytes": self.min_audio_bytes,
                },
            )
            raise SpeechRecognitionError("Audio payload is too short to process.")

        start = time.perf_counter()
        try:
            if self._transcriber:
                text, confidence = self._transcriber(audio_bytes, language)
            else:
                text, confidence = self._fallback_transcribe(audio_bytes)
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.exception("Transcription backend failed", exc_info=exc)
            raise SpeechRecognitionError("Failed to transcribe audio chunk.") from exc

        processing_time_ms = int((time.perf_counter() - start) * 1000)
        if processing_time_ms > self.latency_budget_ms:
            logger.warning(
                "Transcription exceeded latency budget",
                extra={
                    "conversation_id": conversation_id,
                    "latency_ms": processing_time_ms,
                    "budget_ms": self.latency_budget_ms,
                },
            )

        metadata: Dict[str, Any] = {
            "input_bytes": len(audio_bytes),
            "conversation_id": conversation_id,
            "latency_budget_ms": self.latency_budget_ms,
        }

        if not text.strip():
            logger.info(
                "No discernible speech detected", extra={"conversation_id": conversation_id}
            )
            text = "未检测到有效语音"
            confidence = min(confidence, 0.25)

        return SpeechRecognitionResult(
            text=text,
            confidence=self._clamp_confidence(confidence),
            processing_time_ms=processing_time_ms,
            language=language,
            metadata=metadata,
        )

    def _fallback_transcribe(self, audio_bytes: bytes) -> Tuple[str, float]:
        """基础回退逻辑：通过能量与分布生成可预测文本。"""

        # 通过平均偏移量模拟能量水平
        center = 128
        deviations = [abs(value - center) for value in audio_bytes]
        activity_score = sum(deviations) / len(deviations)

        if activity_score < 5:
            return "", 0.2

        dominant_values = [value for value, _ in Counter(audio_bytes).most_common(4)]
        pseudo_vocab = [
            "语音",
            "识别",
            "处理中",
            "请稍候",
            "完成",
            "同步",
            "数据",
            "响应",
        ]
        words = [pseudo_vocab[val % len(pseudo_vocab)] for val in dominant_values]
        transcript = "".join(words)[:32]
        confidence = 0.4 + min(activity_score / 40.0, 0.6)
        return transcript or "识别结果", confidence

    @staticmethod
    def _clamp_confidence(confidence: float) -> float:
        """将置信度限定在 [0, 1]。"""

        return max(0.0, min(confidence, 1.0))
