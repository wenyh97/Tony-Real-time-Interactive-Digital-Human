"""后端测试通用的 pytest fixture 定义。"""

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# 确保从仓库根目录执行测试时可以导入 backend/src 模块
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from api.dependencies import get_speech_recognition_service
from api.app import create_app
from services.speech_recognition import SpeechRecognitionService
from services.text_generation import TextGenerationService
@pytest.fixture(scope="session")
def text_generation_service() -> TextGenerationService:
    """提供共享的文本生成服务实例。"""
    return TextGenerationService()


@pytest.fixture(scope="session")
def speech_service() -> SpeechRecognitionService:
    """提供共享的语音识别服务实例，减少重复构造。"""
    return SpeechRecognitionService()


@pytest.fixture()
def app(speech_service: SpeechRecognitionService) -> FastAPI:
    """构建带语音路由的 FastAPI 应用，供集成测试使用。"""

    application = create_app()
    application.dependency_overrides[get_speech_recognition_service] = lambda: speech_service
    return application


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    """返回绑定上述应用的 FastAPI TestClient。"""

    return TestClient(app)
