"""RED coverage for the exact target and compatibility import surfaces."""

from __future__ import annotations

import inspect

import async_model_gateway.response_cache as response_cache
import async_model_gateway.response_cache.ports as ports


def test_package_root_exports_only_target_facade_identity_and_outcomes() -> None:
    """No port, store, adapter, or legacy value is a normal root import."""
    assert response_cache.__all__ == [
        "ResponseCache",
        "CacheKey",
        "CacheHit",
        "CacheMiss",
        "Remembered",
        "Skipped",
        "Failed",
    ]
    assert all(hasattr(response_cache, name) for name in response_cache.__all__)
    assert all(
        not hasattr(response_cache, name)
        for name in (
            "ResponseCacheEntry",
            "ResponseCacheKey",
            "ResponseCacheKeyFactory",
            "CacheStore",
            "CacheCodec",
            "VersionTokenFactory",
            "CacheInvalidator",
            "LegacyResponseCacheAdapter",
        )
    )


def test_ports_root_does_not_reexport_the_internal_cache_store() -> None:
    """CacheStore remains public only through its dedicated port submodule."""
    assert ports.__all__ == [
        "CacheCodec",
        "CacheInvalidator",
        "VersionTokenFactory",
    ]
    assert all(hasattr(ports, name) for name in ports.__all__)
    assert all(
        not hasattr(ports, name)
        for name in (
            "CacheStore",
            "FeatureHasher",
            "ResponseCacheStore",
            "ResponseCacheKey",
        )
    )


def test_target_ports_are_async_or_sync_at_the_frozen_boundary() -> None:
    """Store and invalidator I/O stay async while codec/token work stays synchronous."""
    from async_model_gateway.response_cache.ports.codec import CacheCodec
    from async_model_gateway.response_cache.ports.invalidator import CacheInvalidator
    from async_model_gateway.response_cache.ports.store import CacheStore
    from async_model_gateway.response_cache.ports.version_token_factory import VersionTokenFactory

    assert tuple(inspect.signature(CacheStore.get).parameters) == ("self", "key")
    assert tuple(inspect.signature(CacheStore.set).parameters) == ("self", "key", "record")
    assert tuple(inspect.signature(CacheStore.delete).parameters) == ("self", "key")
    assert tuple(inspect.signature(CacheStore.delete_if_version).parameters) == (
        "self",
        "key",
        "version_token",
    )
    assert inspect.iscoroutinefunction(CacheStore.get)
    assert inspect.iscoroutinefunction(CacheStore.set)
    assert inspect.iscoroutinefunction(CacheStore.delete)
    assert inspect.iscoroutinefunction(CacheStore.delete_if_version)
    assert inspect.iscoroutinefunction(CacheInvalidator.invalidate)
    assert not inspect.iscoroutinefunction(CacheCodec.encode)
    assert not inspect.iscoroutinefunction(CacheCodec.decode)
    assert not inspect.iscoroutinefunction(VersionTokenFactory.new)


def test_compatibility_submodule_has_the_exact_temporary_direct_import_surface() -> None:
    """The one sanctioned legacy route is narrow and never root-reexported."""
    import async_model_gateway.response_cache.compat as compat

    assert compat.__all__ == [
        "CanonicalFeatureHasher",
        "FeatureHasher",
        "LegacyCacheClosedError",
        "LegacyCacheOperationError",
        "LegacyResponseCacheAdapter",
        "ResponseCacheEntry",
        "ResponseCacheKey",
        "ResponseCacheKeyFactory",
    ]
    assert all(hasattr(compat, name) for name in compat.__all__)
    assert all(
        not hasattr(compat, name)
        for name in (
            "CacheHit",
            "CacheInvalidator",
            "CacheKey",
            "Invalidated",
            "Remembered",
            "ResponseCache",
            "Skipped",
        )
    )
