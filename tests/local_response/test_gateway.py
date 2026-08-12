"""RED coverage for the bounded local ONNX response-generation gateway."""

from __future__ import annotations

import asyncio

import pytest

import async_model_gateway.local_response.gateway as gateway_module
from async_model_gateway.local_response import LocalResponseGateway, LocalResponseRequest
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


class _RecordingRegistry:
    """Record the gateway's one freshness call."""

    def __init__(self, events: list[str], error: BaseException | None = None) -> None:
        self.events = events
        self.error = error
        self.calls: list[dict[str, object]] = []

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
        if self.error is not None:
            raise self.error
        return RegistryFreshnessResult(
            decision=RegistryFreshnessDecision.FIRST_SEEN,
            entry=RegistryEntry(
                model_name=model_name,
                model_source_kind=model_source_kind,
                payload_hash="fresh-payload-hash",
            ),
            previous_payload_hash=None,
        )


class _RecordingCache:
    """Expose cache calls and their private invocation-only contexts."""

    def __init__(
        self,
        events: list[str],
        *,
        lookup_outcomes: list[object] | None = None,
        remember_outcome: object = Remembered(),
    ) -> None:
        self.events = events
        self.lookup_outcomes = lookup_outcomes or [CacheMiss()]
        self.remember_outcome = remember_outcome
        self.lookup_calls: list[tuple[CacheKey, object]] = []
        self.remember_calls: list[tuple[CacheKey, str, object]] = []

    async def lookup(self, *, key: CacheKey, context: object) -> object:
        self.events.append("lookup")
        self.lookup_calls.append((key, context))
        return self.lookup_outcomes.pop(0)

    async def remember(self, *, key: CacheKey, value: str, context: object) -> object:
        self.events.append("remember")
        self.remember_calls.append((key, value, context))
        return self.remember_outcome


def _request(
    *,
    model_source_kind: ModelSourceKind = ModelSourceKind.LOCAL,
    loader_family: LoaderFamily = LoaderFamily.ONNX,
) -> LocalResponseRequest:
    return LocalResponseRequest(
        model_name="demo",
        model_source_kind=model_source_kind,
        model_payload={"revision": 1, "nested": ["value", {"enabled": True}]},
        features={"format": "text"},
        model_artifact=ModelArtifact(
            loader_family=loader_family,
            artifact_path="model.onnx",
            loader_options={},
        ),
        invocation={"prompt": "hello"},
    )


def _gateway(
    *,
    events: list[str],
    registry: _RecordingRegistry,
    cache: _RecordingCache,
    executor_error: BaseException | None = None,
    converter_error: BaseException | None = None,
) -> LocalResponseGateway:
    def hash_features(features: object) -> str:
        events.append("features")
        assert features == {"format": "text"}
        return "feature-hash"

    async def executor(artifact: ModelArtifact, invocation: dict[str, object]) -> list[object]:
        events.append("executor")
        assert artifact.loader_family is LoaderFamily.ONNX
        assert invocation == {"prompt": "hello"}
        if executor_error is not None:
            raise executor_error
        return ["provider-result"]

    def convert_onnx_result(result: list[object]) -> str:
        events.append("converter")
        assert result == ["provider-result"]
        if converter_error is not None:
            raise converter_error
        return "generated"

    return LocalResponseGateway(
        registry=registry,
        response_cache=cache,
        hash_features=hash_features,
        convert_onnx_result=convert_onnx_result,
        executor=executor,
    )


