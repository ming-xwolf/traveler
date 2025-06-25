"""
地理位置数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Index
from sqlalchemy.sql import func

from app.core.database import Base


class Location(Base):
    """地理位置模型"""
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True, comment="地点名称")
    name_en = Column(String(200), comment="英文名称")
    address = Column(String(500), comment="详细地址")
    
    # 地理坐标
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    
    # 地理层级
    country = Column(String(100), comment="国家")
    province = Column(String(100), comment="省份/州")
    city = Column(String(100), comment="城市")
    district = Column(String(100), comment="区/县")
    
    # 地点类型
    type = Column(String(50), comment="地点类型")  # attraction, hotel, restaurant, transport
    category = Column(String(100), comment="分类")
    subcategory = Column(String(100), comment="子分类")
    
    # 地点信息
    description = Column(String(1000), comment="描述")
    rating = Column(Float, comment="评分")
    price_level = Column(Integer, comment="价格等级")
    phone = Column(String(50), comment="联系电话")
    website = Column(String(500), comment="官方网站")
    
    # 营业信息
    opening_hours = Column(JSON, comment="营业时间")
    is_open_24h = Column(Integer, default=0, comment="是否24小时营业")
    
    # 额外信息
    tags = Column(JSON, comment="标签列表")
    amenities = Column(JSON, comment="设施服务")
    photos = Column(JSON, comment="图片列表")
    
    # 百度地图信息
    baidu_poi_id = Column(String(100), comment="百度POI ID")
    baidu_uid = Column(String(100), comment="百度UID")
    baidu_data = Column(JSON, comment="百度地图原始数据")
    
    # 统计信息
    search_count = Column(Integer, default=0, comment="搜索次数")
    reference_count = Column(Integer, default=0, comment="被引用次数")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 创建地理位置索引
    __table_args__ = (
        Index('idx_location_coordinates', 'latitude', 'longitude'),
        Index('idx_location_region', 'country', 'province', 'city'),
        Index('idx_location_type', 'type', 'category'),
    )
    
    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', lat={self.latitude}, lng={self.longitude})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "name_en": self.name_en,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country": self.country,
            "province": self.province,
            "city": self.city,
            "district": self.district,
            "type": self.type,
            "category": self.category,
            "subcategory": self.subcategory,
            "description": self.description,
            "rating": self.rating,
            "price_level": self.price_level,
            "phone": self.phone,
            "website": self.website,
            "opening_hours": self.opening_hours,
            "is_open_24h": self.is_open_24h,
            "tags": self.tags,
            "amenities": self.amenities,
            "photos": self.photos,
            "baidu_poi_id": self.baidu_poi_id,
            "baidu_uid": self.baidu_uid,
            "search_count": self.search_count,
            "reference_count": self.reference_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def get_coordinates(self):
        """获取坐标元组"""
        return (self.latitude, self.longitude)
    
    def get_full_address(self):
        """获取完整地址"""
        parts = [self.country, self.province, self.city, self.district, self.address]
        return ", ".join([part for part in parts if part])
    
    @property
    def location_key(self):
        """生成位置唯一键"""
        return f"{self.name}_{self.latitude}_{self.longitude}" 