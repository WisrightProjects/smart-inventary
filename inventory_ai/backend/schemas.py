"""Pydantic response/request schemas shared across API routers."""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    rack: str
    box_number: str
    current_stock: int
    minimum_stock: int
    maximum_stock: int

    class Config:
        from_attributes = True


class WorkerOut(BaseModel):
    id: int
    name: str
    department: str

    class Config:
        from_attributes = True


class TransactionOut(BaseModel):
    id: int
    worker_id: int
    product_id: int
    expected_quantity: int
    detected_quantity: int
    verification_status: str
    confidence_score: float
    timestamp: dt.datetime

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: int
    product_id: int | None
    alert_type: str
    message: str
    severity: str
    created_at: dt.datetime
    resolved: int

    class Config:
        from_attributes = True


class VerifyRequest(BaseModel):
    box_id: str
    worker_id: int


class VerifyResponse(BaseModel):
    status: str
    expected: dict[str, int]
    detected: dict[str, int]
    details: str
    confidence: float
    transaction_id: int


class CameraStatusOut(BaseModel):
    connected: bool
    fps: float
    frame_count: int
    last_error: str | None
    source: str


class LiveDetectionOut(BaseModel):
    camera: CameraStatusOut
    detections: list[dict]
    counts: dict[str, int]
