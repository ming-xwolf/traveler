"""
数据模型包
"""
from app.models.user import User
from app.models.itinerary import Itinerary, ItineraryDay
from app.models.template import Template
from app.models.location import Location

__all__ = [
    "User",
    "Itinerary", 
    "ItineraryDay",
    "Template",
    "Location"
] 