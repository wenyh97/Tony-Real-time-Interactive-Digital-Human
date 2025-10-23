"""文本对话流程集成测试。"""
import pytest
from services.text_generation import TextGenerationService

def test_generate_reply_and_synthesize(text_generation_service):
    """文本生成与语音合成集成测试。"""
    text = "你好，数字人！今天天气怎么样？"
    result = text_generation_service.generate_reply(text, conversation_id=1)
    from services.voice_synthesis import VoiceSynthesisService
    voice_service = VoiceSynthesisService()
    voice_result = voice_service.synthesize(result.reply)
    assert result.reply.startswith("数字人回复：")
    assert result.confidence >= 0.9
    assert result.processing_time_ms < 100
    assert result.metadata["conversation_id"] == 1
    assert result.metadata["input_length"] == len(text)
    assert voice_result.audio_url.endswith(".wav")
    assert voice_result.duration > 0