@pytest.mark.asyncio
async def test_cache_hit_returns_before_execution_conversion_or_write() -> None:
    """A hit consumes only the identity and lookup portion of the flow."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events, lookup_outcomes=[CacheHit(value="cached")])

    result = await _gateway(events=events, registry=registry, cache=cache).generate(
        request=_request()
    )

    assert result == "cached"
    assert events == ["registry", "features", "lookup"]
    assert registry.calls == [
        {
            "model_name": "demo",
            "model_source_kind": ModelSourceKind.LOCAL,
            "model_payload": {"revision": 1, "nested": ["value", {"enabled": True}]},
        }
    ]
    assert cache.remember_calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "remember_outcome",
    [
        Remembered(),
        Skipped(reason=CacheSkipReason.CLOSED),
        Failed(kind=CacheFailureKind.STORE),
    ],
)
async def test_cache_miss_uses_locked_order_key_and_fail_open_write_outcomes(
    remember_outcome: object,
) -> None:
    """Each declared write outcome returns the converted local response."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events, remember_outcome=remember_outcome)

    result = await _gateway(events=events, registry=registry, cache=cache).generate(
        request=_request()
    )

    assert result == "generated"
    assert events == ["registry", "features", "lookup", "executor", "converter", "remember"]
    assert cache.lookup_calls[0][0] == CacheKey(
        namespace="local-response-v1",
        model_payload_hash="fresh-payload-hash",
        feature_hash="feature-hash",
    )
    assert cache.remember_calls[0][0] == cache.lookup_calls[0][0]
    assert cache.remember_calls[0][1] == "generated"


@pytest.mark.asyncio
async def test_cache_context_sentinels_are_fresh_distinct_objects_and_not_request_data() -> None:
    """Lookup and write contexts are opaque fresh call-site sentinels."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events, lookup_outcomes=[CacheMiss(), CacheMiss()])
    gateway = _gateway(events=events, registry=registry, cache=cache)
    first_request = _request()
    second_request = _request()

    await gateway.generate(request=first_request)
    await gateway.generate(request=second_request)

    lookup_contexts = [call[1] for call in cache.lookup_calls]
    remember_contexts = [call[2] for call in cache.remember_calls]
    all_contexts = lookup_contexts + remember_contexts
    request_values = [
        first_request,
        first_request.model_name,
        first_request.model_source_kind,
        first_request.model_payload,
        first_request.features,
        first_request.model_artifact,
        first_request.invocation,
        second_request,
        second_request.model_name,
        second_request.model_source_kind,
        second_request.model_payload,
        second_request.features,
        second_request.model_artifact,
        second_request.invocation,
    ]

    assert all(type(context) is object for context in all_contexts)
    assert len({id(context) for context in all_contexts}) == 4
    assert all(all(context is not value for value in request_values) for context in all_contexts)


@pytest.mark.asyncio
@pytest.mark.parametrize("loader_family", [LoaderFamily.PICKLE, LoaderFamily.TORCH])
async def test_unsupported_source_or_loader_family_fails_before_any_collaborator_call(
    loader_family: LoaderFamily,
) -> None:
    """Only caller-supplied local ONNX artifacts reach the coordinator flow."""
    for request in (
        _request(model_source_kind=ModelSourceKind.REMOTE),
        _request(loader_family=loader_family),
    ):
        events: list[str] = []
        registry = _RecordingRegistry(events)
        cache = _RecordingCache(events)

        with pytest.raises(NotImplementedError):
            await _gateway(events=events, registry=registry, cache=cache).generate(request=request)

        assert events == []
        assert registry.calls == []
        assert cache.lookup_calls == []
        assert cache.remember_calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("unexpected_on", ["lookup", "remember"])
async def test_unexpected_closed_cache_outcomes_reach_assert_never(unexpected_on: str) -> None:
    """An invalid union member has no broad fallback response."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(
        events,
        lookup_outcomes=[object()] if unexpected_on == "lookup" else [CacheMiss()],
        remember_outcome=object(),
    )

    with pytest.raises(AssertionError):
        await _gateway(events=events, registry=registry, cache=cache).generate(request=_request())

    expected = ["registry", "features", "lookup"]
    if unexpected_on == "remember":
        expected.extend(["executor", "converter", "remember"])
    assert events == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_site", ["registry", "hasher", "executor", "converter"])
