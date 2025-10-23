"""端到端交互性能基准测试 (T029)。

目标: 语音识别+文本生成+语音合成整体耗时 < 1200ms (示例阈值, 可根据实际调整)
"""
from time import perf_counter
from services.speech_recognition import SpeechRecognitionService
from services.text_generation import TextGenerationService
from services.voice_synthesis import VoiceSynthesisService

# 构造模拟音频 (足够长以触发识别逻辑)
audio_sample = bytes([1, 128, 255, 64]) * 6000

THRESHOLD_MS = 1200


def test_end_to_end_interaction_latency():
    speech_service = SpeechRecognitionService(latency_budget_ms=400)
    text_service = TextGenerationService()
    voice_service = VoiceSynthesisService()

    start_all = perf_counter()

    speech_result = speech_service.transcribe(audio_sample, language="zh-CN", conversation_id=777)
    text_result = text_service.generate_reply(speech_result.text, conversation_id=777)
    voice_result = voice_service.synthesize(text_result.reply)

    total_ms = int((perf_counter() - start_all) * 1000)

    # 断言单项性能和总性能
    assert speech_result.processing_time_ms <= 400
    assert text_result.processing_time_ms <= 500
    assert voice_result.processing_time_ms <= 500
    assert total_ms <= THRESHOLD_MS, f"端到端耗时 {total_ms}ms 超过阈值 {THRESHOLD_MS}ms"

    # 基本正确性
    assert speech_result.text.strip() != ""
    assert text_result.reply.startswith("数字人回复：")
    assert voice_result.audio_url.endswith(".wav")
