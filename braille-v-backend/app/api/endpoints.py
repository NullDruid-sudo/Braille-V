"""
Braille-V API Endpoints
REST endpoints for health checks and Braille scanning.
"""

import logging
import time

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.braille_converter import BrailleToEnglish
from app.services.dot_detection import DotDetector
from app.services.preprocessing import preprocess_image
from app.services.recognition import BrailleRecognizer
from app.services.segmentation import segment_cells
from app.database import save_scan as db_save_scan

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Singleton services (initialised once at import) ──────────────────────────
_dot_detector: DotDetector | None = None
_recognizer: BrailleRecognizer | None = None
_converter: BrailleToEnglish | None = None


def _get_services():
    """Lazy-init singletons so import doesn't block."""
    global _dot_detector, _recognizer, _converter
    if _dot_detector is None:
        _dot_detector = DotDetector()
    if _recognizer is None:
        _recognizer = BrailleRecognizer()
    if _converter is None:
        _converter = BrailleToEnglish()
    return _dot_detector, _recognizer, _converter


# ── Routes ───────────────────────────────────────────────────────────────────


@router.get("/health")
async def health_check():
    """Simple liveness / readiness probe."""
    return {"status": "ok", "message": "Braille-V API is running"}


@router.post("/scan")
async def scan_braille(image: UploadFile = File(...)):
    """
    Main endpoint.

    Accepts an image upload and returns:
    - unicode_braille: the Braille text as Unicode symbols
    - english_text:    the decoded English translation
    - num_cells:       how many Braille cells were detected
    - processing_ms:   elapsed time in milliseconds
    """
    dot_detector, recognizer, converter = _get_services()
    start = time.perf_counter()

    # ── Validate content type ────────────────────────────────────────
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Expected an image file, got {image.content_type}",
        )

    try:
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")

        # Step 1: Preprocess
        preprocessed = preprocess_image(image_bytes)

        # Step 2: Detect dots
        dots = dot_detector.detect_dots(preprocessed)
        if len(dots) == 0:
            return {
                "success": False,
                "error": "No Braille dots detected in the image",
                "num_dots": 0,
                "processing_ms": _elapsed_ms(start),
            }

        # Step 3: Segment into cells
        cells = segment_cells(dots, preprocessed.shape)
        if len(cells) == 0:
            return {
                "success": False,
                "error": "Dots detected but could not form Braille cells",
                "num_dots": len(dots),
                "processing_ms": _elapsed_ms(start),
            }

        # Step 4: Recognise characters
        # Use dot-pattern recognition (works without trained CNN)
        for cell in cells:
            cell["character"] = recognizer.recognize_from_dots(
                cell["dot_positions"]
            )

        # If CNN is available, also try image-based recognition
        if recognizer._model is not None:
            for cell in cells:
                cell_img = _extract_cell_image(preprocessed, cell)
                if cell_img is not None:
                    cell["character_cnn"] = recognizer.recognize_cell(cell_img)

        # Step 5: Convert to English
        result = converter.full_pipeline(cells)

        elapsed = _elapsed_ms(start)
        logger.info(
            "Scan complete: %d dots → %d cells → '%s' (%.0f ms)",
            len(dots),
            len(cells),
            result["english_text"],
            elapsed,
        )

        # Auto-save to SQLite history
        try:
            saved = db_save_scan(
                unicode_braille=result["unicode_braille"],
                english_text=result["english_text"],
                num_dots=len(dots),
                num_cells=len(cells),
                processing_ms=elapsed,
            )
            history_id = saved["id"]
        except Exception as db_err:
            logger.warning("History save failed: %s", db_err)
            history_id = None

        return {
            "success": True,
            "id": history_id,
            "unicode_braille": result["unicode_braille"],
            "english_text": result["english_text"],
            "num_dots": len(dots),
            "num_cells": len(cells),
            "cells": [
                {
                    "dot_positions": c["dot_positions"],
                    "character": c.get("character", "?"),
                }
                for c in cells
            ],
            "processing_ms": elapsed,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Scan failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ── Helpers ──────────────────────────────────────────────────────────────────


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 1)


def _extract_cell_image(
    image: np.ndarray, cell: dict, padding: int = 5
) -> np.ndarray | None:
    """
    Extract the image region corresponding to a Braille cell.
    Returns a cropped grayscale image, or None if the region is invalid.
    """
    dots = cell.get("dots", [])
    if not dots:
        return None

    xs = [d["x"] for d in dots]
    ys = [d["y"] for d in dots]

    x_min = max(0, int(min(xs)) - padding)
    y_min = max(0, int(min(ys)) - padding)
    x_max = min(image.shape[1], int(max(xs)) + padding)
    y_max = min(image.shape[0], int(max(ys)) + padding)

    if x_max <= x_min or y_max <= y_min:
        return None

    return image[y_min:y_max, x_min:x_max]
