"""
旅游攻略生成核心服务
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import structlog

from app.services.ai_service import ai_service
from app.services.baidu_map_service import baidu_map_service
from app.models.itinerary import Itinerary, ItineraryDay, ItineraryStatus
from app.models.template import Template
from app.core.config import settings

logger = structlog.get_logger()


class ItineraryService:
    """旅游攻略生成服务"""
    
    def __init__(self):
        self.ai_service = ai_service
        self.map_service = baidu_map_service
    
    async def generate_itinerary_prompt(
        self,
        destination: str,
        days: int,
        travel_style: Optional[str] = None,
        budget_range: Optional[str] = None,
        group_size: int = 2,
        start_date: Optional[datetime] = None,
        special_requirements: Optional[str] = None
    ) -> str:
        """生成攻略生成提示词"""
        
        # 获取目的地地理信息
        location_info = await self.map_service.geocode(destination)
        weather_info = None
        if location_info:
            weather_info = await self.map_service.get_weather(
                location=f"{location_info['latitude']},{location_info['longitude']}"
            )
        
        # 读取攻略概览模板
        overview_template = await self._load_template("overview")
        daily_template = await self._load_template("daily")
        
        # 构建提示词
        prompt = f"""
你是一位专业的旅游规划师，请根据以下要求生成详细的旅游攻略：

## 基本信息
- 目的地：{destination}
- 旅游天数：{days}天
- 出行人数：{group_size}人
- 旅行风格：{travel_style or '休闲'}
- 预算范围：{budget_range or '中等'}
- 出发日期：{start_date.strftime('%Y年%m月%d日') if start_date else '待定'}

## 地理位置信息
{f"经纬度：{location_info['latitude']:.4f}, {location_info['longitude']:.4f}" if location_info else "位置信息待查"}
{f"详细地址：{location_info['formatted_address']}" if location_info else ""}

## 天气信息
{self._format_weather_info(weather_info) if weather_info else "天气信息待查"}

## 特殊要求
{special_requirements or '无特殊要求'}

## 生成要求

请按照以下模板结构生成完整的旅游攻略：

### 1. 旅游概览文件（{destination}旅游概览.md）

{overview_template}

### 2. 每日行程文件（按日期命名，如：2025-06-27-第一天.md）

{daily_template}

## 重要说明

1. **地理位置查询**：对于所有景点、餐厅、住宿，请使用百度地图API进行精确定位
2. **距离和交通**：计算景点间的实际距离和交通时间
3. **实用信息**：提供准确的门票价格、开放时间、联系方式
4. **个性化建议**：根据旅行风格和预算提供针对性建议
5. **安全提示**：包含必要的安全注意事项和应急信息

