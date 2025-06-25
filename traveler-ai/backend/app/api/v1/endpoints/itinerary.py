"""
旅游攻略生成API端点
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field
import structlog

from app.services.itinerary_service import itinerary_service
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()


# Pydantic模型定义
class ItineraryGenerationRequest(BaseModel):
    """攻略生成请求模型"""
    destination: str = Field(..., description="目的地", min_length=2, max_length=100)
    days: int = Field(..., description="旅游天数", ge=1, le=30)
    travel_style: Optional[str] = Field(None, description="旅行风格")
    budget_min: Optional[float] = Field(None, description="预算下限", ge=0)
    budget_max: Optional[float] = Field(None, description="预算上限", ge=0)
    group_size: int = Field(2, description="团体人数", ge=1, le=20)
    start_date: Optional[datetime] = Field(None, description="开始日期")
    ai_provider: Optional[str] = Field(None, description="AI服务提供商")
    special_requirements: Optional[str] = Field(None, description="特殊要求", max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "destination": "新疆伊犁",
                "days": 7,
                "travel_style": "深度游",
                "budget_min": 3000.0,
                "budget_max": 5000.0,
                "group_size": 2,
                "start_date": "2025-06-27T00:00:00",
                "ai_provider": "ollama",
                "special_requirements": "喜欢自然风景，对历史文化感兴趣"
            }
        }


class ItineraryResponse(BaseModel):
    """攻略响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    request_id: Optional[str] = None


class ProgressResponse(BaseModel):
    """进度响应模型"""
    itinerary_id: int
    progress: int = Field(..., description="进度百分比", ge=0, le=100)
    status: str
    message: str
    current_step: Optional[str] = None


# API端点
@router.post("/generate", response_model=ItineraryResponse)
async def generate_itinerary(
    request: ItineraryGenerationRequest,
    background_tasks: BackgroundTasks,
    user_id: int = 1  # 临时固定用户ID，实际应该从认证中获取
):
    """
    生成旅游攻略
    
    根据用户输入的目的地、天数等信息，调用AI服务生成详细的旅游攻略。
    """
    try:
        logger.info("收到攻略生成请求", destination=request.destination, days=request.days)
        
        # 验证请求
        validation_result = await itinerary_service.validate_generation_request(
            destination=request.destination,
            days=request.days,
            user_id=user_id
        )
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "VALIDATION_FAILED",
                    "message": "请求参数验证失败",
                    "errors": validation_result["errors"]
                }
            )
        
        # 检查预算范围
        if request.budget_min and request.budget_max and request.budget_min > request.budget_max:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_BUDGET_RANGE",
                    "message": "预算下限不能大于上限"
                }
            )
        
        # 验证AI服务提供商
        if request.ai_provider and request.ai_provider not in ["ollama", "deepseek", "qwen"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_AI_PROVIDER",
                    "message": f"不支持的AI服务提供商: {request.ai_provider}"
                }
            )
        
        # 开始生成攻略
        result = await itinerary_service.generate_itinerary(
            destination=request.destination,
            days=request.days,
            user_id=user_id,
            travel_style=request.travel_style,
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            group_size=request.group_size,
            start_date=request.start_date,
            ai_provider=request.ai_provider,
            special_requirements=request.special_requirements
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "GENERATION_FAILED",
                    "message": result.get("message", "攻略生成失败"),
                    "details": result.get("error")
                }
            )
        
        logger.info("攻略生成完成", destination=request.destination)
        
        return ItineraryResponse(
            success=True,
            data=result,
            message="攻略生成完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("攻略生成API异常", error=str(e), destination=request.destination)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误，请稍后重试"
            }
        )


@router.get("/progress/{itinerary_id}", response_model=ProgressResponse)
async def get_generation_progress(itinerary_id: int):
    """
    获取攻略生成进度
    
    查询指定攻略的生成进度状态。
    """
    try:
        progress = await itinerary_service.get_generation_progress(itinerary_id)
        
        return ProgressResponse(
            itinerary_id=itinerary_id,
            progress=progress.get("progress", 0),
            status=progress.get("status", "unknown"),
            message=progress.get("message", ""),
            current_step=progress.get("current_step")
        )
        
    except Exception as e:
        logger.error("获取生成进度失败", itinerary_id=itinerary_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PROGRESS_QUERY_FAILED",
                "message": "获取生成进度失败"
            }
        )


