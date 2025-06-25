"""
API v1 路由入口
"""
from fastapi import APIRouter

from app.api.v1.endpoints import itinerary, ai, maps, auth, users

api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(itinerary.router, prefix="/itinerary", tags=["旅游攻略"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI服务"])
api_router.include_router(maps.router, prefix="/maps", tags=["地图服务"]) 