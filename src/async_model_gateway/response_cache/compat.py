"""Temporary deprecated compatibility bridge for the retired cache surface."""

from __future__ import annotations

import json
import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import TypeGuard

from .cache import ResponseCache
from .key import CacheKey
from .outcomes import CacheHit, Invalidated, Remembered, Skipped
from .ports.invalidator import CacheInvalidator

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

ResponseCacheKey = CacheKey


@dataclass(frozen=True, slots=True)
class ResponseCacheEntry:
    """Legacy response wrapper retained only for transition callers."""

    response: str


class FeatureHasher:
    """Legacy feature-hash collaborator shape."""

    def hash_features(self, features: Mapping[str, object]) -> str:
        """Return a stable hash of migration-only feature material."""
        raise NotImplementedError


class CanonicalFeatureHasher(FeatureHasher):
    """Canonical migration-only implementation of the former feature hasher."""

    def hash_features(self, features: Mapping[str, object]) -> str:
        """Return a stable SHA-256 feature digest."""
        normalized = _normalize_features(features)
        serialized = json.dumps(
            normalized,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return sha256(serialized.encode("utf-8")).hexdigest()


class ResponseCacheKeyFactory:
    """Deprecated helper that forms a target key for legacy callers."""

    def __init__(self, *, namespace: str, feature_hasher: FeatureHasher) -> None:
        """Store the temporary factory collaborators and signal its deprecation."""
        warnings.warn(
            "ResponseCacheKeyFactory is deprecated; construct CacheKey directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._namespace = namespace
        self._feature_hasher = feature_hasher

    def create(self, *, model_payload_hash: str, features: Mapping[str, object]) -> CacheKey:
        """Return a target key using the factory's legacy namespace."""
        return self.build(
            namespace=self._namespace,
            model_payload_hash=model_payload_hash,
            features=features,
        )

    def build(
        self,
        *,
        namespace: str,
        model_payload_hash: str,
        features: Mapping[str, object],
    ) -> CacheKey:
        """Retain the former explicit-namespace construction shape temporarily."""
        return CacheKey(
            namespace=namespace,
            model_payload_hash=model_payload_hash,
            feature_hash=self._feature_hasher.hash_features(features),
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

    def __init__(self, *, facade: ResponseCache, invalidator: CacheInvalidator) -> None:
        """Bind transition collaborators and signal the deprecated route."""
        warnings.warn(
            "LegacyResponseCacheAdapter is deprecated; use ResponseCache.lookup, "
            "ResponseCache.remember, and CacheInvalidator.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._facade = facade
        self._invalidator = invalidator

    async def get(self, *, key: CacheKey) -> ResponseCacheEntry | None:
        """Map a target lookup outcome to the former entry-or-none result."""
        result = await self._facade.lookup(key=key, context=object())
        if isinstance(result, CacheHit):
            return ResponseCacheEntry(response=result.value)
        return None

    async def set(self, *, key: CacheKey, entry: ResponseCacheEntry) -> None:
        """Map target write outcomes to the retired legacy error convention."""
        result = await self._facade.remember(
            key=key,
            value=entry.response,
            context=object(),
        )
        if isinstance(result, Remembered):
            return
        if isinstance(result, Skipped):
            raise LegacyCacheClosedError
        raise LegacyCacheOperationError(result.kind)

    async def invalidate(self, *, key: CacheKey) -> bool:
        """Map target invalidation outcomes to the former boolean result."""
        result = await self._invalidator.invalidate(key=key)
        if isinstance(result, Invalidated):
            return True
        return False


def _normalize_features(
    features: Mapping[str, object] | Mapping[object, object],
) -> dict[str, object]:
    """Copy feature mappings into deterministic JSON-compatible material."""
    normalized: dict[str, object] = {}
    for key, value in features.items():
        normalized[_require_key(key)] = _normalize_feature_value(value)
    return normalized


def _require_key(value: object) -> str:
    """Require string feature mapping keys before canonical serialization."""
    if not isinstance(value, str):
        msg = "feature keys must be strings"
        raise TypeError(msg)
    return value


def _normalize_feature_value(value: object) -> object:
    """Normalize the untrusted values at the deprecated feature boundary."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if _is_feature_mapping(value):
        return _normalize_features(value)
    if _is_feature_sequence(value):
        return [_normalize_feature_value(item) for item in value]
    msg = "feature values must be JSON-compatible"
    raise TypeError(msg)


def _is_feature_mapping(value: object) -> TypeGuard[Mapping[object, object]]:
    """Narrow an untrusted nested feature object to a mapping for key validation."""
    return isinstance(value, Mapping)


def _is_feature_sequence(value: object) -> TypeGuard[list[object] | tuple[object, ...]]:
    """Narrow an untrusted nested feature object to a supported sequence."""
    return isinstance(value, (list, tuple))
