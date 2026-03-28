"""Recommendation endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.recommender import RecommenderService
from app.schemas.recommendation import RecommendationResponse

router = APIRouter()
recommender_service = RecommenderService()


@router.get("/user/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: int,
    limit: int = Query(10, ge=1, le=100),
    strategy: str = Query("hybrid", pattern="^(collaborative|content|hybrid)$"),
    db: Session = Depends(get_db),
):
    """Get personalized recommendations for a user"""
    try:
        recommendations = await recommender_service.get_recommendations(
            user_id=user_id,
            limit=limit,
            strategy=strategy,
            db=db,
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{product_id}", response_model=RecommendationResponse)
async def get_similar_products(
    product_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get similar products based on content similarity"""
    try:
        similar_products = await recommender_service.get_similar_products(
            product_id=product_id,
            limit=limit,
            db=db,
        )
        return similar_products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending", response_model=RecommendationResponse)
async def get_trending_products(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get trending products based on recent interactions"""
    try:
        trending = await recommender_service.get_trending_products(
            limit=limit,
            db=db,
        )
        return trending
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
