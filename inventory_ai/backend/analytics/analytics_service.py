"""Aggregation queries powering the analytics dashboard charts."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import Product, Transaction


def daily_verifications(db: Session, days: int = 30) -> list[dict]:
    since = dt.datetime.utcnow() - dt.timedelta(days=days)
    rows = (
        db.query(
            func.date(Transaction.timestamp).label("day"),
            func.count(Transaction.id).label("count"),
        )
        .filter(Transaction.timestamp >= since)
        .group_by("day")
        .order_by("day")
        .all()
    )
    return [{"date": row.day, "count": row.count} for row in rows]


def verification_accuracy(db: Session) -> dict:
    total = db.query(func.count(Transaction.id)).scalar() or 0
    verified = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.verification_status == "VERIFIED")
        .scalar()
        or 0
    )
    accuracy = round((verified / total) * 100, 2) if total else 0.0
    return {"total": total, "verified": verified, "accuracy_percent": accuracy}


def top_products(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.query(Product.name, func.count(Transaction.id).label("count"))
        .join(Transaction, Transaction.product_id == Product.id)
        .group_by(Product.name)
        .order_by(func.count(Transaction.id).desc())
        .limit(limit)
        .all()
    )
    return [{"product": row.name, "count": row.count} for row in rows]


def mismatch_percentage(db: Session) -> dict:
    total = db.query(func.count(Transaction.id)).scalar() or 0
    mismatches = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.verification_status != "VERIFIED")
        .scalar()
        or 0
    )
    percent = round((mismatches / total) * 100, 2) if total else 0.0
    return {"total": total, "mismatches": mismatches, "mismatch_percent": percent}


def status_breakdown(db: Session) -> list[dict]:
    rows = (
        db.query(Transaction.verification_status, func.count(Transaction.id).label("count"))
        .group_by(Transaction.verification_status)
        .all()
    )
    return [{"status": row.verification_status, "count": row.count} for row in rows]


def stock_movement(db: Session, limit: int = 20) -> list[dict]:
    rows = (
        db.query(Product.name, Product.current_stock, Product.minimum_stock, Product.maximum_stock)
        .order_by(Product.current_stock.asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "product": row.name,
            "current_stock": row.current_stock,
            "minimum_stock": row.minimum_stock,
            "maximum_stock": row.maximum_stock,
        }
        for row in rows
    ]
