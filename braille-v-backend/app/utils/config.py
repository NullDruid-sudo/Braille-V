"""
Braille-V Backend Configuration
Centralized settings loaded from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(_backend_root / ".env")


class Settings:
    """Application settings loaded from environment."""

    # Paths
    BASE_DIR: Path = _backend_root
    MODEL_DIR: Path = _backend_root / os.getenv("MODEL_DIR", "app/models")
    YOLO_MODEL_PATH: Path = _backend_root / os.getenv(
        "YOLO_MODEL_PATH", "app/models/yolov8_braille.pt"
    )
    CNN_MODEL_PATH: Path = _backend_root / os.getenv(
        "CNN_MODEL_PATH", "app/models/cnn_classifier.h5"
    )

    # CORS
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")

    # Detection thresholds
    DOT_CONFIDENCE_THRESHOLD: float = float(
        os.getenv("DOT_CONFIDENCE_THRESHOLD", "0.7")
    )

    # Cell segmentation
    CELL_PROXIMITY_THRESHOLD: float = 50.0  # pixels

    # Debug
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
