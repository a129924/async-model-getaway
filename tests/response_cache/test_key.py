"""RED coverage for the target cache identity authority."""

from __future__ import annotations

from dataclasses import fields, is_dataclass

import async_model_gateway.response_cache as response_cache
import pytest


def test_cache_key_is_the_only_frozen_slotted_identity_value() -> None:
    """The target key owns exactly the three already-derived identity components."""
    from async_model_gateway.response_cache.key import CacheKey

    key = CacheKey(
        namespace="response-cache",
        model_payload_hash="payload-a",
        feature_hash="feature-a",
    )

    assert is_dataclass(CacheKey)
    assert CacheKey.__dataclass_params__.frozen is True
    assert hasattr(key, "__slots__")
    assert [field.name for field in fields(CacheKey)] == [
        "namespace",
        "model_payload_hash",
        "feature_hash",
    ]
    assert key == CacheKey("response-cache", "payload-a", "feature-a")
    assert hash(key) == hash(CacheKey("response-cache", "payload-a", "feature-a"))


def test_cache_key_does_not_normalize_or_accept_context_as_identity() -> None:
    """Only the three literal constructor values contribute to equality and hashing."""
    from async_model_gateway.response_cache.key import CacheKey

    first = CacheKey(" namespace ", "payload", "feature")
    second = CacheKey(" namespace ", "payload", "feature")
    other = CacheKey(" namespace ", "payload", "other-feature")

    assert first == second
    assert first != other
    with pytest.raises(TypeError):
        CacheKey("namespace", "payload", "feature", object())


def test_normal_key_module_and_package_root_have_no_legacy_key_name() -> None:
    """The former identity name survives only through the compatibility adapter."""
    from async_model_gateway.response_cache import key

    assert not hasattr(response_cache, "ResponseCacheKey")
    assert not hasattr(key, "ResponseCacheKey")
