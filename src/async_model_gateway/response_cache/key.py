"""Concrete response-cache key surface."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["CacheKey"]


@dataclass(frozen=True, slots=True)
class CacheKey:
    """Immutable cache identity assembled from already-derived values."""

    namespace: str
    model_payload_hash: str
    feature_hash: str
