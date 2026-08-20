"""RED coverage for write-time expiry policy ownership."""

from __future__ import annotations

import inspect
from datetime import datetime, timezone

import pytest


def test_freshness_policy_exposes_only_write_time_expiry_derivation() -> None:
    """Read-time freshness and its second clock input are removed."""
    from async_model_gateway.response_cache.freshness_policy import FreshnessPolicy

    signature = inspect.signature(FreshnessPolicy.expires_at)

    assert tuple(signature.parameters) == ("self", "written_at")
    assert signature.parameters["written_at"].kind is inspect.Parameter.KEYWORD_ONLY
    assert not hasattr(FreshnessPolicy, "is_fresh")


@pytest.mark.asyncio
async def test_expiry_policy_defects_are_not_facade_outcomes() -> None:
    """A malformed policy result stays an ordinary defect for callers to observe."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.key import CacheKey

    class Store:
        async def get(self, *, key: object) -> None:
            return None

        async def set(self, *, key: object, record: object) -> None:
            return None

        async def delete(self, *, key: object) -> bool:
            return False

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            return False

    class Codec:
        codec_id = "utf-8"

        def encode(self, *, value: str) -> bytes:
            return value.encode()

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    class Tokens:
        def new(self) -> object:
            return object()

    class InvalidPolicy:
        def expires_at(self, *, written_at: datetime) -> datetime:
            return written_at

    cache = ResponseCache(
        store=Store(),
        codec=Codec(),
        version_token_factory=Tokens(),
        freshness_policy=InvalidPolicy(),
        clock=lambda: datetime(2026, 8, 6, tzinfo=timezone.utc),
    )

    with pytest.raises(ValueError):
        await cache.remember(
            key=CacheKey("response-cache", "model", "feature", "input"),
            value="response",
            context=object(),
        )
