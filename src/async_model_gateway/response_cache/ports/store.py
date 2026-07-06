"""Async store port for the operational response-cache owner."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..entry import ResponseCacheEntry
from ..key import ResponseCacheKey

__all__ = ["ResponseCacheStore"]


class ResponseCacheStore(ABC):
    """Abstract store collaborator for cache hit/miss lookup and persistence."""

    @abstractmethod
    async def get(self, *, key: ResponseCacheKey) -> ResponseCacheEntry | None:
        """Return the cached entry for the supplied key, if present."""

    @abstractmethod
    async def set(self, *, key: ResponseCacheKey, entry: ResponseCacheEntry) -> None:
        """Persist the supplied entry for the provided key."""
