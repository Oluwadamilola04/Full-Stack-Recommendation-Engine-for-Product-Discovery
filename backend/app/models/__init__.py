"""Database models"""

from app.models.user import User
from app.models.product import Product
from app.models.interaction import UserProductInteraction
from app.models.recommendation import RecommendationCache

__all__ = ["User", "Product", "UserProductInteraction", "RecommendationCache"]
