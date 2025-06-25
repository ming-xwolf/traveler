"""
基于GenAI的旅游攻略生成器 - 后端API服务
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import structlog
import time
import uuid

from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import init_db
from app.core.redis import init_redis
from app.utils.logging import setup_logging

# 设置结构化日志
setup_logging()
logger = structlog.get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="基于GenAI的智能旅游攻略生成服务",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.DEBUG else None,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 信任的主机中间件
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求ID和日志中间件
@app.middleware("http")
async def add_request_id_and_logging(request: Request, call_next):
    """为每个请求添加唯一ID并记录日志"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # 记录请求开始
    logger.info(
        "请求开始",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None
    )
    
    response = await call_next(request)
    
    # 记录请求完成
    process_time = time.time() - start_time
    logger.info(
        "请求完成",
        request_id=request_id,
        status_code=response.status_code,
        process_time=round(process_time, 4)
    )
    
    response.headers["X-Request-ID"] = request_id
    return response

# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """HTTP异常处理"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        "HTTP异常",
        request_id=request_id,
        status_code=exc.status_code,
        detail=exc.detail
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": {}
            },
            "timestamp": time.time(),
            "request_id": request_id
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        "请求验证失败",
        request_id=request_id,
        errors=exc.errors()
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求参数验证失败",
                "details": exc.errors()
            },
            "timestamp": time.time(),
            "request_id": request_id
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        "服务器内部错误",
        request_id=request_id,
        exception=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误，请稍后重试",
                "details": {}
            },
            "timestamp": time.time(),
            "request_id": request_id
        }
    )

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": time.time()
    }

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("正在启动应用服务...")
    
    # 初始化数据库连接
    await init_db()
    logger.info("数据库连接已初始化")
    
    # 初始化Redis连接
    await init_redis()
    logger.info("Redis连接已初始化")
    
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} 启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("正在关闭应用服务...")
    
    # 这里可以添加清理资源的代码
    
    logger.info("应用服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None  # 使用自定义日志配置
    ) 