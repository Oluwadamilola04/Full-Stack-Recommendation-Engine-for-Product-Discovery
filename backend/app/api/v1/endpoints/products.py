"""Product endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse

router = APIRouter()


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 10,
    category: str = None,
    db: Session = Depends(get_db),
):
    """List all products with optional filtering"""
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    db_product = Product(**product.model_dump(exclude_none=True))
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
