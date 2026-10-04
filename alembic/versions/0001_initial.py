"""Initial schema: locations, features, planet_profiles, analog_reasons + FTS5.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-04
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FTS_TABLE = "locations_fts"

_CREATE_FTS = f"""
CREATE VIRTUAL TABLE IF NOT EXISTS {FTS_TABLE} USING fts5(
    name,
    description,
    content='locations',
    content_rowid='id',
    tokenize='unicode61'
)
"""

_TRIGGERS = (
    f"""
    CREATE TRIGGER IF NOT EXISTS locations_fts_ai AFTER INSERT ON locations BEGIN
        INSERT INTO {FTS_TABLE}(rowid, name, description)
        VALUES (new.id, new.name, new.description);
    END
    """,
    f"""
    CREATE TRIGGER IF NOT EXISTS locations_fts_ad AFTER DELETE ON locations BEGIN
        INSERT INTO {FTS_TABLE}({FTS_TABLE}, rowid, name, description)
        VALUES ('delete', old.id, old.name, old.description);
    END
    """,
    f"""
    CREATE TRIGGER IF NOT EXISTS locations_fts_au AFTER UPDATE ON locations BEGIN
        INSERT INTO {FTS_TABLE}({FTS_TABLE}, rowid, name, description)
        VALUES ('delete', old.id, old.name, old.description);
        INSERT INTO {FTS_TABLE}(rowid, name, description)
        VALUES (new.id, new.name, new.description);
    END
    """,
)


def upgrade() -> None:
    """Create the relational schema and the FTS5 search index."""
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("country", sa.String(length=120), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("elevation_m", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("lat >= -90 AND lat <= 90", name="ck_location_lat"),
        sa.CheckConstraint("lon >= -180 AND lon <= 180", name="ck_location_lon"),
        sa.CheckConstraint(
            "type IN ('desert','volcano','cave','glacier','crater','other')",
            name="ck_location_type",
        ),
    )
    op.create_index("ix_locations_lat_lon", "locations", ["lat", "lon"])
    op.create_index("ix_locations_type", "locations", ["type"])
    op.create_index("ix_locations_country", "locations", ["country"])

    op.create_table(
        "features",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("location_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("avg_temp_c", sa.Float(), nullable=False),
        sa.Column("temp_range_c", sa.Float(), nullable=False),
        sa.Column("annual_rainfall_mm", sa.Float(), nullable=False),
        sa.Column("humidity_pct", sa.Float(), nullable=False),
        sa.Column("terrain_roughness", sa.Integer(), nullable=False),
        sa.Column("iron_oxide_level", sa.Integer(), nullable=False),
        sa.Column("basalt_level", sa.Integer(), nullable=False),
        sa.Column("radiation_level", sa.Integer(), nullable=False),
        sa.Column("dust_level", sa.Integer(), nullable=False),
        sa.Column("lava_tubes", sa.Boolean(), nullable=False),
        sa.Column("ice_presence", sa.Boolean(), nullable=False),
        sa.Column("is_estimated", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["location_id"], ["locations.id"], name="fk_features_location", ondelete="CASCADE"
        ),
        sa.CheckConstraint("terrain_roughness BETWEEN 1 AND 10", name="ck_feat_roughness"),
        sa.CheckConstraint("iron_oxide_level BETWEEN 1 AND 10", name="ck_feat_iron"),
        sa.CheckConstraint("basalt_level BETWEEN 1 AND 10", name="ck_feat_basalt"),
        sa.CheckConstraint("radiation_level BETWEEN 1 AND 10", name="ck_feat_radiation"),
        sa.CheckConstraint("dust_level BETWEEN 1 AND 10", name="ck_feat_dust"),
        sa.CheckConstraint("humidity_pct BETWEEN 0 AND 100", name="ck_feat_humidity"),
    )

    op.create_table(
        "planet_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("planet", sa.String(length=10), nullable=False),
        sa.Column("feature_name", sa.String(length=40), nullable=False),
        sa.Column("ideal_value", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.UniqueConstraint("planet", "feature_name", name="uq_planet_feature"),
        sa.CheckConstraint("planet IN ('moon','mars')", name="ck_profile_planet"),
        sa.CheckConstraint("weight > 0", name="ck_profile_weight"),
    )
    op.create_index("ix_planet_profiles_planet", "planet_profiles", ["planet"])

    op.create_table(
        "analog_reasons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("location_id", sa.Integer(), nullable=False),
        sa.Column("planet", sa.String(length=10), nullable=False),
        sa.Column("reason_text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False, server_default="general"),
        sa.ForeignKeyConstraint(
            ["location_id"], ["locations.id"], name="fk_reasons_location", ondelete="CASCADE"
        ),
        sa.CheckConstraint("planet IN ('moon','mars')", name="ck_reason_planet"),
    )
    op.create_index(
        "ix_analog_reasons_location_planet", "analog_reasons", ["location_id", "planet"]
    )

    # --- FTS5 full-text index + synchronisation triggers -------------------
    op.execute(_CREATE_FTS)
    for trigger in _TRIGGERS:
        op.execute(trigger)


def downgrade() -> None:
    """Drop the FTS index and all tables."""
    op.execute(f"DROP TRIGGER IF EXISTS locations_fts_au")
    op.execute(f"DROP TRIGGER IF EXISTS locations_fts_ad")
    op.execute(f"DROP TRIGGER IF EXISTS locations_fts_ai")
    op.execute(f"DROP TABLE IF EXISTS {FTS_TABLE}")

    op.drop_index("ix_analog_reasons_location_planet", table_name="analog_reasons")
    op.drop_table("analog_reasons")
    op.drop_index("ix_planet_profiles_planet", table_name="planet_profiles")
    op.drop_table("planet_profiles")
    op.drop_table("features")
    op.drop_index("ix_locations_country", table_name="locations")
    op.drop_index("ix_locations_type", table_name="locations")
    op.drop_index("ix_locations_lat_lon", table_name="locations")
    op.drop_table("locations")
