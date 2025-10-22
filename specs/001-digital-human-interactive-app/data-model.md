# Data Model: 数字人实时交互应用

**Created**: 2025-10-22
**Purpose**: 定义应用核心实体的数据结构和关系

## 核心实体定义

### User (用户)
用户账户和配置信息的核心实体。

**Fields**:
- `id`: Integer, Primary Key, 用户唯一标识
- `username`: String(50), Unique, 用户名
- `email`: String(100), Unique, 邮箱地址
- `password_hash`: String(255), 密码哈希值
- `created_at`: DateTime, 账户创建时间
- `updated_at`: DateTime, 最后更新时间
- `is_active`: Boolean, 账户状态
- `preferences`: JSON, 用户偏好设置

**Validation Rules**:
- username: 3-50字符，字母数字下划线
- email: 有效邮箱格式
- password: 最少8位，包含大小写字母和数字

**Relationships**:
- One-to-Many: User -> Conversation
- One-to-Many: User -> VoiceProfile
- One-to-Many: User -> AppearanceProfile

### DigitalHuman (数字人)
数字人的3D模型和动画配置。

**Fields**:
- `id`: Integer, Primary Key
- `user_id`: Integer, Foreign Key -> User.id
- `name`: String(100), 数字人名称
- `model_url`: String(500), 3D模型文件URL
- `texture_url`: String(500), 纹理贴图URL
- `animation_config`: JSON, 动画参数配置
- `appearance_params`: JSON, 外观自定义参数
- `is_default`: Boolean, 是否为默认形象
- `created_at`: DateTime, 创建时间
- `updated_at`: DateTime, 更新时间

**Validation Rules**:
- name: 1-100字符
- model_url, texture_url: 有效URL格式
- animation_config: 有效JSON格式

**State Transitions**:
- Created -> Processing -> Ready -> Active
- Active -> Updating -> Ready

### Conversation (对话会话)
用户与数字人的对话会话管理。

**Fields**:
- `id`: Integer, Primary Key
- `user_id`: Integer, Foreign Key -> User.id
- `digital_human_id`: Integer, Foreign Key -> DigitalHuman.id
- `title`: String(200), 对话标题
- `started_at`: DateTime, 会话开始时间
- `ended_at`: DateTime, 会话结束时间（可为空）
- `is_active`: Boolean, 会话是否活跃
- `message_count`: Integer, 消息总数
- `total_duration`: Integer, 总对话时长（秒）

**Validation Rules**:
- title: 1-200字符
- started_at <= ended_at (如果ended_at不为空)
- message_count >= 0

**Relationships**:
- One-to-Many: Conversation -> Message

### Message (消息)
单条对话消息的详细信息。

**Fields**:
- `id`: Integer, Primary Key
- `conversation_id`: Integer, Foreign Key -> Conversation.id
- `sender_type`: Enum('user', 'digital_human'), 发送者类型
- `content_type`: Enum('text', 'audio'), 内容类型
- `text_content`: Text, 文本内容
- `audio_url`: String(500), 音频文件URL（如果是语音消息）
- `audio_duration`: Integer, 音频时长（毫秒）
- `processing_time`: Integer, 处理时间（毫秒）
- `created_at`: DateTime, 消息创建时间
- `metadata`: JSON, 额外元数据（情感分析、置信度等）

**Validation Rules**:
- content_type为'audio'时，audio_url不能为空
- content_type为'text'时，text_content不能为空
- audio_duration >= 0
- processing_time >= 0

### VoiceProfile (音色配置)
数字人的语音合成配置和自定义音色。

**Fields**:
- `id`: Integer, Primary Key
- `user_id`: Integer, Foreign Key -> User.id
- `name`: String(100), 音色名称
- `type`: Enum('preset', 'custom'), 音色类型
- `voice_params`: JSON, 语音合成参数
- `sample_audio_url`: String(500), 音色样本URL
- `training_status`: Enum('pending', 'training', 'ready', 'failed'), 训练状态
- `similarity_score`: Float, 相似度评分（0-1）
- `is_active`: Boolean, 是否启用
- `created_at`: DateTime, 创建时间
- `updated_at`: DateTime, 更新时间

**Validation Rules**:
- name: 1-100字符
- similarity_score: 0.0-1.0范围
- type为'custom'时，sample_audio_url不能为空

**State Transitions**:
- pending -> training -> ready
- pending -> training -> failed

### AppearanceProfile (外观配置)
数字人的外观自定义配置。

**Fields**:
- `id`: Integer, Primary Key
- `user_id`: Integer, Foreign Key -> User.id
- `name`: String(100), 外观配置名称
- `source_type`: Enum('upload', 'preset', 'generated'), 来源类型
- `source_image_url`: String(500), 源图片URL
- `model_params`: JSON, 3D模型参数
- `facial_features`: JSON, 面部特征参数
- `clothing_style`: JSON, 服装风格配置
- `generation_status`: Enum('pending', 'processing', 'ready', 'failed'), 生成状态
- `is_active`: Boolean, 是否启用
- `created_at`: DateTime, 创建时间
- `updated_at`: DateTime, 更新时间

**Validation Rules**:
- name: 1-100字符
- source_type为'upload'时，source_image_url不能为空
- model_params, facial_features: 有效JSON格式

## 实体关系图

```
User (1) -----> (n) Conversation
 |                      |
 |                      v
 |              (1) -----> (n) Message
 |
 |---> (n) VoiceProfile
 |---> (n) AppearanceProfile
 |---> (n) DigitalHuman
```

## 数据库索引策略

### 主要索引
- User: `email`, `username`
- Conversation: `user_id`, `started_at`, `is_active`
- Message: `conversation_id`, `created_at`
- VoiceProfile: `user_id`, `is_active`
- AppearanceProfile: `user_id`, `is_active`
- DigitalHuman: `user_id`, `is_default`

### 复合索引
- Message: `(conversation_id, created_at)` - 按对话时间排序
- Conversation: `(user_id, is_active, started_at)` - 用户活跃对话查询

## 数据完整性约束

### 外键约束
- 所有外键关系启用级联更新
- 删除用户时级联删除相关数据（除非有业务要求保留）

### Check约束
- 时间字段：ended_at >= started_at
- 评分字段：similarity_score BETWEEN 0.0 AND 1.0
- 计数字段：message_count >= 0

## 性能考虑

### 分区策略
- Message表按created_at月份分区（历史数据归档）
- Conversation表按年份分区

### 缓存策略
- 用户活跃对话缓存（Redis）
- 数字人配置缓存（频繁访问）
- 音色配置缓存（语音合成时使用）