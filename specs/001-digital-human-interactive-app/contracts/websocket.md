# WebSocket Protocol: 实时语音交互

**Version**: 1.0.0
**Created**: 2025-10-22

## 连接说明

### 连接端点
```
ws://localhost:8000/ws/conversations/{conversation_id}
```

### 认证
WebSocket连接需要在连接建立时传递JWT令牌：
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/conversations/123', [], {
  headers: {
    'Authorization': 'Bearer <jwt_token>'
  }
});
```

## 消息协议

### 消息格式
所有消息都使用JSON格式，包含以下基本结构：
```json
{
  "type": "message_type",
  "data": {},
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "unique_message_id"
}
```

## 客户端发送消息类型

### 1. 音频数据流 (audio_chunk)
实时语音识别时发送音频数据块。

```json
{
  "type": "audio_chunk",
  "data": {
    "audio_data": "base64_encoded_audio_data",
    "chunk_id": 1,
    "is_final": false,
    "sample_rate": 16000,
    "format": "wav"
  },
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "chunk_1"
}
```

**字段说明**:
- `audio_data`: Base64编码的音频数据
- `chunk_id`: 音频块序号
- `is_final`: 是否为最后一块音频数据
- `sample_rate`: 采样率 (默认16000Hz)
- `format`: 音频格式 (wav/mp3/webm)

### 2. 开始录音 (start_recording)
通知服务器开始语音识别会话。

```json
{
  "type": "start_recording",
  "data": {
    "language": "zh-CN",
    "voice_profile_id": 1
  },
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "start_1"
}
```

### 3. 停止录音 (stop_recording)
通知服务器停止语音识别会话。

```json
{
  "type": "stop_recording",
  "data": {},
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "stop_1"
}
```

### 4. 文本消息 (text_message)
直接发送文本消息。

```json
{
  "type": "text_message",
  "data": {
    "text": "用户输入的文本内容",
    "voice_profile_id": 1
  },
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "text_1"
}
```

### 5. 心跳检测 (ping)
保持连接活跃。

```json
{
  "type": "ping",
  "data": {},
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "ping_1"
}
```

## 服务器发送消息类型

### 1. 连接确认 (connection_ack)
WebSocket连接建立后的确认消息。

```json
{
  "type": "connection_ack",
  "data": {
    "conversation_id": 123,
    "user_id": 456,
    "digital_human": {
      "id": 789,
      "name": "数字助手",
      "model_url": "https://storage.azure.com/models/avatar.glb"
    }
  },
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "ack_1"
}
```

### 2. 语音识别结果 (speech_recognition)
实时语音识别的中间和最终结果。

```json
{
  "type": "speech_recognition",
  "data": {
    "text": "识别出的文本内容",
    "is_final": true,
    "confidence": 0.95,
    "processing_time": 150,
    "chunk_id": 5
  },
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "recognition_1"
}
```

**字段说明**:
- `is_final`: 是否为最终结果（false为中间结果）
- `confidence`: 识别置信度 (0-1)
- `processing_time`: 处理时间（毫秒）

### 3. 数字人回复 (digital_human_response)
数字人的文本和语音回复。

```json
{
  "type": "digital_human_response",
  "data": {
    "message_id": 12345,
    "text": "数字人的回复内容",
    "audio_url": "https://storage.azure.com/audio/response_123.wav",
    "audio_duration": 3500,
    "emotions": {
      "primary": "neutral",
      "intensity": 0.7
    },
    "lip_sync_data": {
      "visemes": [
        {"time": 0.0, "viseme": "sil"},
        {"time": 0.5, "viseme": "AA"},
        {"time": 1.0, "viseme": "N"}
      ]
    },
    "processing_time": 450
  },
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "response_1"
}
```

**字段说明**:
- `lip_sync_data`: 口型同步数据
- `emotions`: 情感表达参数
- `visemes`: 音素时间轴数据

### 4. 状态更新 (status_update)
系统状态变化通知。

```json
{
  "type": "status_update",
  "data": {
    "status": "processing",
    "message": "正在生成回复...",
    "progress": 0.6,
    "eta": 2000
  },
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "status_1"
}
```

**状态类型**:
- `idle`: 空闲状态
- `listening`: 正在监听语音
- `processing`: 正在处理请求
- `speaking`: 数字人正在说话
- `error`: 错误状态

### 5. 错误消息 (error)
处理过程中的错误通知。

```json
{
  "type": "error",
  "data": {
    "error_code": "SPEECH_RECOGNITION_FAILED",
    "message": "语音识别失败，请重试",
    "details": {
      "reason": "audio_quality_too_low",
      "suggestion": "请在安静环境中重新录音"
    },
    "recoverable": true
  },
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "error_1"
}
```

### 6. 心跳回复 (pong)
响应客户端的ping消息。

```json
{
  "type": "pong",
  "data": {},
  "timestamp": "2025-10-22T14:39:00Z",
  "id": "pong_1"
}
```

## 连接生命周期

### 1. 连接建立
```
Client -> Server: WebSocket连接请求 (带JWT认证)
Server -> Client: connection_ack
```

### 2. 语音交互流程
```
Client -> Server: start_recording
Client -> Server: audio_chunk (多次)
Server -> Client: speech_recognition (中间结果)
Client -> Server: stop_recording
Server -> Client: speech_recognition (最终结果)
Server -> Client: status_update (processing)
Server -> Client: digital_human_response
```

### 3. 文本交互流程
```
Client -> Server: text_message
Server -> Client: status_update (processing)
Server -> Client: digital_human_response
```

### 4. 连接维护
```
Client -> Server: ping (每30秒)
Server -> Client: pong
```

### 5. 连接关闭
```
Client -> Server: WebSocket close
Server: 清理会话资源
```

## 错误处理

### 客户端错误
- 音频格式不支持
- 消息格式错误
- 认证失败

### 服务器错误
- 语音识别服务不可用
- AI模型处理超时
- 存储服务错误

### 重连机制
客户端应实现指数退避重连：
```javascript
const reconnectDelays = [1000, 2000, 4000, 8000, 16000]; // 毫秒
```

## 性能优化

### 音频压缩
- 推荐使用16kHz采样率
- 支持Opus编码压缩
- 音频块大小建议100-200ms

### 消息缓存
- 客户端应缓存最近的消息
- 支持断线重连后的消息同步

### 连接复用
- 一个对话会话使用一个WebSocket连接
- 支持多路复用减少连接数量