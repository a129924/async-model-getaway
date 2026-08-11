"""RED coverage for the temporary legacy value and adapter route."""

from __future__ import annotations

from dataclasses import is_dataclass

import pytest


def test_legacy_entry_wrapper_exists_only_in_compat_and_is_immutable() -> None:
    """The target facade uses strings, while old callers retain one frozen wrapper."""
    import async_model_gateway.response_cache.compat as compat

    entry = compat.ResponseCacheEntry(response="legacy response")

    assert is_dataclass(entry)
    assert entry.response == "legacy response"
    with pytest.raises((AttributeError, TypeError)):
        entry.response = "mutated"  # type: ignore[misc]  # Intentional frozen-dataclass mutation.


def test_direct_legacy_entry_module_is_removed() -> None:
    """A normal direct import of the deleted legacy module must fail."""
    with pytest.raises(ModuleNotFoundError):
        import async_model_gateway.response_cache.entry as legacy_entry  # noqa: F401


@pytest.mark.asyncio
async def test_legacy_adapter_get_maps_target_hit_and_miss_without_context_retention() -> None:
    """Legacy get supplies only its private sentinel to the target facade."""
    import async_model_gateway.response_cache.compat as compat
    from async_model_gateway.response_cache.outcomes import CacheHit, CacheMiss

    class Facade:
        def __init__(self) -> None:
            self.contexts: list[object] = []

        async def lookup(self, *, key: object, context: object) -> object:
            self.contexts.append(context)
            return CacheHit(value="target response")

    class Invalidator:
        async def invalidate(self, *, key: object) -> object:
            return object()

    facade = Facade()
    with pytest.warns(DeprecationWarning):
        adapter = compat.LegacyResponseCacheAdapter(facade=facade, invalidator=Invalidator())

    assert await adapter.get(key=object()) == compat.ResponseCacheEntry("target response")

    async def missing(*, key: object, context: object) -> object:
        return CacheMiss()

    facade.lookup = missing  # type: ignore[method-assign]  # Intentional test-double method replacement.
    assert await adapter.get(key=object()) is None
    assert len(facade.contexts) == 1
    assert all(context is not None for context in facade.contexts)
