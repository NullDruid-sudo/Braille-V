"""
Braille-V Cell Segmentation Service
Groups detected dots into standard 2×3 Braille cells.
"""

import numpy as np

from app.utils.config import settings


def segment_cells(
    dots: list[dict], image_shape: tuple
) -> list[dict]:
    """
    Group detected dots into Braille cells.

    Parameters
    ----------
    dots : list[dict]
        Each dot has keys: x, y, width, height, confidence.
    image_shape : tuple
        (height, width) of the source image.

    Returns
    -------
    list[dict]
        Each cell: {dot_positions: list[int], center_x, center_y, dots: list}
        dot_positions are 1-6 following the standard layout:
            1 4
            2 5
            3 6
    """
    if not dots:
        return []

    # ── Step 1: Estimate grid spacing ────────────────────────────────────
    proximity = _estimate_cell_size(dots)

    # ── Step 2: Cluster dots into cells ──────────────────────────────────
    used = set()
    raw_cells: list[list[dict]] = []

    # Sort dots left-to-right, top-to-bottom for deterministic clustering
    sorted_dots = sorted(dots, key=lambda d: (d["x"], d["y"]))

    for i, seed in enumerate(sorted_dots):
        if i in used:
            continue

        cell_dots = [seed]
        used.add(i)

        for j, candidate in enumerate(sorted_dots):
            if j in used:
                continue
            # Check proximity to *any* dot already in this cell
            if any(_distance(candidate, cd) < proximity for cd in cell_dots):
                cell_dots.append(candidate)
                used.add(j)
                if len(cell_dots) >= 6:
                    break  # a Braille cell has at most 6 dots

        raw_cells.append(cell_dots)

    # ── Step 3: Assign dot positions 1-6 within each cell ────────────────
    cells = []
    for cell_dots in raw_cells:
        cell = _assign_dot_positions(cell_dots)
        cells.append(cell)

    # ── Step 4: Sort cells in reading order (left→right, top→bottom) ─────
    cells.sort(key=lambda c: (c["center_y"], c["center_x"]))

    return cells


# ─── Internal helpers ────────────────────────────────────────────────────────


def _distance(a: dict, b: dict) -> float:
    return float(np.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2))


def _estimate_cell_size(dots: list[dict]) -> float:
    """
    Heuristic: the proximity threshold for grouping dots into a cell.
    Uses the median nearest-neighbour distance × 2.5, clamped to a sane range.
    Falls back to the config default if too few dots.
    """
    if len(dots) < 3:
        return settings.CELL_PROXIMITY_THRESHOLD

    # Compute all nearest-neighbour distances
    nn_dists = []
    for i, d1 in enumerate(dots):
        min_dist = float("inf")
        for j, d2 in enumerate(dots):
            if i == j:
                continue
            dist = _distance(d1, d2)
            if dist < min_dist:
                min_dist = dist
        nn_dists.append(min_dist)

    median_nn = float(np.median(nn_dists))
    # A Braille cell spans ~2.5 × the inter-dot spacing
    estimated = median_nn * 2.5
    # Clamp between 20 and 200 px
    return max(20.0, min(estimated, 200.0))


def _assign_dot_positions(cell_dots: list[dict]) -> dict:
    """
    Given a cluster of dots belonging to one Braille cell,
    assign each dot a position number 1-6:

        Col 0  Col 1
        ─────  ─────
        1      4       (top)
        2      5       (middle)
        3      6       (bottom)

    Returns a cell dict with dot_positions, center, and raw dots.
    """
    if not cell_dots:
        return {"dot_positions": [], "center_x": 0, "center_y": 0, "dots": []}

    xs = [d["x"] for d in cell_dots]
    ys = [d["y"] for d in cell_dots]
    center_x = float(np.mean(xs))
    center_y = float(np.mean(ys))

    dot_positions: list[int] = []

    for dot in cell_dots:
        # Left / right column
        col = 0 if dot["x"] < center_x else 1

        # Row: top / middle / bottom (thirds of the vertical span)
        y_min, y_max = min(ys), max(ys)
        y_range = y_max - y_min if y_max > y_min else 1.0
        relative_y = (dot["y"] - y_min) / y_range

        if relative_y < 0.33:
            row = 0  # top
        elif relative_y < 0.67:
            row = 1  # middle
        else:
            row = 2  # bottom

        # Map (col, row) → dot number
        #   col 0: 1, 2, 3
        #   col 1: 4, 5, 6
        dot_num = row + 1 + col * 3
        dot_positions.append(dot_num)

    # De-duplicate (in case two dots land in the same position)
    dot_positions = sorted(set(dot_positions))

    return {
        "dot_positions": dot_positions,
        "center_x": center_x,
        "center_y": center_y,
        "dots": cell_dots,
    }