请生成结构完整、信息详实的旅游攻略，确保实用性和可操作性。
"""
        
        return prompt.strip()
    
    async def _load_template(self, template_type: str) -> str:
        """加载模板内容"""
        try:
            template_files = {
                "overview": "旅游概览模板.md",
                "daily": "每日行程模板.md"
            }
            
            template_file = template_files.get(template_type)
            if not template_file:
                return f"# {template_type}模板\n模板内容待定"
            
            template_path = os.path.join(settings.TEMPLATES_PATH or "templates", template_file)
            
            # 如果模板文件不存在，从项目根目录的templates文件夹读取
            if not os.path.exists(template_path):
                template_path = os.path.join("templates", template_file)
            
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning("模板文件不存在", template_type=template_type, path=template_path)
                return f"# {template_type}模板\n模板内容待定"
                
        except Exception as e:
            logger.error("加载模板失败", template_type=template_type, error=str(e))
            return f"# {template_type}模板\n模板加载失败：{str(e)}"
    
    def _format_weather_info(self, weather_info: Dict[str, Any]) -> str:
        """格式化天气信息"""
        if not weather_info:
            return "天气信息待查"
        
        current = weather_info.get("current", {})
        forecast = weather_info.get("forecast", [])
        
        info = []
        if current:
            info.append(f"当前天气：{current.get('text', '未知')}，温度：{current.get('temperature', '未知')}°C")
        
        if forecast:
            info.append("未来几天天气预报：")
            for day in forecast[:5]:  # 只显示5天
                info.append(f"- {day.get('date', '')}: {day.get('text', '')}，{day.get('low', '')}°C - {day.get('high', '')}°C")
        
        return "\n".join(info)
    
    async def generate_itinerary(
        self,
        destination: str,
        days: int,
        user_id: int,
        travel_style: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        group_size: int = 2,
        start_date: Optional[datetime] = None,
        ai_provider: Optional[str] = None,
        special_requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成旅游攻略"""
        
        try:
            logger.info("开始生成旅游攻略", destination=destination, days=days, user_id=user_id)
            
            # 1. 创建攻略记录
            itinerary_data = {
                "title": f"{destination}{days}日游攻略",
                "destination": destination,
                "days": days,
                "user_id": user_id,
                "travel_style": travel_style,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "group_size": group_size,
                "start_date": start_date,
                "ai_provider": ai_provider or settings.DEFAULT_AI_PROVIDER,
                "status": ItineraryStatus.GENERATING,
                "progress": 0
            }
            
            # 2. 生成提示词
            budget_range = None
            if budget_min and budget_max:
                budget_range = f"{budget_min}-{budget_max}元"
            elif budget_min:
                budget_range = f"{budget_min}元以上"
            elif budget_max:
                budget_range = f"{budget_max}元以内"
            
            prompt = await self.generate_itinerary_prompt(
                destination=destination,
                days=days,
                travel_style=travel_style,
                budget_range=budget_range,
                group_size=group_size,
                start_date=start_date,
                special_requirements=special_requirements
            )
            
            itinerary_data["generation_prompt"] = prompt
            itinerary_data["progress"] = 20
            
            # 3. 调用AI生成攻略内容
            logger.info("调用AI生成攻略内容", ai_provider=ai_provider)
            
            overview_content = await self.ai_service.generate_completion(
                prompt=prompt,
                provider_name=ai_provider,
                temperature=0.8,
                max_tokens=8000
            )
            
            itinerary_data["overview_content"] = overview_content
            itinerary_data["overview_markdown"] = overview_content  # 假设AI直接生成Markdown
            itinerary_data["progress"] = 60
            
            # 4. 解析和增强内容
            await self._enhance_itinerary_content(itinerary_data)
            itinerary_data["progress"] = 80
            
            # 5. 生成每日行程
            daily_itineraries = await self._generate_daily_itineraries(
                itinerary_data, overview_content
            )
            itinerary_data["progress"] = 90
            
            # 6. 完成生成
            itinerary_data["status"] = ItineraryStatus.COMPLETED
            itinerary_data["progress"] = 100
            itinerary_data["completed_at"] = datetime.utcnow()
            
            logger.info("旅游攻略生成完成", destination=destination, days=days)
            
            return {
                "success": True,
                "itinerary": itinerary_data,
                "daily_itineraries": daily_itineraries,
                "message": "攻略生成完成"
            }
            
        except Exception as e:
            logger.error("旅游攻略生成失败", destination=destination, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": "攻略生成失败"
            }
    
    async def _enhance_itinerary_content(self, itinerary_data: Dict[str, Any]):
        """增强攻略内容 - 添加地理位置信息"""
        try:
            destination = itinerary_data["destination"]
            
            # 获取目的地中心坐标
            location_info = await self.map_service.geocode(destination)
            if location_info:
                itinerary_data["center_latitude"] = location_info["latitude"]
                itinerary_data["center_longitude"] = location_info["longitude"]
            
            # 这里可以添加更多增强逻辑，比如：
            # - 提取景点列表并获取详细信息
            # - 计算总预算
            # - 生成地图边界数据
            # - 添加标签
            
        except Exception as e:
            logger.error("增强攻略内容失败", error=str(e))
    
    async def _generate_daily_itineraries(
        self, 
        itinerary_data: Dict[str, Any], 
        overview_content: str
    ) -> List[Dict[str, Any]]:
        """生成每日详细行程"""
        daily_itineraries = []
        
        try:
            days = itinerary_data["days"]
            start_date = itinerary_data.get("start_date")
            
            for day_num in range(1, days + 1):
                current_date = None
                if start_date:
                    current_date = start_date + timedelta(days=day_num - 1)
                
                # 为每一天生成详细提示词
                daily_prompt = f"""
基于以下攻略概览，生成第{day_num}天的详细行程安排：

{overview_content}

请生成第{day_num}天的详细内容，包括：
1. 详细时间安排（每小时）
2. 景点介绍和游览建议
3. 交通路线和时间
4. 餐饮推荐
5. 住宿安排
6. 费用预算
7. 注意事项

格式要求：请使用Markdown格式，结构清晰，信息详实。
"""
                
                # 生成每日内容
                daily_content = await self.ai_service.generate_completion(
                    prompt=daily_prompt,
                    provider_name=itinerary_data.get("ai_provider"),
                    temperature=0.7,
                    max_tokens=4000
                )
                
                daily_data = {
                    "day_number": day_num,
                    "date": current_date,
                    "title": f"第{day_num}天",
                    "content": daily_content,
                    "markdown_content": daily_content,
                }
                
                daily_itineraries.append(daily_data)
                
        except Exception as e:
            logger.error("生成每日行程失败", error=str(e))
        
        return daily_itineraries
    
    async def get_generation_progress(self, itinerary_id: int) -> Dict[str, Any]:
        """获取生成进度"""
        # 这里应该从数据库查询实际进度
        # 暂时返回模拟数据
        return {
            "itinerary_id": itinerary_id,
            "progress": 100,
            "status": "completed",
            "message": "攻略生成完成"
        }
    
    async def validate_generation_request(
        self,
        destination: str,
        days: int,
        user_id: int
    ) -> Dict[str, Any]:
        """验证生成请求"""
        errors = []
        
        if not destination or len(destination.strip()) < 2:
            errors.append("目的地不能为空且至少包含2个字符")
        
        if days < 1 or days > settings.MAX_DAYS:
            errors.append(f"行程天数必须在1-{settings.MAX_DAYS}天之间")
        
        # 这里可以添加更多验证逻辑，比如：
        # - 检查用户权限
        # - 检查并发生成数量
        # - 检查目的地是否支持
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# 全局攻略服务实例
itinerary_service = ItineraryService() 