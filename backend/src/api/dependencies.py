"""FastAPI 依赖注入提供者 (清理重复与修正导入路径)。"""

from __future__ import annotations

from functools import lru_cache

from services.speech_recognition import SpeechRecognitionService
from services.text_generation import TextGenerationService
from services.voice_synthesis import VoiceSynthesisService
from services.avatar_generation import AvatarGenerationService


@lru_cache(maxsize=1)
def get_speech_recognition_service() -> SpeechRecognitionService:
    return SpeechRecognitionService()


@lru_cache(maxsize=1)
def get_text_generation_service() -> TextGenerationService:
    return TextGenerationService()


@lru_cache(maxsize=1)
def get_voice_synthesis_service() -> VoiceSynthesisService:
    return VoiceSynthesisService()


@lru_cache(maxsize=1)
def get_avatar_generation_service() -> AvatarGenerationService:
    return AvatarGenerationService()