@router.get("/validate")
async def validate_destination(destination: str = Query(..., description="目的地名称")):
    """
    验证目的地
    
    检查目的地是否有效，并返回基本地理信息。
    """
    try:
        from app.services.baidu_map_service import baidu_map_service
        
        # 尝试地理编码
        location_info = await baidu_map_service.geocode(destination)
        
        if location_info:
            return {
                "valid": True,
                "destination": destination,
                "location_info": location_info,
                "message": "目的地验证成功"
            }
        else:
            return {
                "valid": False,
                "destination": destination,
                "message": "无法找到该目的地的地理信息"
            }
            
    except Exception as e:
        logger.error("目的地验证失败", destination=destination, error=str(e))
        return {
            "valid": False,
            "destination": destination,
            "message": "目的地验证失败",
            "error": str(e)
        }


@router.get("/templates")
async def get_available_templates():
    """
    获取可用模板
    
    返回系统中可用的攻略模板列表。
    """
    try:
        # 这里应该从数据库查询模板列表
        # 暂时返回固定模板
        templates = [
            {
                "id": 1,
                "name": "标准旅游攻略模板",
                "type": "overview",
                "description": "包含行程概述、每日安排、预算分析等完整结构",
                "category": "standard"
            },
            {
                "id": 2,
                "name": "每日行程模板",
                "type": "daily",
                "description": "详细的每日时间安排、景点介绍、交通指南",
                "category": "daily"
            }
        ]
        
        return {
            "success": True,
            "templates": templates,
            "total": len(templates)
        }
        
    except Exception as e:
        logger.error("获取模板列表失败", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "TEMPLATES_QUERY_FAILED",
                "message": "获取模板列表失败"
            }
        )


@router.get("/examples")
async def get_generation_examples():
    """
    获取生成示例
    
    返回一些攻略生成的示例，帮助用户了解如何使用。
    """
    examples = [
        {
            "title": "新疆伊犁7日深度游",
            "destination": "新疆伊犁",
            "days": 7,
            "travel_style": "深度游",
            "budget_range": "3000-5000元",
            "highlights": ["赛里木湖", "薰衣草园", "果子沟大桥", "霍尔果斯口岸"],
            "description": "体验伊犁河谷的自然风光和多元文化"
        },
        {
            "title": "云南大理丽江5日休闲游",
            "destination": "云南大理丽江",
            "days": 5,
            "travel_style": "休闲游",
            "budget_range": "2000-3500元",
            "highlights": ["洱海", "古城", "玉龙雪山", "泸沽湖"],
            "description": "感受云南的民族风情和自然美景"
        },
        {
            "title": "西藏拉萨10日文化游",
            "destination": "西藏拉萨",
            "days": 10,
            "travel_style": "文化游",
            "budget_range": "5000-8000元",
            "highlights": ["布达拉宫", "大昭寺", "纳木错", "羊卓雍措"],
            "description": "深度体验藏族文化和高原风光"
        }
    ]
    
    return {
        "success": True,
        "examples": examples,
        "total": len(examples)
    }


@router.get("/stats")
async def get_generation_stats():
    """
    获取生成统计
    
    返回系统的攻略生成统计信息。
    """
    try:
        # 这里应该从数据库查询真实统计数据
        stats = {
            "total_itineraries": 1250,
            "total_users": 320,
            "popular_destinations": [
                {"destination": "新疆伊犁", "count": 89},
                {"destination": "云南大理", "count": 76},
                {"destination": "西藏拉萨", "count": 65},
                {"destination": "四川九寨沟", "count": 54},
                {"destination": "海南三亚", "count": 48}
            ],
            "average_days": 6.8,
            "success_rate": 0.96,
            "avg_generation_time": 45.2  # 秒
        }
        
        return {
            "success": True,
            "stats": stats,
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("获取统计数据失败", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "STATS_QUERY_FAILED",
                "message": "获取统计数据失败"
            }
        ) 