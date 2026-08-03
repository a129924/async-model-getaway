"""RED coverage for the minimal operational ResponseCache owner."""

from __future__ import annotations

import asyncio
import inspect
from typing import get_type_hints

import pytest
import async_model_gateway.response_cache.cache as response_cache_cache_module
from async_model_gateway.response_cache import ResponseCache, ResponseCacheEntry, ResponseCacheKey
from async_model_gateway.response_cache.ports.store import ResponseCacheStore


class RecordingStore(ResponseCacheStore):
    """Store test double that records delegated keys and entries."""

    def __init__(
        self,
        *,
        stored_entry: ResponseCacheEntry | None = None,
        get_error: BaseException | None = None,
        set_error: BaseException | None = None,
        invalidation_result: bool = False,
        invalidation_error: BaseException | None = None,
    ) -> None:
        self.get_calls: list[ResponseCacheKey] = []
        self.set_calls: list[tuple[ResponseCacheKey, ResponseCacheEntry]] = []
        self.invalidation_calls: list[ResponseCacheKey] = []
        self._stored_entry = stored_entry
        self._get_error = get_error
        self._set_error = set_error
        self._invalidation_result = invalidation_result
        self._invalidation_error = invalidation_error

    async def get(self, *, key: ResponseCacheKey) -> ResponseCacheEntry | None:
        self.get_calls.append(key)
        if self._get_error is not None:
            raise self._get_error
        return self._stored_entry

    async def set(self, *, key: ResponseCacheKey, entry: ResponseCacheEntry) -> None:
        self.set_calls.append((key, entry))
        if self._set_error is not None:
            raise self._set_error

    async def invalidate(self, *, key: ResponseCacheKey) -> bool:
        self.invalidation_calls.append(key)
        if self._invalidation_error is not None:
            raise self._invalidation_error
        return self._invalidation_result


def test_response_cache_public_contract_is_async_only() -> None:
    """The operational cache owner should stay minimal and async-only."""
    init_signature = inspect.signature(ResponseCache.__init__)
    get_signature = inspect.signature(ResponseCache.get)
    set_signature = inspect.signature(ResponseCache.set)
    invalidate_signature = inspect.signature(ResponseCache.invalidate)

    assert tuple(init_signature.parameters) == ("self", "store")
    assert inspect.iscoroutinefunction(ResponseCache.get)
    assert inspect.iscoroutinefunction(ResponseCache.set)
    assert inspect.iscoroutinefunction(ResponseCache.invalidate)
    assert tuple(get_signature.parameters) == ("self", "key")
    assert get_signature.parameters["key"].kind is inspect.Parameter.KEYWORD_ONLY
    assert tuple(set_signature.parameters) == ("self", "key", "entry")
    assert set_signature.parameters["key"].kind is inspect.Parameter.KEYWORD_ONLY
    assert set_signature.parameters["entry"].kind is inspect.Parameter.KEYWORD_ONLY
    assert tuple(invalidate_signature.parameters) == ("self", "key")
    assert invalidate_signature.parameters["key"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_type_hints(ResponseCache.invalidate) == {
        "key": ResponseCacheKey,
        "return": bool,
    }


def test_response_cache_init_type_hints_resolve_store_port_without_public_reexport() -> None:
    """The constructor annotation must stay runtime-resolvable without a public leak."""
    init_type_hints = get_type_hints(ResponseCache.__init__)

    assert init_type_hints["store"] is ResponseCacheStore
    assert "ResponseCacheStore" not in vars(response_cache_cache_module)


@pytest.mark.asyncio
async def test_response_cache_get_delegates_key_and_returns_store_entry() -> None:
    """A cache hit should return the same entry object from the store."""
    key = ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    entry = ResponseCacheEntry(response="cached response")
    store = RecordingStore(stored_entry=entry)
    cache = ResponseCache(store)

    result = await cache.get(key=key)

    assert result is entry
    assert store.get_calls == [key]


@pytest.mark.asyncio
async def test_response_cache_get_returns_none_for_cache_miss() -> None:
    """A store miss should remain the public None miss surface."""
    key = ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    cache = ResponseCache(RecordingStore(stored_entry=None))

    result = await cache.get(key=key)

    assert result is None


@pytest.mark.asyncio
async def test_response_cache_set_delegates_same_key_and_entry() -> None:
    """The cache owner should pass through key and entry without reshaping them."""
    key = ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    entry = ResponseCacheEntry(response="generated response")
    store = RecordingStore()
    cache = ResponseCache(store)

    result = await cache.set(key=key, entry=entry)

    assert result is None
    assert store.set_calls == [(key, entry)]


@pytest.mark.asyncio
async def test_response_cache_get_propagates_store_failure_unchanged() -> None:
    """Store lookup failures should escape without translation."""
    key = ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    cache = ResponseCache(RecordingStore(get_error=RuntimeError("lookup failed")))

    with pytest.raises(RuntimeError, match="lookup failed"):
        await cache.get(key=key)


@pytest.mark.asyncio
async def test_response_cache_set_propagates_cancelled_error_unchanged() -> None:
    """Cancellation must remain owned by the underlying store awaitable."""
    key = ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    entry = ResponseCacheEntry(response="generated response")
    cache = ResponseCache(RecordingStore(set_error=asyncio.CancelledError()))

    with pytest.raises(asyncio.CancelledError):
        await cache.set(key=key, entry=entry)


@pytest.mark.asyncio
@pytest.mark.parametrize("store_result", [True, False])
async def test_response_cache_invalidate_delegates_the_original_key_and_boolean(
    store_result: bool,
) -> None:
    """Explicit invalidation must return the store result without reshaping it."""
    key = ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    store = RecordingStore(invalidation_result=store_result)
    cache = ResponseCache(store)

    assert await cache.invalidate(key=key) is store_result
    assert store.invalidation_calls == [key]


@pytest.mark.asyncio
async def test_response_cache_invalidate_propagates_store_error_unchanged() -> None:
    """Facade invalidation must not translate a store failure into a miss."""
    key = ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    store_error = RuntimeError("invalidation failed")
    cache = ResponseCache(RecordingStore(invalidation_error=store_error))

    with pytest.raises(RuntimeError, match="invalidation failed") as raised:
        await cache.invalidate(key=key)

    assert raised.value is store_error


@pytest.mark.asyncio
async def test_response_cache_invalidate_propagates_cancelled_error_unchanged() -> None:
    """Facade invalidation must leave cancellation owned by its store awaitable."""
    key = ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    cache = ResponseCache(RecordingStore(invalidation_error=asyncio.CancelledError()))

    with pytest.raises(asyncio.CancelledError):
        await cache.invalidate(key=key)
