"""Worker directory endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.schemas import WorkerOut
from database.models import Worker
from database.session import get_db

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("")
def list_workers(db: Session = Depends(get_db)) -> list[WorkerOut]:
    return list(db.query(Worker).order_by(Worker.name).all())
