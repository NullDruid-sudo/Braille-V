"""
Braille-V Training — Data Preprocessing
Downloads and prepares Braille datasets for model training.

Datasets:
  - Angelina Braille Dataset (annotated Braille pages)
  - Kaggle Braille Character Dataset (individual cell images)

Usage:
    python -m training.preprocess --output ./data
"""

import argparse
import logging
import os
import random
import shutil
from pathlib import Path

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def preprocess_for_yolo(image_path: str, output_size: int = 224) -> np.ndarray:
    """Preprocess a Braille page image for YOLOv8 training."""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    # Resize to square
    img = cv2.resize(img, (output_size, output_size))

    # Convert to grayscale for thresholding
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE normalisation
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    normalized = clahe.apply(gray)

    # Convert back to 3-channel (YOLO expects colour images)
    return cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR)


def preprocess_for_cnn(image_path: str, output_size: int = 48) -> np.ndarray:
    """Preprocess an individual Braille cell image for CNN training."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    # Resize to target
    img = cv2.resize(img, (output_size, output_size))

    # Adaptive threshold
    img = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Gentle blur
    img = cv2.GaussianBlur(img, (3, 3), 0)

    return img


def split_dataset(
    image_dir: Path,
    output_dir: Path,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, int]:
    """
    Split images into train / val / test directories.
    Returns counts per split.
    """
    random.seed(seed)

    images = sorted(
        p for p in image_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"}
    )
    random.shuffle(images)

    n = len(images)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    splits = {
        "train": images[:n_train],
        "val": images[n_train : n_train + n_val],
        "test": images[n_train + n_val :],
    }

    counts = {}
    for split_name, split_images in splits.items():
        split_dir = output_dir / split_name
        split_dir.mkdir(parents=True, exist_ok=True)
        for img_path in split_images:
            shutil.copy2(img_path, split_dir / img_path.name)
        counts[split_name] = len(split_images)
        logger.info("  %s: %d images", split_name, len(split_images))

    return counts


def main():
    parser = argparse.ArgumentParser(description="Preprocess Braille datasets")
    parser.add_argument(
        "--input", type=str, required=True, help="Path to raw dataset directory"
    )
    parser.add_argument(
        "--output", type=str, default="./data", help="Output directory for processed data"
    )
    parser.add_argument(
        "--task",
        choices=["yolo", "cnn", "both"],
        default="both",
        help="Which task to preprocess for",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        logger.error("Input directory does not exist: %s", input_dir)
        return

    if args.task in ("yolo", "both"):
        logger.info("Preprocessing for YOLOv8...")
        yolo_dir = output_dir / "yolo"
        yolo_dir.mkdir(parents=True, exist_ok=True)

        for img_path in input_dir.glob("**/*.png"):
            try:
                processed = preprocess_for_yolo(str(img_path))
                cv2.imwrite(str(yolo_dir / img_path.name), processed)
            except Exception as e:
                logger.warning("Skipping %s: %s", img_path.name, e)

        logger.info("Splitting YOLO dataset...")
        split_dataset(yolo_dir, output_dir / "yolo_split")

    if args.task in ("cnn", "both"):
        logger.info("Preprocessing for CNN...")
        cnn_dir = output_dir / "cnn"
        cnn_dir.mkdir(parents=True, exist_ok=True)

        for img_path in input_dir.glob("**/*.png"):
            try:
                processed = preprocess_for_cnn(str(img_path))
                cv2.imwrite(str(cnn_dir / img_path.name), processed)
            except Exception as e:
                logger.warning("Skipping %s: %s", img_path.name, e)

        logger.info("Splitting CNN dataset...")
        split_dataset(cnn_dir, output_dir / "cnn_split")

    logger.info("Done! Processed data saved to %s", output_dir)


if __name__ == "__main__":
    main()
