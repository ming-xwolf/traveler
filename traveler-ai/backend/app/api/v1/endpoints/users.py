"""
用户管理API端点
"""
from fastapi import APIRouter
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.get("/profile")
async def get_user_profile():
    """
    获取用户档案
    
    返回当前用户的详细档案信息。
    """
    # 临时返回固定用户档案
    return {
        "success": True,
        "data": {
            "id": 1,
            "username": "demo",
            "email": "demo@example.com",
            "full_name": "演示用户",
            "role": "user",
            "avatar": None,
            "preferences": {
                "default_ai_provider": "ollama",
                "language": "zh-CN",
                "timezone": "Asia/Shanghai"
            },
            "stats": {
                "total_itineraries": 5,
                "favorite_destinations": ["新疆伊犁", "云南大理"],
                "member_since": "2024-01-01"
            }
        }
    }


@router.get("/itineraries")
async def get_user_itineraries():
    """
    获取用户攻略列表
    
    返回当前用户创建的所有旅游攻略。
    """
    # 临时返回固定攻略列表
    return {
        "success": True,
        "data": {
            "itineraries": [
                {
                    "id": 1,
                    "title": "新疆伊犁7日深度游",
                    "destination": "新疆伊犁",
                    "days": 7,
                    "status": "completed",
                    "created_at": "2024-12-01T10:00:00Z",
                    "preview": "体验伊犁河谷的自然风光..."
                },
                {
                    "id": 2,
                    "title": "云南大理5日休闲游",
                    "destination": "云南大理",
                    "days": 5,
                    "status": "completed",
                    "created_at": "2024-11-15T14:30:00Z",
                    "preview": "感受大理的风花雪月..."
                }
            ],
            "total": 2,
            "page": 1,
            "page_size": 10
        }
    } 