async def test_pre_remember_failures_propagate_by_identity_without_a_write(
    failure_site: str,
) -> None:
    """The gateway does not translate a non-cache collaborator failure."""
    events: list[str] = []
    failure = RuntimeError(failure_site)
    registry = _RecordingRegistry(events, error=failure if failure_site == "registry" else None)
    cache = _RecordingCache(events)
    gateway = _gateway(
        events=events,
        registry=registry,
        cache=cache,
        executor_error=failure if failure_site == "executor" else None,
        converter_error=failure if failure_site == "converter" else None,
    )
    if failure_site == "hasher":
        def failing_hasher(features: object) -> str:
            events.append("features")
            _ = features
            raise failure

        gateway = LocalResponseGateway(
            registry=registry,
            response_cache=cache,
            hash_features=failing_hasher,
            convert_onnx_result=lambda result: str(result),
            executor=lambda artifact, invocation: asyncio.sleep(0, result=[]),
        )

    with pytest.raises(RuntimeError) as raised:
        await gateway.generate(request=_request())

    assert raised.value is failure
    assert cache.remember_calls == []


@pytest.mark.asyncio
async def test_cancellation_from_executor_propagates_unchanged_without_a_write() -> None:
    """Cancellation remains caller-owned and prevents conversion and remember."""
    events: list[str] = []
    cancellation = asyncio.CancelledError()
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events)
    gateway = _gateway(
        events=events,
        registry=registry,
        cache=cache,
        executor_error=cancellation,
    )

    with pytest.raises(asyncio.CancelledError) as raised:
        await gateway.generate(request=_request())

    assert raised.value is cancellation
    assert events == ["registry", "features", "lookup", "executor"]
    assert cache.remember_calls == []


@pytest.mark.asyncio
async def test_concurrent_same_key_misses_direct_await_separate_execution_paths() -> None:
    """Equivalent misses do not join a shared task, lock, or retry owner."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events, lookup_outcomes=[CacheMiss(), CacheMiss()])
    executions: list[dict[str, object]] = []

    async def executor(artifact: ModelArtifact, invocation: dict[str, object]) -> list[object]:
        events.append("executor")
        executions.append(invocation)
        assert artifact.loader_family is LoaderFamily.ONNX
        execution_number = len(executions)
        await asyncio.sleep(0)
        return [execution_number]

    gateway = LocalResponseGateway(
        registry=registry,
        response_cache=cache,
        hash_features=lambda features: (events.append("features"), "feature-hash")[1],
        convert_onnx_result=lambda result: (events.append("converter"), str(result[0]))[1],
        executor=executor,
    )

    results = await asyncio.gather(
        gateway.generate(request=_request()),
        gateway.generate(request=_request()),
    )

    assert sorted(results) == ["1", "2"]
    assert len(executions) == 2
    assert len(cache.remember_calls) == 2
    assert len({id(context) for _, context in cache.lookup_calls}) == 2


@pytest.mark.asyncio
async def test_default_executor_adapter_delegates_to_existing_private_composition(
    monkeypatch,
) -> None:
    """The optional seam does not promote composition, pool, or executor ownership."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events)

    class Composition:
        async def execute(
            self,
            artifact: ModelArtifact,
            invocation: dict[str, object],
        ) -> list[object]:
            events.append("composition.execute")
            assert artifact.loader_family is LoaderFamily.ONNX
            assert invocation == {"prompt": "hello"}
            return ["provider-result"]

    def create_composition() -> Composition:
        events.append("composition.create")
        return Composition()

    monkeypatch.setattr(gateway_module, "_create_local_runtime_composition", create_composition)
    gateway = LocalResponseGateway(
        registry=registry,
        response_cache=cache,
        hash_features=lambda features: (events.append("features"), "feature-hash")[1],
        convert_onnx_result=lambda result: (events.append("converter"), "generated")[1],
    )

    result = await gateway.generate(request=_request())

    assert result == "generated"
    assert events == [
        "composition.create",
        "registry",
        "features",
        "lookup",
        "composition.execute",
        "converter",
        "remember",
    ]
