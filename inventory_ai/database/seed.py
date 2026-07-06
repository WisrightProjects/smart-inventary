"""Generates dummy products, workers, and verification transactions.

Run with: python -m database.seed
"""
from __future__ import annotations

import datetime as dt
import json
import random

from faker import Faker

from backend.config.settings import settings
from backend.utils.logger import get_logger
from database.product_catalog import PRODUCT_CATALOG
from database.models import Alert, Product, Transaction, VerificationLog, Worker
from database.session import SessionLocal, init_db

logger = get_logger("database")
fake = Faker()

DEPARTMENTS = ["Warehouse", "Quality Control", "Dispatch", "Receiving"]
VERIFICATION_STATUSES = [
    "VERIFIED",
    "WRONG_PRODUCT",
    "MISSING_PRODUCT",
    "EXTRA_PRODUCT",
    "UNEXPECTED_PRODUCT",
    "MIXED_PRODUCTS",
]
# Weighted so most transactions are healthy, matching a realistic warehouse.
STATUS_WEIGHTS = [55, 10, 12, 10, 8, 5]


def seed_products(session, count: int) -> list[Product]:
    names = list(PRODUCT_CATALOG.keys())
    products: list[Product] = []
    for i in range(count):
        name = names[i % len(names)]
        category = PRODUCT_CATALOG[name]
        sku = f"SKU-{i + 1:04d}"
        min_stock = random.randint(5, 20)
        max_stock = random.randint(50, 200)
        product = Product(
            name=name,
            sku=sku,
            category=category,
            rack=f"R{random.randint(1, 10)}",
            box_number=f"B{i + 1:03d}",
            current_stock=random.randint(min_stock, max_stock),
            minimum_stock=min_stock,
            maximum_stock=max_stock,
        )
        products.append(product)
    session.add_all(products)
    session.flush()
    logger.info("Seeded %d products", len(products))
    return products


def seed_workers(session, count: int = 12) -> list[Worker]:
    workers = [
        Worker(name=fake.name(), department=random.choice(DEPARTMENTS))
        for _ in range(count)
    ]
    session.add_all(workers)
    session.flush()
    logger.info("Seeded %d workers", len(workers))
    return workers


def _simulate_detected_products(expected_name: str, expected_qty: int, status: str) -> dict[str, int]:
    """Builds a detected-product-count dict consistent with the given status."""
    other_names = [n for n in PRODUCT_CATALOG if n != expected_name]
    other = random.choice(other_names)

    if status == "VERIFIED":
        return {expected_name: expected_qty}
    if status == "WRONG_PRODUCT":
        return {other: expected_qty}
    if status == "MISSING_PRODUCT":
        return {expected_name: max(0, expected_qty - random.randint(1, 3))}
    if status == "EXTRA_PRODUCT":
        return {expected_name: expected_qty + random.randint(1, 3)}
    if status == "UNEXPECTED_PRODUCT":
        return {expected_name: expected_qty, other: random.randint(1, 2)}
    if status == "MIXED_PRODUCTS":
        partial = max(1, expected_qty - random.randint(1, 3))
        return {expected_name: partial, other: expected_qty - partial or 1}
    return {expected_name: expected_qty}


def seed_transactions(session, products: list[Product], workers: list[Worker], count: int) -> None:
    now = dt.datetime.utcnow()
    for i in range(count):
        product = random.choice(products)
        worker = random.choice(workers)
        expected_qty = random.randint(1, 20)
        status = random.choices(VERIFICATION_STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        detected = _simulate_detected_products(product.name, expected_qty, status)
        detected_qty = sum(detected.values())
        confidence = round(random.uniform(0.72, 0.99), 3)
        timestamp = now - dt.timedelta(minutes=random.randint(0, 60 * 24 * 30))

        transaction = Transaction(
            worker_id=worker.id,
            product_id=product.id,
            expected_quantity=expected_qty,
            detected_quantity=detected_qty,
            verification_status=status,
            confidence_score=confidence,
            timestamp=timestamp,
        )
        session.add(transaction)
        session.flush()

        session.add(
            VerificationLog(
                transaction_id=transaction.id,
                box_id=product.box_number,
                expected_json=json.dumps({product.name: expected_qty}),
                detected_json=json.dumps(detected),
                result=status,
                created_at=timestamp,
            )
        )

        if status != "VERIFIED" and i % 5 == 0:
            session.add(
                Alert(
                    product_id=product.id,
                    alert_type="mismatch",
                    message=f"{status.replace('_', ' ').title()} detected for {product.name} (Box {product.box_number})",
                    severity="critical" if status in ("WRONG_PRODUCT", "MISSING_PRODUCT") else "warning",
                    created_at=timestamp,
                )
            )

    logger.info("Seeded %d transactions", count)


def seed_low_stock_alerts(session, products: list[Product]) -> None:
    for product in products:
        if product.current_stock <= product.minimum_stock:
            session.add(
                Alert(
                    product_id=product.id,
                    alert_type="low_stock",
                    message=f"Low stock: {product.name} (Box {product.box_number}) at {product.current_stock} units",
                    severity="warning",
                )
            )


def run() -> None:
    init_db()
    session = SessionLocal()
    try:
        if session.query(Product).count() > 0:
            logger.info("Database already seeded, skipping.")
            return
        products = seed_products(session, settings.dummy_product_count)
        workers = seed_workers(session)
        seed_transactions(session, products, workers, settings.dummy_transaction_count)
        seed_low_stock_alerts(session, products)
        session.commit()
        logger.info("Database seeding complete.")
    except Exception:
        session.rollback()
        logger.exception("Seeding failed")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
