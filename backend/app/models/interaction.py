"""User-Product Interaction model"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class UserProductInteraction(Base):
    """Model for storing user-product interactions"""

    __tablename__ = "user_product_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False)
    interaction_type = Column(String(50), index=True, nullable=False)  # view, click, add_to_cart, purchase
    rating = Column(Float, nullable=True)
    interaction_weight = Column(Float, default=1.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    class Config:
        from_attributes = True
