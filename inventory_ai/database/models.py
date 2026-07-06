"""SQLAlchemy ORM models for the inventory verification system."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False, index=True)
    rack = Column(String, nullable=False)
    box_number = Column(String, nullable=False)
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=5)
    maximum_stock = Column(Integer, default=100)

    transactions = relationship("Transaction", back_populates="product")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="worker")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    expected_quantity = Column(Integer, nullable=False)
    detected_quantity = Column(Integer, nullable=False)
    verification_status = Column(String, nullable=False, index=True)
    confidence_score = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=dt.datetime.utcnow, index=True)

    worker = relationship("Worker", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")
    verification_logs = relationship("VerificationLog", back_populates="transaction")


class VerificationLog(Base):
    __tablename__ = "verification_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    box_id = Column(String, nullable=False)
    expected_json = Column(String, nullable=False)
    detected_json = Column(String, nullable=False)
    result = Column(String, nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    transaction = relationship("Transaction", back_populates="verification_logs")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, default=dt.datetime.utcnow)

    product = relationship("Product")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    alert_type = Column(String, nullable=False)  # low_stock, mismatch, camera_offline
    message = Column(String, nullable=False)
    severity = Column(String, default="warning")  # info, warning, critical
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    resolved = Column(Integer, default=0)  # boolean flag (SQLite has no bool type)

    product = relationship("Product")
