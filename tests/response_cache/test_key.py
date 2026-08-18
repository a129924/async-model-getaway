"""RED coverage for the target cache identity authority."""

from __future__ import annotations

from dataclasses import fields, is_dataclass

import async_model_gateway.response_cache as response_cache
import pytest


def test_cache_key_is_the_only_frozen_slotted_four_field_identity_value() -> None:
    """The target key owns exactly four already-derived identity components."""
    from async_model_gateway.response_cache.key import CacheKey

    key = CacheKey(
        namespace="response-cache",
        model_identity_hash="model-a",
        feature_hash="feature-a",
        prediction_input_hash="input-a",
    )

    assert is_dataclass(CacheKey)
    assert CacheKey.__dataclass_params__.frozen is True
    assert hasattr(key, "__slots__")
    assert [field.name for field in fields(CacheKey)] == [
        "namespace",
        "model_identity_hash",
        "feature_hash",
        "prediction_input_hash",
    ]
    assert key == CacheKey("response-cache", "model-a", "feature-a", "input-a")
    assert hash(key) == hash(CacheKey("response-cache", "model-a", "feature-a", "input-a"))


def test_cache_key_does_not_normalize_and_each_literal_field_changes_identity() -> None:
    """Only the four literal constructor values contribute to equality and hashing."""
    from async_model_gateway.response_cache.key import CacheKey

    first = CacheKey(" namespace ", "model", "feature", "input")
    second = CacheKey(" namespace ", "model", "feature", "input")
    alternatives = (
        CacheKey("other-namespace", "model", "feature", "input"),
        CacheKey(" namespace ", "other-model", "feature", "input"),
        CacheKey(" namespace ", "model", "other-feature", "input"),
        CacheKey(" namespace ", "model", "feature", "other-input"),
    )

    assert first == second
    assert all(first != other for other in alternatives)
    assert all(hash(first) != hash(other) for other in alternatives)
    with pytest.raises(TypeError):
        CacheKey("namespace", "model", "feature")
    with pytest.raises(TypeError):
        CacheKey("namespace", "model", "feature", "input", object())


def test_cache_key_has_no_payload_identity_field() -> None:
    """The breaking replacement removes the former payload-hash attribute."""
    from async_model_gateway.response_cache.key import CacheKey

    key = CacheKey("namespace", "model", "feature", "input")

    assert not hasattr(key, "model_payload_hash")


def test_normal_key_module_and_package_root_have_no_legacy_key_name() -> None:
    """The former identity name survives only through the compatibility adapter."""
    from async_model_gateway.response_cache import key

    assert not hasattr(response_cache, "ResponseCacheKey")
    assert not hasattr(key, "ResponseCacheKey")
