"""Temporary deprecated compatibility bridge for the retired cache surface."""

from __future__ import annotations

import json
import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import TypeGuard

from .cache import ResponseCache as _ResponseCache
from .key import CacheKey as _CacheKey
from .outcomes import CacheHit as _CacheHit
from .outcomes import Invalidated as _Invalidated
from .outcomes import Remembered as _Remembered
from .outcomes import Skipped as _Skipped
from .ports.invalidator import CacheInvalidator as _CacheInvalidator

__all__ = [
    "CanonicalFeatureHasher",
    "FeatureHasher",
    "LegacyCacheClosedError",
    "LegacyCacheOperationError",
    "LegacyResponseCacheAdapter",
    "ResponseCacheEntry",
    "ResponseCacheKey",
    "ResponseCacheKeyFactory",
]

ResponseCacheKey = _CacheKey


def _is_feature_string(value: object) -> TypeGuard[str]:
    """Return whether runtime feature identity material is a string."""
    return isinstance(value, str)


@dataclass(frozen=True, slots=True)
class ResponseCacheEntry:
    """Legacy response wrapper retained only for transition callers."""

    response: str


class FeatureHasher:
    """Legacy feature-hash collaborator shape."""

    def hash_features(self, features: Mapping[str, str]) -> str:
        """Return a stable hash of migration-only feature material."""
        raise NotImplementedError


class CanonicalFeatureHasher(FeatureHasher):
    """Canonical migration-only implementation of the former feature hasher."""

    def hash_features(self, features: Mapping[str, str]) -> str:
        """Return the predecessor canonical SHA-256 digest for ``features``."""
        pairs: list[tuple[str, str]] = []
        for key, value in features.items():
            if not _is_feature_string(key):
                msg = "feature keys must be strings"
                raise TypeError(msg)
            if not _is_feature_string(value):
                msg = "feature values must be strings"
                raise TypeError(msg)
            pairs.append((str.__str__(key), str.__str__(value)))

        pairs.sort()
        serialized_pairs = json.dumps(
            pairs,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        try:
            encoded_pairs = serialized_pairs.encode("utf-8")
        except UnicodeEncodeError as exc:
            msg = "feature identity material must be strictly UTF-8 encodable"
            raise TypeError(msg) from exc
        return sha256(encoded_pairs).hexdigest()


class ResponseCacheKeyFactory:
    """Deprecated helper that forms a target key for legacy callers."""

    def __init__(self, hasher: FeatureHasher) -> None:
        """Store the temporary factory collaborators and signal its deprecation."""
        warnings.warn(
            "ResponseCacheKeyFactory is deprecated; construct CacheKey directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._hasher = hasher

    def build(
        self,
        *,
        namespace: str,
        model_payload_hash: str,
        features: Mapping[str, str],
    ) -> _CacheKey:
        """Retain the former explicit-namespace construction shape temporarily."""
        return _CacheKey(
            namespace=namespace,
            model_payload_hash=model_payload_hash,
            feature_hash=self._hasher.hash_features(features),
        )


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
