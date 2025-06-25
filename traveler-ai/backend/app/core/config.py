"""
应用核心配置
"""
from typing import List, Optional, Union
from pydantic import BaseSettings, validator, AnyHttpUrl
import secrets


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    PROJECT_NAME: str = "TravelerAI - 智能旅游攻略生成器"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/traveler_ai"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/traveler_ai"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1小时
    
    # AI服务配置
    # Ollama配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:14b"
    OLLAMA_TIMEOUT: int = 300  # 5分钟
    
    # DeepSeek配置
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 阿里云百炼配置
    BAILIAN_API_KEY: Optional[str] = None
    BAILIAN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    BAILIAN_MODEL: str = "qwen-max"
    
    # 默认AI服务提供商
    DEFAULT_AI_PROVIDER: str = "ollama"  # ollama, deepseek, bailian
    
    # 百度地图API配置
    BAIDU_MAP_AK: Optional[str] = None
    BAIDU_MAP_BASE_URL: str = "https://api.map.baidu.com"
    BAIDU_MAP_TIMEOUT: int = 30
    
    # 文件存储配置
    UPLOAD_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    STATIC_FILES_PATH: str = "/app/static"
    TEMPLATES_PATH: str = "/app/templates"
    
    # 攻略生成配置
    MAX_DAYS: int = 30  # 最大行程天数
    MAX_CONCURRENT_GENERATIONS: int = 3  # 最大并发生成数
    GENERATION_TIMEOUT: int = 600  # 10分钟
    
    # Celery配置（异步任务）
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # 邮件配置（可选）
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # 如果没有设置DATABASE_URL，使用环境变量构建
        return f"postgresql://{values.get('POSTGRES_USER', 'postgres')}:{values.get('POSTGRES_PASSWORD', 'password')}@{values.get('POSTGRES_HOST', 'localhost')}:{values.get('POSTGRES_PORT', 5432)}/{values.get('POSTGRES_DB', 'traveler_ai')}"
    
    @validator("ASYNC_DATABASE_URL", pre=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # 如果没有设置ASYNC_DATABASE_URL，基于DATABASE_URL构建
        db_url = values.get("DATABASE_URL", "")
        if db_url.startswith("postgresql://"):
            return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return db_url
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建配置实例
settings = Settings()


# AI服务提供商配置映射
AI_PROVIDERS = {
    "ollama": {
        "base_url": settings.OLLAMA_BASE_URL,
        "model": settings.OLLAMA_MODEL,
        "timeout": settings.OLLAMA_TIMEOUT,
        "api_key": None
    },
    "deepseek": {
        "base_url": settings.DEEPSEEK_BASE_URL,
        "model": settings.DEEPSEEK_MODEL,
        "timeout": 60,
        "api_key": settings.DEEPSEEK_API_KEY
    },
    "bailian": {
        "base_url": settings.BAILIAN_BASE_URL,
        "model": settings.BAILIAN_MODEL,
        "timeout": 60,
        "api_key": settings.BAILIAN_API_KEY
    }
}


# 常用常量定义
class Constants:
    """应用常量"""
    
    # 用户角色
    USER_ROLE_GUEST = "guest"
    USER_ROLE_USER = "user"
    USER_ROLE_PREMIUM = "premium"
    USER_ROLE_ADMIN = "admin"
    
    # 攻略状态
    ITINERARY_STATUS_PENDING = "pending"
    ITINERARY_STATUS_GENERATING = "generating"
    ITINERARY_STATUS_COMPLETED = "completed"
    ITINERARY_STATUS_FAILED = "failed"
    
    # 导出格式
    EXPORT_FORMAT_MARKDOWN = "markdown"
    EXPORT_FORMAT_HTML = "html"
    EXPORT_FORMAT_PDF = "pdf"
    
    # 缓存键前缀
    CACHE_PREFIX_USER = "user:"
    CACHE_PREFIX_ITINERARY = "itinerary:"
    CACHE_PREFIX_AI_RESPONSE = "ai_response:"
    CACHE_PREFIX_MAP_DATA = "map_data:"
    
    # 任务队列名称
    QUEUE_ITINERARY_GENERATION = "itinerary_generation"
    QUEUE_FILE_EXPORT = "file_export"
    QUEUE_EMAIL_NOTIFICATION = "email_notification"
    
    # 默认配置
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 4000
    DEFAULT_PAGE_SIZE = 20
    DEFAULT_MAX_PAGE_SIZE = 100 