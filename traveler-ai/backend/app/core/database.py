"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# 同步数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# 异步数据库引擎
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# 会话创建器
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 异步会话创建器
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_engine
)

# 声明性基类
Base = declarative_base()


async def init_db():
    """初始化数据库连接"""
    try:
        # 测试连接
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error("数据库连接失败", error=str(e))
        raise


def get_db():
    """获取同步数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = async_engine
        self.session_factory = AsyncSessionLocal
    
    async def create_session(self) -> AsyncSession:
        """创建异步数据库会话"""
        return self.session_factory()
    
    async def close_session(self, session: AsyncSession):
        """关闭异步数据库会话"""
        await session.close()
    
    async def execute_transaction(self, func, *args, **kwargs):
        """执行事务"""
        async with self.session_factory() as session:
            try:
                async with session.begin():
                    result = await func(session, *args, **kwargs)
                    return result
            except Exception as e:
                await session.rollback()
                logger.error("事务执行失败", error=str(e))
                raise
            finally:
                await session.close()


# 全局数据库管理器实例
db_manager = DatabaseManager() 