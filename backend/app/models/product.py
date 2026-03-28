"""Product model"""

from sqlalchemy import BigInteger, Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Product(Base):
    """Product model for storing product information"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(BigInteger, unique=False, index=True, nullable=True)
    prod_id = Column(Integer, unique=True, index=True, nullable=True)
    name = Column(String(255), index=True, nullable=False)
    brand = Column(String(255), index=True, nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), index=True, nullable=False)
    category_raw = Column(Text, nullable=True)
    subcategory = Column(String(100), nullable=True)
    price = Column(Float, nullable=True)
    tags = Column(JSON, nullable=True)
    average_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    image_urls = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    class Config:
        from_attributes = True
