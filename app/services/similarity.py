"""Similarity algorithm: normalise, weight, compare.

Math
----
Each feature ``i`` of a location is min-max normalised into ``[0, 1]`` using a
global, physically motivated range (see :data:`FEATURE_SPECS`)::

    x_i = (value_i - min_i) / (max_i - min_i)          # clamped to [0, 1]

The same transform is applied to the *ideal* planetary value, giving
``p_i`` in ``[0, 1]``.  The dissimilarity is a **weighted Euclidean (RMS)
distance**::

    d = sqrt( sum_i w_i * (x_i - p_i)^2 / sum_i w_i )

Because every term ``(x_i - p_i)^2`` is itself in ``[0, 1]``, the weighted mean
is also in ``[0, 1]`` and therefore so is ``d``.  Similarity is reported as::

    score = (1 - d) * 100                              # percent in [0, 100]

Weights ``w_i`` come from the ``planet_profiles`` table, so the ranking can be
tuned (e.g. iron-oxide and dust matter more for Mars) without touching code.

A weighted **cosine similarity** variant is also provided for comparison /
experimentation; it ignores magnitude differences but is more sensitive to the
all-zero-vector edge case.

Complexity
----------
With ``F`` features (constant, ``F = 11`` here):

* ``weighted_similarity``      -> O(F)  == O(1)
* ``feature_contributions``    -> O(F log F) (sort of F contributions)
* ``cosine_similarity``        -> O(F)
Rating every location for one planet is therefore O(N).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Mapping

# --------------------------------------------------------------------------- #
# Feature catalogue
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class FeatureSpec:
    """Static metadata describing one feature and its normalisation range."""

    name: str
    label: str
    unit: str
    min_value: float
    max_value: float
    kind: str = "numeric"  # "numeric" | "boolean"


# The min/max ranges below are physically motivated bounds chosen so that every
# realistic Earth value (and the Moon/Mars ideal value) maps into [0, 1].
FEATURE_SPECS: tuple[FeatureSpec, ...] = (
    FeatureSpec("avg_temp_c", "O'rtacha harorat", "°C", -90.0, 60.0),
    FeatureSpec("temp_range_c", "Harorat tebranishi", "°C", 0.0, 300.0),
    FeatureSpec("annual_rainfall_mm", "Yillik yog'in", "mm", 0.0, 2000.0),
    FeatureSpec("humidity_pct", "Namlik", "%", 0.0, 100.0),
    FeatureSpec("terrain_roughness", "Relyef notekisligi", "/10", 1.0, 10.0),
    FeatureSpec("iron_oxide_level", "Temir oksidi", "/10", 1.0, 10.0),
    FeatureSpec("basalt_level", "Bazalt", "/10", 1.0, 10.0),
    FeatureSpec("radiation_level", "Radiatsiya", "/10", 1.0, 10.0),
    FeatureSpec("dust_level", "Chang", "/10", 1.0, 10.0),
    FeatureSpec("lava_tubes", "Lava quvurlari", "", 0.0, 1.0, kind="boolean"),
    FeatureSpec("ice_presence", "Muz mavjudligi", "", 0.0, 1.0, kind="boolean"),
)

FEATURE_INDEX: Mapping[str, FeatureSpec] = {spec.name: spec for spec in FEATURE_SPECS}
FEATURE_NAMES: tuple[str, ...] = tuple(spec.name for spec in FEATURE_SPECS)

# A profile maps feature_name -> (ideal_raw_value, weight).
Profile = Mapping[str, tuple[float, float]]


# --------------------------------------------------------------------------- #
# Normalisation
# --------------------------------------------------------------------------- #


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp ``value`` into ``[low, high]``."""
    return max(low, min(high, value))


def normalize(value: float, spec: FeatureSpec) -> float:
    """Min-max normalise ``value`` using ``spec``'s range into ``[0, 1]``."""
    span = spec.max_value - spec.min_value
    if span == 0:
        return 0.0
    return clamp((float(value) - spec.min_value) / span)


