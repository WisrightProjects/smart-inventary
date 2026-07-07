# How to Label Images for RT-DETR Fine-Tuning

The COCO-pretrained checkpoint only recognizes generic COCO classes. To
recognize the full product catalog (Sharpener, Highlighter, Sketch Pen,
etc.) you need to fine-tune on labeled photos of your own products.

## 1. Capture Images

Place each product (and realistic mixes of products) inside the
transparent verification tray under the lighting you'll use in production.

Use the built-in capture tool — it opens your configured webcam, shows a
live preview, and saves consistently-named photos on each SPACE press:

```bash
cd inventory_ai
python -m backend.training.capture_images --product "Pencil" --count 60
```

Controls: **SPACE** to capture, **ESC** to stop early. Files are saved to
`dataset/images/pencil_001.jpg`, `pencil_002.jpg`, etc. Re-running the same
`--product` continues numbering instead of overwriting earlier captures, so
you can top up a product's photos across multiple sessions.

Repeat once per catalog product (see `database/product_catalog.py` for the
full list), varying:
- Position/orientation within the tray
- Quantity (1 item, several items, overlapping items)
- Mixed with other products (for cases like `MIXED_PRODUCTS` /
  `UNEXPECTED_PRODUCT`)

Aim for 50-150 images per product. If you'd rather supply photos from
another source (phone camera, existing product photography), just drop
them into `dataset/images/` directly — the capture tool is a convenience,
not a requirement.

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
