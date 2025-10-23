"""文本生成服务性能基准 (T029)。"""

from services.text_generation import TextGenerationService


def test_text_generation_within_latency_budget():
    service = TextGenerationService()
    result = service.generate_reply("今天天气怎么样？", conversation_id=99)
    # 目标: <500ms
    assert result.processing_time_ms <= 500
    assert result.reply.startswith("数字人回复：")