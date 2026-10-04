"""``/api/top`` and ``/api/compare`` endpoints.

* ``/api/top``     - best K analogs for a planet, selected with a bounded heap
                     (``heapq.nlargest``) in O(N log K).
* ``/api/compare`` - 2-3 locations side by side, returning radar-chart data.
"""

from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Location
from app.schemas import CompareResponse, RadarDataset, TopResponse
from app.services import analytics
from app.services.ranking import available_axes, compare_datasets, top_k
from app.services.similarity import FEATURE_INDEX

router = APIRouter(prefix="/api", tags=["ranking"])

MAX_COMPARE = 3


@router.get("/top", response_model=TopResponse)
def top(
    planet: Literal["moon", "mars"] = Query(..., description="Sayyora"),
    k: int = Query(5, ge=1, le=50, description="Nechta eng yaxshi analog"),
    db: Session = Depends(get_db),
) -> TopResponse:
    """Return the ``k`` locations most similar to ``planet``.

    Complexity: O(N) scoring + O(N log k) heap selection.
    """
    profiles = analytics.load_profiles(db)
    locations = db.execute(select(Location)).scalars().all()

    pairs = [
        (location.id, analytics.score_location(location, profiles).get(planet, 0.0))
        for location in locations
    ]
    ranked = top_k(pairs, k)

    by_id = {location.id: location for location in locations}
    items = [
        analytics.summarize(by_id[location_id], profiles)
        for location_id, _score in ranked
        if location_id in by_id
    ]
    return TopResponse(planet=planet, k=k, count=len(items), items=items)


@router.get("/compare", response_model=CompareResponse)
def compare(
    ids: str = Query(..., description="Vergul bilan ajratilgan 2-3 ta joy id: 1,2,3"),
    axes: Optional[str] = Query(
        None,
        description="Vergul bilan ajratilgan o'qlar (bo'sh bo'lsa standart to'plam)",
    ),
    db: Session = Depends(get_db),
) -> CompareResponse:
    """Compare 2-3 locations and return normalised radar-chart datasets.

    Complexity: O(m * F) with m locations and F axes.
    """
    parsed = _parse_ids(ids)
    if not (2 <= len(parsed) <= MAX_COMPARE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"2 tadan {MAX_COMPARE} tagacha joy id kerak (berildi: {len(parsed)})",
        )

    requested_axes = _parse_axes(axes)
    if requested_axes is None:
        return _build(db, parsed, available_axes())
    return _build(db, parsed, requested_axes)


def _parse_ids(raw: str) -> list[int]:
    """Parse a ``"1,2,3"`` string into an ordered list of unique ints."""
    result: list[int] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            value = int(chunk)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{chunk}' yaroqli id emas",
            ) from exc
        if value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"id musbat bo'lishi kerak: {value}",
            )
        if value not in result:
            result.append(value)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kamida 2 ta joy id kerak",
        )
    return result


def _parse_axes(raw: Optional[str]) -> Optional[list[str]]:
    """Validate requested radar axes, returning ``None`` for the default set."""
    if raw is None or not raw.strip():
        return None
    axes = [name.strip() for name in raw.split(",") if name.strip()]
    invalid = [name for name in axes if name not in FEATURE_INDEX]
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Noma'lum o'qlar: {', '.join(invalid)}",
        )
    if not axes:
        return None
    return axes


def _build(db: Session, ids: list[int], axes: list[str]) -> CompareResponse:
    """Load the locations and build the comparison payload."""
    locations = db.execute(select(Location).where(Location.id.in_(ids))).scalars().all()
    by_id = {location.id: location for location in locations}

    missing = [location_id for location_id in ids if location_id not in by_id]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Joy(lar) topilmadi: {', '.join(str(m) for m in missing)}",
        )

    series: list[tuple[int, str, dict[str, float]]] = []
    for location_id in ids:
        location = by_id[location_id]
        if location.features is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Location {location_id} uchun xususiyatlar mavjud emas",
            )
        series.append((location.id, location.name, location.features.as_vector()))

    axis_names, axis_labels, datasets = compare_datasets(axes, series)
    return CompareResponse(
        axes=axis_names,
        axis_labels=axis_labels,
        datasets=[RadarDataset(**dataset) for dataset in datasets],
    )
