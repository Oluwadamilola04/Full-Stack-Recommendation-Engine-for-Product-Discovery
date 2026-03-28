"""Tests for recommendation service"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.product import Product
from app.models.interaction import UserProductInteraction
from app.services.recommender import RecommenderService


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Add test data
    users = [
        User(username="user1", email="user1@test.com", hashed_password="pwd1"),
        User(username="user2", email="user2@test.com", hashed_password="pwd2"),
    ]
    db.add_all(users)
    db.commit()
    
    products = [
        Product(name="Product 1", category="Electronics", price=100.0),
        Product(name="Product 2", category="Electronics", price=150.0),
        Product(name="Product 3", category="Clothing", price=50.0),
    ]
    db.add_all(products)
    db.commit()
    
    interactions = [
        UserProductInteraction(user_id=1, product_id=1, interaction_type="purchase", rating=5.0),
        UserProductInteraction(user_id=1, product_id=2, interaction_type="view"),
        UserProductInteraction(user_id=2, product_id=1, interaction_type="purchase", rating=4.0),
    ]
    db.add_all(interactions)
    db.commit()
    
    yield db
    db.close()


@pytest.mark.asyncio
async def test_get_recommendations(test_db):
    """Test getting recommendations"""
    recommender = RecommenderService()
    
    recommendations = await recommender.get_recommendations(
        user_id=1,
        limit=5,
        strategy="hybrid",
        db=test_db
    )
    
    assert recommendations is not None
    assert recommendations.user_id == 1
    assert len(recommendations.recommendations) <= 5


@pytest.mark.asyncio
async def test_similar_products(test_db):
    """Test getting similar products"""
    recommender = RecommenderService()
    
    similar = await recommender.get_similar_products(
        product_id=1,
        limit=5,
        db=test_db
    )
    
    assert similar is not None
    assert similar.strategy == "content"


@pytest.mark.asyncio
async def test_trending_products(test_db):
    """Test getting trending products"""
    recommender = RecommenderService()
    
    trending = await recommender.get_trending_products(
        limit=5,
        db=test_db
    )
    
    assert trending is not None
    assert trending.strategy == "trending"
