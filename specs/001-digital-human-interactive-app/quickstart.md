# Quickstart Guide: 数字人实时交互应用

**Created**: 2025-10-22
**Purpose**: 开发环境搭建和基本功能演示指南

## 系统要求

### 软件依赖
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis 6.0+ (可选，用于缓存)
- Git

### 硬件推荐
- RAM: 16GB+ (AI模型加载需要)
- GPU: NVIDIA GTX 1660+ (可选，加速AI推理)
- 存储: 50GB+ 可用空间
- 网络: 稳定互联网连接 (下载AI模型)

## 快速开始 (5分钟设置)

### 1. 克隆项目
```bash
git clone https://github.com/wenyh97/Tony-Real-time-Interactive-Digital-Human.git
cd Tony-Real-time-Interactive-Digital-Human
```

### 2. 环境配置
```bash
# 创建Python虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装Python依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend  
npm install
```

### 3. 数据库设置
```bash
# 启动MySQL (使用Docker)
docker run --name mysql-db -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql:8.0

# 创建数据库
mysql -h localhost -u root -p -e "CREATE DATABASE digital_human_db;"

# 运行数据库迁移
cd ../backend
python manage.py migrate
```

### 4. 环境变量配置
创建 `backend/.env` 文件：
```env
# 数据库配置
DATABASE_URL=mysql://root:password@localhost:3306/digital_human_db

# Azure存储配置
AZURE_STORAGE_ACCOUNT=your_storage_account
AZURE_STORAGE_KEY=your_storage_key
AZURE_CONTAINER_NAME=digital-human-assets

# JWT配置
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_EXPIRE_HOURS=24

# AI模型配置
WHISPER_MODEL_SIZE=base
TTS_MODEL_PATH=./models/tts
LLM_MODEL_PATH=./models/qwen

# 调试模式
DEBUG=true
LOG_LEVEL=INFO
```

### 5. 下载AI模型
```bash
# 下载Whisper模型
python scripts/download_models.py --whisper base

# 下载TTS模型
python scripts/download_models.py --tts coqui

# 下载LLM模型 (可选，文件较大)
python scripts/download_models.py --llm qwen2-7b-instruct
```

### 6. 启动服务
```bash
# 启动后端服务
cd backend
uvicorn main:app --reload --port 8000

# 新终端窗口 - 启动前端开发服务器
cd frontend
npm run dev
```

### 7. 验证安装
访问 http://localhost:3000，您应该看到数字人应用界面。

## 基本功能演示

### 用户注册和登录
1. 打开浏览器访问 http://localhost:3000
2. 点击"注册"按钮创建账户
3. 使用邮箱和密码登录

### 创建第一个数字人
1. 登录后进入"形象定制"页面
2. 选择预设模板或上传照片
3. 等待3D模型生成（约30秒）
4. 保存并设为默认形象

### 语音对话测试
1. 进入"对话"页面
2. 点击"开始对话"按钮
3. 允许浏览器访问麦克风
4. 对着麦克风说"你好"
5. 观察数字人的语音回复和口型同步

### 文本对话测试
1. 在对话界面下方找到文本输入框
2. 输入"今天天气怎么样？"
3. 点击发送按钮
4. 查看数字人的文字和语音回复

## 开发工作流

### 后端开发
```bash
# 进入后端目录
cd backend

# 安装新依赖
pip install package_name
pip freeze > requirements.txt

# 运行测试
pytest tests/

# 代码格式化
black src/
pylint src/

# 启动开发服务器
uvicorn main:app --reload --port 8000
```

### 前端开发
```bash
# 进入前端目录
cd frontend

# 安装新依赖
npm install package_name

# 运行测试
npm test

# 代码格式化
npm run lint
npm run format

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 数据库管理
```bash
# 创建新的数据库迁移
cd backend
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 重置数据库
python manage.py reset_db
```

## API测试

### 使用Postman
1. 导入API文档：`specs/001-digital-human-interactive-app/contracts/api.yaml`
2. 设置环境变量：
   - `base_url`: http://localhost:8000/api/v1
   - `auth_token`: 从登录接口获取

### 使用curl
```bash
# 用户注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 用户登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 获取对话列表 (需要替换TOKEN)
curl -X GET http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## WebSocket测试

### 使用JavaScript
```javascript
// 连接WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/conversations/1');

// 监听连接
ws.onopen = function() {
  console.log('WebSocket连接已建立');
  
  // 发送心跳
  ws.send(JSON.stringify({
    type: 'ping',
    data: {},
    timestamp: new Date().toISOString(),
    id: 'ping_1'
  }));
};

// 监听消息
ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  console.log('收到消息:', message);
};
```

## 故障排除

### 常见问题

**1. 数据库连接失败**
```bash
# 检查MySQL服务状态
docker ps | grep mysql

# 重新启动MySQL
docker restart mysql-db
```

**2. AI模型加载失败**
```bash
# 检查模型文件是否存在
ls -la backend/models/

# 重新下载模型
python scripts/download_models.py --all
```

**3. 音频权限被拒绝**
- 确保浏览器允许麦克风访问
- 使用HTTPS协议（Chrome要求）
- 检查系统音频设备设置

**4. WebSocket连接失败**
```bash
# 检查防火墙设置
sudo ufw allow 8000

# 检查端口占用
netstat -tulpn | grep :8000
```

### 日志查看
```bash
# 后端日志
tail -f backend/logs/app.log

# 前端控制台
# 浏览器开发者工具 -> Console

# 数据库日志
docker logs mysql-db
```

### 性能监控
```bash
# 系统资源监控
htop

# Python进程监控
py-spy top --pid $(pgrep -f uvicorn)

# 内存使用
free -h
```

## 下一步

完成基本设置后，您可以：

1. 阅读 [API文档](./contracts/api.yaml) 了解完整接口
2. 查看 [数据模型](./data-model.md) 理解数据结构  
3. 参考 [WebSocket协议](./contracts/websocket.md) 实现实时功能
4. 运行 `/speckit.tasks` 命令生成详细的开发任务列表

### 推荐开发顺序
1. 完善用户认证和会话管理
2. 实现基础的文本对话功能
3. 集成语音识别和合成
4. 添加3D数字人渲染
5. 实现形象和音色定制
6. 性能优化和用户体验改进

## 技术支持

如果遇到问题，请：
1. 检查上述故障排除指南
2. 查看项目issue列表
3. 参考技术文档和API规范