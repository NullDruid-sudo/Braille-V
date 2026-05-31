"""
Braille-V Training — YOLOv8 Dot Detector
Trains a YOLOv8n model to detect individual Braille dots.

Prerequisites:
    pip install ultralytics

Usage:
    python -m training.train_yolo --data ./data/yolo_split/data.yaml

The data.yaml should follow the Ultralytics format:
    path: /absolute/path/to/yolo_split
    train: train/images
    val: val/images
    test: test/images
    names:
      0: dot
"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Default training hyperparameters
DEFAULTS = {
    "model": "yolov8n.pt",       # YOLOv8 nano — fastest variant
    "epochs": 100,
    "imgsz": 224,
    "batch": 16,
    "lr0": 0.01,
    "device": "",                # auto-detect (GPU if available)
    "project": "runs/braille_dots",
    "name": "yolov8_braille",
}


def create_data_yaml(data_dir: Path, output_path: Path) -> Path:
    """Generate a YOLO data.yaml if one doesn't exist."""
    yaml_content = f"""# Braille-V YOLOv8 dataset configuration
path: {data_dir.resolve()}
train: train/images
val: val/images
test: test/images

names:
  0: dot
"""
    output_path.write_text(yaml_content)
    logger.info("Created data.yaml at %s", output_path)
    return output_path


def train(args):
    """Run YOLOv8 training."""
    from ultralytics import YOLO

    data_path = Path(args.data)
    if not data_path.exists():
        logger.error("Data config not found: %s", data_path)
        return

    logger.info("Loading base model: %s", args.model)
    model = YOLO(args.model)

    logger.info("Starting training...")
    results = model.train(
        data=str(data_path),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        lr0=args.lr0,
        device=args.device or None,
        project=args.project,
        name=args.name,
        exist_ok=True,
        verbose=True,
    )

    # Export best weights
    best_path = Path(args.project) / args.name / "weights" / "best.pt"
    export_path = Path("app/models/yolov8_braille.pt")
    export_path.parent.mkdir(parents=True, exist_ok=True)

    if best_path.exists():
        import shutil
        shutil.copy2(best_path, export_path)
        logger.info("Best model exported to %s", export_path)
    else:
        logger.warning("Best weights not found at %s", best_path)

    # Validate
    logger.info("Running validation...")
    metrics = model.val()
    logger.info("mAP50: %.4f  |  mAP50-95: %.4f", metrics.box.map50, metrics.box.map)

    return results


def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8 Braille dot detector")
    parser.add_argument("--data", type=str, required=True, help="Path to data.yaml")
    parser.add_argument("--model", type=str, default=DEFAULTS["model"])
    parser.add_argument("--epochs", type=int, default=DEFAULTS["epochs"])
    parser.add_argument("--imgsz", type=int, default=DEFAULTS["imgsz"])
    parser.add_argument("--batch", type=int, default=DEFAULTS["batch"])
    parser.add_argument("--lr0", type=float, default=DEFAULTS["lr0"])
    parser.add_argument("--device", type=str, default=DEFAULTS["device"])
    parser.add_argument("--project", type=str, default=DEFAULTS["project"])
    parser.add_argument("--name", type=str, default=DEFAULTS["name"])

    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
