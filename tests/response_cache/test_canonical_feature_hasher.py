"""RED coverage for the compatibility-only feature hashing helpers."""

from __future__ import annotations

import pytest


def test_legacy_feature_hashers_live_only_in_compat_and_factory_warns() -> None:
    """No target cache collaborator recalculates a feature hash."""
    import async_model_gateway.response_cache.compat as compat
    from async_model_gateway.response_cache.key import CacheKey

    assert issubclass(compat.CanonicalFeatureHasher, compat.FeatureHasher)
    with pytest.warns(DeprecationWarning):
        factory = compat.ResponseCacheKeyFactory(
            namespace="response-cache", feature_hasher=compat.CanonicalFeatureHasher()
        )

    key = factory.create(model_payload_hash="payload", features={"mode": "fast"})

    assert isinstance(key, CacheKey)
    assert key.namespace == "response-cache"
    assert key.model_payload_hash == "payload"


def test_direct_legacy_feature_hasher_routes_are_removed() -> None:
    """Only the documented compatibility module may expose this old helper family."""
    with pytest.raises(ModuleNotFoundError):
        import async_model_gateway.response_cache._canonical_feature_hasher as legacy_hasher  # noqa: F401
    with pytest.raises(ModuleNotFoundError):
        import async_model_gateway.response_cache.ports.feature_hasher as legacy_port  # noqa: F401
