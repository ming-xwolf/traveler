# 基于GenAI的旅游攻略生成器

## 🌟 项目简介

这是一个基于人工智能的智能旅游攻略生成器，用户只需提供目的地、天数等基本信息，系统将自动生成专业、详细、个性化的旅游攻略。

### ✨ 核心特性

- 🤖 **多AI模型支持**：集成Ollama、DeepSeek、阿里云百炼多种大语言模型
- 🗺️ **智能地理位置**：集成百度地图API，自动获取准确的位置和路线信息
- 📝 **专业模板**：基于成熟的旅游攻略模板，生成结构化内容
- 📱 **响应式界面**：现代化Vue.js前端，支持多设备访问
- ⚡ **实时生成**：WebSocket实时推送生成进度
- 📄 **多格式导出**：支持Markdown、HTML、PDF格式导出

### 🎯 主要功能

1. **智能攻略生成**
   - 根据用户偏好生成个性化行程
   - 自动规划每日详细安排
   - 智能推荐景点、餐厅、住宿

2. **地理位置服务**
   - 精确的地址和坐标信息
   - 智能路线规划和距离计算
   - 实时交通状况查询

3. **内容管理**
   - 攻略保存和编辑
   - 分享和协作功能
   - 历史记录管理

## 🏗️ 系统架构

```
Frontend (Vue.js 3 + TypeScript)
    ↓
API Gateway (Nginx)
    ↓
Backend Services (FastAPI + LangChain)
    ↓
AI Models (Ollama/DeepSeek/阿里云百炼) + Baidu Maps API
    ↓
Database (PostgreSQL) + Cache (Redis) + Storage (MinIO)
```

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Node.js 18+ (本地开发)
- Python 3.9+ (本地开发)

### 一键启动

```bash
# 1. 克隆项目
git clone <repository-url>
cd traveler-ai

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的API密钥

# 3. 启动所有服务
docker-compose up -d

# 4. 初始化数据库
docker-compose exec backend alembic upgrade head

# 5. 下载AI模型（首次运行）
docker-compose exec ollama ollama pull llama2
```

### 访问应用

- 🌐 **前端应用**: http://localhost:3000
- 📊 **API文档**: http://localhost:8000/docs
- 🔧 **管理面板**: http://localhost:5555 (Celery Flower)
- 💾 **文件存储**: http://localhost:9001 (MinIO Console)

## 🔧 配置说明

### 环境变量配置

创建 `.env` 文件并配置以下变量：

```env
# AI服务配置
DEEPSEEK_API_KEY=your_deepseek_api_key
BAILIAN_API_KEY=your_bailian_api_key

# 百度地图API
BAIDU_MAP_API_KEY=your_baidu_map_api_key

# 安全配置
SECRET_KEY=your_secret_key_here

# 数据库配置（开发环境使用默认值）
DATABASE_URL=postgresql://postgres:password@postgres:5432/traveler
REDIS_URL=redis://redis:6379
```

### AI模型配置

#### Ollama本地模型

```bash
# 安装常用模型
docker-compose exec ollama ollama pull llama2
docker-compose exec ollama ollama pull qwen:7b
docker-compose exec ollama ollama pull deepseek-coder
```

#### 商业模型API

- **DeepSeek**: 访问 [DeepSeek官网](https://www.deepseek.com) 获取API密钥
- **阿里云百炼**: 访问 [阿里云百炼平台](https://bailian.console.aliyun.com) 获取API密钥

## 📖 使用指南

### 1. 创建旅游攻略

1. 访问前端应用主页
2. 点击"创建新攻略"
3. 填写基本信息：
   - 目的地
   - 旅游天数
   - 人数
   - 出发日期
   - 预算类型
   - 旅游偏好
4. 选择AI模型
5. 点击"生成攻略"

### 2. 查看生成进度

生成过程中可以实时查看：
- 当前生成步骤
- 完成进度
- 预计剩余时间

### 3. 编辑和导出

- 查看生成的攻略内容
- 在线编辑修改
- 导出为Markdown/HTML/PDF
- 分享给朋友

## 🛠️ 开发指南

### 本地开发环境

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 代码规范

#### 后端代码规范

```bash
# 代码格式化
black app/

# 代码检查
flake8 app/

# 类型检查
mypy app/
```

#### 前端代码规范

```bash
# 代码检查和格式化
npm run lint

# 类型检查
npm run type-check
```

### 测试

#### 后端测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_travel_plan.py

# 测试覆盖率
pytest --cov=app tests/
```

#### 前端测试

```bash
# 单元测试
npm run test:unit

# E2E测试
npm run test:e2e
```

## 🌍 API文档

### 核心API端点

#### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/profile` - 获取用户信息

#### 攻略管理
- `POST /api/v1/travel-plans` - 创建攻略项目
- `GET /api/v1/travel-plans` - 获取攻略列表
- `GET /api/v1/travel-plans/{id}` - 获取攻略详情
- `POST /api/v1/travel-plans/{id}/generate` - 生成攻略内容

#### 地理位置
- `GET /api/v1/locations/search` - 搜索地点
- `POST /api/v1/locations/route` - 路线规划

完整API文档请访问：http://localhost:8000/docs

## 🚀 部署指南

### 生产环境部署

```bash
# 1. 准备生产环境配置
cp docker-compose.prod.yml.example docker-compose.prod.yml

# 2. 设置生产环境变量
cp .env.prod.example .env.prod

# 3. 构建和启动
docker-compose -f docker-compose.prod.yml up -d

# 4. 设置Nginx反向代理和SSL证书
```

### 性能优化

- 启用Redis缓存
- 配置CDN加速
- 数据库连接池优化
- AI模型响应缓存

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式化
refactor: 代码重构
test: 测试用例
chore: 构建工具或辅助工具变动
```

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 故障排除

### 常见问题

#### 1. Ollama模型下载失败
```bash
# 检查网络连接
docker-compose exec ollama ollama list

# 手动下载模型
docker-compose exec ollama ollama pull llama2
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose ps postgres

# 查看日志
docker-compose logs postgres
```

#### 3. AI服务调用失败
- 检查API密钥配置
- 确认网络连接
- 查看服务日志

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
```

## 📞 支持与联系

- 📧 邮箱: support@traveler-ai.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-org/traveler-ai/issues)
- 📖 文档: [项目文档](https://docs.traveler-ai.com)

---

**Made with ❤️ by Traveler AI Team** 