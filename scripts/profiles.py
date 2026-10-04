"""Ideal feature profiles for the Moon and Mars.

Each entry is ``(feature_name, ideal_value, weight)``:

* ``ideal_value`` is the physically representative value of that feature on the
  target body (e.g. Mars mean surface temperature ~ -63 °C).
* ``weight`` encodes how *diagnostic* the feature is for recognising a surface
  analog.  Higher weight == more influence on the similarity score.  Weights are
  data (stored in ``planet_profiles``), never hard-coded in the algorithm, so
  they can be retuned without touching Python code.

Values are drawn from published NASA / ESA planetary science summaries and are
intentionally rounded.
"""

from __future__ import annotations

# --- Mars ------------------------------------------------------------------ #
MARS_PROFILE: list[tuple[str, float, float]] = [
    ("avg_temp_c", -63.0, 1.0),          # mean surface temperature
    ("temp_range_c", 90.0, 0.8),         # strong diurnal swing
    ("annual_rainfall_mm", 0.0, 1.2),    # no rain
    ("humidity_pct", 1.0, 1.2),          # extremely dry atmosphere
    ("terrain_roughness", 8.0, 0.8),     # canyons, craters, dunes
    ("iron_oxide_level", 9.0, 1.5),      # rusty red dust is diagnostic
    ("basalt_level", 8.0, 1.0),          # basaltic crust
    ("radiation_level", 9.0, 0.8),       # thin atmosphere
    ("dust_level", 9.0, 1.2),            # global dust storms
    ("lava_tubes", 1.0, 0.6),            # lava tubes are candidate shelters
    ("ice_presence", 1.0, 0.5),          # polar caps / subsurface ice
]

# --- Moon ------------------------------------------------------------------ #
MOON_PROFILE: list[tuple[str, float, float]] = [
    ("avg_temp_c", -20.0, 0.8),          # mean surface temperature
    ("temp_range_c", 280.0, 1.2),        # ~ -173 °C .. +127 °C
    ("annual_rainfall_mm", 0.0, 1.0),    # no atmosphere, no rain
    ("humidity_pct", 0.0, 1.0),          # vacuum
    ("terrain_roughness", 9.0, 1.2),     # regolith, craters, ejecta
    ("iron_oxide_level", 7.0, 0.8),      # iron-rich regolith
    ("basalt_level", 8.0, 1.2),          # mare basalts
    ("radiation_level", 10.0, 1.5),      # no atmosphere / magnetosphere
    ("dust_level", 9.0, 1.0),            # abrasive regolith dust
    ("lava_tubes", 1.0, 0.8),            # e.g. Marius Hills pits
    ("ice_presence", 1.0, 0.5),          # cold traps at the poles
]

PLANET_PROFILES: dict[str, list[tuple[str, float, float]]] = {
    "mars": MARS_PROFILE,
    "moon": MOON_PROFILE,
}
