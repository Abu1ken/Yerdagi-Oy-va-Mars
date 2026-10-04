"""Geographic helper functions: great-circle distance and bearing.

All maths is pure Python (no heavy GIS dependency) so it is trivially testable.
"""

from __future__ import annotations

import math

EARTH_RADIUS_KM = 6371.0088  # IUGG mean Earth radius


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two WGS84 points.

    Uses the haversine formula which is numerically stable for small distances.

    Complexity: O(1).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial compass bearing (0-360) from point 1 to point 2.

    Complexity: O(1).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)

    x = math.sin(d_lambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(
        d_lambda
    )
    theta = math.atan2(x, y)
    return (math.degrees(theta) + 360.0) % 360.0


def bounding_box(lat: float, lon: float, radius_km: float) -> tuple[float, float, float, float]:
    """Return ``(min_lat, min_lon, max_lat, max_lon)`` covering ``radius_km``.

    Used as a cheap SQL prefilter before the exact haversine check, keeping the
    nearest-location query close to O(log N) on the ``lat/lon`` index.
    """
    lat_delta = radius_km / 111.320  # ~km per degree of latitude
    cos_lat = max(math.cos(math.radians(lat)), 1e-6)
    lon_delta = radius_km / (111.320 * cos_lat)

    return (lat - lat_delta, lon - lon_delta, lat + lat_delta, lon + lon_delta)
