"""Concrete response-cache key surface."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ResponseCacheKey"]


@dataclass(frozen=True, slots=True)
class ResponseCacheKey:
    """Immutable keyed identity material for future response-cache consumers."""

    namespace: str
    model_payload_hash: str
    feature_hash: str
