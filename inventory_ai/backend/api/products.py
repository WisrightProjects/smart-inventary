"""Product catalog endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas import ProductOut
from database.models import Product
from database.session import get_db

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products(category: str | None = None, db: Session = Depends(get_db)) -> list[ProductOut]:
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    return list(query.order_by(Product.name).all())


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductOut:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
