"""RED coverage for coherent complete-record in-memory storage."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


def _record(*, value: str, token: str, expires_at: datetime | None = None) -> object:
    """Build one valid target envelope without involving a facade."""
    from async_model_gateway.response_cache.record import CacheVersionToken, StoredCacheRecord

    written_at = datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc)
    return StoredCacheRecord(
        schema_version=1,
        codec_id="utf-8",
        payload=value.encode(),
        written_at=written_at,
        expires_at=expires_at or written_at + timedelta(seconds=30),
        version_token=CacheVersionToken(value=token),
        metadata=(),
    )


def _key(*, feature_hash: str = "feature") -> object:
    from async_model_gateway.response_cache.key import CacheKey

    return CacheKey("response-cache", "payload", feature_hash)


@pytest.mark.asyncio
async def test_store_returns_the_same_complete_record_and_replaces_whole_records() -> None:
    """A write replaces the envelope atomically rather than merging entry-shaped state."""
    from async_model_gateway.response_cache._in_memory_store import InMemoryCacheStore

    store = InMemoryCacheStore()
    key = _key()
    original = _record(value="first", token="A")
    replacement = _record(value="second", token="B")

    await store.set(key=key, record=original)
    assert await store.get(key=key) is original
    await store.set(key=key, record=replacement)

    assert await store.get(key=key) is replacement


@pytest.mark.asyncio
async def test_store_compare_delete_is_token_guarded_and_key_local() -> None:
    """A stale observed token cannot delete a later same-key replacement or another key."""
    from async_model_gateway.response_cache._in_memory_store import InMemoryCacheStore
    from async_model_gateway.response_cache.record import CacheVersionToken

    store = InMemoryCacheStore()
    first_key = _key(feature_hash="first")
    second_key = _key(feature_hash="second")
    old = _record(value="old", token="A")
    replacement = _record(value="new", token="B")
    other = _record(value="other", token="C")
    await store.set(key=first_key, record=old)
    await store.set(key=second_key, record=other)
    await store.set(key=first_key, record=replacement)

    assert (
        await store.delete_if_version(key=first_key, version_token=CacheVersionToken(value="A"))
        is False
    )
    assert await store.get(key=first_key) is replacement
    assert await store.get(key=second_key) is other
    assert (
        await store.delete_if_version(key=first_key, version_token=CacheVersionToken(value="B"))
        is True
    )
    assert await store.get(key=first_key) is None
    assert await store.get(key=second_key) is other


@pytest.mark.asyncio
async def test_store_ordinary_delete_is_reserved_for_separate_invalidation() -> None:
    """The store offers key-local deletion but no old boolean invalidation operation."""
    from async_model_gateway.response_cache._in_memory_store import InMemoryCacheStore

    store = InMemoryCacheStore()
    key = _key()
    await store.set(key=key, record=_record(value="value", token="A"))

    assert await store.delete(key=key) is True
    assert await store.delete(key=key) is False
    assert not hasattr(store, "invalidate")


def test_in_memory_store_has_no_clock_or_freshness_policy_owner() -> None:
    """Read-time policy and the former in-memory clock cannot reappear."""
    from async_model_gateway.response_cache import _in_memory_store
    from async_model_gateway.response_cache._in_memory_store import InMemoryCacheStore

    assert not hasattr(_in_memory_store, "_utc_now")
    assert "freshness_policy" not in InMemoryCacheStore.__init__.__annotations__


def test_old_in_memory_store_class_name_is_absent() -> None:
    """The former entry-oriented implementation name has no normal import route."""
    from async_model_gateway.response_cache import _in_memory_store

    assert not hasattr(_in_memory_store, "InMemoryResponseCacheStore")
    with pytest.raises(ImportError):
        from async_model_gateway.response_cache._in_memory_store import (
            InMemoryResponseCacheStore as LegacyInMemoryResponseCacheStore,
        )

        assert LegacyInMemoryResponseCacheStore is None
