"""Data synchronization endpoints between local and cloud databases."""
from __future__ import annotations

import datetime as dt
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.utils.logger import get_logger
from database.models import Product, Worker, Transaction, VerificationLog, Alert
from database.session import get_db, SessionLocal

router = APIRouter(prefix="/sync", tags=["sync"])
logger = get_logger("sync")


class SyncProduct(BaseModel):
    sku: str
    current_stock: int


class SyncTransaction(BaseModel):
    id: int  # local ID
    worker_name: str
    worker_department: str
    product_sku: str
    expected_quantity: int
    detected_quantity: int
    verification_status: str
    confidence_score: float
    timestamp: dt.datetime


class SyncVerificationLog(BaseModel):
    local_transaction_id: int
    box_id: str
    expected_json: str
    detected_json: str
    result: str
    created_at: dt.datetime


class SyncPayload(BaseModel):
    products: List[SyncProduct]
    transactions: List[SyncTransaction]
    logs: List[SyncVerificationLog]


@router.post("/push")
def push_sync(payload: SyncPayload, db: Session = Depends(get_db)) -> dict:
    """Receives local database updates and merges them into the remote database."""
    try:
        # 1. Sync product stock levels
        for p_data in payload.products:
            prod = db.query(Product).filter(Product.sku == p_data.sku).first()
            if prod:
                prod.current_stock = p_data.current_stock

        # 2. Map workers
        worker_map = {}
        all_workers = db.query(Worker).all()
        for w in all_workers:
            worker_map[w.name.lower()] = w.id

        # 3. Map products
        product_map = {}
        all_products = db.query(Product).all()
        for p in all_products:
            product_map[p.sku.lower()] = p.id

        # 4. Sync transactions and map local transaction ID to remote transaction ID
        tx_id_map = {}
        for tx_data in payload.transactions:
            remote_prod_id = product_map.get(tx_data.product_sku.lower())
            if not remote_prod_id:
                logger.warning("Product SKU %s not found in remote DB, skipping transaction %d", tx_data.product_sku, tx_data.id)
                continue

            remote_worker_id = worker_map.get(tx_data.worker_name.lower())
            if not remote_worker_id:
                new_worker = Worker(name=tx_data.worker_name, department=tx_data.worker_department)
                db.add(new_worker)
                db.flush()
                worker_map[tx_data.worker_name.lower()] = new_worker.id
                remote_worker_id = new_worker.id

            # Check if this transaction already exists (by timestamp, product, worker)
            existing = db.query(Transaction).filter(
                Transaction.timestamp == tx_data.timestamp,
                Transaction.product_id == remote_prod_id,
                Transaction.worker_id == remote_worker_id
            ).first()

            if existing:
                tx_id_map[tx_data.id] = existing.id
            else:
                new_tx = Transaction(
                    worker_id=remote_worker_id,
                    product_id=remote_prod_id,
                    expected_quantity=tx_data.expected_quantity,
                    detected_quantity=tx_data.detected_quantity,
                    verification_status=tx_data.verification_status,
                    confidence_score=tx_data.confidence_score,
                    timestamp=tx_data.timestamp
                )
                db.add(new_tx)
                db.flush()
                tx_id_map[tx_data.id] = new_tx.id

                # Also generate remote mismatch alert if necessary
                if tx_data.verification_status != "VERIFIED":
                    existing_alert = db.query(Alert).filter(
                        Alert.product_id == remote_prod_id,
                        Alert.created_at == tx_data.timestamp
                    ).first()
                    if not existing_alert:
                        prod = db.query(Product).filter(Product.id == remote_prod_id).first()
                        db.add(Alert(
                            product_id=remote_prod_id,
                            alert_type="mismatch",
                            message=f"{tx_data.verification_status.replace('_', ' ').title()} detected for {prod.name if prod else ''} (Box {prod.box_number if prod else ''})",
                            severity="critical" if tx_data.verification_status in ("WRONG_PRODUCT", "MISSING_PRODUCT") else "warning",
                            created_at=tx_data.timestamp
                        ))

        # 5. Sync verification logs
        for log_data in payload.logs:
            remote_tx_id = tx_id_map.get(log_data.local_transaction_id)
            if not remote_tx_id:
                continue

            existing_log = db.query(VerificationLog).filter(
                VerificationLog.transaction_id == remote_tx_id
            ).first()

            if not existing_log:
                db.add(VerificationLog(
                    transaction_id=remote_tx_id,
                    box_id=log_data.box_id,
                    expected_json=log_data.expected_json,
                    detected_json=log_data.detected_json,
                    result=log_data.result,
                    created_at=log_data.created_at
                ))

        db.commit()
        return {"status": "ok", "message": f"Successfully synced {len(payload.transactions)} transactions and {len(payload.products)} products."}
    except Exception as e:
        db.rollback()
        logger.exception("Sync push failed")
        raise HTTPException(status_code=500, detail=str(e))


def trigger_sync_push() -> dict:
    """Queries all local products, transactions, and logs, and pushes them to the remote server."""
    import httpx
    db = SessionLocal()
    try:
        # Load products
        products = db.query(Product).all()
        sync_products = [{"sku": p.sku, "current_stock": p.current_stock} for p in products]

        # Load transactions
        transactions = db.query(Transaction).all()
        sync_txs = []
        for tx in transactions:
            sync_txs.append({
                "id": tx.id,
                "worker_name": tx.worker.name,
                "worker_department": tx.worker.department,
                "product_sku": tx.product.sku,
                "expected_quantity": tx.expected_quantity,
                "detected_quantity": tx.detected_quantity,
                "verification_status": tx.verification_status,
                "confidence_score": tx.confidence_score,
                "timestamp": tx.timestamp.isoformat()
            })

        # Load logs
        logs = db.query(VerificationLog).all()
        sync_logs = [{
            "local_transaction_id": log.transaction_id,
            "box_id": log.box_id,
            "expected_json": log.expected_json,
            "detected_json": log.detected_json,
            "result": log.result,
            "created_at": log.created_at.isoformat()
        } for log in logs]

        payload = {
            "products": sync_products,
            "transactions": sync_txs,
            "logs": sync_logs
        }

        url = f"{settings.remote_sync_url}/sync/push"
        logger.info("Triggering cloud push sync to %s...", url)
        resp = httpx.post(url, json=payload, timeout=15.0)
        resp.raise_for_status()
        res_data = resp.json()
        logger.info("Successfully pushed local data to remote: %s", res_data)
        return {"status": "ok", "message": res_data.get("message", "Sync complete")}
    except Exception as e:
        logger.error("Failed to push local data to remote: %s", e)
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@router.post("/trigger")
def trigger_sync() -> dict:
    """Local endpoint to manually trigger a synchronization push to the cloud."""
    return trigger_sync_push()
