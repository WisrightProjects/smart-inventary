"""One-off maintenance: mark a handful of existing products as low stock.

`seed.py` only runs on a fresh (empty) database, so it can't backfill this on
a DB that's already seeded (e.g. production, which currently has 0 low-stock
products purely by random chance). This script is idempotent - safe to run
any number of times - and only touches products that aren't already low.

Run with: python -m database.fix_low_stock
"""
from __future__ import annotations

import random

from backend.utils.logger import get_logger
from database.models import Alert, Product
from database.session import SessionLocal

logger = get_logger("database")

# How many products to force into a low-stock state for demo/testing purposes.
COUNT = 6


def run() -> None:
    session = SessionLocal()
    try:
        already_low = session.query(Product).filter(Product.current_stock <= Product.minimum_stock).count()
        if already_low > 0:
            logger.info("%d product(s) already low stock, nothing to do.", already_low)
            return

        candidates = session.query(Product).order_by(Product.id).limit(COUNT).all()
        if not candidates:
            logger.info("No products in database, nothing to do.")
            return

        for product in candidates:
            product.current_stock = max(0, product.minimum_stock - random.randint(1, 4))
            session.add(
                Alert(
                    product_id=product.id,
                    alert_type="low_stock",
                    message=f"Low stock: {product.name} (Box {product.box_number}) at {product.current_stock} units",
                    severity="warning",
                )
            )

        session.commit()
        logger.info("Marked %d product(s) as low stock.", len(candidates))
    except Exception:
        session.rollback()
        logger.exception("fix_low_stock failed")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run()
