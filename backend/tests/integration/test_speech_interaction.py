"""覆盖语音识别 HTTP 接口与 WebSocket 流程的集成测试。"""

import base64
from datetime import datetime, timezone


def test_speech_recognition_http_and_websocket_flow(client):
    # 构造待上传的音频字节流
    audio_bytes = bytes([1, 2, 3, 4]) * 4000

    # 校验 HTTP 语音识别接口
    response = client.post(
        "/api/v1/speech/recognize",
        files={"audio_file": ("sample.wav", audio_bytes, "audio/wav")},
        data={"conversation_id": "1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["text"]
    assert 0.0 <= payload["confidence"] <= 1.0
    assert payload["processing_time"] <= 200
    assert payload["message"]["conversation_id"] == 1

    # 校验 WebSocket 音频分片实时识别流程
    with client.websocket_connect("/ws/conversations/1") as websocket:
        ack_message = websocket.receive_json()
        assert ack_message["type"] == "connection_ack"

        websocket.send_json(
            {
                "type": "audio_chunk",
                "data": {
                    "audio_data": base64.b64encode(audio_bytes).decode("ascii"),
                    "chunk_id": 1,
                    "is_final": True,
                    "sample_rate": 16000,
                    "format": "wav",
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "id": "chunk_1",
            }
        )

        recognition_message = websocket.receive_json()
        assert recognition_message["type"] == "speech_recognition"
        assert recognition_message["data"]["chunk_id"] == 1
        assert recognition_message["data"]["is_final"] is True
        assert recognition_message["data"]["text"]
        assert 0.0 <= recognition_message["data"]["confidence"] <= 1.0
