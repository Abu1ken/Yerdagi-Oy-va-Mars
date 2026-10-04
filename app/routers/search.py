"""``/api/search`` endpoint: FTS5 full-text search by name and description."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SearchResponse
from app.services import analytics, fulltext

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search_locations(
    q: str = Query(..., min_length=1, max_length=200, description="Qidiruv so'zi"),
    limit: int = Query(20, ge=1, le=100, description="Maksimal natijalar soni"),
    db: Session = Depends(get_db),
) -> SearchResponse:
    """Return locations whose name or description matches ``q``.

    Search is performed with SQLite **FTS5** (inverted index, ~O(log N + matches)).
    Scores for every hit are filled in so the front-end can show markers directly.
    """
    query = q.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Qidiruv so'zi (q) bo'sh bo'lmasligi kerak",
        )

    profiles = analytics.load_profiles(db)
    locations = fulltext.search_locations(db, query, limit)
    items = analytics.summarize_many(locations, profiles)
    return SearchResponse(query=query, count=len(items), items=items)
