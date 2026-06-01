"""
Braille-V — SQLite Database Layer
Stores scan history. Uses Python's built-in sqlite3 — no extra deps needed.
"""

import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

# Database lives at the backend root
_DB_PATH = Path(__file__).resolve().parent.parent / "braille_v.db"

# Max history entries to keep
MAX_HISTORY = 50


def init_db() -> None:
    """Create tables if they don't exist. Called once on app startup."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       REAL    NOT NULL,          -- Unix epoch (float)
                unicode_braille TEXT    NOT NULL DEFAULT '',
                english_text    TEXT    NOT NULL DEFAULT '',
                num_dots        INTEGER NOT NULL DEFAULT 0,
                num_cells       INTEGER NOT NULL DEFAULT 0,
                processing_ms   REAL    NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


@contextmanager
def _connect():
    """Context manager that yields a sqlite3 Connection with row_factory set."""
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ── CRUD ─────────────────────────────────────────────────────────────────────

def save_scan(
    unicode_braille: str,
    english_text: str,
    num_dots: int,
    num_cells: int,
    processing_ms: float,
) -> dict:
    """
    Insert a new scan record and trim the table to MAX_HISTORY rows.
    Returns the saved row as a dict.
    """
    with _connect() as conn:
        ts = time.time()
        cursor = conn.execute(
            """
            INSERT INTO scans (timestamp, unicode_braille, english_text,
                               num_dots, num_cells, processing_ms)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (ts, unicode_braille, english_text, num_dots, num_cells, processing_ms),
        )
        new_id = cursor.lastrowid

        # Keep only the most recent MAX_HISTORY rows
        conn.execute(
            """
            DELETE FROM scans
            WHERE id NOT IN (
                SELECT id FROM scans ORDER BY timestamp DESC LIMIT ?
            )
            """,
            (MAX_HISTORY,),
        )
        conn.commit()

    return get_scan(new_id)


def get_scan(scan_id: int) -> dict | None:
    """Fetch a single scan by ID."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM scans WHERE id = ?", (scan_id,)
        ).fetchone()
        return dict(row) if row else None


def get_history(limit: int = MAX_HISTORY) -> list[dict]:
    """Return up to `limit` most-recent scans, newest first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM scans ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def delete_scan(scan_id: int) -> bool:
    """Delete a scan by ID. Returns True if a row was deleted."""
    with _connect() as conn:
        cursor = conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
        conn.commit()
        return cursor.rowcount > 0


def clear_history() -> int:
    """Delete all scan records. Returns the number of deleted rows."""
    with _connect() as conn:
        cursor = conn.execute("DELETE FROM scans")
        conn.commit()
        return cursor.rowcount
