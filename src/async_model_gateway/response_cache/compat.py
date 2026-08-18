"""Temporary deprecated compatibility bridge for the retired cache surface."""

from __future__ import annotations

import warnings
from dataclasses import dataclass

from .cache import ResponseCache as _ResponseCache
from .key import CacheKey as _CacheKey
from .outcomes import CacheHit as _CacheHit
from .outcomes import Invalidated as _Invalidated
from .outcomes import Remembered as _Remembered
from .outcomes import Skipped as _Skipped
from .ports.invalidator import CacheInvalidator as _CacheInvalidator

__all__ = [
    "LegacyCacheClosedError",
    "LegacyCacheOperationError",
    "LegacyResponseCacheAdapter",
    "ResponseCacheEntry",
]


@dataclass(frozen=True, slots=True)
class ResponseCacheEntry:
    """Legacy response wrapper retained only for transition callers."""

    response: str


class LegacyCacheClosedError(Exception):
    """Legacy write signal for a closed target cache store."""


class LegacyCacheOperationError(Exception):
    """Legacy write signal for a classified target cache failure."""

    def __init__(self, kind: object) -> None:
        """Retain the target failure kind for transition callers."""
        self.kind = kind
        super().__init__(str(kind))


class LegacyResponseCacheAdapter:
    """Map retired methods onto the target facade and separate invalidator."""

    __slots__ = ("_facade", "_invalidator")

    def __init__(
        self,
        *,
        facade: _ResponseCache,
        invalidator: _CacheInvalidator,
    ) -> None:
        """Bind transition collaborators and signal the deprecated route."""
        warnings.warn(
            "LegacyResponseCacheAdapter is deprecated; use ResponseCache.lookup, "
            "ResponseCache.remember, and CacheInvalidator.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._facade = facade
        self._invalidator = invalidator

    async def get(self, *, key: _CacheKey) -> ResponseCacheEntry | None:
        """Map a target lookup outcome to the former entry-or-none result."""
        result = await self._facade.lookup(key=key, context=object())
        if isinstance(result, _CacheHit):
            return ResponseCacheEntry(response=result.value)
        return None

    async def set(self, *, key: _CacheKey, entry: ResponseCacheEntry) -> None:
        """Map target write outcomes to the retired legacy error convention."""
        result = await self._facade.remember(
            key=key,
            value=entry.response,
            context=object(),
        )
        if isinstance(result, _Remembered):
            return
        if isinstance(result, _Skipped):
            raise LegacyCacheClosedError
        raise LegacyCacheOperationError(result.kind)

    async def invalidate(self, *, key: _CacheKey) -> bool:
        """Map target invalidation outcomes to the former boolean result."""
        result = await self._invalidator.invalidate(key=key)
        if isinstance(result, _Invalidated):
            return True
        return False
