# How to Train (and Retrain) RT-DETR

By default the system uses a COCO-pretrained RT-DETR checkpoint
(`PekingU/rtdetr_r50vd_coco_o365`), which only recognizes the subset of
catalog products with a COCO analogue (see the mapping table in
`backend/models/product_recognizer.py`). To recognize the full catalog
(Sharpener, Sketch Pen, Whiteboard Marker, etc.) you need to fine-tune on
your own labeled images.

## 1. Collect and Label Images

Follow [labeling.md](labeling.md) to capture and annotate photos of each
product in the transparent verification tray, exporting COCO-format JSON
into `dataset/labels/instances.json` and images into `dataset/images/`.

## 2. Split Train/Validation Sets

```bash
cd inventory_ai
python -m backend.training.prepare_dataset \
    --input dataset/labels/instances.json \
    --output-dir dataset/labels \
    --val-ratio 0.2
```

This produces `dataset/labels/train.json` and `dataset/labels/val.json`.

## 3. Fine-Tune

```bash
python -m backend.training.train_rtdetr \
    --train-annotations dataset/labels/train.json \
    --val-annotations dataset/labels/val.json \
    --images-dir dataset/images \
    --output-dir backend/models/checkpoints/rtdetr-products \
    --epochs 30 \
    --batch-size 4
```

- CPU training works but is slow — a GPU is strongly recommended for
  fine-tuning (inference can still run on CPU afterward if needed).
- Start with the defaults (30 epochs, batch size 4, lr 1e-5) and watch the
  validation loss; increase epochs if it's still decreasing, reduce if it
  plateaus early.

## 4. Point the System at the New Checkpoint

Set the environment variable (no code changes needed):

```bash
set INV_RTDETR_CHECKPOINT=backend/models/checkpoints/rtdetr-products
```

Restart the backend. `RTDETRDetector` loads whatever checkpoint path is
configured, and `product_recognizer.py`'s COCO-label mapping becomes a
pass-through once your model's labels already match catalog names exactly
(label the training data with catalog names, and no mapping is needed).

## Retraining

As you add new products or collect more/better images, repeat steps 1-3
using the previous fine-tuned checkpoint as `--base-checkpoint` instead of
the original COCO checkpoint, so you build on what the model already
learned rather than starting from scratch:

```bash
python -m backend.training.train_rtdetr \
    --base-checkpoint backend/models/checkpoints/rtdetr-products \
    ... (same as above, with new/expanded dataset)
```

## Evaluating Quality

After training, run a handful of `/api/verify` calls against known box
contents and check the confusion is where you'd expect (e.g. visually
similar products like Pen vs Marker are the most common source of
misclassification — add more contrastive training examples for those
pairs if so).
