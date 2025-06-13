# 基于官方Nginx Alpine镜像
FROM nginx:alpine

# 设置维护者信息
LABEL maintainer="travel-guide@example.com"
LABEL description="新疆伊犁旅游自驾路线地图服务"

# 安装必要的工具
RUN apk add --no-cache \
    tzdata \
    curl

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制自定义Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制网站文件
COPY . /usr/share/nginx/html/

# 设置正确的权限
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# 创建日志目录
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"] 