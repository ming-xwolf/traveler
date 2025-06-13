# 新疆伊犁旅游自驾路线地图 - Docker部署

## 📋 项目简介

这是一个基于Docker Compose的新疆伊犁旅游自驾路线地图Web服务，提供交互式的旅游路线展示和每日行程详情查看功能。

## 🚀 快速启动

### 方式一：使用 start.sh 脚本（推荐）

项目提供了便捷的 `start.sh` 脚本来管理 Docker 服务：

```bash
# 一键启动服务（推荐）
./start.sh

# 或者使用其他命令
./start.sh start    # 启动服务
./start.sh stop     # 停止服务
./start.sh restart  # 重启服务
./start.sh status   # 查看状态
./start.sh logs     # 查看日志
./start.sh help     # 显示帮助
```

**首次运行前，请确保脚本有执行权限：**
```bash
chmod +x start.sh
```

### 方式二：使用 Docker Compose

```bash
# 启动服务（指定项目名称）
docker-compose -p travel-plan up -d

# 查看服务状态
docker-compose -p travel-plan ps

# 查看日志
docker-compose -p travel-plan logs -f
```

### 方式三：使用自定义镜像

```bash
# 构建镜像
docker build -t travel-plan .

# 运行容器
docker run -d \
  --name travel-plan \
  -p 8080:80 \
  travel-plan
```

## 🌐 访问地址

启动成功后，可通过以下地址访问：

- **主地图页面**: http://localhost:8080
- **健康检查**: http://localhost:8080/health
- **具体文件**: http://localhost:8080/新疆伊犁旅游自驾路线地图.html

## 📁 项目结构

```
新疆伊犁旅游攻略/
├── docker-compose.yml          # Docker Compose配置
├── Dockerfile                  # 自定义镜像构建文件
├── nginx.conf                  # Nginx配置文件
├── start.sh                    # 便捷启动脚本
├── README.md                   # 部署说明文档
├── 新疆伊犁旅游自驾路线地图.html  # 主地图文件
├── 新疆伊犁旅游概览.html        # 旅游概览
├── 新疆伊犁旅游概览.md          # 旅游概览Markdown
├── 2025-06-27-第一天.html      # 每日行程HTML文件
├── 2025-06-27-第一天.md        # 每日行程Markdown文件
├── ...                         # 其他每日行程文件
└── pictures/                   # 图片资源目录
    ├── 交通/
    ├── 景点/
    └── 美食/
```

## ⚙️ 配置说明

### Docker Compose配置

- **项目名称**: travel-plan
- **端口映射**: 8080:80 (可修改本地端口)
- **容器名称**: travel-plan
- **网络**: travel-network
- **时区**: Asia/Shanghai
- **重启策略**: unless-stopped

### Nginx配置特性

- ✅ 支持中文文件名
- ✅ Gzip压缩优化
- ✅ 静态资源缓存
- ✅ 安全头设置
- ✅ 健康检查端点
- ✅ UTF-8字符集支持

## 🔧 常用命令

### 使用 start.sh 脚本管理（推荐）

```bash
# 启动服务（包含环境检查和服务就绪等待）
./start.sh start
# 或者直接运行
./start.sh

# 停止服务
./start.sh stop

# 重启服务
./start.sh restart

# 查看服务状态
./start.sh status

# 查看实时日志
./start.sh logs

# 显示帮助信息
./start.sh help
```

**start.sh 脚本功能特性：**
- ✅ 自动检查 Docker 环境
- ✅ 端口占用检查
- ✅ 必要文件完整性检查
- ✅ 服务健康状况等待
- ✅ 彩色输出和友好提示
- ✅ 完整的访问信息展示

### 使用 Docker Compose 直接管理

```bash
# 启动服务
docker-compose -p travel-plan up -d

# 停止服务
docker-compose -p travel-plan down

# 重启服务
docker-compose -p travel-plan restart

# 查看服务状态
docker-compose -p travel-plan ps

# 查看实时日志
docker-compose -p travel-plan logs -f travel-plan
```

### 容器管理

```bash
# 进入容器
docker-compose -p travel-plan exec travel-plan sh

# 查看Nginx配置
docker-compose -p travel-plan exec travel-plan nginx -t

# 重载Nginx配置
docker-compose -p travel-plan exec travel-plan nginx -s reload
```

## 🚀 start.sh 脚本详细说明

### 脚本功能介绍

`start.sh` 是项目提供的一站式部署和管理脚本，具有以下特性：

- **智能环境检查**: 自动检查 Docker 和 Docker Compose 是否正确安装
- **端口冲突检测**: 启动前检查端口 8080 是否被占用
- **文件完整性检查**: 确保所有必要文件存在
- **健康状态监控**: 等待服务完全启动并进行健康检查
- **友好的用户界面**: 彩色输出和清晰的状态提示
- **完整的管理功能**: 支持启动、停止、重启、状态查看等操作

