"""Strict static checks for internal runtime binding generic continuity."""

from __future__ import annotations

import asyncio

from typing_extensions import assert_type

from async_model_gateway.model_runtime.model_artifact import ModelArtifact
from async_model_gateway.model_runtime.model_execution.execution import ModelExecutor
from async_model_gateway.model_runtime.model_pool._local_model_loader import ModelLoader
from async_model_gateway.model_runtime.model_pool._runtime_binding import RuntimeBinding
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    LoadedRuntimeModel,
)


class _Runtime:
    """Represent one concrete provider runtime type."""


class _Invocation:
    """Represent one concrete invocation type."""


class _Result:
    """Represent one concrete result type."""


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


async def check_loaded_resource_and_executor_result_stay_precise(
    artifact: ModelArtifact,
) -> None:
    runtime = await _Loader().load(artifact)
    model = LoadedRuntimeModel(runtime=runtime, execution_gate=asyncio.Semaphore(1))
    result = await _Executor().execute(model, _Invocation())

    assert_type(model, LoadedRuntimeModel[_Runtime])
    assert_type(result, _Result)
