"""Recommendation schemas"""

from pydantic import BaseModel
from typing import List


class ProductRecommendation(BaseModel):
    """Schema for a single product recommendation"""

    product_id: int
    score: float
    reason: str = "Personalized recommendation"


class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""

    user_id: int = None
    recommendations: List[ProductRecommendation]
    strategy: str = "hybrid"
    total_recommendations: int
