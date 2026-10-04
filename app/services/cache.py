"""A tiny thread-safe in-memory cache for expensive derivations.

Similarity scores depend only on the (immutable until reseed) location features
and the planet profile, so caching them keyed by ``(planet, location_id)``
avoids recomputing the same value on every request.

The cache is invalidated explicitly (see :func:`invalidate_all`) whenever the
seed data or planet profiles change.
"""

from __future__ import annotations

import threading
from typing import Any, Callable, Hashable


class ScoreCache:
    """Minimal dict-backed cache guarded by a lock."""

    def __init__(self) -> None:
        self._store: dict[Hashable, Any] = {}
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def get_or_compute(self, key: Hashable, factory: Callable[[], Any]) -> Any:
        """Return the cached value for ``key`` or compute and store it once."""
        with self._lock:
            if key in self._store:
                self.hits += 1
                return self._store[key]

        value = factory()

        with self._lock:
            self._store[key] = value
            self.misses += 1
        return value

    def clear(self) -> None:
        """Drop every cached entry."""
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:  # pragma: no cover - diagnostic helper
        with self._lock:
            return len(self._store)


# Process-wide cache shared by all requests.
score_cache = ScoreCache()


def invalidate_all() -> None:
    """Clear the shared cache (call after seed / profile changes)."""
    score_cache.clear()
