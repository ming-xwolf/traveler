"""
Redis连接和缓存管理
"""
import json
import pickle
from typing import Any, Optional, Union
import redis.asyncio as redis
import structlog

from app.core.config import settings, Constants

logger = structlog.get_logger()

# Redis连接池
redis_pool = None


async def init_redis():
    """初始化Redis连接"""
    global redis_pool
    try:
        redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=20,
            decode_responses=False  # 保持二进制数据
        )
        # 测试连接
        redis_client = redis.Redis(connection_pool=redis_pool)
        await redis_client.ping()
        logger.info("Redis连接成功")
    except Exception as e:
        logger.error("Redis连接失败", error=str(e))
        raise


async def get_redis() -> redis.Redis:
    """获取Redis客户端"""
    return redis.Redis(connection_pool=redis_pool)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.default_ttl = settings.REDIS_CACHE_TTL
    
    async def get_client(self) -> redis.Redis:
        """获取Redis客户端"""
        return await get_redis()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        try:
            client = await self.get_client()
            value = await client.get(key)
            if value is None:
                return default
            
            # 尝试解析JSON，失败则使用pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
        except Exception as e:
            logger.error("缓存获取失败", key=key, error=str(e))
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize_method: str = "json"
    ) -> bool:
        """设置缓存值"""
        try:
            client = await self.get_client()
            ttl = ttl or self.default_ttl
            
            # 序列化数据
            if serialize_method == "json":
                try:
                    serialized_value = json.dumps(value, ensure_ascii=False)
                except (TypeError, ValueError):
                    # JSON序列化失败，使用pickle
                    serialized_value = pickle.dumps(value)
            else:
                serialized_value = pickle.dumps(value)
            
            await client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error("缓存设置失败", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            client = await self.get_client()
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            logger.error("缓存删除失败", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            client = await self.get_client()
            return bool(await client.exists(key))
        except Exception as e:
            logger.error("缓存检查失败", key=key, error=str(e))
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        try:
            client = await self.get_client()
            return bool(await client.expire(key, ttl))
        except Exception as e:
            logger.error("缓存过期时间设置失败", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """批量删除匹配模式的缓存"""
        try:
            client = await self.get_client()
            keys = await client.keys(pattern)
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            logger.error("批量删除缓存失败", pattern=pattern, error=str(e))
            return 0
    
    async def get_hash(self, key: str, field: str, default: Any = None) -> Any:
        """获取哈希字段值"""
        try:
            client = await self.get_client()
            value = await client.hget(key, field)
            if value is None:
                return default
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
        except Exception as e:
            logger.error("哈希缓存获取失败", key=key, field=field, error=str(e))
            return default
    
    async def set_hash(
        self, 
        key: str, 
        field: str, 
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """设置哈希字段值"""
        try:
            client = await self.get_client()
            
            # 序列化数据
            try:
                serialized_value = json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError):
                serialized_value = pickle.dumps(value)
            
            await client.hset(key, field, serialized_value)
            
            if ttl:
                await client.expire(key, ttl)
            
            return True
        except Exception as e:
            logger.error("哈希缓存设置失败", key=key, field=field, error=str(e))
            return False
    
    async def delete_hash(self, key: str, field: str) -> bool:
        """删除哈希字段"""
        try:
            client = await self.get_client()
            result = await client.hdel(key, field)
            return result > 0
        except Exception as e:
            logger.error("哈希缓存删除失败", key=key, field=field, error=str(e))
            return False
    
    # 业务相关的缓存方法
    def get_user_cache_key(self, user_id: int) -> str:
        """获取用户缓存键"""
        return f"{Constants.CACHE_PREFIX_USER}{user_id}"
    
    def get_itinerary_cache_key(self, itinerary_id: int) -> str:
        """获取攻略缓存键"""
        return f"{Constants.CACHE_PREFIX_ITINERARY}{itinerary_id}"
    
    def get_ai_response_cache_key(self, prompt_hash: str) -> str:
        """获取AI响应缓存键"""
        return f"{Constants.CACHE_PREFIX_AI_RESPONSE}{prompt_hash}"
    
    def get_map_data_cache_key(self, location: str) -> str:
        """获取地图数据缓存键"""
        return f"{Constants.CACHE_PREFIX_MAP_DATA}{location}"
    
    async def cache_user_data(self, user_id: int, user_data: dict, ttl: int = 3600):
        """缓存用户数据"""
        key = self.get_user_cache_key(user_id)
        return await self.set(key, user_data, ttl)
    
    async def get_user_data(self, user_id: int) -> Optional[dict]:
        """获取用户缓存数据"""
        key = self.get_user_cache_key(user_id)
        return await self.get(key)
    
    async def cache_ai_response(
        self, 
        prompt_hash: str, 
        response: str, 
        ttl: int = 3600 * 24  # 24小时
    ):
        """缓存AI响应"""
        key = self.get_ai_response_cache_key(prompt_hash)
        return await self.set(key, response, ttl)
    
    async def get_ai_response(self, prompt_hash: str) -> Optional[str]:
        """获取AI响应缓存"""
        key = self.get_ai_response_cache_key(prompt_hash)
        return await self.get(key)
    
    async def cache_map_data(
        self, 
        location: str, 
        map_data: dict, 
        ttl: int = 3600 * 24 * 7  # 7天
    ):
        """缓存地图数据"""
        key = self.get_map_data_cache_key(location)
        return await self.set(key, map_data, ttl)
    
    async def get_map_data(self, location: str) -> Optional[dict]:
        """获取地图数据缓存"""
        key = self.get_map_data_cache_key(location)
        return await self.get(key)


# 全局缓存管理器实例
cache = CacheManager() 