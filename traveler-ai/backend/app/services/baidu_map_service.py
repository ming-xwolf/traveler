"""
百度地图服务集成
"""
import json
from typing import Dict, List, Any, Optional, Tuple
import httpx
import structlog

from app.core.config import settings
from app.core.redis import cache

logger = structlog.get_logger()


class BaiduMapService:
    """百度地图服务"""
    
    def __init__(self):
        self.base_url = settings.BAIDU_MAP_BASE_URL
        self.ak = settings.BAIDU_MAP_AK
        self.timeout = settings.BAIDU_MAP_TIMEOUT
    
    def _check_ak(self):
        """检查API密钥"""
        if not self.ak:
            raise ValueError("百度地图API密钥未配置")
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发起API请求"""
        self._check_ak()
        
        # 添加API密钥
        params["ak"] = self.ak
        params["output"] = "json"
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                result = response.json()
                
                # 检查百度API状态
                if result.get("status") != 0:
                    error_msg = result.get("message", f"百度地图API错误，状态码: {result.get('status')}")
                    logger.error("百度地图API请求失败", error=error_msg, params=params)
                    raise ValueError(error_msg)
                
                return result
                
        except httpx.HTTPError as e:
            logger.error("百度地图API请求失败", error=str(e), url=url, params=params)
            raise
    
    async def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """地理编码：地址转坐标"""
        cache_key = f"geocode_{address}"
        
        # 检查缓存
        cached_result = await cache.get_map_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                "address": address,
                "city": "",  # 可以指定城市范围
            }
            
            result = await self._make_request("geocoding/v3", params)
            
            if result.get("result") and result["result"].get("location"):
                location_data = result["result"]["location"]
                formatted_result = {
                    "latitude": location_data["lat"],
                    "longitude": location_data["lng"],
                    "address": address,
                    "formatted_address": result["result"].get("formatted_address", address),
                    "level": result["result"].get("level", "未知"),
                    "confidence": result["result"].get("confidence", 0),
                }
                
                # 缓存结果
                await cache.cache_map_data(cache_key, formatted_result)
                return formatted_result
            
            return None
            
        except Exception as e:
            logger.error("地理编码失败", address=address, error=str(e))
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """逆地理编码：坐标转地址"""
        cache_key = f"reverse_geocode_{latitude}_{longitude}"
        
        # 检查缓存
        cached_result = await cache.get_map_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                "location": f"{latitude},{longitude}",
                "coordtype": "wgs84ll",
                "pois": 1,
                "radius": 1000,
            }
            
            result = await self._make_request("reverse_geocoding/v3", params)
            
            if result.get("result"):
                result_data = result["result"]
                formatted_result = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "formatted_address": result_data.get("formatted_address", ""),
                    "country": result_data.get("addressComponent", {}).get("country", ""),
                    "province": result_data.get("addressComponent", {}).get("province", ""),
                    "city": result_data.get("addressComponent", {}).get("city", ""),
                    "district": result_data.get("addressComponent", {}).get("district", ""),
                    "street": result_data.get("addressComponent", {}).get("street", ""),
                    "pois": result_data.get("pois", []),
                }
                
                # 缓存结果
                await cache.cache_map_data(cache_key, formatted_result)
                return formatted_result
            
            return None
            
        except Exception as e:
            logger.error("逆地理编码失败", latitude=latitude, longitude=longitude, error=str(e))
            return None
    
    async def search_places(
        self, 
        query: str, 
        region: Optional[str] = None,
        location: Optional[str] = None,
        radius: Optional[int] = None,
        tag: Optional[str] = None,
        page_num: int = 0,
        page_size: int = 20
    ) -> Optional[Dict[str, Any]]:
        """地点检索"""
        cache_key = f"search_places_{query}_{region}_{location}_{radius}_{tag}_{page_num}_{page_size}"
        
        # 检查缓存
        cached_result = await cache.get_map_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                "query": query,
                "page_num": page_num,
                "page_size": page_size,
            }
            
            if region:
                params["region"] = region
            if location and radius:
                params["location"] = location
                params["radius"] = radius
            if tag:
                params["tag"] = tag
            
            result = await self._make_request("place/v2/search", params)
            
            if result.get("results"):
                places = []
                for place in result["results"]:
                    formatted_place = {
                        "name": place.get("name", ""),
                        "address": place.get("address", ""),
                        "latitude": place.get("location", {}).get("lat"),
                        "longitude": place.get("location", {}).get("lng"),
                        "uid": place.get("uid", ""),
                        "area": place.get("area", ""),
                        "city": place.get("city", ""),
                        "province": place.get("province", ""),
                        "telephone": place.get("telephone", ""),
                        "detail": place.get("detail", 0),
                        "tag": place.get("tag", ""),
                        "type": place.get("type", ""),
                        "detail_info": place.get("detail_info", {}),
                    }
                    places.append(formatted_place)
                
                formatted_result = {
                    "total": result.get("total", 0),
                    "places": places,
                    "page_num": page_num,
                    "page_size": page_size,
                }
                
                # 缓存结果
                await cache.cache_map_data(cache_key, formatted_result, ttl=3600)  # 1小时缓存
                return formatted_result
            
            return None
            
        except Exception as e:
            logger.error("地点检索失败", query=query, error=str(e))
            return None
    
    async def get_place_details(self, uid: str) -> Optional[Dict[str, Any]]:
        """获取地点详情"""
        cache_key = f"place_details_{uid}"
        
        # 检查缓存
        cached_result = await cache.get_map_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                "uid": uid,
                "scope": 2,  # 获取详细信息
            }
            
            result = await self._make_request("place/v2/detail", params)
            
            if result.get("result"):
                place_data = result["result"]
                formatted_result = {
                    "uid": uid,
                    "name": place_data.get("name", ""),
                    "address": place_data.get("address", ""),
                    "latitude": place_data.get("location", {}).get("lat"),
                    "longitude": place_data.get("location", {}).get("lng"),
                    "telephone": place_data.get("telephone", ""),
                    "tag": place_data.get("tag", ""),
                    "type": place_data.get("type", ""),
                    "detail_info": place_data.get("detail_info", {}),
                    "photos": place_data.get("photos", []),
                    "comment_num": place_data.get("comment_num", 0),
                    "score": place_data.get("score", 0),
                    "price": place_data.get("price", ""),
                    "shop_hours": place_data.get("shop_hours", ""),
                    "overall_rating": place_data.get("overall_rating", {}),
                }
                
                # 缓存结果
                await cache.cache_map_data(cache_key, formatted_result, ttl=3600 * 24)  # 24小时缓存
                return formatted_result
            
            return None
            
        except Exception as e:
            logger.error("获取地点详情失败", uid=uid, error=str(e))
            return None
    
    async def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving"  # driving, riding, walking, transit
    ) -> Optional[Dict[str, Any]]:
        """路线规划"""
        cache_key = f"directions_{origin}_{destination}_{mode}"
        
        # 检查缓存
        cached_result = await cache.get_map_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            endpoint_map = {
                "driving": "direction/v2/driving",
                "riding": "direction/v2/riding", 
                "walking": "direction/v2/walking",
                "transit": "direction/v2/transit"
            }
            
            endpoint = endpoint_map.get(mode, "direction/v2/driving")
            
            params = {
                "origin": origin,
                "destination": destination,
            }
            
            # 公交路线需要城市参数
            if mode == "transit":
                # 从起点推断城市
                origin_geocode = await self.geocode(origin)
                if origin_geocode:
                    # 这里可能需要额外的城市识别逻辑
                    pass
            
            result = await self._make_request(endpoint, params)
            
            if result.get("result") and result["result"].get("routes"):
                route_data = result["result"]["routes"][0]  # 取第一条路线
                
                formatted_result = {
                    "distance": route_data.get("distance", 0),  # 米
                    "duration": route_data.get("duration", 0),  # 秒
                    "origin": origin,
                    "destination": destination,
                    "mode": mode,
                    "steps": route_data.get("steps", []),
                    "polyline": route_data.get("polyline", ""),
                    "taxi_fee": route_data.get("taxi_fee", {}),
                }
                
                # 缓存结果
                await cache.cache_map_data(cache_key, formatted_result, ttl=3600)  # 1小时缓存
                return formatted_result
            
            return None
            
        except Exception as e:
            logger.error("路线规划失败", origin=origin, destination=destination, mode=mode, error=str(e))
            return None
    
    async def get_directions_matrix(
        self,
        origins: List[str],
        destinations: List[str],
        mode: str = "driving"
    ) -> Optional[Dict[str, Any]]:
        """批量算路"""
        origins_str = "|".join(origins)
        destinations_str = "|".join(destinations)
        cache_key = f"directions_matrix_{origins_str}_{destinations_str}_{mode}"
        
        # 检查缓存
        cached_result = await cache.get_map_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            endpoint_map = {
                "driving": "routematrix/v2/driving",
                "riding": "routematrix/v2/riding",
                "walking": "routematrix/v2/walking"
            }
            
            endpoint = endpoint_map.get(mode, "routematrix/v2/driving")
            
            params = {
                "origins": origins_str,
                "destinations": destinations_str,
            }
            
            result = await self._make_request(endpoint, params)
            
            if result.get("result"):
                formatted_result = {
                    "origins": origins,
                    "destinations": destinations,
                    "mode": mode,
                    "matrix": result["result"],
                }
                
                # 缓存结果
                await cache.cache_map_data(cache_key, formatted_result, ttl=3600)  # 1小时缓存
                return formatted_result
            
            return None
            
        except Exception as e:
            logger.error("批量算路失败", origins=origins, destinations=destinations, mode=mode, error=str(e))
            return None
    
    async def get_weather(
        self,
        location: Optional[str] = None,
        district_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """天气查询"""
        cache_key = f"weather_{location}_{district_id}"
        
        # 检查缓存
        cached_result = await cache.get_map_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {}
            
            if location:
                params["location"] = location
            if district_id:
                params["district_id"] = district_id
            
            result = await self._make_request("weather/v1", params)
            
            if result.get("result"):
                weather_data = result["result"]
                formatted_result = {
                    "location": location or f"district_{district_id}",
                    "current": weather_data.get("now", {}),
                    "forecast": weather_data.get("forecasts", []),
                    "update_time": weather_data.get("update_time", ""),
                }
                
                # 缓存结果（较短时间）
                await cache.cache_map_data(cache_key, formatted_result, ttl=1800)  # 30分钟缓存
                return formatted_result
            
            return None
            
        except Exception as e:
            logger.error("天气查询失败", location=location, district_id=district_id, error=str(e))
            return None
    
    async def ip_location(self, ip: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """IP定位"""
        cache_key = f"ip_location_{ip or 'current'}"
        
        # 检查缓存
        cached_result = await cache.get_map_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {}
            if ip:
                params["ip"] = ip
            
            result = await self._make_request("location/ip", params)
            
            if result.get("content"):
                content = result["content"]
                formatted_result = {
                    "ip": ip or "current",
                    "address": content.get("address", ""),
                    "city": content.get("address_detail", {}).get("city", ""),
                    "province": content.get("address_detail", {}).get("province", ""),
                    "point": content.get("point", {}),
                }
                
                # 缓存结果
                await cache.cache_map_data(cache_key, formatted_result, ttl=3600)  # 1小时缓存
                return formatted_result
            
            return None
            
        except Exception as e:
            logger.error("IP定位失败", ip=ip, error=str(e))
            return None


# 全局百度地图服务实例
baidu_map_service = BaiduMapService() 