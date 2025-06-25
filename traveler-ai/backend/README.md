# TravelerAI 后端服务

基于GenAI的智能旅游攻略生成器后端API服务。

## 项目概述

本项目是一个基于FastAPI构建的后端服务，支持多种AI大模型（Ollama、DeepSeek、Qwen），集成百度地图服务，提供智能旅游攻略生成功能。

## 技术栈

- **Web框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+ (异步支持)
- **缓存**: Redis 6+
- **AI服务**: Ollama, DeepSeek, Qwen
- **地图服务**: 百度地图API
- **日志**: Structlog
- **ORM**: SQLAlchemy 2.0+
- **HTTP客户端**: httpx

## 项目结构

```
backend/
├── app/                     # 应用主目录
│   ├── api/                # API路由层
│   │   └── v1/            # API v1版本
│   │       ├── endpoints/ # 具体端点
│   │       └── router.py  # 路由汇总
│   ├── core/              # 核心模块
│   │   ├── config.py      # 配置管理
│   │   ├── database.py    # 数据库连接
│   │   └── redis.py       # Redis连接
│   ├── models/            # 数据模型
│   ├── services/          # 业务服务层
│   ├── utils/             # 工具模块
│   └── main.py            # 应用入口
├── requirements.txt       # Python依赖
├── config.env.example     # 环境变量示例
└── run.py                # 启动脚本
```

## 安装与配置

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 环境配置

复制环境变量示例文件：

```bash
cp config.env.example .env
```

编辑 `.env` 文件，配置以下关键参数：

#### 数据库配置
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/traveler_ai
ASYNC_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/traveler_ai
```

#### Redis配置
```env
REDIS_URL=redis://localhost:6379/0
```

#### AI服务配置
```env
DEFAULT_AI_PROVIDER=ollama

# Ollama (本地部署)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b

# DeepSeek (商业API)
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat

# 阿里云百炼
BAILIAN_API_KEY=your-bailian-api-key
BAILIAN_MODEL=qwen-max
```

#### 百度地图配置
```env
BAIDU_MAP_AK=your-baidu-map-api-key
```

### 3. 数据库初始化

```bash
# 创建数据库（如果不存在）
createdb traveler_ai

# 运行数据库迁移（后续会添加）
# python -m alembic upgrade head
```

## 启动服务

### 开发模式

```bash
python run.py
```

服务将启动在 `http://localhost:8000`

### 生产模式

```bash
# 使用Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或者使用Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API文档

启动服务后，可以访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 核心功能模块

### 1. 旅游攻略生成 (`/api/v1/itinerary`)

- `POST /generate` - 生成旅游攻略
- `GET /progress/{id}` - 查询生成进度
- `GET /validate` - 验证目的地
- `GET /templates` - 获取模板列表
- `GET /examples` - 获取示例
- `GET /stats` - 获取统计信息

### 2. AI服务 (`/api/v1/ai`)

- `GET /providers` - 获取可用AI服务商
- `POST /test` - 测试AI服务商
- `POST /generate` - AI文本生成
- `GET /config` - 获取AI配置

### 3. 地图服务 (`/api/v1/maps`)

- `POST /geocode` - 地理编码
- `POST /reverse-geocode` - 逆地理编码
- `POST /search-places` - 地点搜索
- `GET /place-details/{uid}` - 地点详情
- `POST /directions` - 路线规划
- `GET /weather` - 天气查询
- `GET /ip-location` - IP定位

### 4. 用户认证 (`/api/v1/auth`)

- `POST /login` - 用户登录
- `POST /logout` - 用户登出
- `GET /me` - 获取当前用户信息

### 5. 用户管理 (`/api/v1/users`)

- `GET /profile` - 获取用户档案
- `GET /itineraries` - 获取用户攻略列表

## 配置说明

### AI服务配置

系统支持三种AI服务提供商：

1. **Ollama** (本地部署，免费)
   - 需要本地安装Ollama服务
   - 推荐模型：qwen2.5:7b, llama3.1:8b

2. **DeepSeek** (商业API)
   - 需要申请API密钥
   - 高质量中文支持

3. **Qwen** (阿里云)
   - 需要阿里云账号和API密钥
   - 强大的中文理解能力

### 百度地图配置

- 需要申请百度地图开放平台账号
- 开启以下服务：
  - 地理编码服务
  - 逆地理编码服务  
  - 地点检索服务
  - 路线规划服务
  - 天气服务
  - IP定位服务

### 缓存配置

- AI响应缓存：默认1小时
- 地图数据缓存：默认2小时
- 可通过环境变量调整缓存TTL

## 日志配置

系统使用Structlog进行结构化日志记录：

- 开发环境：彩色控制台输出
- 生产环境：JSON格式输出
- 日志级别：DEBUG/INFO/WARNING/ERROR

## 性能优化

### 1. 数据库优化

- 使用异步SQLAlchemy
- 连接池配置
- 查询优化和索引

### 2. 缓存策略

- Redis缓存热点数据
- AI响应缓存避免重复调用
- 地图数据缓存减少API调用

### 3. 并发处理

- 异步编程模型
- 后台任务处理
- 请求限流和防护

## 错误处理

系统提供统一的错误处理机制：

```json
{
  "error": "ERROR_CODE",
  "message": "用户友好的错误信息",
  "details": "详细错误信息"
}
```

常见错误码：
- `VALIDATION_FAILED` - 参数验证失败
- `GENERATION_FAILED` - 攻略生成失败
- `AI_SERVICE_UNAVAILABLE` - AI服务不可用
- `MAP_SERVICE_ERROR` - 地图服务错误

## 开发指南

### 1. 添加新的API端点

1. 在 `app/api/v1/endpoints/` 下创建新模块
2. 定义Pydantic模型
3. 实现端点函数
4. 在 `app/api/v1/router.py` 中注册路由

### 2. 添加新的服务

1. 在 `app/services/` 下创建服务类
2. 实现业务逻辑
3. 在需要的地方注入服务

### 3. 添加新的数据模型

1. 在 `app/models/` 下定义SQLAlchemy模型
2. 生成数据库迁移
3. 更新模型导入

## 部署说明

### Docker部署

```bash
# 构建镜像
docker build -t traveler-ai-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env traveler-ai-backend
```

### Docker Compose部署

参考项目根目录的 `docker-compose.yml` 文件。

## 监控与日志

- 使用Structlog进行结构化日志
- 支持Prometheus指标收集
- 健康检查端点：`/health`

## 安全考虑

- JWT令牌认证
- 请求参数验证
- SQL注入防护
- XSS攻击防护
- API调用频率限制

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题，请创建Issue或联系开发团队。 