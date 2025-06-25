#!/usr/bin/env python3
"""
TravelerAI 后端服务启动脚本
"""
import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.utils.logging import setup_logging


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        use_colors=True
    )


if __name__ == "__main__":
    main() 