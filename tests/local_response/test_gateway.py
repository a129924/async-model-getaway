"""RED coverage for the bounded local ONNX response-generation gateway."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Iterator, Mapping

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


class _PausingRegistry(_RecordingRegistry):
    """Expose the first registry suspension as a deterministic test boundary."""

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
        self.calls.append(
            {
                "model_name": model_name,
                "model_source_kind": model_source_kind,
                "model_payload": model_payload,
            }
        )
        self.awaited.set()
        await self.resume.wait()
        return RegistryFreshnessResult(
            decision=RegistryFreshnessDecision.FIRST_SEEN,
            entry=RegistryEntry(
                model_name=model_name,
                model_source_kind=model_source_kind,
                payload_hash="fresh-payload-hash",
            ),
            previous_payload_hash=None,
        )


class _ExplodingInvocation(Mapping[str, object]):
    """Raise the exact sentinel when the gateway materializes a mapping copy."""

    def __init__(self, error: BaseException) -> None:
        self._error = error

    def __getitem__(self, _key: str) -> object:
        raise self._error

    def __iter__(self) -> Iterator[str]:
        raise self._error

    def __len__(self) -> int:
        return 1


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


class _KeyedRecordingCache:
    """Model cache hits by the opaque key received from the gateway."""

    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.values: dict[CacheKey, str] = {}
        self.lookup_calls: list[tuple[CacheKey, object]] = []
        self.remember_calls: list[tuple[CacheKey, str, object]] = []

    async def lookup(self, *, key: CacheKey, context: object) -> object:
        self.events.append("lookup")
        self.lookup_calls.append((key, context))
        value = self.values.get(key)
        return CacheMiss() if value is None else CacheHit(value=value)

    async def remember(self, *, key: CacheKey, value: str, context: object) -> object:
        self.events.append("remember")
        self.remember_calls.append((key, value, context))
        self.values[key] = value
        return Remembered()


class _RecordingKeyDeriver:
    """Derive opaque test keys while recording every locked identity input."""

    def __init__(
        self,
        events: list[str],
        *,
        error: BaseException | None = None,
    ) -> None:
        self.events = events
        self.error = error
        self.calls: list[dict[str, object]] = []
        self.keys: list[CacheKey] = []

    def __call__(
        self,
        *,
        model_name: str,
        model_payload_hash: str,
        features: Mapping[str, str],
        model_artifact: ModelArtifact,
        invocation: dict[str, object],
    ) -> CacheKey:
        self.events.append("deriver")
        self.calls.append(
            {
                "model_name": model_name,
                "model_payload_hash": model_payload_hash,
                "features": features,
                "model_artifact": model_artifact,
                "invocation": invocation,
            }
        )
        if self.error is not None:
            raise self.error

        identity = {
            "model_name": model_name,
            "model_payload_hash": model_payload_hash,
            "features": dict(features),
            "loader_family": model_artifact.loader_family.value,
            "artifact_path": model_artifact.artifact_path,
            "loader_options": repr(model_artifact.loader_options),
            "invocation": invocation,
        }
        digest = hashlib.sha256(
            json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        key = CacheKey(
            namespace="test-local-response-v1",
            model_payload_hash=model_payload_hash,
            feature_hash=digest,
        )
        self.keys.append(key)
        return key


def _request(
    *,
    model_name: str = "demo",
    model_source_kind: ModelSourceKind = ModelSourceKind.LOCAL,
    loader_family: LoaderFamily = LoaderFamily.ONNX,
    model_artifact: ModelArtifact | None = None,
    invocation: dict[str, object] | None = None,
) -> LocalResponseRequest:
    return LocalResponseRequest(
        model_name=model_name,
        model_source_kind=model_source_kind,
        model_payload={"revision": 1, "nested": ["value", {"enabled": True}]},
        features={"format": "text"},
        model_artifact=(
            ModelArtifact(
                loader_family=loader_family,
                artifact_path="model.onnx",
                loader_options={},
            )
            if model_artifact is None
            else model_artifact
        ),
        invocation={"prompt": "hello"} if invocation is None else invocation,
    )


def _gateway(
    *,
    events: list[str],
    registry: _RecordingRegistry,
    cache: _RecordingCache,
    deriver: _RecordingKeyDeriver | None = None,
    executor_error: BaseException | None = None,
    converter_error: BaseException | None = None,
) -> LocalResponseGateway:
    cache_key_deriver = deriver or _RecordingKeyDeriver(events)

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
        cache_key_deriver=cache_key_deriver,
        convert_onnx_result=convert_onnx_result,
        executor=executor,
    )


def _cross_identity_gateway(
    *,
    events: list[str],
    registry: _RecordingRegistry,
    cache: _KeyedRecordingCache,
    deriver: _RecordingKeyDeriver,
    executions: list[dict[str, object]],
) -> LocalResponseGateway:
    """Build a gateway whose result distinguishes each independent execution."""

    async def executor(artifact: ModelArtifact, invocation: dict[str, object]) -> list[object]:
        events.append("executor")
        assert artifact.loader_family is LoaderFamily.ONNX
        executions.append(invocation)
        return [len(executions)]

    def convert_onnx_result(result: list[object]) -> str:
        events.append("converter")
        return f"generated-{result[0]}"

    return LocalResponseGateway(
        registry=registry,
        response_cache=cache,
        cache_key_deriver=deriver,
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
    assert events == ["registry", "deriver", "lookup"]
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
    deriver = _RecordingKeyDeriver(events)
    request = _request()

    result = await _gateway(
        events=events,
        registry=registry,
        cache=cache,
        deriver=deriver,
    ).generate(
        request=request
    )

    assert result == "generated"
    assert events == ["registry", "deriver", "lookup", "executor", "converter", "remember"]
    assert deriver.calls == [
        {
            "model_name": request.model_name,
            "model_payload_hash": "fresh-payload-hash",
            "features": request.features,
            "model_artifact": request.model_artifact,
            "invocation": request.invocation,
        }
    ]
    assert cache.lookup_calls[0][0] is deriver.keys[0]
    assert cache.remember_calls[0][0] is deriver.keys[0]
    assert cache.remember_calls[0][1] == "generated"


@pytest.mark.asyncio
async def test_changed_invocation_derives_a_distinct_key_without_a_cross_hit() -> None:
    """Invocation identity prevents one request from reusing another response."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _KeyedRecordingCache(events)
    deriver = _RecordingKeyDeriver(events)
    executions: list[dict[str, object]] = []
    artifact = ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path="models/alpha.onnx",
        loader_options={},
    )
    gateway = _cross_identity_gateway(
        events=events,
        registry=registry,
        cache=cache,
        deriver=deriver,
        executions=executions,
    )
    first = _request(model_artifact=artifact, invocation={"prompt": "prompt-alpha"})
    second = _request(model_artifact=artifact, invocation={"prompt": "prompt-beta"})

    assert await gateway.generate(request=first) == "generated-1"
    assert await gateway.generate(request=second) == "generated-2"
    assert deriver.keys[0] != deriver.keys[1]
    assert len(executions) == 2
    assert len(cache.remember_calls) == 2
    assert cache.lookup_calls[0][0] is deriver.keys[0]
    assert cache.lookup_calls[1][0] is deriver.keys[1]
    assert deriver.calls[0]["model_artifact"] is artifact
    assert deriver.calls[1]["model_artifact"] is artifact
    for key in deriver.keys:
        assert all(
            raw not in field
            for raw in ("prompt-alpha", "prompt-beta", artifact.artifact_path)
            for field in (key.namespace, key.model_payload_hash, key.feature_hash)
        )


