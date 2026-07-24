"""Strict static checks for internal runtime binding generic continuity."""

from __future__ import annotations

import asyncio

from typing_extensions import assert_type

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_execution.execution import (
    ModelExecutor,
    _OnnxModelExecutor,  # pyright: ignore[reportPrivateUsage]
)
from async_model_gateway.model_runtime.model_pool.loaders._model_loader import ModelLoader
from async_model_gateway.model_runtime.model_pool.loaders._onnx_model_loader import (
    _OnnxModelLoader,  # pyright: ignore[reportPrivateUsage]
)
from async_model_gateway.model_runtime.model_pool._runtime_binding import (
    RuntimeBinding,
    _RuntimeBindingResolver,  # pyright: ignore[reportPrivateUsage]
)
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    LoadedRuntimeModel,
)
from async_model_gateway.model_runtime.runtime_model._onnx_runtime import (
    _OnnxRuntime,  # pyright: ignore[reportPrivateUsage]
)


class _Runtime:
    """Represent one concrete provider runtime type."""


class _Invocation:
    """Represent one concrete invocation type."""


class _Result:
    """Represent one concrete result type."""


class _FakeOnnxRuntime:
    """Satisfy the minimum private ONNX runtime protocol."""

    def get_providers(self) -> list[str]:
        return ["CPUExecutionProvider"]


def _accept_onnx_runtime(runtime: _OnnxRuntime) -> None:
    """Require the private provider runtime protocol at this type boundary."""
    _ = runtime


class _Loader(ModelLoader[_Runtime]):
    """Return the same concrete runtime type declared by the binding."""

    async def load(self, artifact: ModelArtifact) -> _Runtime:
        return _Runtime()


class _Executor(ModelExecutor[_Runtime, _Invocation, _Result]):
    """Consume the same concrete runtime type declared by the binding."""

    async def _invoke(self, runtime: _Runtime, invocation: _Invocation) -> _Result:
        assert_type(runtime, _Runtime)
        assert_type(invocation, _Invocation)
        return _Result()


def check_binding_preserves_loader_executor_runtime_pairing() -> None:
    loader = _Loader()
    executor = _Executor()
    binding = RuntimeBinding[_Runtime, _Invocation, _Result](
        loader=loader,
        executor=executor,
        max_concurrency=1,
    )

    assert_type(binding.loader, ModelLoader[_Runtime])
    assert_type(binding.executor, ModelExecutor[_Runtime, _Invocation, _Result])


def check_production_onnx_pairing_remains_precise_until_resolver_erasure() -> None:
    """Keep the ONNX loader and executor on the shared runtime protocol."""
    loader: ModelLoader[_OnnxRuntime] = _OnnxModelLoader()
    executor: ModelExecutor[_OnnxRuntime, object, object] = _OnnxModelExecutor()
    binding = RuntimeBinding[_OnnxRuntime, object, object](
        loader=loader,
        executor=executor,
        max_concurrency=1,
    )
    resolver = _RuntimeBindingResolver()

    _accept_onnx_runtime(_FakeOnnxRuntime())
    assert_type(binding.loader, ModelLoader[_OnnxRuntime])
    assert_type(binding.executor, ModelExecutor[_OnnxRuntime, object, object])
    assert_type(resolver.resolve(LoaderFamily.ONNX), RuntimeBinding[object, object, object])


async def check_loaded_resource_and_executor_result_stay_precise(
    artifact: ModelArtifact,
) -> None:
    runtime = await _Loader().load(artifact)
    model = LoadedRuntimeModel(runtime=runtime, execution_gate=asyncio.Semaphore(1))
    result = await _Executor().execute(model, _Invocation())

    assert_type(model, LoadedRuntimeModel[_Runtime])
    assert_type(result, _Result)
