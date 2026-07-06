# How to Add New Products

## 1. Add to the Catalog

Edit `inventory_ai/database/product_catalog.py` and add the new product
name and category to `PRODUCT_CATALOG`:

```python
PRODUCT_CATALOG: dict[str, str] = {
    ...
    "Correction Tape": "Office Supplies",
}
```

This is the single source of truth used by both the dummy-data seeder and
the AI recognition mapping layer.

## 2. Register It in the Database

If seeding fresh, just re-run:

```bash
python -m database.seed
```

(delete `database/inventory.db` first if it already has data, since seeding
skips if products already exist).

To add a single product to an existing database without reseeding
everything, insert directly via a short script or the `/docs` Swagger UI's
interactive endpoints, e.g.:

```python
from database.session import SessionLocal
from database.models import Product

session = SessionLocal()
session.add(Product(
    name="Correction Tape", sku="SKU-0101", category="Office Supplies",
    rack="R3", box_number="B101", current_stock=40,
    minimum_stock=10, maximum_stock=100,
))
session.commit()
```

## 3. Teach the AI to Recognize It

If the product has no reasonable COCO analogue (most stationery items
don't), the out-of-the-box RT-DETR checkpoint won't recognize it — it will
show up as `Unknown (<raw coco label>)` or simply go undetected. You need
to:

1. Capture and label sample images of the new product — see
   [labeling.md](labeling.md).
2. Include it in the next fine-tuning run — see
   [training.md](training.md), using the previous fine-tuned checkpoint as
   the base so existing products aren't forgotten.

Once fine-tuned with the catalog name as the label, no changes to
`product_recognizer.py`'s mapping table are needed — the model's own label
output will already match the catalog name.
