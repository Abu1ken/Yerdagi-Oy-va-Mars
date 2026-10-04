"""ORM models for the analog location database.

Tables
------
* ``locations``       - one row per real Earth location.
* ``features``        - 1:1 environmental feature vector for a location.
* ``planet_profiles`` - ideal values + weights per feature for Moon and Mars.
* ``analog_reasons``  - curated human readable explanations per location/planet.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

LOCATION_TYPES = ("desert", "volcano", "cave", "glacier", "crater", "other")
PLANETS = ("moon", "mars")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Location(Base):
    """A real location on Earth that can act as a Moon/Mars analog."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    elevation_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # 1:1 feature vector, deleted together with the location.
    features: Mapped["Feature"] = relationship(
        back_populates="location",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
    reasons: Mapped[list["AnalogReason"]] = relationship(
        back_populates="location",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("lat >= -90 AND lat <= 90", name="ck_location_lat"),
        CheckConstraint("lon >= -180 AND lon <= 180", name="ck_location_lon"),
        CheckConstraint(
            "type IN ('desert','volcano','cave','glacier','crater','other')",
            name="ck_location_type",
        ),
        # Composite index speeds up the common "filter by type + planet score"
        # style range scans and the nearest-neighbour bounding-box prefilter.
        Index("ix_locations_lat_lon", "lat", "lon"),
        Index("ix_locations_type", "type"),
        Index("ix_locations_country", "country"),
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Location {self.id} {self.name!r} ({self.type})>"


class Feature(Base):
    """Environmental feature vector of a location (normalised 1-10 scales)."""

    __tablename__ = "features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    avg_temp_c: Mapped[float] = mapped_column(Float, nullable=False)
    temp_range_c: Mapped[float] = mapped_column(Float, nullable=False)
    annual_rainfall_mm: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[float] = mapped_column(Float, nullable=False)
    terrain_roughness: Mapped[int] = mapped_column(Integer, nullable=False)
    iron_oxide_level: Mapped[int] = mapped_column(Integer, nullable=False)
    basalt_level: Mapped[int] = mapped_column(Integer, nullable=False)
    radiation_level: Mapped[int] = mapped_column(Integer, nullable=False)
    dust_level: Mapped[int] = mapped_column(Integer, nullable=False)
    lava_tubes: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    ice_presence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # True when the values are approximate / interpolated rather than measured.
    is_estimated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    location: Mapped["Location"] = relationship(back_populates="features")

    __table_args__ = (
        CheckConstraint("terrain_roughness BETWEEN 1 AND 10", name="ck_feat_roughness"),
        CheckConstraint("iron_oxide_level BETWEEN 1 AND 10", name="ck_feat_iron"),
        CheckConstraint("basalt_level BETWEEN 1 AND 10", name="ck_feat_basalt"),
        CheckConstraint("radiation_level BETWEEN 1 AND 10", name="ck_feat_radiation"),
        CheckConstraint("dust_level BETWEEN 1 AND 10", name="ck_feat_dust"),
        CheckConstraint("humidity_pct BETWEEN 0 AND 100", name="ck_feat_humidity"),
    )

    def as_vector(self) -> dict[str, float]:
        """Return the numeric feature vector used by the similarity algorithm."""
        return {
            "avg_temp_c": float(self.avg_temp_c),
            "temp_range_c": float(self.temp_range_c),
            "annual_rainfall_mm": float(self.annual_rainfall_mm),
            "humidity_pct": float(self.humidity_pct),
            "terrain_roughness": float(self.terrain_roughness),
            "iron_oxide_level": float(self.iron_oxide_level),
            "basalt_level": float(self.basalt_level),
            "radiation_level": float(self.radiation_level),
            "dust_level": float(self.dust_level),
            "lava_tubes": 1.0 if self.lava_tubes else 0.0,
            "ice_presence": 1.0 if self.ice_presence else 0.0,
        }


class PlanetProfile(Base):
    """Ideal feature value and weight describing a target planetary surface."""

    __tablename__ = "planet_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    planet: Mapped[str] = mapped_column(String(10), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(40), nullable=False)
    ideal_value: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)

    __table_args__ = (
        UniqueConstraint("planet", "feature_name", name="uq_planet_feature"),
        CheckConstraint("planet IN ('moon','mars')", name="ck_profile_planet"),
        CheckConstraint("weight > 0", name="ck_profile_weight"),
        Index("ix_planet_profiles_planet", "planet"),
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<PlanetProfile {self.planet}.{self.feature_name}={self.ideal_value}>"


class AnalogReason(Base):
    """A curated, human readable explanation of a location/planet analogy."""

    __tablename__ = "analog_reasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"), nullable=False
    )
    planet: Mapped[str] = mapped_column(String(10), nullable=False)
    reason_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False, default="general")

    location: Mapped["Location"] = relationship(back_populates="reasons")

    __table_args__ = (
        CheckConstraint("planet IN ('moon','mars')", name="ck_reason_planet"),
        Index("ix_analog_reasons_location_planet", "location_id", "planet"),
    )
