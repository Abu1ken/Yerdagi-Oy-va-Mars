"""Seed the SQLite database with planet profiles and real analog locations.

Run from the project root::

    python -m scripts.seed

The script recreates the schema, builds the FTS5 index and inserts every
location, its feature vector, the planet profiles and the curated analog reasons
**in a single transaction** (one ``COMMIT``), which is dramatically faster and
safer than committing row by row.
"""

from __future__ import annotations

from app.database import Base, SessionLocal, engine
from app.models import AnalogReason, Feature, Location, PlanetProfile
from app.services.cache import invalidate_all
from app.services.fulltext import ensure_fts_schema
from scripts.locations_part1 import LOCATIONS_1
from scripts.locations_part2 import LOCATIONS_2
from scripts.profiles import PLANET_PROFILES

# Feature names that must fall within the 1-10 scale enforced by CHECK constraints.
_SCALED_1_10 = (
    "terrain_roughness",
    "iron_oxide_level",
    "basalt_level",
    "radiation_level",
    "dust_level",
)


def reset_schema() -> None:
    """Drop and recreate all tables plus the FTS5 index."""
    # The FTS virtual table has no ORM model, so drop it (and its triggers) first.
    with engine.begin() as connection:
        connection.exec_driver_sql("DROP TABLE IF EXISTS locations_fts")
        connection.exec_driver_sql("DROP TRIGGER IF EXISTS locations_fts_ai")
        connection.exec_driver_sql("DROP TRIGGER IF EXISTS locations_fts_ad")
        connection.exec_driver_sql("DROP TRIGGER IF EXISTS locations_fts_au")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        ensure_fts_schema(connection)


def validate(locations: list[dict]) -> None:
    """Fail fast on obviously invalid seed values before touching the database."""
    for item in locations:
        features = item["features"]
        for name in _SCALED_1_10:
            value = features[name]
            if not 1 <= value <= 10:
                raise ValueError(f"{item['name']}: {name}={value} 1-10 oralig'ida emas")
        humidity = features["humidity_pct"]
        if not 0 <= humidity <= 100:
            raise ValueError(f"{item['name']}: humidity_pct={humidity} 0-100 emas")


def seed() -> dict[str, int]:
    """Create the schema and insert all seed data. Returns row counts."""
    reset_schema()

    locations_data = LOCATIONS_1 + LOCATIONS_2
    validate(locations_data)

    with SessionLocal() as session:
        # --- planet profiles ------------------------------------------------
        profiles = [
            PlanetProfile(planet=planet, feature_name=name, ideal_value=value, weight=weight)
            for planet, rows in PLANET_PROFILES.items()
            for name, value, weight in rows
        ]
        session.add_all(profiles)

        # --- locations with their 1:1 features and 1:N reasons --------------
        for item in locations_data:
            location = Location(
                name=item["name"],
                country=item["country"],
                lat=item["lat"],
                lon=item["lon"],
                type=item["type"],
                elevation_m=item["elevation_m"],
                description=item["description"],
                source_url=item["source_url"],
            )
            location.features = Feature(
                is_estimated=item["estimated"], **item["features"]
            )
            for reason in item["reasons"]:
                location.reasons.append(
                    AnalogReason(
                        planet=reason["planet"],
                        reason_text=reason["text"],
                        category=reason["category"],
                    )
                )
            session.add(location)

        # Single transaction: one flush/commit for the whole batch.
        session.commit()

        counts = {
            "locations": session.query(Location).count(),
            "features": session.query(Feature).count(),
            "profiles": session.query(PlanetProfile).count(),
            "reasons": session.query(AnalogReason).count(),
        }

    # Cached profiles/scores are now stale.
    invalidate_all()
    return counts


def main() -> None:
    """Entry point for ``python -m scripts.seed``."""
    counts = seed()
    print("Seed tugadi:")
    for name, value in counts.items():
        print(f"  {name:>10}: {value}")


if __name__ == "__main__":
    main()
