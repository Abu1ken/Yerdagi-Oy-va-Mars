"""High level analytics service.

Bridges the ORM layer and the pure algorithm modules:

* loads (and caches) the Moon/Mars planet profiles,
* scores a location against one or both planets using the shared cache,
* builds serialisable summary dictionaries for the API layer.

Every scoring call is O(F); the per ``(planet, location_id)`` cache turns
repeated requests on the same data into O(1) dictionary lookups.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Location, PlanetProfile
from app.services.cache import score_cache
from app.services.reasons import generate_reasons
from app.services.similarity import (
    FEATURE_NAMES,
    Profile,
    build_profile,
    feature_contributions,
    weighted_similarity,
)

PROFILES_CACHE_KEY = "planet_profiles:v1"


def load_profiles(db: Session, force: bool = False) -> dict[str, dict[str, tuple[float, float]]]:
    """Return ``{planet: {feature: (ideal, weight)}}`` from the database.

    Cached process-wide; call :func:`app.services.cache.invalidate_all` after
    changing the ``planet_profiles`` table.
    """

    def _compute() -> dict[str, dict[str, tuple[float, float]]]:
        rows = db.execute(select(PlanetProfile)).scalars().all()
        grouped: dict[str, list[PlanetProfile]] = {"moon": [], "mars": []}
        for row in rows:
            grouped.setdefault(row.planet, []).append(row)
        return {planet: build_profile(rows_) for planet, rows_ in grouped.items()}

    if force:
        score_cache.clear()
    return score_cache.get_or_compute(PROFILES_CACHE_KEY, _compute)


def score_location(
    location: Location, profiles: Mapping[str, Mapping[str, tuple[float, float]]]
) -> dict[str, float]:
    """Return ``{planet: score}`` for a single location (cached)."""
    if location.features is None:
        return {}

    scores: dict[str, float] = {}
    for planet, profile in profiles.items():
        if not profile:
            continue
        key = (planet, location.id)
        scores[planet] = score_cache.get_or_compute(
            key, lambda vec=location.features.as_vector(), prof=profile: weighted_similarity(vec, prof)
        )
    return scores


def best_planet(scores: Mapping[str, float]) -> tuple[str | None, float | None]:
    """Return the planet with the highest score and that score."""
    if not scores:
        return None, None
    planet = max(scores, key=lambda p: scores[p])
    return planet, scores[planet]


def summarize(
    location: Location, profiles: Mapping[str, Mapping[str, tuple[float, float]]]
) -> dict:
    """Build the compact summary dictionary used across list endpoints."""
    scores = score_location(location, profiles)
    planet, best = best_planet(scores)
    return {
        "id": location.id,
        "name": location.name,
        "country": location.country,
        "lat": location.lat,
        "lon": location.lon,
        "type": location.type,
        "elevation_m": location.elevation_m,
        "description": location.description,
        "source_url": location.source_url,
        "is_estimated": bool(location.features.is_estimated) if location.features else True,
        "moon_score": scores.get("moon"),
        "mars_score": scores.get("mars"),
        "best_planet": planet,
        "best_score": best,
    }


def detail(
    location: Location, profiles: Mapping[str, Mapping[str, tuple[float, float]]]
) -> dict:
    """Build the full detail dictionary including reasons for both planets."""
    base = summarize(location, profiles)
    features = location.features

    scores_out = [
        {"planet": planet, "score": score}
        for planet, score in sorted(base_planet_scores(base).items())
    ]

    reasons_out: list[dict] = []
    if features is not None:
        vector = features.as_vector()
        for planet, profile in profiles.items():
            if not profile:
                continue
            reasons_out.extend(
                generate_reasons(vector, profile, planet, top_n=5)
            )

    curated = [
        {"planet": reason.planet, "text": reason.reason_text, "category": reason.category}
        for reason in location.reasons
    ]

    payload = dict(base)
    payload.update(
        {
            "features": {
                "avg_temp_c": features.avg_temp_c,
                "temp_range_c": features.temp_range_c,
                "annual_rainfall_mm": features.annual_rainfall_mm,
                "humidity_pct": features.humidity_pct,
                "terrain_roughness": features.terrain_roughness,
                "iron_oxide_level": features.iron_oxide_level,
                "basalt_level": features.basalt_level,
                "radiation_level": features.radiation_level,
                "dust_level": features.dust_level,
                "lava_tubes": bool(features.lava_tubes),
                "ice_presence": bool(features.ice_presence),
                "is_estimated": bool(features.is_estimated),
            }
            if features is not None
            else None,
            "scores": scores_out,
            "reasons": reasons_out,
            "curated_reasons": curated,
        }
    )
    return payload


def base_planet_scores(summary: Mapping) -> dict[str, float]:
    """Extract ``{planet: score}`` from a summary dictionary."""
    result: dict[str, float] = {}
    for planet in ("moon", "mars"):
        value = summary.get(f"{planet}_score")
        if value is not None:
            result[planet] = value
    return result


def contributions_for(
    vector: Mapping[str, float], profile: Profile
) -> list[tuple[str, float]]:
    """Return contributions as a sorted ``(feature, share)`` list."""
    shares = feature_contributions(vector, profile)
    return list(shares.items())


def feature_names() -> Sequence[str]:
    """Expose the canonical feature ordering."""
    return FEATURE_NAMES


def summarize_many(
    locations: Iterable[Location],
    profiles: Mapping[str, Mapping[str, tuple[float, float]]],
) -> list[dict]:
    """Summarise an iterable of locations (single profile load, O(n) scoring)."""
    return [summarize(location, profiles) for location in locations]
