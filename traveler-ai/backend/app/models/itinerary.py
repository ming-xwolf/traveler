"""
旅游攻略数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base
from app.core.config import Constants


class ItineraryStatus(str, enum.Enum):
    """攻略状态枚举"""
    PENDING = Constants.ITINERARY_STATUS_PENDING
    GENERATING = Constants.ITINERARY_STATUS_GENERATING
    COMPLETED = Constants.ITINERARY_STATUS_COMPLETED
    FAILED = Constants.ITINERARY_STATUS_FAILED


class ExportFormat(str, enum.Enum):
    """导出格式枚举"""
    MARKDOWN = Constants.EXPORT_FORMAT_MARKDOWN
    HTML = Constants.EXPORT_FORMAT_HTML
    PDF = Constants.EXPORT_FORMAT_PDF


class Itinerary(Base):
    """旅游攻略模型"""
    __tablename__ = "itineraries"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="攻略标题")
    destination = Column(String(100), nullable=False, index=True, comment="目的地")
    days = Column(Integer, nullable=False, comment="旅游天数")
    
    # 用户信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    
    # 基本信息
    description = Column(Text, comment="攻略描述")
    budget_min = Column(Float, comment="预算下限")
    budget_max = Column(Float, comment="预算上限")
    travel_style = Column(String(50), comment="旅行风格")  # 休闲、深度、探险等
    group_size = Column(Integer, default=2, comment="团体人数")
    
    # 时间信息
    start_date = Column(DateTime(timezone=True), comment="开始日期")
    end_date = Column(DateTime(timezone=True), comment="结束日期")
    season = Column(String(20), comment="旅行季节")
    
    # 生成配置
    ai_provider = Column(String(20), comment="AI服务提供商")
    ai_model = Column(String(50), comment="AI模型")
    generation_prompt = Column(Text, comment="生成提示词")
    generation_config = Column(JSON, comment="生成配置")
    
    # 状态信息
    status = Column(Enum(ItineraryStatus), default=ItineraryStatus.PENDING, comment="攻略状态")
    progress = Column(Integer, default=0, comment="生成进度(0-100)")
    error_message = Column(Text, comment="错误信息")
    
    # 内容数据
    overview_content = Column(Text, comment="概览内容")
    overview_markdown = Column(Text, comment="概览Markdown")
    overview_html = Column(Text, comment="概览HTML")
    
    # 统计信息
    view_count = Column(Integer, default=0, comment="查看次数")
    like_count = Column(Integer, default=0, comment="点赞次数")
    share_count = Column(Integer, default=0, comment="分享次数")
    download_count = Column(Integer, default=0, comment="下载次数")
    
    # 地理信息
    center_latitude = Column(Float, comment="中心纬度")
    center_longitude = Column(Float, comment="中心经度")
    bounds_data = Column(JSON, comment="地理边界数据")
    
    # 元数据
    tags = Column(JSON, comment="标签列表")
    featured_attractions = Column(JSON, comment="特色景点列表")
    cost_breakdown = Column(JSON, comment="费用明细")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    
    # 关联关系
    user = relationship("User", back_populates="itineraries")
    itinerary_days = relationship("ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Itinerary(id={self.id}, title='{self.title}', destination='{self.destination}')>"
    
    def to_dict(self, include_content=False):
        """转换为字典格式"""
        data = {
            "id": self.id,
            "title": self.title,
            "destination": self.destination,
            "days": self.days,
            "user_id": self.user_id,
            "description": self.description,
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "travel_style": self.travel_style,
            "group_size": self.group_size,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "season": self.season,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "error_message": self.error_message,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "share_count": self.share_count,
            "download_count": self.download_count,
            "center_latitude": self.center_latitude,
            "center_longitude": self.center_longitude,
            "bounds_data": self.bounds_data,
            "tags": self.tags,
            "featured_attractions": self.featured_attractions,
            "cost_breakdown": self.cost_breakdown,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
        
        if include_content:
            data.update({
                "overview_content": self.overview_content,
                "overview_markdown": self.overview_markdown,
                "overview_html": self.overview_html,
                "generation_prompt": self.generation_prompt,
                "generation_config": self.generation_config,
            })
            
        return data
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == ItineraryStatus.COMPLETED
    
    @property
    def is_generating(self) -> bool:
        """是否正在生成"""
        return self.status == ItineraryStatus.GENERATING
    
    @property
    def is_failed(self) -> bool:
        """是否生成失败"""
        return self.status == ItineraryStatus.FAILED
    
    @property
    def total_budget(self) -> float:
        """总预算(取中值)"""
        if self.budget_min is not None and self.budget_max is not None:
            return (self.budget_min + self.budget_max) / 2
        return self.budget_max or self.budget_min or 0.0


class ItineraryDay(Base):
    """每日行程模型"""
    __tablename__ = "itinerary_days"
    
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True, comment="攻略ID")
    day_number = Column(Integer, nullable=False, comment="第几天")
    date = Column(DateTime(timezone=True), comment="日期")
    
    # 基本信息
    title = Column(String(200), comment="每日标题")
    summary = Column(Text, comment="每日概要")
    theme = Column(String(100), comment="主题")
    
    # 住宿信息
    accommodation_name = Column(String(200), comment="住宿名称")
    accommodation_address = Column(String(500), comment="住宿地址")
    accommodation_latitude = Column(Float, comment="住宿纬度")
    accommodation_longitude = Column(Float, comment="住宿经度")
    accommodation_price = Column(Float, comment="住宿价格")
    
    # 内容数据
    content = Column(Text, comment="详细内容")
    markdown_content = Column(Text, comment="Markdown内容")
    html_content = Column(Text, comment="HTML内容")
    
    # 活动安排
    activities = Column(JSON, comment="活动列表")
    attractions = Column(JSON, comment="景点列表")
    restaurants = Column(JSON, comment="餐厅列表")
    
    # 交通信息
    transportation = Column(JSON, comment="交通安排")
    total_distance = Column(Float, comment="总里程(公里)")
    total_duration = Column(Integer, comment="总时长(分钟)")
    
    # 费用信息
    estimated_cost = Column(Float, comment="预估费用")
    cost_breakdown = Column(JSON, comment="费用明细")
    
    # 实用信息
    weather_info = Column(JSON, comment="天气信息")
    tips = Column(JSON, comment="小贴士列表")
    warnings = Column(JSON, comment="注意事项")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    itinerary = relationship("Itinerary", back_populates="itinerary_days")
    
    def __repr__(self):
        return f"<ItineraryDay(id={self.id}, itinerary_id={self.itinerary_id}, day_number={self.day_number})>"
    
    def to_dict(self, include_content=False):
        """转换为字典格式"""
        data = {
            "id": self.id,
            "itinerary_id": self.itinerary_id,
            "day_number": self.day_number,
            "date": self.date.isoformat() if self.date else None,
            "title": self.title,
            "summary": self.summary,
            "theme": self.theme,
            "accommodation_name": self.accommodation_name,
            "accommodation_address": self.accommodation_address,
            "accommodation_latitude": self.accommodation_latitude,
            "accommodation_longitude": self.accommodation_longitude,
            "accommodation_price": self.accommodation_price,
            "activities": self.activities,
            "attractions": self.attractions,
            "restaurants": self.restaurants,
            "transportation": self.transportation,
            "total_distance": self.total_distance,
            "total_duration": self.total_duration,
            "estimated_cost": self.estimated_cost,
            "cost_breakdown": self.cost_breakdown,
            "weather_info": self.weather_info,
            "tips": self.tips,
            "warnings": self.warnings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_content:
            data.update({
                "content": self.content,
                "markdown_content": self.markdown_content,
                "html_content": self.html_content,
            })
            
        return data 