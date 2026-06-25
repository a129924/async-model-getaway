"""RED coverage for the async ModelRegistry boundary."""

from __future__ import annotations

import asyncio
import inspect

import pytest
from async_model_gateway.model_registry import ModelRegistry
from async_model_gateway.model_registry.entry import ModelSourceKind
from async_model_gateway.model_registry.freshness_result import RegistryFreshnessDecision
from async_model_gateway.model_registry.model_payload import ModelPayloadHasher
from async_model_gateway.model_registry.entry import RegistryEntry
from async_model_gateway.model_registry.ports.store import RegistryStore


class RecordingStore(RegistryStore):
    """Simple registry-store test double for behavior-focused tests."""

    def __init__(
        self,
        *,
        stored_entry: RegistryEntry | None = None,
        lookup_error: BaseException | None = None,
        upsert_error: BaseException | None = None,
    ) -> None:
        self.lookup_calls: list[dict[str, str | ModelSourceKind]] = []
        self.upserted_entries: list[RegistryEntry] = []
        self._stored_entry = stored_entry
        self._lookup_error = lookup_error
        self._upsert_error = upsert_error

    async def get_entry(
        self,
        *,
        model_name: str,
        model_source_kind: ModelSourceKind,
    ) -> RegistryEntry | None:
        self.lookup_calls.append(
            {
                "model_name": model_name,
                "model_source_kind": model_source_kind,
            }
        )
        if self._lookup_error is not None:
            raise self._lookup_error
        return self._stored_entry

    async def upsert_entry(self, entry: RegistryEntry) -> None:
        self.upserted_entries.append(entry)
        if self._upsert_error is not None:
            raise self._upsert_error


def test_model_registry_public_contract_is_async_only() -> None:
    """The new boundary should stay class-first and async-only."""
    init_signature = inspect.signature(ModelRegistry.__init__)
    resolve_signature = inspect.signature(ModelRegistry.resolve_freshness)

    assert tuple(init_signature.parameters) == (
        "self",
        "store",
        "freshness_policy",
        "payload_hasher",
    )
    assert init_signature.parameters["freshness_policy"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )
    assert init_signature.parameters["payload_hasher"].kind is inspect.Parameter.KEYWORD_ONLY

    assert inspect.iscoroutinefunction(ModelRegistry.resolve_freshness)
    assert tuple(resolve_signature.parameters) == (
        "self",
        "model_name",
        "model_source_kind",
        "model_payload",
    )
    assert resolve_signature.parameters["model_name"].kind is inspect.Parameter.KEYWORD_ONLY
    assert resolve_signature.parameters["model_source_kind"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )
    assert resolve_signature.parameters["model_payload"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )


@pytest.mark.asyncio
async def test_model_registry_first_seen_payload_upserts_candidate_entry() -> None:
    """A missing store entry should produce first-seen and persist the candidate."""
    store = RecordingStore()
    registry = ModelRegistry(store=store)
    payload = {
        "config": {"revision": 1, "temperature": 0.1},
        "features": ["vision"],
    }

    result = await registry.resolve_freshness(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload=payload,
    )

    expected_hash = ModelPayloadHasher().hash_model_payload(payload)

    assert store.lookup_calls == [
        {"model_name": "demo", "model_source_kind": ModelSourceKind.LOCAL},
    ]
    assert len(store.upserted_entries) == 1
    assert isinstance(store.upserted_entries[0], RegistryEntry)
    assert result.decision is RegistryFreshnessDecision.FIRST_SEEN
    assert result.previous_payload_hash is None
    assert result.entry is store.upserted_entries[0]
    assert result.entry.model_name == "demo"
    assert result.entry.model_source_kind is ModelSourceKind.LOCAL
    assert result.entry.payload_hash == expected_hash


@pytest.mark.asyncio
async def test_model_registry_unchanged_payload_skips_upsert() -> None:
    """The unchanged path should not trigger a write."""
    payload = {"config": {"revision": 1}, "features": ["vision", "tool-call"]}
    payload_hash = ModelPayloadHasher().hash_model_payload(payload)
    stored_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.REMOTE,
        payload_hash=payload_hash,
    )
    store = RecordingStore(stored_entry=stored_entry)
    registry = ModelRegistry(store=store)

    result = await registry.resolve_freshness(
        model_name="demo",
        model_source_kind=ModelSourceKind.REMOTE,
        model_payload=payload,
    )

    assert store.lookup_calls == [
        {"model_name": "demo", "model_source_kind": ModelSourceKind.REMOTE},
    ]
    assert store.upserted_entries == []
    assert result.decision is RegistryFreshnessDecision.UNCHANGED
    assert result.entry.model_name == "demo"
    assert result.entry.model_source_kind is ModelSourceKind.REMOTE
    assert result.entry.payload_hash == payload_hash


