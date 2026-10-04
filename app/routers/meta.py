"""Meta endpoints: health check and radar-chart axis catalogue."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Location
from app.schemas import HealthResponse
from app.services.ranking import available_axes

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    """Return service status and the number of seeded locations."""
    settings = get_settings()
    total = db.scalar(select(func.count(Location.id))) or 0
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        locations=int(total),
    )


@router.get("/axes", response_model=list[str])
def axes() -> list[str]:
    """Return the feature names available as radar-chart axes."""
    return available_axes()
