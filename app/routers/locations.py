"""``/api/locations`` endpoints: filtered listing and full detail."""

from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LOCATION_TYPES, Location, PlanetProfile
from app.schemas import (
    LocationDetail,
    LocationListResponse,
    PlanetProfileOut,
)
from app.services import analytics

router = APIRouter(prefix="/api", tags=["locations"])

SortField = Literal["score", "name", "country", "elevation"]


@router.get("/locations", response_model=LocationListResponse)
def list_locations(
    planet: Optional[Literal["moon", "mars"]] = Query(
        None, description="Faqat shu sayyoraga o'xshash joylar (min_score bilan)"
    ),
    type: Optional[Literal["desert", "volcano", "cave", "glacier", "crater", "other"]] = Query(
        None, description="Joy turi"
    ),
    country: Optional[str] = Query(None, description="Davlat nomi bo'yicha filtr"),
    min_score: float = Query(0.0, ge=0, le=100, description="Minimal o'xshashlik %"),
    sort: SortField = Query("score", description="Saralash maydoni"),
    order: Literal["asc", "desc"] = Query("desc", description="Saralash tartibi"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> LocationListResponse:
    """Return a filtered, sorted and paginated list of analog locations.

    Scores are computed once per location (O(n)) and filtered/sorted in memory so
    that a ``planet`` + ``min_score`` filter stays consistent with ``/api/top``.
    """
    profiles = analytics.load_profiles(db)

    stmt = select(Location)
    if type is not None:
        stmt = stmt.where(Location.type == type)
    if country:
        stmt = stmt.where(func.lower(Location.country) == country.strip().lower())

    locations = db.execute(stmt.order_by(Location.id)).scalars().all()
    summaries = analytics.summarize_many(locations, profiles)

    # --- in-memory filtering by score (O(n)) ---
    # When a planet is given we keep only locations whose score for *that*
    # planet reaches ``min_score`` (a location can be a great Mars analog even
    # if its Moon score is low).  Otherwise we filter on the best score.
    if planet is not None:
        summaries = [s for s in summaries if (s[f"{planet}_score"] or 0) >= min_score]
    elif min_score > 0:
        summaries = [s for s in summaries if (s["best_score"] or 0) >= min_score]

    # --- sorting ---
    reverse = order == "desc"
    if sort == "score":
        key_field = planet if planet else "best_score"
        summaries.sort(key=lambda s: (s.get(key_field) or 0), reverse=reverse)
    elif sort == "name":
        summaries.sort(key=lambda s: s["name"].lower(), reverse=reverse)
    elif sort == "country":
        summaries.sort(key=lambda s: s["country"].lower(), reverse=reverse)
    else:  # elevation
        summaries.sort(key=lambda s: (s["elevation_m"] if s["elevation_m"] is not None else -1e9), reverse=reverse)

    total = len(summaries)
    start = (page - 1) * page_size
    page_items = summaries[start : start + page_size]

    return LocationListResponse(
        total=total,
        page=page,
        page_size=page_size,
        count=len(page_items),
        items=page_items,
    )


@router.get("/locations/{location_id}", response_model=LocationDetail)
def get_location(location_id: int, db: Session = Depends(get_db)) -> LocationDetail:
    """Return full detail for one location: features, both scores and reasons."""
    location = db.get(Location, location_id)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location {location_id} topilmadi",
        )

    profiles = analytics.load_profiles(db)
    payload = analytics.detail(location, profiles)

    if payload.get("features") is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Location {location_id} uchun xususiyatlar mavjud emas",
        )
    return LocationDetail(**payload)


@router.get("/types", response_model=list[str], tags=["meta"])
def list_types() -> list[str]:
    """Return the allowed location types."""
    return list(LOCATION_TYPES)


@router.get("/planets", response_model=list[PlanetProfileOut], tags=["meta"])
def list_planets(db: Session = Depends(get_db)) -> list[PlanetProfileOut]:
    """Return Moon and Mars profiles with every feature weight."""
    rows = db.execute(select(PlanetProfile)).scalars().all()
    grouped: dict[str, list[dict]] = {"moon": [], "mars": []}
    for row in rows:
        grouped.setdefault(row.planet, []).append(
            {
                "feature_name": row.feature_name,
                "ideal_value": row.ideal_value,
                "weight": row.weight,
            }
        )
    return [
        PlanetProfileOut(planet=planet, features=features)  # type: ignore[arg-type]
        for planet, features in grouped.items()
        if features
    ]
