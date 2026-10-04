"""``/api/nearest`` endpoint: closest analog locations to a coordinate.

Uses a Haversine great-circle distance with an optional SQL bounding-box
prefilter (served by the ``ix_locations_lat_lon`` index) and a bounded heap for
selection.
"""

from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Location
from app.schemas import NearestResponse
from app.services import analytics
from app.services.geo import bounding_box
from app.services.ranking import bearing_to, nearest_k

router = APIRouter(prefix="/api", tags=["nearest"])


@router.get("/nearest", response_model=NearestResponse)
def nearest(
    lat: float = Query(..., ge=-90, le=90, description="Kenglik"),
    lon: float = Query(..., ge=-180, le=180, description="Uzunlik"),
    planet: Optional[Literal["moon", "mars"]] = Query(
        None, description="Faqat shu sayyora analogini hisobga olish"
    ),
    limit: int = Query(5, ge=1, le=50, description="Natijalar soni"),
    radius_km: Optional[float] = Query(
        None, gt=0, le=20000, description="Faqat shu radius ichidagi joylar"
    ),
    min_score: float = Query(
        0.0, ge=0, le=100, description="Tanlangan sayyora uchun minimal o'xshashlik %"
    ),
    db: Session = Depends(get_db),
) -> NearestResponse:
    """Return the ``limit`` closest analog locations to ``(lat, lon)``.

    When ``planet`` is given, only locations whose score for that planet is at
    least ``min_score`` are kept.  Complexity: O(N) distance computations with
    O(N log limit) heap selection; the optional bounding box narrows N first.
    """
    profiles = analytics.load_profiles(db)

    stmt = select(Location)
    if radius_km is not None:
        min_lat, min_lon, max_lat, max_lon = bounding_box(lat, lon, radius_km)
        stmt = stmt.where(
            Location.lat.between(min_lat, max_lat),
            Location.lon.between(min_lon, max_lon),
        )
    locations = db.execute(stmt).scalars().all()
    by_id = {location.id: location for location in locations}

    points = [(location.id, location.lat, location.lon) for location in locations]
    # Ask for a few extra candidates so planet/min_score filtering still yields
    # the requested number of items in common cases.
    fetch = limit if planet is None and min_score <= 0 else min(len(points), limit * 5)
    ranked = nearest_k((lat, lon), points, k=fetch, radius_km=radius_km)

    items: list[dict] = []
    for location_id, distance in ranked:
        location = by_id.get(location_id)
        if location is None:
            continue
        summary = analytics.summarize(location, profiles)
        if planet is not None and (summary.get(f"{planet}_score") or 0) < min_score:
            continue
        summary["distance_km"] = round(distance, 2)
        summary["bearing_deg"] = bearing_to((lat, lon), location.lat, location.lon)
        items.append(summary)
        if len(items) >= limit:
            break

    return NearestResponse(
        origin={"lat": lat, "lon": lon},
        planet=planet,
        count=len(items),
        items=items,
    )
