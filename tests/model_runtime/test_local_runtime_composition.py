"""RED architecture coverage for pre-acquire runtime binding continuity."""

from __future__ import annotations

import asyncio
import inspect

import pytest

from async_model_gateway.model_runtime._local_runtime_composition import (
    _LocalRuntimeComposition,
)
from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_execution.execution import ModelExecutor
from async_model_gateway.model_runtime.model_pool.loaders._model_loader import ModelLoader
from async_model_gateway.model_runtime.model_pool._runtime_binding import (
    RuntimeBinding,
    _RuntimeBindingResolver,
)
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    LoadedRuntimeModel,
)
import async_model_gateway.model_runtime._local_runtime_composition as composition_module
import async_model_gateway.model_runtime.model_pool._runtime_binding as binding_module


class _Runtime:
    """Represent a provider runtime for continuity assertions."""


class _Invocation:
    """Represent one invocation identity."""


class _Result:
    """Represent one result identity."""


class _Loader(ModelLoader[_Runtime]):
    def __init__(self, events: list[str], runtime: _Runtime) -> None:
        self.events = events
        self.runtime = runtime

    async def load(self, _artifact: ModelArtifact) -> _Runtime:
        self.events.append("load")
        return self.runtime


class _Executor(ModelExecutor[_Runtime, _Invocation, _Result]):
    def __init__(self, events: list[str], result: _Result) -> None:
        self.events = events
        self.result = result
        self.calls: list[tuple[LoadedRuntimeModel[_Runtime], _Invocation]] = []

    async def _invoke(self, _runtime: _Runtime, _invocation: _Invocation) -> _Result:
        return self.result

    async def execute(
        self,
        model: LoadedRuntimeModel[_Runtime],
        invocation: _Invocation,
    ) -> _Result:
        self.events.append("execute")
        self.calls.append((model, invocation))
        return await super().execute(model, invocation)


class _Resolver:
    def __init__(
        self,
        events: list[str],
        binding: RuntimeBinding[_Runtime, _Invocation, _Result],
    ) -> None:
        self.events = events
        self.binding = binding
        self.calls: list[LoaderFamily] = []

    def resolve(
        self,
        loader_family: LoaderFamily,
    ) -> RuntimeBinding[_Runtime, _Invocation, _Result]:
        self.events.append("resolve")
        self.calls.append(loader_family)
        return self.binding


class _Pool:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.calls: list[tuple[ModelArtifact, ModelLoader[_Runtime], int]] = []

    async def acquire(
        self,
        artifact: ModelArtifact,
        *,
        loader: ModelLoader[_Runtime],
        max_concurrency: int,
    ) -> LoadedRuntimeModel[_Runtime]:
        self.events.append("acquire")
        self.calls.append((artifact, loader, max_concurrency))
        runtime = await loader.load(artifact)
        return LoadedRuntimeModel(
            runtime=runtime,
            execution_gate=asyncio.Semaphore(max_concurrency),
        )


def _artifact(loader_family: LoaderFamily = LoaderFamily.ONNX) -> ModelArtifact:
    return ModelArtifact(
        loader_family=loader_family,
        artifact_path="models/bound.onnx",
        loader_options={},
    )


@pytest.mark.asyncio
async def test_composition_resolves_once_then_preserves_binding_through_pool_and_executor() -> None:
    events: list[str] = []
    runtime = _Runtime()
    invocation = _Invocation()
    result = _Result()
    loader = _Loader(events, runtime)
    executor = _Executor(events, result)
    binding = RuntimeBinding(loader=loader, executor=executor, max_concurrency=1)
    resolver = _Resolver(events, binding)
    pool = _Pool(events)
    composition = _LocalRuntimeComposition(model_pool=pool, binding_resolver=resolver)

    actual = await composition.execute(_artifact(), invocation)

    assert actual is result
    assert events == ["resolve", "acquire", "load", "execute"]
    assert resolver.calls == [LoaderFamily.ONNX]
    assert pool.calls == [(_artifact(), loader, 1)]
    assert executor.calls[0][0].runtime is runtime
    assert executor.calls[0][1] is invocation


@pytest.mark.asyncio
async def test_composition_does_not_acquire_when_pre_acquire_resolution_fails() -> None:
    class _UnsupportedResolver:
        def resolve(self, _loader_family: LoaderFamily) -> RuntimeBinding[object, object, object]:
            raise NotImplementedError

    class _NeverPool:
        async def acquire(self, **_kwargs: object) -> LoadedRuntimeModel[object]:
            raise AssertionError("pool must not run after resolution failure")

    composition = _LocalRuntimeComposition(
        model_pool=_NeverPool(),
        binding_resolver=_UnsupportedResolver(),
    )

    with pytest.raises(NotImplementedError):
        await composition.execute(_artifact(LoaderFamily.TORCH), object())


@pytest.mark.asyncio
@pytest.mark.parametrize("loader_family", [LoaderFamily.PICKLE, LoaderFamily.TORCH])
async def test_actual_binding_resolver_fails_closed_before_pool_can_load(
    loader_family: LoaderFamily,
) -> None:
    class _NeverPool:
        def __init__(self) -> None:
            self.acquire_calls = 0

        async def acquire(self, **_kwargs: object) -> LoadedRuntimeModel[object]:
            self.acquire_calls += 1
            raise AssertionError("pool must not acquire or load after resolution failure")

    pool = _NeverPool()
    composition = _LocalRuntimeComposition(
        model_pool=pool,
        binding_resolver=_RuntimeBindingResolver(),
    )

    with pytest.raises(NotImplementedError):
        await composition.execute(_artifact(loader_family), object())

    assert pool.acquire_calls == 0


def test_composition_keeps_the_private_onnx_session_pairing_exact() -> None:
    execute_signature = inspect.signature(_LocalRuntimeComposition.execute)
    composition_source = inspect.getsource(composition_module)
    binding_source = inspect.getsource(binding_module)

    assert execute_signature.parameters["invocation"].annotation == "dict[str, object]"
    assert execute_signature.return_annotation == "list[object]"
    assert "OnnxRuntimeSession" in composition_source
    assert "OnnxRuntimeSession" in binding_source
    assert "RuntimeBinding[object, object, object]" not in binding_source
    assert "cast(" not in binding_source
