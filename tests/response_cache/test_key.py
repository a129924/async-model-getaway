"""Tests for the response-cache key value surface."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import get_type_hints

from async_model_gateway.response_cache import ResponseCacheKey


def test_response_cache_key_is_a_frozen_dataclass_with_three_string_fields() -> None:
    """The key surface should stay minimal and immutable."""
    assert is_dataclass(ResponseCacheKey)
    assert ResponseCacheKey.__dataclass_params__.frozen is True
    assert [field.name for field in fields(ResponseCacheKey)] == [
        "namespace",
        "model_payload_hash",
        "feature_hash",
    ]
    assert get_type_hints(ResponseCacheKey) == {
        "namespace": str,
        "model_payload_hash": str,
        "feature_hash": str,
    }


def test_response_cache_key_preserves_literal_identity_material() -> None:
    """The key should not synthesize or normalize its fields."""
    key = ResponseCacheKey(
        namespace="  demo-namespace  ",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )

    assert key.namespace == "  demo-namespace  "
    assert key.model_payload_hash == "payload-hash"
    assert key.feature_hash == "feature-hash"

