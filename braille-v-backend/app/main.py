"""
Braille-V Backend — FastAPI Application
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import router
from app.api.history import router as history_router
from app.database import init_db
from app.utils.config import settings

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── FastAPI app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Braille-V API",
    description="Braille image recognition and translation API",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialise database ──────────────────────────────────────────────────────
init_db()
logger.info("SQLite database initialised")

# ── Mount routes ─────────────────────────────────────────────────────────────
app.include_router(router)
app.include_router(history_router)

logger.info("Braille-V API ready  |  CORS origins: %s", settings.CORS_ORIGINS)


# ── Entry point (for `python -m app.main`) ───────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
