"""API v1 routes"""

from fastapi import APIRouter

from app.api.v1.endpoints import recommendations, products, users, interactions

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
