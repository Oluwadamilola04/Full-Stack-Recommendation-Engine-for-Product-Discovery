"""Product schemas"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """Schema for creating a product"""

    source_id: Optional[int] = None
    prod_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: str
    category_raw: Optional[str] = None
    brand: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[float] = None
    tags: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    average_rating: Optional[float] = None
    review_count: Optional[int] = None


class ProductResponse(BaseModel):
    """Schema for product response"""

    id: int
    source_id: Optional[int] = None
    prod_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    category: str
    category_raw: Optional[str] = None
    brand: Optional[str] = None
    subcategory: Optional[str] = None
    price: Optional[float] = None
    tags: Optional[List[str]] = None
    average_rating: float
    review_count: int
    image_urls: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True
