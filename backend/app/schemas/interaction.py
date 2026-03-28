"""Interaction schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class InteractionCreate(BaseModel):
    """Schema for creating an interaction"""

    user_id: int
    product_id: int
    interaction_type: str  # view, click, add_to_cart, purchase
    rating: Optional[float] = None


class InteractionResponse(BaseModel):
    """Schema for interaction response"""

    id: int
    user_id: int
    product_id: int
    interaction_type: str
    rating: Optional[float] = None
    interaction_weight: float
    timestamp: datetime

    class Config:
        from_attributes = True
