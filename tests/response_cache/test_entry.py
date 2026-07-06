"""RED coverage for the ResponseCacheEntry value surface."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from typing import get_type_hints

import pytest
from async_model_gateway.response_cache import ResponseCacheEntry


def test_response_cache_entry_is_a_frozen_dataclass_with_one_string_field() -> None:
    """The entry surface should stay immutable and metadata-free."""
    assert is_dataclass(ResponseCacheEntry)
    assert ResponseCacheEntry.__dataclass_params__.frozen is True
    assert [field.name for field in fields(ResponseCacheEntry)] == ["response"]
    assert get_type_hints(ResponseCacheEntry) == {"response": str}


def test_response_cache_entry_preserves_literal_response_without_normalization() -> None:
    """The entry should store the caller-provided response as-is."""
    entry = ResponseCacheEntry(response="  cached response  ")

    assert entry.response == "  cached response  "


def test_response_cache_entry_rejects_mutation_after_construction() -> None:
    """The entry contract should stay immutable after creation."""
    entry = ResponseCacheEntry(response="cached response")

    with pytest.raises(FrozenInstanceError):
        entry.response = "new response"
