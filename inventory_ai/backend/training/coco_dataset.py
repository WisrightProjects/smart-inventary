"""COCO-format dataset loader for RT-DETR fine-tuning."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CocoDetectionDataset:
    """Minimal COCO-annotation dataset compatible with HF Trainer.

    Deliberately dependency-light (no pycocotools requirement) since the
    annotation format needed here is simple: images + bounding boxes +
    category ids.
    """

    def __init__(self, images_dir: Path, annotations_path: Path, processor: Any) -> None:
        self.images_dir = Path(images_dir)
        self.processor = processor

        with open(annotations_path, encoding="utf-8") as f:
            coco = json.load(f)

        self.images_by_id = {img["id"]: img for img in coco["images"]}
        self.categories = {c["id"]: c["name"] for c in coco["categories"]}
        self.id2label = self.categories

        self.annotations_by_image: dict[int, list[dict]] = {}
        for ann in coco["annotations"]:
            self.annotations_by_image.setdefault(ann["image_id"], []).append(ann)

        self.image_ids = list(self.images_by_id.keys())

    def __len__(self) -> int:
        return len(self.image_ids)

    def __getitem__(self, index: int) -> dict:
        from PIL import Image

        image_id = self.image_ids[index]
        image_info = self.images_by_id[image_id]
        image_path = self.images_dir / image_info["file_name"]
        image = Image.open(image_path).convert("RGB")

        annotations = self.annotations_by_image.get(image_id, [])
        target = {
            "image_id": image_id,
            "annotations": [
                {
                    "bbox": ann["bbox"],
                    "category_id": ann["category_id"],
                    "area": ann.get("area", ann["bbox"][2] * ann["bbox"][3]),
                    "iscrowd": ann.get("iscrowd", 0),
                }
                for ann in annotations
            ],
        }

        encoding = self.processor(images=image, annotations=target, return_tensors="pt")
        return {
            "pixel_values": encoding["pixel_values"][0],
            "labels": encoding["labels"][0],
        }

    @staticmethod
    def collate_fn(batch: list[dict]) -> dict:
        import torch

        pixel_values = torch.stack([item["pixel_values"] for item in batch])
        labels = [item["labels"] for item in batch]
        return {"pixel_values": pixel_values, "labels": labels}
