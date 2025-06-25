"""
模板数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class Template(Base):
    """模板模型"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, comment="模板名称")
    type = Column(String(50), nullable=False, comment="模板类型")  # overview, daily
    category = Column(String(50), comment="模板分类")
    
    # 模板内容
    content = Column(Text, nullable=False, comment="模板内容")
    description = Column(Text, comment="模板描述")
    
    # 模板变量
    variables = Column(JSON, comment="模板变量定义")
    default_values = Column(JSON, comment="默认值")
    
    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_system = Column(Boolean, default=False, comment="是否系统模板")
    version = Column(String(20), default="1.0", comment="版本号")
    
    # 使用统计
    usage_count = Column(Integer, default=0, comment="使用次数")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}', type='{self.type}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "category": self.category,
            "content": self.content,
            "description": self.description,
            "variables": self.variables,
            "default_values": self.default_values,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "version": self.version,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 