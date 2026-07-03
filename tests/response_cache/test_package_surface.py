"""Tests for the minimal response-cache package surface."""

from __future__ import annotations

import async_model_gateway.response_cache as response_cache_module
import async_model_gateway.response_cache.ports as response_cache_ports_module
from async_model_gateway.response_cache import ResponseCacheKey, ResponseCacheKeyFactory
from async_model_gateway.response_cache.ports import FeatureHasher


def test_response_cache_package_reexports_only_minimal_key_surfaces() -> None:
    """The package root must stay constrained to the keyed public contract."""
    assert response_cache_module.__all__ == [
        "ResponseCacheKey",
        "ResponseCacheKeyFactory",
    ]
    assert response_cache_module.ResponseCacheKey is ResponseCacheKey
    assert response_cache_module.ResponseCacheKeyFactory is ResponseCacheKeyFactory


def test_response_cache_package_does_not_reexport_feature_hasher_port() -> None:
    """The feature-hash collaborator must remain outside the package root."""
    assert not hasattr(response_cache_module, "FeatureHasher")


def test_response_cache_ports_package_exposes_feature_hasher() -> None:
    """The abstract collaborator should stay submodule-public."""
    assert response_cache_ports_module.__all__ == ["FeatureHasher"]
    assert response_cache_ports_module.FeatureHasher is FeatureHasher

