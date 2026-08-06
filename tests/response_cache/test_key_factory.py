"""RED coverage for the deprecated key-factory bridge."""

from __future__ import annotations

import pytest


def test_compat_factory_is_deprecated_and_returns_the_target_cache_key() -> None:
    """The factory remains migration-only and never becomes a normal target import."""
    import async_model_gateway.response_cache.compat as compat
    from async_model_gateway.response_cache.key import CacheKey

    with pytest.warns(DeprecationWarning, match="CacheKey"):
        factory = compat.ResponseCacheKeyFactory(
            namespace="response-cache", feature_hasher=compat.CanonicalFeatureHasher()
        )

    key = factory.create(model_payload_hash="payload", features={"a": ["b"]})

    assert type(key) is CacheKey
    assert key.feature_hash


def test_direct_legacy_factory_module_and_normal_key_factory_name_are_absent() -> None:
    """Old direct imports cannot accidentally establish a second normal route."""
    from async_model_gateway.response_cache import key

    assert not hasattr(key, "ResponseCacheKeyFactory")
    with pytest.raises(ModuleNotFoundError):
        import async_model_gateway.response_cache.key_factory as legacy_factory

        assert legacy_factory is None
