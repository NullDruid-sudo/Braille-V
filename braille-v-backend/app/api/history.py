"""
Braille-V History API
CRUD endpoints for scan history stored in SQLite.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import (
    get_history,
    get_scan,
    delete_scan,
    clear_history,
    save_scan,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/history", tags=["history"])


# ── Request/Response models ──────────────────────────────────────────────────

class SaveScanRequest(BaseModel):
    unicode_braille: str = ""
    english_text: str = ""
    num_dots: int = 0
    num_cells: int = 0
    processing_ms: float = 0.0


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("")
async def list_history(limit: int = 50):
    """Return the most recent scans, newest first."""
    rows = get_history(limit=min(limit, 50))
    return {"success": True, "scans": rows, "count": len(rows)}


@router.get("/{scan_id}")
async def get_scan_by_id(scan_id: int):
    """Fetch a single scan record."""
    row = get_scan(scan_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"success": True, "scan": row}


@router.post("")
async def save_scan_manually(body: SaveScanRequest):
    """
    Manually save a scan to history.
    (Scans from /scan are auto-saved; this is the explicit 'Save' button endpoint.)
    """
    row = save_scan(
        unicode_braille=body.unicode_braille,
        english_text=body.english_text,
        num_dots=body.num_dots,
        num_cells=body.num_cells,
        processing_ms=body.processing_ms,
    )
    return {"success": True, "scan": row}


@router.delete("/{scan_id}")
async def delete_scan_by_id(scan_id: int):
    """Delete a single scan record."""
    deleted = delete_scan(scan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"success": True, "deleted_id": scan_id}


@router.delete("")
async def clear_all_history():
    """Delete all scan history."""
    count = clear_history()
    logger.info("Cleared %d scan records", count)
    return {"success": True, "deleted_count": count}
