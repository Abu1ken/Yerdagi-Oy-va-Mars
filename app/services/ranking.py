"""Ranking helpers built on Python's ``heapq``.

* ``top_k``      - best K items of a stream,             O(n log k)
* ``nearest_k``  - closest K items by great-circle dist, O(n log k)
* ``compare``    - normalised vectors for a radar chart, O(m * F)
"""

from __future__ import annotations

import heapq
from typing import Iterable, Sequence

from app.services.geo import bearing_deg, haversine_km
from app.services.similarity import FEATURE_INDEX, FEATURE_NAMES, FeatureSpec, normalize


def top_k(pairs: Iterable[tuple[int, float]], k: int) -> list[tuple[int, float]]:
    """Return the ``k`` pairs with the highest score, sorted descending.

    Uses a bounded heap so memory stays O(k) even for very large inputs.

    Complexity: O(n log k) time, O(k) space.
    """
    if k <= 0:
        return []
    return heapq.nlargest(k, pairs, key=lambda pair: pair[1])


def nearest_k(
    origin: tuple[float, float],
    points: Iterable[tuple[int, float, float]],
    k: int,
    radius_km: float | None = None,
) -> list[tuple[int, float]]:
    """Return ``(id, distance_km)`` for the ``k`` closest points to ``origin``.

    ``points`` yields ``(id, lat, lon)``.  Optional ``radius_km`` filters out
    anything farther away.

    Complexity: O(n) distance computations, O(n log k) heap operations.
    """
    if k <= 0:
        return []

    lat0, lon0 = origin
    distances: list[tuple[int, float]] = []
    for point_id, lat, lon in points:
        distance = haversine_km(lat0, lon0, lat, lon)
        if radius_km is not None and distance > radius_km:
            continue
        distances.append((point_id, distance))

    return heapq.nsmallest(k, distances, key=lambda pair: pair[1])


def bearing_to(origin: tuple[float, float], lat: float, lon: float) -> float:
    """Compass bearing from ``origin`` to ``(lat, lon)`` in degrees."""
    return round(bearing_deg(origin[0], origin[1], lat, lon), 1)


def _axis_specs(axes: Sequence[str]) -> list[FeatureSpec]:
    return [FEATURE_INDEX[name] for name in axes if name in FEATURE_INDEX]


def compare_datasets(
    axes: Sequence[str],
    series: Sequence[tuple[int, str, dict[str, float]]],
) -> tuple[list[str], list[str], list[dict]]:
    """Build radar-chart datasets for 2-3 locations.

    ``series`` is a sequence of ``(location_id, label, vector)``.  Every axis is
    min-max normalised to ``0-100`` using the global feature ranges so the radar
    chart is directly comparable across locations.

    Returns ``(axes, axis_labels, datasets)``.

    Complexity: O(m * F) with m locations and F axes.
    """
    valid_specs = _axis_specs(axes)
    axis_names = [spec.name for spec in valid_specs]
    axis_labels = [spec.label for spec in valid_specs]

    datasets: list[dict] = []
    for location_id, label, vector in series:
        values = [
            round(normalize(vector.get(spec.name, spec.min_value), spec) * 100.0, 2)
            for spec in valid_specs
        ]
        datasets.append({"location_id": location_id, "label": label, "values": values})

    return axis_names, axis_labels, datasets


def available_axes() -> list[str]:
    """Feature names suitable for a radar chart (excludes boolean flags)."""
    return [name for name in FEATURE_NAMES if FEATURE_INDEX[name].kind == "numeric"]
