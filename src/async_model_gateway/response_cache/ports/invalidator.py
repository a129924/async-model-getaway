"""Async key-local cache invalidation port."""

from __future__ import annotations

from typing import Protocol

from ..key import CacheKey
from ..outcomes import Invalidated, NotFound

__all__ = ["CacheInvalidator"]


class CacheInvalidator(Protocol):
    """Invalidate a supplied key without participating in the facade."""

    async def invalidate(self, *, key: CacheKey) -> Invalidated | NotFound:
        """Invalidate ``key`` when present."""
        ...
