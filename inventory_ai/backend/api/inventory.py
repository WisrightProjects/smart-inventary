"""Current stock / low-stock endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.schemas import ProductOut
from database.models import Product
from database.session import get_db

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("")
def list_inventory(db: Session = Depends(get_db)) -> list[ProductOut]:
    return list(db.query(Product).order_by(Product.category, Product.name).all())


@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db)) -> list[ProductOut]:
    products = db.query(Product).all()
    return [p for p in products if p.current_stock <= p.minimum_stock]
