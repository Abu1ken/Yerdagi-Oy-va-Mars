"""Pydantic response/request schemas for the public API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Planet = Literal["moon", "mars"]
LocationType = Literal["desert", "volcano", "cave", "glacier", "crater", "other"]


class FeaturesOut(BaseModel):
    """Full feature vector as returned by the API."""

    avg_temp_c: float
    temp_range_c: float
    annual_rainfall_mm: float
    humidity_pct: float
    terrain_roughness: int
    iron_oxide_level: int
    basalt_level: int
    radiation_level: int
    dust_level: int
    lava_tubes: bool
    ice_presence: bool
    is_estimated: bool

    model_config = {"from_attributes": True}


class ReasonOut(BaseModel):
    """Human readable analogy explanation."""

    category: str
    text: str
    contribution_pct: float = Field(
        ..., ge=0, le=100, description="Share of the total similarity distance"
    )
    feature: str


class ScoreOut(BaseModel):
    """Similarity score for a single planet."""

    planet: Planet
    score: float = Field(..., ge=0, le=100, description="Weighted similarity in percent")


class CuratedReasonOut(BaseModel):
    """A hand-written, source-backed explanation stored in ``analog_reasons``."""

    planet: Planet
    text: str
    category: str


class LocationSummary(BaseModel):
    """Compact location representation used in lists and map markers."""

    id: int
    name: str
    country: str
    lat: float
    lon: float
    type: LocationType
    elevation_m: float | None = None
    description: str
    source_url: str | None = None
    is_estimated: bool = True
    moon_score: float | None = None
    mars_score: float | None = None
    best_planet: Planet | None = None
    best_score: float | None = None


class LocationDetail(LocationSummary):
    """Detailed view including features and generated reasons."""

    features: FeaturesOut
    scores: list[ScoreOut]
    reasons: list[ReasonOut]
    curated_reasons: list[CuratedReasonOut] = Field(default_factory=list)


class LocationListResponse(BaseModel):
    """Paginated list response."""

    total: int
    page: int
    page_size: int
    count: int
    items: list[LocationSummary]


class SearchResponse(BaseModel):
    """Full-text search results."""

    query: str
    count: int
    items: list[LocationSummary]


class NearestResponse(BaseModel):
    """Nearest analog search result."""

    origin: dict[str, float]
    planet: Planet | None = None
    count: int
    items: list["NearestItem"]


class NearestItem(LocationSummary):
    """A nearest result augmented with distance information."""

    distance_km: float
    bearing_deg: float


class TopResponse(BaseModel):
    """Top-K analog ranking for a planet."""

    planet: Planet
    k: int
    count: int
    items: list[LocationSummary]


class RadarDataset(BaseModel):
    """One dataset of the radar chart (normalised 0-100 per axis)."""

    location_id: int
    label: str
    values: list[float]


class CompareResponse(BaseModel):
    """Side by side comparison payload with radar-chart data."""

    axes: list[str]
    axis_labels: list[str]
    datasets: list[RadarDataset]


class PlanetWeight(BaseModel):
    """A single feature weight in a planet profile."""

    feature_name: str
    ideal_value: float
    weight: float


class PlanetProfileOut(BaseModel):
    """Planet profile with all feature weights."""

    planet: Planet
    features: list[PlanetWeight]


class HealthResponse(BaseModel):
    """Service health status."""

    status: str
    app: str
    version: str
    locations: int


NearestResponse.model_rebuild()
