"""RED coverage for the in-memory registry-store implementation contract."""

from __future__ import annotations

import asyncio
import inspect

import pytest
from async_model_gateway.model_registry.entry import ModelSourceKind, RegistryEntry
from async_model_gateway.model_registry.ports.store import RegistryStore


def test_in_memory_registry_store_public_contract_is_bounded() -> None:
    """The concrete store should stay async-only with an empty constructor."""
    from async_model_gateway.model_registry.stores import InMemoryRegistryStore

    init_signature = inspect.signature(InMemoryRegistryStore.__init__)
    get_entry_signature = inspect.signature(InMemoryRegistryStore.get_entry)
    upsert_entry_signature = inspect.signature(InMemoryRegistryStore.upsert_entry)

    assert issubclass(InMemoryRegistryStore, RegistryStore)
    assert tuple(init_signature.parameters) == ("self",)
    assert inspect.iscoroutinefunction(InMemoryRegistryStore.get_entry)
    assert inspect.iscoroutinefunction(InMemoryRegistryStore.upsert_entry)
    assert tuple(get_entry_signature.parameters) == (
        "self",
        "model_name",
        "model_source_kind",
    )
    assert get_entry_signature.parameters["model_name"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_entry_signature.parameters["model_source_kind"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )
    assert tuple(upsert_entry_signature.parameters) == ("self", "entry")
    assert getattr(InMemoryRegistryStore.get_entry, "__override__", False) is True
    assert getattr(InMemoryRegistryStore.upsert_entry, "__override__", False) is True


@pytest.mark.asyncio
async def test_in_memory_registry_store_returns_none_for_missing_lookup() -> None:
    """A fresh store should return None when the lookup identity is absent."""
    from async_model_gateway.model_registry.stores import InMemoryRegistryStore

    store = InMemoryRegistryStore()

    result = await store.get_entry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
    )

    assert result is None


@pytest.mark.asyncio
async def test_in_memory_registry_store_upsert_overwrites_same_lookup_identity() -> None:
    """Re-upserting the same model identity should replace the stored entry."""
    from async_model_gateway.model_registry.stores import InMemoryRegistryStore

    store = InMemoryRegistryStore()
    original_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash="payload-v1",
    )
    replacement_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash="payload-v2",
    )

    await store.upsert_entry(original_entry)
    await store.upsert_entry(replacement_entry)

    result = await store.get_entry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
    )

    assert result == replacement_entry


@pytest.mark.asyncio
async def test_in_memory_registry_store_distinguishes_source_kind_for_same_model_name() -> None:
    """The lookup identity should keep local and remote entries separate."""
    from async_model_gateway.model_registry.stores import InMemoryRegistryStore

    store = InMemoryRegistryStore()
    local_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash="local-payload",
    )
    remote_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.REMOTE,
        payload_hash="remote-payload",
    )

    await store.upsert_entry(local_entry)
    await store.upsert_entry(remote_entry)

    local_result = await store.get_entry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
    )
    remote_result = await store.get_entry(
        model_name="demo",
        model_source_kind=ModelSourceKind.REMOTE,
    )

    assert local_result == local_entry
    assert remote_result == remote_entry


class _RecordingLock:
    """A real async lock wrapper that records serialized acquisitions."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self.enter_count = 0
        self.max_active = 0
        self._active = 0

    async def __aenter__(self) -> _RecordingLock:
        await self._lock.acquire()
        self.enter_count += 1
        self._active += 1
        self.max_active = max(self.max_active, self._active)
        await asyncio.sleep(0)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        self._active -= 1
        self._lock.release()


@pytest.mark.asyncio
async def test_in_memory_registry_store_serializes_reads_and_writes_with_one_lock() -> None:
    """Reads and writes on one instance should share the same serialized lock."""
    from async_model_gateway.model_registry.stores import InMemoryRegistryStore

    store = InMemoryRegistryStore()
    assert isinstance(store._lock, asyncio.Lock)

    recording_lock = _RecordingLock()
    store._lock = recording_lock

    entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash="payload-v1",
    )

    get_task = asyncio.create_task(
        store.get_entry(
            model_name="demo",
            model_source_kind=ModelSourceKind.LOCAL,
        )
    )
    upsert_task = asyncio.create_task(store.upsert_entry(entry))

    get_result, upsert_result = await asyncio.gather(get_task, upsert_task)

    assert get_result is None
    assert upsert_result is None
    assert recording_lock.enter_count == 2
    assert recording_lock.max_active == 1