@pytest.mark.asyncio
async def test_model_registry_changed_payload_returns_previous_hash_and_upserts() -> None:
    """A changed payload should persist the candidate and report the old hash."""
    old_payload_hash = ModelPayloadHasher().hash_model_payload({"revision": 1})
    stored_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash=old_payload_hash,
    )
    store = RecordingStore(stored_entry=stored_entry)
    registry = ModelRegistry(store=store)
    new_payload = {"revision": 2}

    result = await registry.resolve_freshness(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload=new_payload,
    )

    assert store.lookup_calls == [
        {"model_name": "demo", "model_source_kind": ModelSourceKind.LOCAL},
    ]
    assert len(store.upserted_entries) == 1
    assert result.decision is RegistryFreshnessDecision.CHANGED
    assert result.previous_payload_hash == old_payload_hash
    assert result.entry is store.upserted_entries[0]
    assert result.entry.payload_hash == ModelPayloadHasher().hash_model_payload(new_payload)


@pytest.mark.asyncio
async def test_model_registry_lookup_identity_ignores_payload_hash() -> None:
    """Identical payload hashes must not collapse distinct lookup identities."""
    store = RecordingStore()
    registry = ModelRegistry(store=store)
    payload = {"shared": {"revision": 1}}

    await registry.resolve_freshness(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload=payload,
    )
    await registry.resolve_freshness(
        model_name="demo",
        model_source_kind=ModelSourceKind.REMOTE,
        model_payload=payload,
    )

    assert store.lookup_calls == [
        {"model_name": "demo", "model_source_kind": ModelSourceKind.LOCAL},
        {"model_name": "demo", "model_source_kind": ModelSourceKind.REMOTE},
    ]
    assert len(store.upserted_entries) == 2


@pytest.mark.asyncio
async def test_model_registry_uses_model_payload_hasher_contract_without_wrapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The registry should delegate payload hashing to the existing owner as-is."""
    observed_payloads: list[dict[str, object]] = []

    def fake_hash(self: ModelPayloadHasher, model_payload: dict[str, object]) -> str:
        observed_payloads.append(model_payload)
        return "sentinel-payload-hash"

    monkeypatch.setattr(ModelPayloadHasher, "hash_model_payload", fake_hash)
    store = RecordingStore()
    registry = ModelRegistry(store=store, payload_hasher=ModelPayloadHasher())
    payload = {"alpha": [1, 2, 3]}

    result = await registry.resolve_freshness(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload=payload,
    )

    assert observed_payloads == [payload]
    assert result.entry.payload_hash == "sentinel-payload-hash"


@pytest.mark.asyncio
async def test_model_registry_invalid_payload_raises_type_error_before_write() -> None:
    """Unsupported payload values should still fail closed without any write."""
    store = RecordingStore()
    registry = ModelRegistry(store=store)

    with pytest.raises(TypeError):
        await registry.resolve_freshness(
            model_name="demo",
            model_source_kind=ModelSourceKind.LOCAL,
            model_payload={"nested": [{"value": object()}]},
        )

    assert store.lookup_calls == [
        {"model_name": "demo", "model_source_kind": ModelSourceKind.LOCAL},
    ]
    assert store.upserted_entries == []


@pytest.mark.asyncio
async def test_model_registry_propagates_store_lookup_failures_without_translation() -> None:
    """Lookup failures should propagate unchanged."""
    store = RecordingStore(
        lookup_error=RuntimeError("lookup failed"),
    )
    registry = ModelRegistry(store=store)

    with pytest.raises(RuntimeError, match="lookup failed"):
        await registry.resolve_freshness(
            model_name="demo",
            model_source_kind=ModelSourceKind.LOCAL,
            model_payload={"revision": 1},
        )

    assert store.upserted_entries == []


@pytest.mark.asyncio
async def test_model_registry_propagates_cancelled_error_without_translation() -> None:
    """Cancellation from store I/O should not be swallowed."""
    store = RecordingStore(
        lookup_error=asyncio.CancelledError(),
    )
    registry = ModelRegistry(store=store)

    with pytest.raises(asyncio.CancelledError):
        await registry.resolve_freshness(
            model_name="demo",
            model_source_kind=ModelSourceKind.REMOTE,
            model_payload={"revision": 1},
        )


@pytest.mark.asyncio
async def test_model_registry_propagates_store_upsert_failures_without_translation() -> None:
    """Upsert failures should propagate unchanged after the candidate is built."""
    store = RecordingStore(
        upsert_error=RuntimeError("upsert failed"),
    )
    registry = ModelRegistry(store=store)

    with pytest.raises(RuntimeError, match="upsert failed"):
        await registry.resolve_freshness(
            model_name="demo",
            model_source_kind=ModelSourceKind.LOCAL,
            model_payload={"revision": 1},
        )

    assert len(store.upserted_entries) == 1


@pytest.mark.asyncio
async def test_model_registry_propagates_upsert_cancelled_error_without_translation() -> None:
    """Cancellation during upsert should not be swallowed."""
    store = RecordingStore(
        upsert_error=asyncio.CancelledError(),
    )
    registry = ModelRegistry(store=store)

    with pytest.raises(asyncio.CancelledError):
        await registry.resolve_freshness(
            model_name="demo",
            model_source_kind=ModelSourceKind.LOCAL,
            model_payload={"revision": 1},
        )

    assert len(store.upserted_entries) == 1
