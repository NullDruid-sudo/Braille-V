"""
Braille-V Dot Detection Service
YOLOv8-based dot detection with OpenCV connected-components fallback.
"""

import logging
from pathlib import Path

import cv2
import numpy as np

from app.utils.config import settings

logger = logging.getLogger(__name__)


class DotDetector:
    """Detect individual raised Braille dots in a preprocessed image."""

    def __init__(self, model_path: Path | None = None):
        self._model = None
        self._model_path = model_path or settings.YOLO_MODEL_PATH
        self.conf_threshold = settings.DOT_CONFIDENCE_THRESHOLD
        self._load_model()

    # ── public API ───────────────────────────────────────────────────────

    def detect_dots(self, image: np.ndarray) -> list[dict]:
        """
        Detect dots in a preprocessed (binary) image.

        Returns
        -------
        list[dict]
            Each dict: {x, y, width, height, confidence}
        """
        dots: list[dict] = []

        # Primary: YOLOv8
        if self._model is not None:
            dots = self._yolo_detect(image)

        # Fallback: OpenCV connected components
        if len(dots) == 0:
            logger.info("YOLO returned 0 dots – falling back to OpenCV")
            dots = self._opencv_fallback(image)

        return dots

    # ── private helpers ──────────────────────────────────────────────────

    def _load_model(self) -> None:
        """Load YOLOv8 model if the weight file exists."""
        if self._model_path.exists():
            try:
                from ultralytics import YOLO

                self._model = YOLO(str(self._model_path))
                logger.info("YOLOv8 model loaded from %s", self._model_path)
            except Exception as exc:
                logger.warning("Failed to load YOLO model: %s", exc)
                self._model = None
        else:
            logger.warning(
                "YOLO weights not found at %s – using OpenCV fallback only",
                self._model_path,
            )

    def _yolo_detect(self, image: np.ndarray) -> list[dict]:
        """Run YOLOv8 inference and return detected dots."""
        # YOLOv8 expects BGR or RGB; our binary image is single-channel,
        # so convert to 3-channel.
        if len(image.shape) == 2:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            img_rgb = image

        results = self._model(img_rgb, conf=self.conf_threshold, verbose=False)

        dots: list[dict] = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                dots.append(
                    {
                        "x": float((x1 + x2) / 2),
                        "y": float((y1 + y2) / 2),
                        "width": float(x2 - x1),
                        "height": float(y2 - y1),
                        "confidence": confidence,
                    }
                )
        return dots

    def _opencv_fallback(self, image: np.ndarray) -> list[dict]:
        """
        Connected-components analysis as a fallback when YOLO is unavailable
        or returns no detections.
        """
        # Ensure binary (the image should already be, but guard against edge cases)
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        dots: list[dict] = []
        for i in range(1, num_labels):  # skip background (label 0)
            x, y, w, h, area = stats[i]

            # Filter by area — ignore tiny noise and huge blobs
            if not (20 < area < 800):
                continue

            # Circularity check — real dots are roughly circular
            aspect_ratio = w / max(h, 1)
            if not (0.4 < aspect_ratio < 2.5):
                continue

            dots.append(
                {
                    "x": float(centroids[i][0]),
                    "y": float(centroids[i][1]),
                    "width": float(w),
                    "height": float(h),
                    "confidence": min(float(area) / 500.0, 1.0),
                }
            )

        return dots
