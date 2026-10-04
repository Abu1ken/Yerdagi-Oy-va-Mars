"""FastAPI application entry point.

Wires together configuration, CORS, the API routers and the static front-end.
A small lifespan hook makes sure the FTS5 search index exists on start-up so the
``/api/search`` endpoint works even if the migration was not run.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import engine
from app.routers import locations, meta, nearest, ranking, search
from app.services.fulltext import ensure_fts_schema

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the FTS5 index (idempotent) when the app starts."""
    settings = get_settings()
    if settings.is_sqlite:
        with engine.begin() as connection:
            ensure_fts_schema(connection)
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Yer yuzidagi Oy va Marsga o'xshash joylarni topish, baholash va "
        "tushuntirish uchun API."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API routers -----------------------------------------------------------
app.include_router(search.router)
app.include_router(locations.router)
app.include_router(nearest.router)
app.include_router(ranking.router)
app.include_router(meta.router)


@app.get("/api", tags=["meta"])
def api_root() -> dict[str, str]:
    """Small root endpoint describing the API."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
    }


# --- Static front-end (mounted last so /api/* wins) ------------------------
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
