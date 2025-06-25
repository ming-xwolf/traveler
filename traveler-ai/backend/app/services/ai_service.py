"""
AI服务集成层 - 支持多种大模型
"""
import hashlib
import json
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import httpx
import structlog

from app.core.config import settings, AI_PROVIDERS
from app.core.redis import cache

logger = structlog.get_logger()


class BaseAIProvider(ABC):
    """AI服务提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config["base_url"]
        self.model = config["model"]
        self.api_key = config.get("api_key")
        self.timeout = config.get("timeout", 60)
    
    @abstractmethod
    async def generate_completion(
        self, 
        prompt: str, 
        **kwargs
    ) -> str:
        """生成文本完成"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self, 
        prompt: str, 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """生成流式文本"""
        pass


class OllamaProvider(BaseAIProvider):
    """Ollama本地模型提供商"""
    
    async def generate_completion(
        self, 
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """生成文本完成"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            logger.error("Ollama生成失败", error=str(e))
            raise
    
    async def generate_stream(
        self, 
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """生成流式文本"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    }
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error("Ollama流式生成失败", error=str(e))
            raise


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek API提供商"""
    
    async def generate_completion(
        self, 
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """生成文本完成"""
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("DeepSeek生成失败", error=str(e))
            raise
    
    async def generate_stream(
        self, 
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """生成流式文本"""
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True
                    }
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            line = line[6:]
                            if line.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(line)
                                if "choices" in data and data["choices"]:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error("DeepSeek流式生成失败", error=str(e))
            raise


class BailianProvider(BaseAIProvider):
    """阿里云百炼API提供商"""
    
    async def generate_completion(
        self, 
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """生成文本完成"""
        if not self.api_key:
            raise ValueError("阿里云百炼API密钥未配置")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("阿里云百炼生成失败", error=str(e))
            raise
    
    async def generate_stream(
        self, 
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """生成流式文本"""
        if not self.api_key:
            raise ValueError("阿里云百炼API密钥未配置")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True
                    }
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            line = line[6:]
                            if line.strip() == "[DONE]":
                                break
                            try:
                                data = json.loads(line)
                                if "choices" in data and data["choices"]:
                                    delta = data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error("阿里云百炼流式生成失败", error=str(e))
            raise


class AIService:
    """AI服务管理器"""
    
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """初始化AI服务提供商"""
        for provider_name, config in AI_PROVIDERS.items():
            if provider_name == "ollama":
                self.providers[provider_name] = OllamaProvider(config)
            elif provider_name == "deepseek":
                if config["api_key"]:
                    self.providers[provider_name] = DeepSeekProvider(config)
            elif provider_name == "bailian":
                if config["api_key"]:
                    self.providers[provider_name] = BailianProvider(config)
        
        logger.info("AI服务提供商初始化完成", providers=list(self.providers.keys()))
    
    def get_provider(self, provider_name: Optional[str] = None) -> BaseAIProvider:
        """获取AI服务提供商"""
        provider_name = provider_name or settings.DEFAULT_AI_PROVIDER
        
        if provider_name not in self.providers:
            available = list(self.providers.keys())
            raise ValueError(f"AI服务提供商 '{provider_name}' 不可用，可用的有: {available}")
        
        return self.providers[provider_name]
    
    def _generate_cache_key(self, prompt: str, **kwargs) -> str:
        """生成缓存键"""
        # 创建包含所有参数的字符串
        cache_data = {
            "prompt": prompt,
            **kwargs
        }
        cache_string = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    async def generate_completion(
        self,
        prompt: str,
        provider_name: Optional[str] = None,
        use_cache: bool = True,
        **kwargs
    ) -> str:
        """生成文本完成"""
        # 检查缓存
        if use_cache:
            cache_key = self._generate_cache_key(prompt, provider=provider_name, **kwargs)
            cached_response = await cache.get_ai_response(cache_key)
            if cached_response:
                logger.info("使用缓存的AI响应", cache_key=cache_key)
                return cached_response
        
        # 获取提供商并生成
        provider = self.get_provider(provider_name)
        
        try:
            logger.info(
                "开始AI文本生成", 
                provider=provider_name or settings.DEFAULT_AI_PROVIDER,
                prompt_length=len(prompt)
            )
            
            response = await provider.generate_completion(prompt, **kwargs)
            
            # 缓存响应
            if use_cache and response:
                await cache.cache_ai_response(cache_key, response)
            
            logger.info(
                "AI文本生成完成",
                provider=provider_name or settings.DEFAULT_AI_PROVIDER,
                response_length=len(response)
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "AI文本生成失败",
                provider=provider_name or settings.DEFAULT_AI_PROVIDER,
                error=str(e)
            )
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """生成流式文本"""
        provider = self.get_provider(provider_name)
        
        try:
            logger.info(
                "开始AI流式生成",
                provider=provider_name or settings.DEFAULT_AI_PROVIDER,
                prompt_length=len(prompt)
            )
            
            async for chunk in provider.generate_stream(prompt, **kwargs):
                yield chunk
                
        except Exception as e:
            logger.error(
                "AI流式生成失败",
                provider=provider_name or settings.DEFAULT_AI_PROVIDER,
                error=str(e)
            )
            raise
    
    async def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """获取可用的AI服务提供商"""
        result = {}
        for name, provider in self.providers.items():
            result[name] = {
                "name": name,
                "model": provider.model,
                "base_url": provider.base_url,
                "available": True
            }
        return result
    
    async def test_provider(self, provider_name: str) -> Dict[str, Any]:
        """测试AI服务提供商"""
        try:
            provider = self.get_provider(provider_name)
            test_prompt = "你好，请回复'测试成功'"
            
            start_time = asyncio.get_event_loop().time()
            response = await provider.generate_completion(test_prompt, max_tokens=50)
            end_time = asyncio.get_event_loop().time()
            
            return {
                "provider": provider_name,
                "status": "success",
                "response_time": round(end_time - start_time, 2),
                "response": response[:100],  # 只返回前100个字符
            }
        except Exception as e:
            return {
                "provider": provider_name,
                "status": "error",
                "error": str(e)
            }


# 全局AI服务实例
ai_service = AIService() 