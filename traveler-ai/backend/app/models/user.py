"""
用户数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base
from app.core.config import Constants


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    GUEST = Constants.USER_ROLE_GUEST
    USER = Constants.USER_ROLE_USER
    PREMIUM = Constants.USER_ROLE_PREMIUM
    ADMIN = Constants.USER_ROLE_ADMIN


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    full_name = Column(String(100), comment="真实姓名")
    avatar_url = Column(String(500), comment="头像URL")
    phone = Column(String(20), comment="手机号")
    
    # 用户状态
    role = Column(Enum(UserRole), default=UserRole.USER, comment="用户角色")
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否验证邮箱")
    is_premium = Column(Boolean, default=False, comment="是否高级用户")
    
    # 用户偏好
    preferred_language = Column(String(10), default="zh-CN", comment="偏好语言")
    preferred_ai_provider = Column(String(20), default="ollama", comment="偏好AI服务商")
    
    # 使用统计
    itinerary_count = Column(Integer, default=0, comment="生成攻略数量")
    total_usage_time = Column(Integer, default=0, comment="总使用时长(秒)")
    last_login_at = Column(DateTime(timezone=True), comment="最后登录时间")
    last_active_at = Column(DateTime(timezone=True), comment="最后活跃时间")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 其他信息
    bio = Column(Text, comment="个人简介")
    location = Column(String(100), comment="所在地")
    website = Column(String(500), comment="个人网站")
    
    # 关联关系
    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self, include_sensitive=False):
        """转换为字典格式"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "phone": self.phone,
            "role": self.role.value if self.role else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_premium": self.is_premium,
            "preferred_language": self.preferred_language,
            "preferred_ai_provider": self.preferred_ai_provider,
            "itinerary_count": self.itinerary_count,
            "total_usage_time": self.total_usage_time,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "bio": self.bio,
            "location": self.location,
            "website": self.website,
        }
        
        if include_sensitive:
            data["hashed_password"] = self.hashed_password
            
        return data
    
    @property
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role == UserRole.ADMIN
    
    @property
    def can_generate_premium_itinerary(self) -> bool:
        """是否可以生成高级攻略"""
        return self.is_premium or self.is_admin
    
    @property
    def max_concurrent_generations(self) -> int:
        """最大并发生成数"""
        if self.is_admin:
            return 10
        elif self.is_premium:
            return 5
        else:
            return 3 