@pytest.mark.asyncio
async def test_changed_model_name_derives_a_distinct_key_without_a_cross_hit() -> None:
    """Model identity prevents a differently named request from reusing a response."""
    events: list[str] = []
    registry = _RecordingRegistry(events)
    cache = _KeyedRecordingCache(events)
    deriver = _RecordingKeyDeriver(events)
    executions: list[dict[str, object]] = []
    artifact = ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path="models/alpha.onnx",
        loader_options={},
    )
    gateway = _cross_identity_gateway(
        events=events,
        registry=registry,
        cache=cache,
        deriver=deriver,
        executions=executions,
    )
    first = _request(
        model_name="model-alpha",
        model_artifact=artifact,
        invocation={"prompt": "prompt-shared"},
    )
    second = _request(
        model_name="model-beta",
        model_artifact=artifact,
        invocation={"prompt": "prompt-shared"},
    )

    assert await gateway.generate(request=first) == "generated-1"
    assert await gateway.generate(request=second) == "generated-2"
    assert deriver.keys[0] != deriver.keys[1]
    assert len(executions) == 2
    assert len(cache.remember_calls) == 2
    assert deriver.calls[0]["model_name"] == "model-alpha"
    assert deriver.calls[1]["model_name"] == "model-beta"
    assert deriver.calls[0]["model_artifact"] is artifact
    assert deriver.calls[1]["model_artifact"] is artifact
    for key in deriver.keys:
        assert all(
            raw not in field
            for raw in ("model-alpha", "model-beta", artifact.artifact_path)
            for field in (key.namespace, key.model_payload_hash, key.feature_hash)
        )


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

    expected = ["registry", "deriver", "lookup"]
    if unexpected_on == "remember":
        expected.extend(["executor", "converter", "remember"])
    assert events == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_site", ["registry", "executor", "converter"])
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
    with pytest.raises(RuntimeError) as raised:
        await gateway.generate(request=_request())

    assert raised.value is failure
    assert cache.remember_calls == []


