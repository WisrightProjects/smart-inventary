"""Verifies core ORM models persist and relate correctly."""
from database.models import Product, Transaction, Worker


def test_product_transaction_relationship(db_session):
    product = Product(
        name="Pencil", sku="SKU-0001", category="Stationery",
        rack="R1", box_number="B001", current_stock=10,
        minimum_stock=5, maximum_stock=50,
    )
    worker = Worker(name="Jane Doe", department="Warehouse")
    db_session.add_all([product, worker])
    db_session.flush()

    transaction = Transaction(
        worker_id=worker.id, product_id=product.id,
        expected_quantity=10, detected_quantity=10,
        verification_status="VERIFIED", confidence_score=0.95,
    )
    db_session.add(transaction)
    db_session.commit()

    fetched = db_session.query(Transaction).first()
    assert fetched.product.name == "Pencil"
    assert fetched.worker.name == "Jane Doe"
    assert fetched.verification_status == "VERIFIED"
