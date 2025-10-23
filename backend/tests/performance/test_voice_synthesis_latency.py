"""语音合成服务性能基准 (T029)。"""

from services.voice_synthesis import VoiceSynthesisService


def test_voice_synthesis_within_latency_budget():
    service = VoiceSynthesisService()
    result = service.synthesize("测试语音合成性能", voice_profile_id=None)
    # 目标: <500ms
    assert result.processing_time_ms <= 500
    assert result.audio_url.endswith(".wav")