def normalize_vector(vector: Mapping[str, float]) -> dict[str, float]:
    """Return a fully normalised copy of ``vector`` (missing -> 0.0)."""
    return {
        name: normalize(vector.get(name, FEATURE_INDEX[name].min_value), FEATURE_INDEX[name])
        for name in FEATURE_NAMES
    }


# --------------------------------------------------------------------------- #
# Similarity scoring
# --------------------------------------------------------------------------- #


def weighted_similarity(vector: Mapping[str, float], profile: Profile) -> float:
    """Weighted Euclidean similarity of a location to a planet profile.

    Returns a percentage in ``[0, 100]`` (higher == more similar).

    Complexity: O(F) where F = len(FEATURE_NAMES) (constant).
    """
    if not profile:
        raise ValueError("profile must contain at least one feature")

    weighted_sq_sum = 0.0
    total_weight = 0.0

    for name in FEATURE_NAMES:
        if name not in profile:
            continue
        spec = FEATURE_INDEX[name]
        ideal_raw, weight = profile[name]
        if weight is None or weight <= 0:
            continue

        x = normalize(vector.get(name, spec.min_value), spec)
        ideal = normalize(ideal_raw, spec)
        delta = x - ideal
        weighted_sq_sum += weight * delta * delta
        total_weight += weight

    if total_weight == 0:
        return 0.0

    distance = math.sqrt(weighted_sq_sum / total_weight)  # in [0, 1]
    return round(clamp(1.0 - distance) * 100.0, 2)


def feature_contributions(
    vector: Mapping[str, float], profile: Profile
) -> dict[str, float]:
    """Return each feature's share (0-1) of the total weighted distance.

    Used by the explanation generator to pick the most influential features.

    Complexity: O(F log F) due to the final sort.
    """
    raw: dict[str, float] = {}
    total = 0.0
    for name in FEATURE_NAMES:
        if name not in profile:
            continue
        spec = FEATURE_INDEX[name]
        ideal_raw, weight = profile[name]
        if weight is None or weight <= 0:
            continue
        x = normalize(vector.get(name, spec.min_value), spec)
        ideal = normalize(ideal_raw, spec)
        contribution = weight * (x - ideal) ** 2
        raw[name] = contribution
        total += contribution

    if total <= 0:
        return {name: 0.0 for name in raw}

    shares = {name: c / total for name, c in raw.items()}
    return dict(sorted(shares.items(), key=lambda kv: -kv[1]))


def signed_delta(
    vector: Mapping[str, float], profile: Profile, feature_name: str
) -> float:
    """Normalised signed difference ``x_i - p_i`` for one feature.

    Positive means the location has *more* of the feature than the planet's
    ideal; negative means *less*.
    """
    spec = FEATURE_INDEX[feature_name]
    ideal_raw, _weight = profile[feature_name]
    return normalize(vector.get(feature_name, spec.min_value), spec) - normalize(ideal_raw, spec)


def cosine_similarity(vector: Mapping[str, float], profile: Profile) -> float:
    """Weighted cosine similarity as an alternative metric (0-100).

    Cosine similarity compares the *direction* of the vectors and ignores
    magnitude, which can be useful when only relative feature dominance matters.
    It is provided for experimental comparison with ``weighted_similarity``.
    """
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for name in FEATURE_NAMES:
        if name not in profile:
            continue
        spec = FEATURE_INDEX[name]
        ideal_raw, weight = profile[name]
        w = math.sqrt(max(weight, 0.0))
        a = normalize(vector.get(name, spec.min_value), spec) * w
        b = normalize(ideal_raw, spec) * w
        dot += a * b
        norm_a += a * a
        norm_b += b * b

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return round(clamp(dot / (math.sqrt(norm_a) * math.sqrt(norm_b))) * 100.0, 2)


def build_profile(rows: Iterable) -> dict[str, tuple[float, float]]:
    """Convert ``PlanetProfile`` ORM rows into a ``{feature: (ideal, weight)}`` map."""
    return {
        row.feature_name: (float(row.ideal_value), float(row.weight))
        for row in rows
        if row.feature_name in FEATURE_INDEX
    }
