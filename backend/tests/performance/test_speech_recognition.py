"""语音识别服务的性能测试用例。"""

import pytest

from services.speech_recognition import (
    SpeechRecognitionError,
    SpeechRecognitionService,
)


# 人为构造的音频字节流，用于触发回退识别逻辑
audio_sample = bytes([1, 128, 255, 64]) * 4000


def test_transcribe_completes_within_latency_budget():
    service = SpeechRecognitionService(latency_budget_ms=200)
    result = service.transcribe(audio_sample, language="zh-CN", conversation_id=42)

    assert result.text.strip() != ""
    assert 0.0 <= result.confidence <= 1.0
    assert result.processing_time_ms <= 200
    assert result.language == "zh-CN"
    assert result.metadata["conversation_id"] == 42
    assert result.metadata["input_bytes"] == len(audio_sample)


def test_transcribe_rejects_empty_audio():
    service = SpeechRecognitionService()

    # 空音频应触发业务异常
    with pytest.raises(SpeechRecognitionError):
        service.transcribe(b"", conversation_id=1)
