"""
Braille-V Image Preprocessing Service
Handles adaptive thresholding, perspective correction, and lighting normalisation.
"""

import cv2
import numpy as np


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Full preprocessing pipeline.

    Parameters
    ----------
    image_bytes : bytes
        Raw image bytes received from the frontend.

    Returns
    -------
    np.ndarray
        Preprocessed grayscale image ready for dot detection.
    """
    # Decode bytes → BGR image
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image from provided bytes")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Normalise lighting with CLAHE *before* thresholding so the
    # adaptive threshold has a more uniform input.
    normalized = _normalize_lighting(gray)

    # Adaptive thresholding for varying lighting conditions
    thresh = cv2.adaptiveThreshold(
        normalized,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=11,
        C=2,
    )

    # Gentle Gaussian blur to reduce salt-and-pepper noise
    blurred = cv2.GaussianBlur(thresh, (3, 3), 0)

    # Attempt perspective correction (robust: returns original on failure)
    corrected = _correct_perspective(blurred, image.shape)

    return corrected


# ─── Internal helpers ────────────────────────────────────────────────────────


def _normalize_lighting(gray: np.ndarray) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalisation)."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _correct_perspective(binary: np.ndarray, original_shape: tuple) -> np.ndarray:
    """
    Detect the Braille page quadrilateral and warp to a top-down view.
    Falls back to the input image if no suitable contour is found.
    """
    try:
        # Dilate slightly to close small gaps before contour detection
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(binary, kernel, iterations=2)

        contours, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return binary

        # Largest contour by area (hopefully the Braille page)
        largest = max(contours, key=cv2.contourArea)

        # Minimum area must be at least 20 % of image to be a page
        image_area = binary.shape[0] * binary.shape[1]
        if cv2.contourArea(largest) < 0.2 * image_area:
            return binary

        # Approximate polygon
        peri = cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, 0.02 * peri, True)

        if len(approx) != 4:
            return binary  # Not a quadrilateral

        corners = _order_corners(approx.reshape(4, 2).astype(np.float32))
        return _warp_perspective(binary, corners)

    except Exception:
        # Any geometry error → return unmodified image
        return binary


def _order_corners(pts: np.ndarray) -> np.ndarray:
    """Order four points as [top-left, top-right, bottom-right, bottom-left]."""
    rect = np.zeros((4, 2), dtype=np.float32)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left has smallest x+y
    rect[2] = pts[np.argmax(s)]   # bottom-right has largest x+y
    d = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(d)]   # top-right has smallest y-x
    rect[3] = pts[np.argmax(d)]   # bottom-left has largest y-x
    return rect


def _warp_perspective(image: np.ndarray, corners: np.ndarray) -> np.ndarray:
    """Warp quadrilateral to a rectangle."""
    tl, tr, br, bl = corners

    width_top = np.linalg.norm(tr - tl)
    width_bot = np.linalg.norm(br - bl)
    width = int(max(width_top, width_bot))

    height_left = np.linalg.norm(bl - tl)
    height_right = np.linalg.norm(br - tr)
    height = int(max(height_left, height_right))

    dst = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype=np.float32,
    )

    M = cv2.getPerspectiveTransform(corners, dst)
    return cv2.warpPerspective(image, M, (width, height))
