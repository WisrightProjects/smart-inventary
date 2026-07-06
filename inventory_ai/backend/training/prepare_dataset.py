"""Splits a single COCO-format annotation file into train/val sets.

Usage:
    python -m backend.training.prepare_dataset \
        --input dataset/labels/instances.json \
        --output-dir dataset/labels \
        --val-ratio 0.2
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def split_coco_annotations(input_path: Path, output_dir: Path, val_ratio: float, seed: int = 42) -> None:
    with open(input_path, encoding="utf-8") as f:
        coco = json.load(f)

    images = coco["images"]
    random.Random(seed).shuffle(images)
    split_index = int(len(images) * (1 - val_ratio))
    train_images, val_images = images[:split_index], images[split_index:]

    def subset(images_subset: list[dict]) -> dict:
        image_ids = {img["id"] for img in images_subset}
        annotations = [a for a in coco["annotations"] if a["image_id"] in image_ids]
        return {
            "images": images_subset,
            "annotations": annotations,
            "categories": coco["categories"],
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "train.json", "w", encoding="utf-8") as f:
        json.dump(subset(train_images), f)
    with open(output_dir / "val.json", "w", encoding="utf-8") as f:
        json.dump(subset(val_images), f)

    print(f"Train images: {len(train_images)}, Val images: {len(val_images)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    args = parser.parse_args()
    split_coco_annotations(args.input, args.output_dir, args.val_ratio)


if __name__ == "__main__":
    main()
