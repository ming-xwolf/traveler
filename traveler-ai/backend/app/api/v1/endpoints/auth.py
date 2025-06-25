"""
认证API端点
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()
router = APIRouter()


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


@router.post("/login")
async def login(request: LoginRequest):
    """
    用户登录
    
    验证用户凭据并返回访问令牌。
    """
    # 临时简单实现，实际应该验证数据库中的用户
    if request.username == "demo" and request.password == "demo123":
        return {
            "success": True,
            "data": {
                "access_token": "demo_token_123456",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "demo",
                    "role": "user"
                }
            },
            "message": "登录成功"
        }
    else:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": "用户名或密码错误"
            }
        )


@router.post("/logout")
async def logout():
    """
    用户登出
    
    使当前访问令牌失效。
    """
    return {
        "success": True,
        "message": "登出成功"
    }


@router.get("/me")
async def get_current_user():
    """
    获取当前用户信息
    
    返回当前登录用户的基本信息。
    """
    # 临时返回固定用户信息
    return {
        "success": True,
        "data": {
            "id": 1,
            "username": "demo",
            "email": "demo@example.com",
            "role": "user",
            "created_at": "2024-01-01T00:00:00Z"
        }
    } 