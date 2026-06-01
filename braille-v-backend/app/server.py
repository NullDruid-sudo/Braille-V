"""
Braille-V Backend — aiohttp Server
Uses aiohttp (pre-installed) instead of FastAPI since PyPI is unreachable.
Serves both the API and the frontend static files.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

from aiohttp import web
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Import services ──────────────────────────────────────────────────────────
from app.services.braille_converter import BrailleToEnglish
from app.services.segmentation import segment_cells
from app.utils.grade2_mapping import GRADE1_MAP, dots_to_unicode

# Lazy singletons
_converter = None
_dot_detector = None


def _get_converter():
    global _converter
    if _converter is None:
        _converter = BrailleToEnglish()
    return _converter


def _get_dot_detector():
    global _dot_detector
    if _dot_detector is None:
        try:
            from app.services.dot_detection import DotDetector
            _dot_detector = DotDetector()
        except Exception as e:
            logger.warning("DotDetector init failed (OpenCV may be missing): %s", e)
            _dot_detector = None
    return _dot_detector


# ── CORS middleware ──────────────────────────────────────────────────────────
@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        resp = web.Response(status=204)
    else:
        try:
            resp = await handler(request)
        except web.HTTPException as ex:
            resp = ex
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


# ── API Routes ───────────────────────────────────────────────────────────────
async def health(request):
    return web.json_response({
        "status": "ok",
        "message": "Braille-V API is running",
        "opencv_available": _get_dot_detector() is not None,
    })


async def scan(request):
    start = time.perf_counter()
    converter = _get_converter()
    detector = _get_dot_detector()

    try:
        reader = await request.multipart()
        field = await reader.next()

        if field is None:
            return web.json_response({"success": False, "error": "No image uploaded"}, status=400)

        image_bytes = await field.read()
        if len(image_bytes) == 0:
            return web.json_response({"success": False, "error": "Empty image file"}, status=400)

        dots = []

        # Try OpenCV-based detection if available
        if detector is not None:
            try:
                from app.services.preprocessing import preprocess_image
                preprocessed = preprocess_image(image_bytes)
                dots = detector.detect_dots(preprocessed)
            except Exception as e:
                logger.warning("Image processing failed: %s", e)

        elapsed = round((time.perf_counter() - start) * 1000, 1)

        if len(dots) == 0:
            return web.json_response({
                "success": False,
                "error": "No Braille dots detected. Point camera at embossed Braille text.",
                "num_dots": 0,
                "processing_ms": elapsed,
            })

        # Segment into cells
        cells = segment_cells(dots, (480, 640) if detector is None else preprocessed.shape)

        # Recognise via dot-pattern lookup
        from app.services.recognition import BrailleRecognizer
        recognizer = BrailleRecognizer()
        for cell in cells:
            cell["character"] = recognizer.recognize_from_dots(cell["dot_positions"])

        # Convert
        result = converter.full_pipeline(cells)
        elapsed = round((time.perf_counter() - start) * 1000, 1)

        logger.info("Scan: %d dots → %d cells → '%s' (%.0fms)",
                     len(dots), len(cells), result["english_text"], elapsed)

        return web.json_response({
            "success": True,
            "unicode_braille": result["unicode_braille"],
            "english_text": result["english_text"],
            "num_dots": len(dots),
            "num_cells": len(cells),
            "cells": [{"dot_positions": c["dot_positions"], "character": c.get("character", "?")} for c in cells],
            "processing_ms": elapsed,
        })

    except Exception as exc:
        logger.exception("Scan failed")
        return web.json_response({"success": False, "error": str(exc)}, status=500)


# ── Frontend serving ─────────────────────────────────────────────────────────
FRONTEND_DIR = PROJECT_ROOT.parent / "braille-v-web"


async def index_handler(request):
    return web.FileResponse(FRONTEND_DIR / "index.html")


# ── App factory ──────────────────────────────────────────────────────────────
def create_app():
    app = web.Application(middlewares=[cors_middleware])

    # API
    app.router.add_get("/health", health)
    app.router.add_post("/scan", scan)
    app.router.add_route("OPTIONS", "/scan", health)

    # Frontend
    if (FRONTEND_DIR / "dist").exists():
        # Production build
        app.router.add_get("/", lambda r: web.FileResponse(FRONTEND_DIR / "dist" / "index.html"))
        app.router.add_static("/assets/", FRONTEND_DIR / "dist" / "assets")
    elif (FRONTEND_DIR / "index.html").exists():
        app.router.add_get("/", index_handler)

    logger.info("Braille-V API: http://localhost:8000")
    logger.info("Frontend dir: %s", FRONTEND_DIR)
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=8000)