### 使用方法

```bash
# 赋予执行权限（首次运行）
chmod +x start.sh

# 一键启动（推荐方式）
./start.sh

# 查看所有可用命令
./start.sh help
```

### 命令参数说明

| 命令 | 功能 | 说明 |
|------|------|------|
| `./start.sh` 或 `./start.sh start` | 启动服务 | 执行完整的启动流程，包括环境检查 |
| `./start.sh stop` | 停止服务 | 优雅停止所有容器 |
| `./start.sh restart` | 重启服务 | 重启容器服务 |
| `./start.sh status` | 查看状态 | 显示当前服务运行状态 |
| `./start.sh logs` | 查看日志 | 实时查看服务日志 |
| `./start.sh help` | 显示帮助 | 显示所有可用命令 |

### 启动流程说明

执行 `./start.sh` 时，脚本会按以下顺序执行：

1. **🔍 环境检查阶段**
   - 检查 Docker 是否安装
   - 检查 Docker Compose 是否安装
   - 检查端口 8080 是否被占用

2. **📋 文件检查阶段**
   - 验证 `新疆伊犁旅游自驾路线地图.html` 文件存在
   - 验证 `docker-compose.yml` 配置文件存在
   - 验证 `nginx.conf` 配置文件存在

3. **🚀 服务启动阶段**
   - 停止可能存在的旧容器
   - 启动新的 Docker 服务
   - 项目名称：`travel-plan`

4. **⏳ 健康检查阶段**
   - 等待服务完全启动（最多 60 秒）
   - 检查健康检查端点：`http://localhost:8080/health`
   - 确保服务正常响应

5. **✅ 完成提示阶段**
   - 显示访问地址和管理命令
   - 提供后续管理建议

### 故障排除

如果脚本执行失败，请检查：

1. **权限问题**
   ```bash
   chmod +x start.sh
   ```

2. **Docker 未安装**
   ```bash
   # macOS
   brew install docker docker-compose
   
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose
   ```

3. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :8080
   
   # 修改 docker-compose.yml 中的端口
   ports:
     - "8081:80"  # 修改为其他端口
   ```

## 📊 监控和日志

### 健康检查

```bash
# 检查服务健康状态
curl http://localhost:8080/health

# 查看容器健康状态
docker-compose -p travel-plan ps
```

### 日志查看

```bash
# 查看访问日志
docker-compose -p travel-plan exec travel-plan tail -f /var/log/nginx/access.log

# 查看错误日志
docker-compose -p travel-plan exec travel-plan tail -f /var/log/nginx/error.log
```

## 🔒 安全配置

### 已配置的安全头

- `X-Frame-Options`: 防止点击劫持
- `X-XSS-Protection`: XSS保护
- `X-Content-Type-Options`: MIME类型嗅探保护
- `Referrer-Policy`: 引用策略
- `Content-Security-Policy`: 内容安全策略

### 建议的额外安全措施

1. **使用HTTPS**: 在生产环境中配置SSL证书
2. **访问控制**: 根据需要配置IP白名单
3. **防火墙**: 配置适当的防火墙规则
4. **定期更新**: 保持Docker镜像和依赖的最新版本

## 🌍 生产环境部署

### 使用反向代理

```nginx
# 在主Nginx服务器中配置
server {
    listen 80;
    server_name travel-map.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 使用Traefik

Docker Compose文件中已包含Traefik标签配置，可直接与Traefik集成。

## 🐛 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 修改docker-compose.yml中的端口映射
   ports:
     - "8081:80"  # 改为其他端口
   ```

2. **中文文件名显示问题**
   ```bash
   # 确保系统支持UTF-8编码
   locale -a | grep -i utf
   ```

3. **权限问题**
   ```bash
   # 检查文件权限
   ls -la 新疆伊犁旅游自驾路线地图.html
   
   # 修复权限
   chmod 644 *.html
   ```

### 日志分析

```bash
# 查看详细错误信息
docker-compose -p travel-plan logs travel-plan | grep -i error

# 查看访问统计
docker-compose -p travel-plan exec travel-plan \
  awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr
```

## 📞 技术支持

如遇到问题，请检查：

1. Docker和Docker Compose版本
2. 端口是否被占用
3. 文件权限设置
4. 网络连接状态
5. 容器日志信息

## 📄 许可证

本项目仅用于学习和演示目的。

---

**制作时间**: 2025年7月7日  
**技术栈**: Docker + Nginx + HTML/CSS/JavaScript  
**维护者**: Cursor 🗺️✨ 