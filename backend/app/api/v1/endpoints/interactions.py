"""User-Product Interaction endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.interaction import UserProductInteraction
from app.schemas.interaction import InteractionCreate, InteractionResponse

router = APIRouter()


@router.post("/", response_model=InteractionResponse)
async def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db),
):
    """Record a user-product interaction"""
    # Map interaction type to weight
    weight_mapping = {
        "view": 1.0,
        "click": 2.0,
        "add_to_cart": 3.0,
        "purchase": 5.0,
    }

    db_interaction = UserProductInteraction(
        user_id=interaction.user_id,
        product_id=interaction.product_id,
        interaction_type=interaction.interaction_type,
        rating=interaction.rating,
        interaction_weight=weight_mapping.get(interaction.interaction_type, 1.0),
    )

    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction


@router.get("/user/{user_id}", response_model=list[InteractionResponse])
async def get_user_interactions(
    user_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all interactions for a user"""
    interactions = (
        db.query(UserProductInteraction)
        .filter(UserProductInteraction.user_id == user_id)
        .order_by(UserProductInteraction.timestamp.desc())
        .limit(limit)
        .all()
    )
    return interactions
