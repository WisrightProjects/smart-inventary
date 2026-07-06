"""RT-DETR object detection wrapper.

Uses HuggingFace `transformers`' RT-DETR implementation so no custom model
code has to be vendored. Ships with a COCO-pretrained checkpoint by default;
call `RTDETRDetector(checkpoint=...)` with a fine-tuned checkpoint once one
has been trained on the product dataset (see training/README.md).

This is intentionally the ONLY place that imports torch/transformers directly
so swapping model architecture later never touches camera/verification code.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from backend.config.settings import settings
from backend.utils.logger import get_logger

logger = get_logger("ai")


@dataclass
class Detection:
    label: str
    confidence: float
    box: tuple[float, float, float, float]  # x_min, y_min, x_max, y_max


class RTDETRDetector:
    """Lazy-loading RT-DETR wrapper.

    The model is loaded on first `detect()` call (not at import time) so the
    rest of the API can start up instantly even before torch has finished
    initializing, and so unit tests that don't touch inference never pay the
    model-load cost.
    """

    def __init__(
        self,
        checkpoint: str | None = None,
        device: str | None = None,
        confidence_threshold: float | None = None,
    ) -> None:
        self.checkpoint = checkpoint or settings.rtdetr_checkpoint
        self.device = device or settings.rtdetr_device
        self.confidence_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else settings.rtdetr_confidence_threshold
        )
        self._model: Any = None
        self._processor: Any = None

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import RTDetrForObjectDetection, RTDetrImageProcessor

        logger.info("Loading RT-DETR checkpoint '%s' on %s", self.checkpoint, self.device)
        self._processor = RTDetrImageProcessor.from_pretrained(self.checkpoint)
        self._model = RTDetrForObjectDetection.from_pretrained(self.checkpoint)
        self._model.to(self.device)
        self._model.eval()
        self._torch = torch
        logger.info("RT-DETR model loaded successfully")

    def detect(self, frame_bgr: np.ndarray) -> list[Detection]:
        """Runs detection on a single BGR frame (as read by OpenCV).

        Returns a list of Detection objects above the confidence threshold.
        """
        self._ensure_loaded()
        import cv2

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        inputs = self._processor(images=rgb, return_tensors="pt").to(self.device)

        with self._torch.no_grad():
            outputs = self._model(**inputs)

        target_sizes = self._torch.tensor([rgb.shape[:2]])
        results = self._processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=self.confidence_threshold
        )[0]

        detections: list[Detection] = []
        for score, label_id, box in zip(results["scores"], results["labels"], results["boxes"]):
            label = self._model.config.id2label[int(label_id)]
            x_min, y_min, x_max, y_max = (float(v) for v in box.tolist())
            detections.append(
                Detection(
                    label=label,
                    confidence=float(score),
                    box=(x_min, y_min, x_max, y_max),
                )
            )

        logger.debug("Detected %d objects above threshold %.2f", len(detections), self.confidence_threshold)
        return detections


# Shared singleton so the model is loaded once per process.
detector = RTDETRDetector()
