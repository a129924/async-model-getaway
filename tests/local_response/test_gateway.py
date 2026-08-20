"""RED coverage for the migrated bounded local response gateway."""

from __future__ import annotations

import asyncio

import pytest

from async_model_gateway.local_response import LocalResponseGateway, LocalResponseRequest
from async_model_gateway.local_response import gateway as gateway_module
from async_model_gateway.model_registry.entry import ModelSourceKind, RegistryEntry
from async_model_gateway.model_registry.freshness_result import (
    RegistryFreshnessDecision,
    RegistryFreshnessResult,
)
from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.response_cache import (
    CacheHit,
    CacheKey,
    CacheMiss,
    Failed,
    Remembered,
    Skipped,
)
from async_model_gateway.response_cache.outcomes import CacheFailureKind, CacheSkipReason

_DEFAULT_LOOKUP_OUTCOME = object()
_DEFAULT_REMEMBER_OUTCOME = object()


class _RecordingRegistry:
    """Record freshness interactions and return one immutable registry entry."""

    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.calls: list[dict[str, object]] = []
        self.entry = RegistryEntry(
            model_name="demo",
            model_source_kind=ModelSourceKind.LOCAL,
            payload_hash="raw-payload-hash",
        )

    async def resolve_freshness(
        self,
        *,
        model_name: str,
        model_source_kind: ModelSourceKind,
        model_payload: dict[str, object],
    ) -> RegistryFreshnessResult:
        self.events.append("registry")
        self.calls.append(
            {
                "model_name": model_name,
                "model_source_kind": model_source_kind,
                "model_payload": model_payload,
            }
        )
        return RegistryFreshnessResult(
            decision=RegistryFreshnessDecision.FIRST_SEEN,
            entry=self.entry,
            previous_payload_hash=None,
        )


class _PausingRegistry(_RecordingRegistry):
    """Expose the first registry await for shallow-snapshot observations."""

    def __init__(self, events: list[str]) -> None:
        super().__init__(events)
        self.awaited = asyncio.Event()
        self.resume = asyncio.Event()

    async def resolve_freshness(
        self,
        *,
        model_name: str,
        model_source_kind: ModelSourceKind,
        model_payload: dict[str, object],
    ) -> RegistryFreshnessResult:
        self.events.append("registry")
        self.awaited.set()
        await self.resume.wait()
        return RegistryFreshnessResult(
            decision=RegistryFreshnessDecision.FIRST_SEEN,
            entry=self.entry,
            previous_payload_hash=None,
        )


class _RecordingCache:
    """Capture cache calls without introducing cache behavior into this suite."""

    def __init__(
        self,
        events: list[str],
        outcome: object = _DEFAULT_LOOKUP_OUTCOME,
        remember_outcome: object = _DEFAULT_REMEMBER_OUTCOME,
    ) -> None:
        self.events = events
        self.outcome = CacheMiss() if outcome is _DEFAULT_LOOKUP_OUTCOME else outcome
        self.remember_outcome = (
            Remembered() if remember_outcome is _DEFAULT_REMEMBER_OUTCOME else remember_outcome
        )
        self.lookup_calls: list[CacheKey] = []
        self.remember_calls: list[tuple[CacheKey, str]] = []

    async def lookup(self, *, key: CacheKey, context: object) -> object:
        self.events.append("lookup")
        self.lookup_calls.append(key)
        assert type(context) is object
        return self.outcome

    async def remember(self, *, key: CacheKey, value: str, context: object) -> object:
        self.events.append("remember")
        self.remember_calls.append((key, value))
        assert type(context) is object
        return self.remember_outcome


def _request(
    *, invocation: dict[str, object] | None = None, features: object = None
) -> LocalResponseRequest:
    """Build one supported request with an optional identity-boundary override."""
    return LocalResponseRequest(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload={"revision": 1},
        features={"format": "text"} if features is None else features,  # type: ignore[arg-type]
        model_artifact=ModelArtifact(
            loader_family=LoaderFamily.ONNX,
            artifact_path="model.onnx",
            loader_options={},
        ),
        invocation={"prompt": "hello"} if invocation is None else invocation,
    )


def _gateway(
    *,
    events: list[str],
    registry: _RecordingRegistry,
    cache: _RecordingCache,
    observed_invocations: list[dict[str, object]] | None = None,
) -> LocalResponseGateway:
    """Build the post-migration public constructor with a recording executor."""

    async def executor(artifact: ModelArtifact, invocation: dict[str, object]) -> list[object]:
        events.append("executor")
        assert artifact.loader_family is LoaderFamily.ONNX
        if observed_invocations is not None:
            observed_invocations.append(invocation)
        return ["provider-result"]

    def convert_onnx_result(result: list[object]) -> str:
        events.append("converter")
        assert result == ["provider-result"]
        return "generated"

    return LocalResponseGateway(
        registry=registry,  # type: ignore[arg-type]
        response_cache=cache,  # type: ignore[arg-type]
        convert_onnx_result=convert_onnx_result,
        executor=executor,
    )


