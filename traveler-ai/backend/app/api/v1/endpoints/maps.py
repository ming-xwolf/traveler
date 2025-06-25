"""
地图服务API端点
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import structlog

from app.services.baidu_map_service import baidu_map_service

logger = structlog.get_logger()
router = APIRouter()


class GeocodeRequest(BaseModel):
    """地理编码请求模型"""
    address: str = Field(..., description="地址", max_length=200)


class ReverseGeocodeRequest(BaseModel):
    """逆地理编码请求模型"""
    latitude: float = Field(..., description="纬度", ge=-90.0, le=90.0)
    longitude: float = Field(..., description="经度", ge=-180.0, le=180.0)


class PlaceSearchRequest(BaseModel):
    """地点搜索请求模型"""
    query: str = Field(..., description="搜索关键词", max_length=100)
    region: Optional[str] = Field(None, description="城市区域", max_length=50)
    location: Optional[str] = Field(None, description="中心点坐标")
    radius: Optional[int] = Field(None, description="搜索半径(米)", ge=1, le=50000)
    tag: Optional[str] = Field(None, description="分类标签", max_length=100)
    page_num: int = Field(0, description="页码", ge=0)
    page_size: int = Field(20, description="每页数量", ge=1, le=100)


class DirectionsRequest(BaseModel):
    """路线规划请求模型"""
    origin: str = Field(..., description="起点", max_length=200)
    destination: str = Field(..., description="终点", max_length=200)
    mode: str = Field("driving", description="出行方式")

    class Config:
        json_schema_extra = {
            "example": {
                "origin": "北京市天安门",
                "destination": "北京市颐和园",
                "mode": "driving"
            }
        }


@router.post("/geocode")
async def geocode_address(request: GeocodeRequest):
    """
    地理编码
    
    将地址转换为经纬度坐标。
    """
    try:
        logger.info("收到地理编码请求", address=request.address)
        
        result = await baidu_map_service.geocode(request.address)
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "地理编码成功"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "未找到地址对应的坐标信息"
            }
            
    except Exception as e:
        logger.error("地理编码失败", address=request.address, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "GEOCODE_FAILED",
                "message": f"地理编码失败: {str(e)}"
            }
        )


@router.post("/reverse-geocode")
async def reverse_geocode_coordinates(request: ReverseGeocodeRequest):
    """
    逆地理编码
    
    将经纬度坐标转换为地址信息。
    """
    try:
        logger.info("收到逆地理编码请求", latitude=request.latitude, longitude=request.longitude)
        
        result = await baidu_map_service.reverse_geocode(request.latitude, request.longitude)
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "逆地理编码成功"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "未找到坐标对应的地址信息"
            }
            
    except Exception as e:
        logger.error("逆地理编码失败", latitude=request.latitude, longitude=request.longitude, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "REVERSE_GEOCODE_FAILED",
                "message": f"逆地理编码失败: {str(e)}"
            }
        )


@router.post("/search-places")
async def search_places(request: PlaceSearchRequest):
    """
    地点搜索
    
    根据关键词搜索地点信息。
    """
    try:
        logger.info("收到地点搜索请求", query=request.query, region=request.region)
        
        result = await baidu_map_service.search_places(
            query=request.query,
            region=request.region,
            location=request.location,
            radius=request.radius,
            tag=request.tag,
            page_num=request.page_num,
            page_size=request.page_size
        )
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "地点搜索成功"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "未找到相关地点"
            }
            
    except Exception as e:
        logger.error("地点搜索失败", query=request.query, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PLACE_SEARCH_FAILED",
                "message": f"地点搜索失败: {str(e)}"
            }
        )


@router.get("/place-details/{uid}")
async def get_place_details(uid: str):
    """
    获取地点详情
    
    根据地点UID获取详细信息。
    """
    try:
        logger.info("收到地点详情请求", uid=uid)
        
        result = await baidu_map_service.get_place_details(uid)
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "获取地点详情成功"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "未找到地点详情"
            }
            
    except Exception as e:
        logger.error("获取地点详情失败", uid=uid, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PLACE_DETAILS_FAILED",
                "message": f"获取地点详情失败: {str(e)}"
            }
        )


@router.post("/directions")
async def get_directions(request: DirectionsRequest):
    """
    路线规划
    
    计算两点间的路线和距离。
    """
    try:
        logger.info("收到路线规划请求", origin=request.origin, destination=request.destination, mode=request.mode)
        
        # 验证出行方式
        valid_modes = ["driving", "riding", "walking", "transit"]
        if request.mode not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_MODE",
                    "message": f"不支持的出行方式: {request.mode}，支持的方式: {valid_modes}"
                }
            )
        
        result = await baidu_map_service.get_directions(
            origin=request.origin,
            destination=request.destination,
            mode=request.mode
        )
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "路线规划成功"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "无法规划路线"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("路线规划失败", origin=request.origin, destination=request.destination, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "DIRECTIONS_FAILED",
                "message": f"路线规划失败: {str(e)}"
            }
        )


@router.get("/weather")
async def get_weather(
    location: Optional[str] = Query(None, description="位置坐标"),
    district_id: Optional[int] = Query(None, description="行政区划代码")
):
    """
    天气查询
    
    查询指定位置的天气信息。
    """
    try:
        if not location and not district_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "MISSING_LOCATION",
                    "message": "请提供location或district_id参数"
                }
            )
        
        logger.info("收到天气查询请求", location=location, district_id=district_id)
        
        result = await baidu_map_service.get_weather(
            location=location,
            district_id=district_id
        )
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "天气查询成功"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "未获取到天气信息"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("天气查询失败", location=location, district_id=district_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "WEATHER_QUERY_FAILED",
                "message": f"天气查询失败: {str(e)}"
            }
        )


@router.get("/ip-location")
async def get_ip_location(ip: Optional[str] = Query(None, description="IP地址，为空则获取当前IP")):
    """
    IP定位
    
    根据IP地址获取位置信息。
    """
    try:
        logger.info("收到IP定位请求", ip=ip)
        
        result = await baidu_map_service.ip_location(ip)
        
        if result:
            return {
                "success": True,
                "data": result,
                "message": "IP定位成功"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "IP定位失败"
            }
            
    except Exception as e:
        logger.error("IP定位失败", ip=ip, error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "IP_LOCATION_FAILED",
                "message": f"IP定位失败: {str(e)}"
            }
        )


@router.get("/config")
async def get_map_config():
    """
    获取地图服务配置
    
    返回地图服务的配置信息。
    """
    try:
        from app.core.config import settings
        
        config = {
            "base_url": settings.BAIDU_MAP_BASE_URL,
            "timeout": settings.BAIDU_MAP_TIMEOUT,
            "api_key_configured": bool(settings.BAIDU_MAP_AK),
            "cache_enabled": True,  # 假设缓存默认启用
            "supported_modes": ["driving", "riding", "walking", "transit"],
            "max_search_radius": 50000,
            "default_page_size": 20
        }
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error("获取地图配置失败", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CONFIG_QUERY_FAILED",
                "message": "获取地图配置失败"
            }
        ) 