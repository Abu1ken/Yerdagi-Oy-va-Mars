"""SQLite FTS5 full-text search over location name + description.

SQLite's FTS5 module provides an inverted index so that a ``MATCH`` query runs
in roughly **O(log N + matches)** instead of the O(N) full table scan that a
``LIKE '%term%'`` would require.

The virtual table ``locations_fts`` is an *external content* table: it does not
duplicate the data, it only stores the inverted index and reads rows back from
``locations``.  Three triggers keep the index in sync on INSERT/UPDATE/DELETE.

``build_match_query`` converts arbitrary user text into a safe FTS5 expression
where every word becomes a quoted prefix term (``"term"*``).  Quoting neutralises
FTS5 operators (``AND``/``OR``/``NEAR``/``*`` ...) so a hostile or malformed
query can never raise a syntax error or inject SQL - values are always passed as
bound parameters.
"""

from __future__ import annotations

import re

from sqlalchemy import or_, select, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

from app.models import Location

# Word characters only (letters, digits).  The underscore is excluded so that
# FTS5 column names such as ``rowid`` never leak into the query.
_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)

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

_CREATE_TRIGGER_INSERT = f"""
CREATE TRIGGER IF NOT EXISTS locations_fts_ai AFTER INSERT ON locations BEGIN
    INSERT INTO {FTS_TABLE}(rowid, name, description)
    VALUES (new.id, new.name, new.description);
END
"""

_CREATE_TRIGGER_DELETE = f"""
CREATE TRIGGER IF NOT EXISTS locations_fts_ad AFTER DELETE ON locations BEGIN
    INSERT INTO {FTS_TABLE}({FTS_TABLE}, rowid, name, description)
    VALUES ('delete', old.id, old.name, old.description);
END
"""

_CREATE_TRIGGER_UPDATE = f"""
CREATE TRIGGER IF NOT EXISTS locations_fts_au AFTER UPDATE ON locations BEGIN
    INSERT INTO {FTS_TABLE}({FTS_TABLE}, rowid, name, description)
    VALUES ('delete', old.id, old.name, old.description);
    INSERT INTO {FTS_TABLE}(rowid, name, description)
    VALUES (new.id, new.name, new.description);
END
"""


def ensure_fts_schema(connection) -> None:
    """Create the FTS5 virtual table and its synchronisation triggers.

    Idempotent: safe to call on every start-up / migration run.

    Complexity: O(1) DDL statements.
    """
    cursor = connection.cursor() if hasattr(connection, "cursor") else None
    statements = (
        _CREATE_FTS,
        _CREATE_TRIGGER_INSERT,
        _CREATE_TRIGGER_DELETE,
        _CREATE_TRIGGER_UPDATE,
    )
    if cursor is not None:  # raw DBAPI connection (seed script)
        for statement in statements:
            cursor.execute(statement)
        cursor.close()
        return
    for statement in statements:  # SQLAlchemy Connection
        connection.exec_driver_sql(statement)


def build_match_query(raw: str) -> str | None:
    """Turn free user text into a safe FTS5 MATCH expression.

    Returns ``None`` when ``raw`` contains no usable word characters.

    Complexity: O(L) in the length of the input string.
    """
    tokens = _TOKEN_RE.findall(raw or "")
    if not tokens:
        return None
    return " ".join(f'"{token}"*' for token in tokens)


def fts_available(db: Session) -> bool:
    """Return ``True`` when the ``locations_fts`` table exists."""
    row = db.execute(
        text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = :name"),
        {"name": FTS_TABLE},
    ).first()
    return row is not None


def search_locations(db: Session, query: str, limit: int) -> list[Location]:
    """Return locations matching ``query`` ranked by FTS5 relevance.

    Falls back to a parameterised ``LIKE`` scan if FTS5 is unavailable or the
    match expression raises a database error, so the endpoint never 500s.

    Complexity: FTS5 path ~O(log N + m); LIKE fallback O(N).
    """
    match = build_match_query(query)
    if match is None:
        return []

    if fts_available(db):
        sql = text(
            f"""
            SELECT l.id AS id
            FROM {FTS_TABLE}
            JOIN locations AS l ON l.id = {FTS_TABLE}.rowid
            WHERE {FTS_TABLE} MATCH :match
            ORDER BY bm25({FTS_TABLE}), l.id
            LIMIT :limit
            """
        )
        try:
            rows = db.execute(sql, {"match": match, "limit": limit}).all()
        except DatabaseError:
            rows = None
        if rows is not None:
            ids = [row.id for row in rows]
            if not ids:
                return []
            loaded = db.execute(select(Location).where(Location.id.in_(ids))).scalars().all()
            by_id = {loc.id: loc for loc in loaded}
            return [by_id[i] for i in ids if i in by_id]

    # --- fallback: simple case-insensitive substring search ----------------
    needle = f"%{query.strip()}%"
    stmt = (
        select(Location)
        .where(or_(Location.name.ilike(needle), Location.description.ilike(needle)))
        .order_by(Location.name)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())
