"""Interactive webcam capture tool for building the fine-tuning dataset.

Walks you through photographing each catalog product in the verification
tray so you have a consistent, well-named image set ready to hand to a
labeling tool (CVAT/Roboflow/Label Studio — see docs/labeling.md).

Usage:
    python -m backend.training.capture_images --product "Pencil"
    python -m backend.training.capture_images --product "Notebook" --count 80

Controls (shown in the window):
    SPACE  - capture a photo
    ESC    - quit

Images are saved to dataset/images/<product-slug>_<NNN>.jpg, continuing
numbering from any existing files for that product so re-runs don't
overwrite earlier captures.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import cv2

from backend.config.settings import settings, BASE_DIR
from backend.utils.logger import get_logger

logger = get_logger("camera")

IMAGES_DIR = BASE_DIR / "dataset" / "images"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def next_index(slug: str) -> int:
    existing = list(IMAGES_DIR.glob(f"{slug}_*.jpg"))
    if not existing:
        return 1
    numbers = [int(p.stem.split("_")[-1]) for p in existing if p.stem.split("_")[-1].isdigit()]
    return (max(numbers) + 1) if numbers else 1


def capture(product: str, target_count: int, source: int | str) -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    slug = slugify(product)
    index = next_index(slug)
    end_index = index + target_count

    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.camera_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.camera_height)
    if not cap.isOpened():
        logger.error("Could not open camera source %s", source)
        return

    window = f"Capture: {product}  (SPACE=capture, ESC=quit)"
    print(f"\nCapturing '{product}' -> {IMAGES_DIR}")
    print(f"Starting at {slug}_{index:03d}.jpg, target {target_count} photos.")
    print("Vary position, orientation, and quantity between shots for best training results.\n")

    captured = 0
    try:
        while index < end_index:
            ok, frame = cap.read()
            if not ok:
                logger.warning("Frame read failed")
                continue

            preview = frame.copy()
            cv2.putText(
                preview,
                f"{product}  |  {captured}/{target_count} captured",
                (16, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 140, 255),
                2,
            )
            cv2.imshow(window, preview)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            if key == 32:  # SPACE
                filename = IMAGES_DIR / f"{slug}_{index:03d}.jpg"
                cv2.imwrite(str(filename), frame)
                print(f"  saved {filename.name}")
                index += 1
                captured += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()

    print(f"\nDone. Captured {captured} photo(s) for '{product}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--product", required=True, help="Catalog product name, e.g. 'Pencil'")
    parser.add_argument("--count", type=int, default=60, help="Number of photos to capture (default 60)")
    parser.add_argument("--source", default=settings.camera_source, help="Camera index or URI (default: configured webcam)")
    args = parser.parse_args()

    capture(args.product, args.count, args.source)


if __name__ == "__main__":
    main()
