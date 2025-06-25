"""
AI服务API端点
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

from app.services.ai_service import ai_service

logger = structlog.get_logger()
router = APIRouter()


class AITestRequest(BaseModel):
    """AI测试请求模型"""
    provider: str = Field(..., description="AI服务提供商")
    prompt: str = Field(..., description="测试提示词", max_length=500)


class AIGenerationRequest(BaseModel):
    """AI生成请求模型"""
    prompt: str = Field(..., description="生成提示词", max_length=10000)
    provider: Optional[str] = Field(None, description="AI服务提供商")
    temperature: float = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    max_tokens: int = Field(4000, description="最大令牌数", ge=1, le=8000)


@router.get("/providers")
async def get_available_providers():
    """
    获取可用的AI服务提供商
    
    返回系统中配置的AI服务提供商列表及其状态。
    """
    try:
        providers = await ai_service.get_available_providers()
        
        return {
            "success": True,
            "providers": providers,
            "total": len(providers)
        }
        
    except Exception as e:
        logger.error("获取AI服务提供商失败", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PROVIDERS_QUERY_FAILED",
                "message": "获取AI服务提供商失败"
            }
        )


@router.post("/test")
async def test_ai_provider(request: AITestRequest):
    """
    测试AI服务提供商
    
    测试指定AI服务提供商的连接和响应能力。
    """
    try:
        result = await ai_service.test_provider(request.provider)
        
        return {
            "success": result["status"] == "success",
            "result": result
        }
        
    except Exception as e:
        logger.error("测试AI服务提供商失败", provider=request.provider, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PROVIDER_TEST_FAILED",
                "message": f"测试AI服务提供商失败: {str(e)}"
            }
        )


@router.post("/generate")
async def generate_text(request: AIGenerationRequest):
    """
    AI文本生成
    
    调用AI服务生成文本内容。
    """
    try:
        logger.info("收到AI文本生成请求", provider=request.provider, prompt_length=len(request.prompt))
        
        response = await ai_service.generate_completion(
            prompt=request.prompt,
            provider_name=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return {
            "success": True,
            "response": response,
            "provider": request.provider or ai_service.settings.DEFAULT_AI_PROVIDER,
            "prompt_length": len(request.prompt),
            "response_length": len(response)
        }
        
    except Exception as e:
        logger.error("AI文本生成失败", error=str(e), provider=request.provider)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "GENERATION_FAILED",
                "message": f"AI文本生成失败: {str(e)}"
            }
        )


@router.get("/config")
async def get_ai_config():
    """
    获取AI服务配置
    
    返回当前AI服务的配置信息。
    """
    try:
        from app.core.config import settings
        
        config = {
            "default_provider": settings.DEFAULT_AI_PROVIDER,
            "providers": {
                "ollama": {
                    "base_url": settings.OLLAMA_BASE_URL,
                    "model": settings.OLLAMA_MODEL,
                    "available": bool(settings.OLLAMA_BASE_URL)
                },
                "deepseek": {
                    "base_url": settings.DEEPSEEK_BASE_URL,
                    "model": settings.DEEPSEEK_MODEL,
                    "available": bool(settings.DEEPSEEK_API_KEY)
                },
                "bailian": {
                    "base_url": settings.BAILIAN_BASE_URL,
                    "model": settings.BAILIAN_MODEL,
                    "available": bool(settings.BAILIAN_API_KEY)
                }
            },
            "cache_enabled": settings.AI_CACHE_ENABLED,
            "cache_ttl": settings.AI_CACHE_TTL
        }
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error("获取AI配置失败", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CONFIG_QUERY_FAILED",
                "message": "获取AI配置失败"
            }
        ) 