#!/bin/bash

# 新疆伊犁旅游地图 - 启动脚本
# 作者: Cursor
# 日期: 2025年7月7日

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  新疆伊犁旅游地图 Docker部署${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_message "Docker 和 Docker Compose 已安装"
}

# 检查端口是否被占用
check_port() {
    local port=8080
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 $port 已被占用，请修改 docker-compose.yml 中的端口配置"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查必要文件
check_files() {
    local required_files=(
        "新疆伊犁旅游自驾路线地图.html"
        "docker-compose.yml"
        "nginx.conf"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "缺少必要文件: $file"
            exit 1
        fi
    done
    
    print_message "所有必要文件检查完成"
}

# 启动服务
start_service() {
    print_message "正在启动新疆伊犁旅游地图服务..."
    
    # 停止可能存在的旧容器
    docker-compose -p travel-plan down 2>/dev/null || true
    
    # 启动服务
    docker-compose -p travel-plan up -d
    
    if [[ $? -eq 0 ]]; then
        print_message "服务启动成功！"
    else
        print_error "服务启动失败"
        exit 1
    fi
}

# 等待服务就绪
wait_for_service() {
    print_message "等待服务就绪..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s http://localhost:8080/health >/dev/null 2>&1; then
            print_message "服务已就绪！"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "服务启动超时"
    return 1
}

# 显示访问信息
show_access_info() {
    echo
    print_message "🎉 部署完成！"
    echo
    echo -e "${GREEN}访问地址:${NC}"
    echo -e "  主地图页面: ${BLUE}http://localhost:8080${NC}"
    echo -e "  健康检查:   ${BLUE}http://localhost:8080/health${NC}"
    echo
    echo -e "${GREEN}管理命令:${NC}"
    echo -e "  查看状态:   ${YELLOW}docker-compose -p travel-plan ps${NC}"
    echo -e "  查看日志:   ${YELLOW}docker-compose -p travel-plan logs -f${NC}"
    echo -e "  停止服务:   ${YELLOW}docker-compose -p travel-plan down${NC}"
    echo -e "  重启服务:   ${YELLOW}docker-compose -p travel-plan restart${NC}"
    echo
}

# 主函数
main() {
    print_header
    
    # 检查环境
    check_docker
    check_port
    check_files
    
    # 启动服务
    start_service
    
    # 等待服务就绪
    if wait_for_service; then
        show_access_info
    else
        print_error "服务可能未正常启动，请检查日志: docker-compose -p travel-plan logs"
        exit 1
    fi
}

# 处理脚本参数
case "${1:-}" in
    "start"|"")
        main
        ;;
    "stop")
        print_message "正在停止服务..."
        docker-compose -p travel-plan down
        print_message "服务已停止"
        ;;
    "restart")
        print_message "正在重启服务..."
        docker-compose -p travel-plan restart
        print_message "服务已重启"
        ;;
    "status")
        docker-compose -p travel-plan ps
        ;;
    "logs")
        docker-compose -p travel-plan logs -f
        ;;
    "help"|"-h"|"--help")
        echo "用法: $0 [命令]"
        echo
        echo "命令:"
        echo "  start     启动服务 (默认)"
        echo "  stop      停止服务"
        echo "  restart   重启服务"
        echo "  status    查看状态"
        echo "  logs      查看日志"
        echo "  help      显示帮助"
        ;;
    *)
        print_error "未知命令: $1"
        echo "使用 '$0 help' 查看帮助"
        exit 1
        ;;
esac 