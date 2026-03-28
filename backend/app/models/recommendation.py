"""Recommendation Cache model"""

from sqlalchemy import Column, Integer, JSON, DateTime, String
from sqlalchemy.sql import func
from app.core.database import Base


class RecommendationCache(Base):
    """Model for caching recommendation results"""

    __tablename__ = "recommendation_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    recommendation_type = Column(String(50), nullable=False)
    product_ids = Column(JSON, nullable=False)
    scores = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    class Config:
        from_attributes = True
