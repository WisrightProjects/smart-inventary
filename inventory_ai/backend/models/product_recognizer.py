"""Maps raw RT-DETR labels to catalog product names, and counts detections.

RT-DETR's COCO checkpoint only knows generic COCO classes (e.g. "book",
"scissors", "cell phone"). This module maps whatever label set the active
checkpoint produces onto the warehouse's product catalog names, so the rest
of the system always deals in catalog names. Once a fine-tuned checkpoint is
trained directly on the product catalog (see backend/training/), this
mapping becomes the identity mapping.
"""
from __future__ import annotations

from collections import Counter

from backend.inference.rtdetr_detector import Detection
from database.product_catalog import PRODUCT_CATALOG

# Maps COCO label -> catalog product name, for the subset of catalog items
# that have a reasonable COCO analogue. Anything not listed here is treated
# as "unrecognized" and surfaced to the operator with a low-confidence tag
# rather than silently guessed.
_COCO_TO_CATALOG = {
    "book": "Book",
    "scissors": "Scissors",
    "cell phone": "Calculator",
    "remote": "Calculator",
    "mouse": "Mouse",
    "keyboard": "Keyboard",
    "bottle": "Water Bottle",
    "handbag": "Bag",
    "backpack": "Bag",
    "cup": "Water Bottle",
}


class RecognizedProduct:
    __slots__ = ("name", "confidence", "box", "raw_label")

    def __init__(self, name: str, confidence: float, box: tuple[float, float, float, float], raw_label: str) -> None:
        self.name = name
        self.confidence = confidence
        self.box = box
        self.raw_label = raw_label

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "confidence": round(self.confidence, 3),
            "box": self.box,
            "raw_label": self.raw_label,
        }


def recognize(detections: list[Detection]) -> list[RecognizedProduct]:
    """Converts raw detector output into catalog-aware recognized products."""
    recognized = []
    for det in detections:
        catalog_name = _COCO_TO_CATALOG.get(det.label.lower())
        if catalog_name is None:
            catalog_name = det.label.title() if det.label.title() in PRODUCT_CATALOG else f"Unknown ({det.label})"
        recognized.append(RecognizedProduct(catalog_name, det.confidence, det.box, det.label))
    return recognized


def count_products(recognized: list[RecognizedProduct]) -> dict[str, int]:
    """Aggregates recognized products into {product_name: count}."""
    return dict(Counter(r.name for r in recognized))
