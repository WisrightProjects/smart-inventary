"""Box scan -> AI verification endpoint."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.camera.webcam_stream import camera_stream
from backend.inference.rtdetr_detector import detector
from backend.models.product_recognizer import count_products, recognize
from backend.schemas import VerifyRequest, VerifyResponse
from backend.utils.logger import get_logger
from backend.verification.verifier import verify
from database.models import Product, Transaction, VerificationLog, Worker
from database.session import get_db

router = APIRouter(prefix="/verify", tags=["verify"])
logger = get_logger("system")


@router.post("")
def verify_box(payload: VerifyRequest, db: Session = Depends(get_db)) -> VerifyResponse:
    product = db.query(Product).filter(Product.box_number == payload.box_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail=f"No product registered for box '{payload.box_id}'")

    worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
    if worker is None:
        raise HTTPException(status_code=404, detail=f"Worker {payload.worker_id} not found")

    frame = camera_stream.get_frame()
    if frame is None:
        raise HTTPException(status_code=503, detail="Camera not available. Start the camera first.")

    raw_detections = detector.detect(frame)
    recognized = recognize(raw_detections)
    detected_counts = count_products(recognized)
    expected_counts = {product.name: product.current_stock}

    result = verify(expected_counts, detected_counts)
    avg_confidence = (
        sum(r.confidence for r in recognized) / len(recognized) if recognized else 0.0
    )

    transaction = Transaction(
        worker_id=worker.id,
        product_id=product.id,
        expected_quantity=expected_counts[product.name],
        detected_quantity=sum(detected_counts.values()),
        verification_status=result.status.value,
        confidence_score=round(avg_confidence, 3),
    )
    db.add(transaction)
    db.flush()

    db.add(
        VerificationLog(
            transaction_id=transaction.id,
            box_id=payload.box_id,
            expected_json=json.dumps(expected_counts),
            detected_json=json.dumps(detected_counts),
            result=result.status.value,
        )
    )
    db.commit()

    logger.info("Verified box %s -> %s", payload.box_id, result.status.value)

    return VerifyResponse(
        status=result.status.value,
        expected=result.expected,
        detected=result.detected,
        details=result.details,
        confidence=round(avg_confidence, 3),
        transaction_id=transaction.id,
    )
