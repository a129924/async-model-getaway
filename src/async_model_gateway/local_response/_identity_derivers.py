"""Private local-response cache identity derivation."""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import json
from typing import TypeVar

from async_model_gateway.model_registry.model_payload import ModelPayloadHasher
from async_model_gateway.response_cache import CacheKey

from .request import ModelPayloadValue

_NAMESPACE_TOKENS = (
    "local-response",
    "local-response-v1",
    "cache-string-v1",
)

_FeatureKey = TypeVar("_FeatureKey")
_FeatureValue = TypeVar("_FeatureValue")


class FeatureIdentityHasher:
    """Derive a canonical identity from strictly string local features."""

    def hash_features(
        self,
        features: Mapping[_FeatureKey, _FeatureValue],
    ) -> str:
        """Return a hash or reject non-string feature identity material."""
        pairs: list[tuple[str, str]] = []
        for key, value in features.items():
            if not isinstance(key, str):
                msg = "feature keys must be strings"
                raise TypeError(msg)
            if not isinstance(value, str):
                msg = "feature values must be strings"
                raise TypeError(msg)
            pairs.append((key, value))

        pairs.sort()
        return _hash_canonical_json(pairs, field_name="feature identity material")


def _derive_feature_hash(  # pyright: ignore[reportUnusedFunction]
    features: Mapping[_FeatureKey, _FeatureValue],
) -> str:
    """Return the canonical identity for strict local feature material."""
    return FeatureIdentityHasher().hash_features(features)


def _derive_prediction_input_hash(  # pyright: ignore[reportUnusedFunction]
    invocation: dict[str, ModelPayloadValue],
) -> str:
    """Delegate canonical JSON-like input identity to the existing hash owner."""
    return ModelPayloadHasher().hash_model_payload(invocation)


def _derive_namespace() -> str:  # pyright: ignore[reportUnusedFunction]
    """Return the fixed three-token namespace identity for this projection."""
    return _hash_canonical_json(list(_NAMESPACE_TOKENS), field_name="namespace tokens")


def _assemble_cache_key(  # pyright: ignore[reportUnusedFunction]
    *,
    namespace: str,
    model_identity_hash: str,
    feature_hash: str,
    prediction_input_hash: str,
) -> CacheKey:
    """Assemble a cache key from four identities without derivation policy."""
    return CacheKey(
        namespace=namespace,
        model_identity_hash=model_identity_hash,
        feature_hash=feature_hash,
        prediction_input_hash=prediction_input_hash,
    )


def _hash_canonical_json(value: object, *, field_name: str) -> str:
    """Hash canonical JSON and reject material that cannot be encoded as UTF-8."""
    serialized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    try:
        encoded = serialized.encode("utf-8")
    except UnicodeEncodeError as exc:
        msg = f"{field_name} must be strictly UTF-8 encodable"
        raise TypeError(msg) from exc
    return sha256(encoded).hexdigest()
