"""Fine-tunes RT-DETR on the labeled product dataset.

This uses HuggingFace `transformers` + `datasets` so no custom training loop
plumbing has to be maintained by hand. Run after preparing train.json/val.json
with prepare_dataset.py (see docs/training.md for the full walkthrough).

Usage:
    python -m backend.training.train_rtdetr \
        --train-annotations dataset/labels/train.json \
        --val-annotations dataset/labels/val.json \
        --images-dir dataset/images \
        --output-dir backend/models/checkpoints/rtdetr-products \
        --epochs 30
"""
from __future__ import annotations

import argparse
from pathlib import Path

from backend.utils.logger import get_logger

logger = get_logger("ai")


def train(
    train_annotations: Path,
    val_annotations: Path,
    images_dir: Path,
    output_dir: Path,
    base_checkpoint: str,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> None:
    """Fine-tunes RT-DETR. Imports heavy ML deps lazily so this module can be
    inspected/imported without requiring a GPU-ready environment.
    """
    import torch
    from transformers import (
        RTDetrForObjectDetection,
        RTDetrImageProcessor,
        Trainer,
        TrainingArguments,
    )

    from backend.training.coco_dataset import CocoDetectionDataset

    processor = RTDetrImageProcessor.from_pretrained(base_checkpoint)
    train_dataset = CocoDetectionDataset(images_dir, train_annotations, processor)
    val_dataset = CocoDetectionDataset(images_dir, val_annotations, processor)

    id2label = train_dataset.id2label
    label2id = {v: k for k, v in id2label.items()}

    model = RTDetrForObjectDetection.from_pretrained(
        base_checkpoint,
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True,
    )

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=10,
        remove_unused_columns=False,
        dataloader_pin_memory=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=train_dataset.collate_fn,
    )

    logger.info("Starting RT-DETR fine-tuning for %d epochs", epochs)
    trainer.train()
    trainer.save_model(str(output_dir))
    processor.save_pretrained(str(output_dir))
    logger.info("Training complete. Checkpoint saved to %s", output_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-annotations", type=Path, required=True)
    parser.add_argument("--val-annotations", type=Path, required=True)
    parser.add_argument("--images-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-checkpoint", default="PekingU/rtdetr_r50vd_coco_o365")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    args = parser.parse_args()

    train(
        args.train_annotations,
        args.val_annotations,
        args.images_dir,
        args.output_dir,
        args.base_checkpoint,
        args.epochs,
        args.batch_size,
        args.learning_rate,
    )


if __name__ == "__main__":
    main()
