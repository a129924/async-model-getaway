"""Strict static contract checks for the minimal ModelExecution boundary."""

from __future__ import annotations

from typing_extensions import assert_type

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_execution import ModelExecution
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel


class _FakeRuntime:
    """Represent one concrete provider runtime type."""


class _FakeInvocation:
    """Represent one concrete invocation type."""


class _FakeResult:
    """Represent one concrete result type."""


class _TestLoadedRuntimeModel(LoadedRuntimeModel[_FakeRuntime]):
    """Supply a typed test-local provider handle to ModelExecution."""

    def __init__(self, runtime: _FakeRuntime) -> None:
        self._runtime = runtime

    @property
    def loader_family(self) -> LoaderFamily:
        return LoaderFamily.TORCH

    def _provider_runtime(self) -> _FakeRuntime:
        return self._runtime


def _as_loaded_runtime_model(
    model: LoadedRuntimeModel[_FakeRuntime],
) -> LoadedRuntimeModel[_FakeRuntime]:
    """Preserve the public opaque-handle type for the execution fixture."""
    return model


async def _invoke(
    runtime: _FakeRuntime,
    invocation: _FakeInvocation,
) -> _FakeResult:
    assert_type(runtime, _FakeRuntime)
    assert_type(invocation, _FakeInvocation)
    return _FakeResult()


async def check_execution_preserves_all_concrete_types() -> None:
    model: LoadedRuntimeModel[_FakeRuntime] = _as_loaded_runtime_model(
        _TestLoadedRuntimeModel(_FakeRuntime())
    )
    execution = ModelExecution[_FakeRuntime, _FakeInvocation, _FakeResult](invoke=_invoke)

    assert_type(model, LoadedRuntimeModel[_FakeRuntime])
    assert_type(execution, ModelExecution[_FakeRuntime, _FakeInvocation, _FakeResult])
    result = await execution.execute(model, _FakeInvocation())
    assert_type(result, _FakeResult)


async def check_model_pool_acquisition_remains_erased() -> None:
    artifact = ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path="models/runtime-model.bin",
        loader_options={},
    )

    pool_model = await ModelPool().acquire(artifact)

    assert_type(pool_model, LoadedRuntimeModel[object])