@pytest.mark.asyncio
async def test_cache_hit_uses_complete_registry_identity_before_execution() -> None:
    """The hit key takes the exact complete registry identity, never payload hash."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events, outcome=CacheHit(value="cached"))

    result = await _gateway(events=events, registry=registry, cache=cache).generate(
        request=_request()
    )

    key = cache.lookup_calls[0]
    assert result == "cached"
    assert events == ["registry", "lookup"]
    assert key.model_identity_hash == registry.entry.model_identity_hash
    assert key.model_identity_hash != registry.entry.payload_hash
    assert cache.remember_calls == []


@pytest.mark.asyncio
async def test_cache_miss_reuses_one_snapshot_for_identity_and_execution() -> None:
    """A top-level mutation during the registry await cannot alter execution input."""
    events: list[str] = []
    registry = _PausingRegistry(events)
    cache = _RecordingCache(events)
    observed_invocations: list[dict[str, object]] = []
    original = {"prompt": "before", "nested": ["same-leaf"]}
    gateway = _gateway(
        events=events,
        registry=registry,
        cache=cache,
        observed_invocations=observed_invocations,
    )

    generation = asyncio.create_task(gateway.generate(request=_request(invocation=original)))
    await registry.awaited.wait()
    original["prompt"] = "after"
    registry.resume.set()

    assert await generation == "generated"
    assert observed_invocations == [{"prompt": "before", "nested": ["same-leaf"]}]
    assert observed_invocations[0] is not original
    assert cache.lookup_calls[0] == cache.remember_calls[0][0]
    assert events == ["registry", "lookup", "executor", "converter", "remember"]


@pytest.mark.asyncio
async def test_default_adapter_passes_identity_snapshot_to_composition(monkeypatch) -> None:
    """The default adapter preserves the gateway's identity/execution snapshot."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events)
    identity_invocations: list[dict[str, object]] = []
    composition_invocations: list[dict[str, object]] = []

    class Composition:
        async def execute(
            self,
            artifact: ModelArtifact,
            invocation: dict[str, object],
        ) -> list[object]:
            assert artifact.loader_family is LoaderFamily.ONNX
            composition_invocations.append(invocation)
            return ["provider-result"]

    def create_composition() -> Composition:
        return Composition()

    def derive_prediction_input_hash(invocation: dict[str, object]) -> str:
        identity_invocations.append(invocation)
        return "prediction-input-hash"

    monkeypatch.setattr(gateway_module, "_create_local_runtime_composition", create_composition)
    monkeypatch.setattr(
        gateway_module,
        "_derive_prediction_input_hash",
        derive_prediction_input_hash,
    )
    gateway = LocalResponseGateway(
        registry=registry,  # type: ignore[arg-type]
        response_cache=cache,  # type: ignore[arg-type]
        convert_onnx_result=lambda result: "generated",
    )

    assert await gateway.generate(request=_request()) == "generated"
    assert composition_invocations[0] is identity_invocations[0]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "local_request",
    [
        _request(features={"format": object()}),
        _request(features={1: "text"}),
        _request(invocation={"nested": [object()]}),
        _request(invocation={1: "invalid-key"}),
    ],
)
async def test_invalid_identity_material_stops_before_registry_cache_or_execution(
    local_request: LocalResponseRequest,
) -> None:
    """Feature/input validation is fail-closed before the first awaited collaborator."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events)
    gateway = _gateway(events=events, registry=registry, cache=cache)

    with pytest.raises(TypeError):
        await gateway.generate(request=local_request)

    assert events == []
    assert registry.calls == []
    assert cache.lookup_calls == []
    assert cache.remember_calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "remember_outcome",
    (
        Remembered(),
        Skipped(reason=CacheSkipReason.CLOSED),
        Failed(kind=CacheFailureKind.STORE),
    ),
    ids=("remembered", "skipped", "failed"),
)
async def test_cache_miss_remember_outcomes_are_fail_open_without_reexecution_or_reconversion(
    remember_outcome: Remembered | Skipped | Failed,
) -> None:
    """Each closed write outcome returns the one already-generated local response."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events, remember_outcome=remember_outcome)

    assert (
        await _gateway(events=events, registry=registry, cache=cache).generate(request=_request())
        == "generated"
    )

    assert events == ["registry", "lookup", "executor", "converter", "remember"]
    assert events.count("executor") == 1
    assert events.count("converter") == 1
    assert len(cache.remember_calls) == 1


@pytest.mark.asyncio
async def test_changed_prediction_input_cannot_cross_hit_in_an_opaque_cache() -> None:
    """Input identity prevents a second local request from reusing the first response."""
    events: list[str] = []
    registry = _RecordingRegistry(events)

    class KeyedCache(_RecordingCache):
        def __init__(self, events: list[str]) -> None:
            super().__init__(events)
            self.values: dict[CacheKey, str] = {}

        async def lookup(self, *, key: CacheKey, context: object) -> object:
            self.events.append("lookup")
            self.lookup_calls.append(key)
            return CacheHit(value=self.values[key]) if key in self.values else CacheMiss()

        async def remember(self, *, key: CacheKey, value: str, context: object) -> object:
            self.events.append("remember")
            self.remember_calls.append((key, value))
            self.values[key] = value
            return Remembered()

    cache = KeyedCache(events)
    executions: list[dict[str, object]] = []
    gateway = _gateway(
        events=events,
        registry=registry,
        cache=cache,
        observed_invocations=executions,
    )

    assert await gateway.generate(request=_request(invocation={"prompt": "first"})) == "generated"
    assert await gateway.generate(request=_request(invocation={"prompt": "second"})) == "generated"
    assert len(executions) == 2
    assert cache.lookup_calls[0] != cache.lookup_calls[1]
    assert (
        cache.lookup_calls[0].prediction_input_hash != cache.lookup_calls[1].prediction_input_hash
    )


@pytest.mark.asyncio
async def test_unsupported_source_and_loader_remain_guarded_before_identity_work() -> None:
    """The existing local-ONNX guards stay before registry and cache interactions."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events)
    request = _request()
    remote_request = LocalResponseRequest(
        model_name=request.model_name,
        model_source_kind=ModelSourceKind.REMOTE,
        model_payload=request.model_payload,
        features=request.features,
        model_artifact=request.model_artifact,
        invocation=request.invocation,
    )

    with pytest.raises(NotImplementedError):
        gateway = _gateway(events=events, registry=registry, cache=cache)
        await gateway.generate(request=remote_request)

    assert events == []
