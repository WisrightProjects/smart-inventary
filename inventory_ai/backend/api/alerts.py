"""Alert feed endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.schemas import AlertOut
from database.models import Alert
from database.session import get_db

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
def list_alerts(resolved: bool | None = None, limit: int = 50, db: Session = Depends(get_db)) -> list[AlertOut]:
    query = db.query(Alert)
    if resolved is not None:
        query = query.filter(Alert.resolved == int(resolved))
    return list(query.order_by(Alert.created_at.desc()).limit(limit).all())