@pytest.mark.asyncio
async def test_deriver_failure_propagates_before_lookup_or_remember() -> None:
    """A failed identity derivation has no cache or execution side effect."""
    events: list[str] = []
    failure = RuntimeError("deriver")
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events)
    deriver = _RecordingKeyDeriver(events, error=failure)
    gateway = _gateway(events=events, registry=registry, cache=cache, deriver=deriver)

    with pytest.raises(RuntimeError) as raised:
        await gateway.generate(request=_request())

    assert raised.value is failure
    assert events == ["registry", "deriver"]
    assert cache.lookup_calls == []
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
    assert events == ["registry", "deriver", "lookup", "executor"]
    assert cache.remember_calls == []


@pytest.mark.asyncio
async def test_registry_suspension_keeps_cache_identity_and_execution_on_one_shallow_snapshot(
) -> None:
    """A top-level caller mutation cannot split the derived key from execution input."""
    events: list[str] = []
    registry = _PausingRegistry(events)
    cache = _RecordingCache(events)
    deriver = _RecordingKeyDeriver(events)
    executor_calls: list[tuple[ModelArtifact, dict[str, object]]] = []
    opaque_leaf = ["nested-leaf"]
    original_invocation: dict[str, object] = {"prompt": "A", "opaque_leaf": opaque_leaf}
    request = _request(invocation=original_invocation)

    async def executor(artifact: ModelArtifact, invocation: dict[str, object]) -> list[object]:
        events.append("executor")
        executor_calls.append((artifact, invocation))
        return [invocation["prompt"]]

    def convert_onnx_result(result: list[object]) -> str:
        events.append("converter")
        return str(result[0])

    gateway = LocalResponseGateway(
        registry=registry,
        response_cache=cache,
        cache_key_deriver=deriver,
        convert_onnx_result=convert_onnx_result,
        executor=executor,
    )

    generation = asyncio.create_task(gateway.generate(request=request))
    await registry.awaited.wait()

    assert events == ["registry"]
    assert deriver.calls == []
    assert cache.lookup_calls == []
    assert executor_calls == []

    original_invocation["prompt"] = "B"
    registry.resume.set()

    assert await generation == "A"
    snapshot = deriver.calls[0]["invocation"]
    assert snapshot == {"prompt": "A", "opaque_leaf": opaque_leaf}
    assert snapshot["opaque_leaf"] is opaque_leaf
    assert snapshot is executor_calls[0][1]
    assert snapshot is not original_invocation
    assert executor_calls[0][0] is request.model_artifact
    assert original_invocation == {"prompt": "B", "opaque_leaf": opaque_leaf}
    assert deriver.calls == [
        {
            "model_name": request.model_name,
            "model_payload_hash": "fresh-payload-hash",
            "features": request.features,
            "model_artifact": request.model_artifact,
            "invocation": snapshot,
        }
    ]
    assert cache.lookup_calls[0][0] is deriver.keys[0]
    assert cache.remember_calls[0][0] is deriver.keys[0]
    assert events == ["registry", "deriver", "lookup", "executor", "converter", "remember"]


@pytest.mark.asyncio
async def test_snapshot_materialization_failure_prevents_all_collaborator_observation() -> None:
    """The unchanged materialization error occurs before the first async boundary."""
    events: list[str] = []
    failure = RuntimeError("snapshot materialization")
    registry = _RecordingRegistry(events)
    cache = _RecordingCache(events)
    deriver = _RecordingKeyDeriver(events)
    gateway = _gateway(events=events, registry=registry, cache=cache, deriver=deriver)

    with pytest.raises(RuntimeError) as raised:
        await gateway.generate(request=_request(invocation=_ExplodingInvocation(failure)))

    assert raised.value is failure
    assert events == []
    assert registry.calls == []
    assert deriver.calls == []
    assert cache.lookup_calls == []
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
        cache_key_deriver=_RecordingKeyDeriver(events),
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
        cache_key_deriver=_RecordingKeyDeriver(events),
        convert_onnx_result=lambda result: (events.append("converter"), "generated")[1],
    )

    result = await gateway.generate(request=_request())

    assert result == "generated"
    assert events == [
        "composition.create",
        "registry",
        "deriver",
        "lookup",
        "composition.execute",
        "converter",
        "remember",
    ]
