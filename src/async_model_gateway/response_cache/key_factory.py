"""Factory for minimal response-cache key construction."""

from __future__ import annotations

from collections.abc import Mapping

from .key import ResponseCacheKey
from .ports import FeatureHasher

__all__ = ["ResponseCacheKeyFactory"]


class ResponseCacheKeyFactory:
    """Coordinate explicit hash owners into a concrete response-cache key."""

    def __init__(self, feature_hasher: FeatureHasher) -> None:
        """Store the feature-hash collaborator for later key construction."""
        self._feature_hasher = feature_hasher

    def build(
        self,
        *,
        namespace: str,
        model_payload_hash: str,
        features: Mapping[str, str],
    ) -> ResponseCacheKey:
        """Return a key built from literal namespace and delegated hash owners."""
        feature_hash = self._feature_hasher.hash_features(features)
        return ResponseCacheKey(
            namespace=namespace,
            model_payload_hash=model_payload_hash,
            feature_hash=feature_hash,
        )
