"""
音色配置管理模型
路径：backend/src/models/voice_profile.py
"""
from typing import Optional

class VoiceProfile:
    """
    用户音色配置模型
    """
    def __init__(self, user_id: str, voice_id: str, sample_url: str, status: str = "created"):
        self.user_id = user_id
        self.voice_id = voice_id
        self.sample_url = sample_url
        self.status = status
        # 可扩展：音色参数、训练状态等

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "voice_id": self.voice_id,
            "sample_url": self.sample_url,
            "status": self.status
        }
