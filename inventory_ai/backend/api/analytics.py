"""Analytics endpoints backing dashboard charts."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.analytics import analytics_service as svc
from database.session import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/daily-verifications")
def daily_verifications(days: int = 30, db: Session = Depends(get_db)) -> list[dict]:
    return svc.daily_verifications(db, days)


@router.get("/accuracy")
def accuracy(db: Session = Depends(get_db)) -> dict:
    return svc.verification_accuracy(db)


@router.get("/top-products")
def top_products(limit: int = 10, db: Session = Depends(get_db)) -> list[dict]:
    return svc.top_products(db, limit)


@router.get("/mismatch-percentage")
def mismatch_percentage(db: Session = Depends(get_db)) -> dict:
    return svc.mismatch_percentage(db)


@router.get("/status-breakdown")
def status_breakdown(db: Session = Depends(get_db)) -> list[dict]:
    return svc.status_breakdown(db)


@router.get("/stock-movement")
def stock_movement(limit: int = 20, db: Session = Depends(get_db)) -> list[dict]:
    return svc.stock_movement(db, limit)
