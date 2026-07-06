"""Transaction / verification history endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.schemas import TransactionOut
from database.models import Transaction
from database.session import get_db

router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def list_history(
    status: str | None = None,
    worker_id: int | None = None,
    product_id: int | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[TransactionOut]:
    query = db.query(Transaction)
    if status:
        query = query.filter(Transaction.verification_status == status)
    if worker_id:
        query = query.filter(Transaction.worker_id == worker_id)
    if product_id:
        query = query.filter(Transaction.product_id == product_id)
    return list(query.order_by(Transaction.timestamp.desc()).limit(limit).all())
