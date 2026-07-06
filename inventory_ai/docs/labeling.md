# How to Label Images for RT-DETR Fine-Tuning

The COCO-pretrained checkpoint only recognizes generic COCO classes. To
recognize the full product catalog (Sharpener, Highlighter, Sketch Pen,
etc.) you need to fine-tune on labeled photos of your own products.

## 1. Capture Images

- Place each product (and realistic mixes of products) inside the
  transparent verification tray under the lighting you'll use in
  production.
- Capture 50-150 images per product class, varying:
  - Position/orientation within the tray
  - Quantity (1 item, several items, overlapping items)
  - Mixed with other products (for cases like `MIXED_PRODUCTS` /
    `UNEXPECTED_PRODUCT`)
- Save images into `inventory_ai/dataset/images/` as `.jpg` or `.png`.

## 2. Annotate Bounding Boxes

Use a free annotation tool that exports COCO-format JSON:

- [CVAT](https://www.cvat.ai/) (self-hosted or cloud) — recommended for
  batch labeling with keyboard shortcuts.
- [Label Studio](https://labelstud.io/) — good if you also want to manage
  review/QA workflows.
- [Roboflow](https://roboflow.com/) — fastest to get started, has a free
  tier, and can export directly in the COCO format RT-DETR training expects.

For each image, draw a tight bounding box around every visible product and
assign it the exact catalog name from
`inventory_ai/database/product_catalog.py` (keep names consistent — e.g.
always "Glue Stick", never "glue" or "Glue-Stick").

## 3. Export

Export annotations in **COCO JSON** format. Place:

- Images in `inventory_ai/dataset/images/`
- The exported `instances.json` (or split into `train.json`/`val.json`) in
  `inventory_ai/dataset/labels/`

## 4. Split Train/Validation

Aim for an 80/20 train/validation split, stratified so every product class
appears in both sets. `inventory_ai/backend/training/prepare_dataset.py`
(see [training.md](training.md)) can perform this split automatically if
you provide a single combined `instances.json`.

## Labeling Tips

- Label ALL products visible in an image, even background ones — RT-DETR
  learns to ignore clutter only if it sees consistent full annotation.
- Keep box edges tight; loose boxes reduce localization accuracy and can
  cause miscounts.
- If two products of the same class touch/overlap, still draw two separate
  boxes — this is what teaches the model to count them individually.
