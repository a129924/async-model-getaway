"""Tests for the minimal response-cache package surface."""

from __future__ import annotations

import inspect
from typing import get_type_hints

import async_model_gateway.response_cache as response_cache_module
import async_model_gateway.response_cache.cache as response_cache_cache_module
import async_model_gateway.response_cache.ports as response_cache_ports_module
import async_model_gateway.response_cache.ports.store as response_cache_store_module
from async_model_gateway.response_cache import ResponseCacheKey, ResponseCacheKeyFactory
from async_model_gateway.response_cache._in_memory_store import InMemoryResponseCacheStore
from async_model_gateway.response_cache.freshness_policy import FreshnessPolicy
from async_model_gateway.response_cache.ports import FeatureHasher
from async_model_gateway.response_cache.ttl_freshness_policy import TtlFreshnessPolicy


def test_response_cache_package_reexports_operational_and_key_surfaces() -> None:
    """The package root must expose the bounded operational owner and keyed inputs."""
    assert response_cache_module.__all__ == [
        "ResponseCache",
        "ResponseCacheEntry",
        "ResponseCacheKey",
        "ResponseCacheKeyFactory",
    ]
    assert response_cache_module.ResponseCache.__name__ == "ResponseCache"
    assert response_cache_module.ResponseCacheEntry.__name__ == "ResponseCacheEntry"
    assert response_cache_module.ResponseCacheKey is ResponseCacheKey
    assert response_cache_module.ResponseCacheKeyFactory is ResponseCacheKeyFactory


def test_response_cache_package_does_not_reexport_feature_hasher_port() -> None:
    """The feature-hash collaborator must remain outside the package root."""
    assert not hasattr(response_cache_module, "FeatureHasher")


def test_response_cache_ports_package_exposes_feature_hasher() -> None:
    """The abstract collaborator should stay submodule-public."""
    assert response_cache_ports_module.__all__ == ["FeatureHasher"]
    assert response_cache_ports_module.FeatureHasher is FeatureHasher


def test_response_cache_package_does_not_reexport_store_port() -> None:
    """The store port must not become part of the package-root promise."""
    assert not hasattr(response_cache_module, "ResponseCacheStore")


def test_response_cache_ports_package_does_not_reexport_store_port() -> None:
    """The ports package root should keep store exposure off the gateway module."""
    assert not hasattr(response_cache_ports_module, "ResponseCacheStore")


def test_response_cache_packages_do_not_reexport_internal_freshness_or_store_types() -> None:
    """Freshness policy and concrete storage must remain module-internal details."""
    internal_type_names = {
        FreshnessPolicy.__name__,
        TtlFreshnessPolicy.__name__,
        InMemoryResponseCacheStore.__name__,
    }

    assert internal_type_names.isdisjoint(response_cache_module.__all__)
    assert all(not hasattr(response_cache_module, name) for name in internal_type_names)
    assert internal_type_names.isdisjoint(response_cache_ports_module.__all__)
    assert all(not hasattr(response_cache_ports_module, name) for name in internal_type_names)


def test_response_cache_cache_module_does_not_expose_store_port() -> None:
    """The operational owner module must not expose the store port at runtime."""
    assert not hasattr(response_cache_cache_module, "ResponseCacheStore")


def test_response_cache_store_is_only_public_from_store_submodule() -> None:
    """The store port should stay submodule-public with a locked async contract."""
    response_cache_store = response_cache_store_module.ResponseCacheStore
    get_signature = inspect.signature(response_cache_store.get)
    set_signature = inspect.signature(response_cache_store.set)
    invalidate_signature = inspect.signature(response_cache_store.invalidate)

    assert response_cache_store_module.__all__ == ["ResponseCacheStore"]
    assert inspect.isabstract(response_cache_store)
    assert inspect.iscoroutinefunction(response_cache_store.get)
    assert inspect.iscoroutinefunction(response_cache_store.set)
    assert inspect.iscoroutinefunction(response_cache_store.invalidate)
    assert tuple(get_signature.parameters) == ("self", "key")
    assert get_signature.parameters["key"].kind is inspect.Parameter.KEYWORD_ONLY
    assert tuple(set_signature.parameters) == ("self", "key", "entry")
    assert set_signature.parameters["key"].kind is inspect.Parameter.KEYWORD_ONLY
    assert set_signature.parameters["entry"].kind is inspect.Parameter.KEYWORD_ONLY
    assert tuple(invalidate_signature.parameters) == ("self", "key")
    assert invalidate_signature.parameters["key"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_type_hints(response_cache_store.invalidate) == {
        "key": ResponseCacheKey,
        "return": bool,
    }
    private_name = "_CacheLookupDecision"

    assert private_name not in response_cache_module.__all__
    assert private_name not in response_cache_ports_module.__all__
    assert not hasattr(response_cache_module, private_name)
    assert not hasattr(response_cache_module.ResponseCache, private_name)
    assert not hasattr(response_cache_cache_module, private_name)
    assert not hasattr(response_cache_ports_module, private_name)
    assert not hasattr(response_cache_store_module, private_name)
    assert not hasattr(response_cache_store, private_name)
