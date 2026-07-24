"""Internal execution lifecycle for loaded provider runtimes."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    LoadedRuntimeModel,
)
from async_model_gateway.model_runtime.runtime_model._onnx_runtime import (
    _OnnxRuntime,  # pyright: ignore[reportPrivateUsage]
)

RuntimeT = TypeVar("RuntimeT")
InvocationT = TypeVar("InvocationT")
ResultT = TypeVar("ResultT")


class ModelExecutor(ABC, Generic[RuntimeT, InvocationT, ResultT]):
    """Run one invocation while owning the loaded runtime's execution gate."""

    async def execute(
        self,
        model: LoadedRuntimeModel[RuntimeT],
        invocation: InvocationT,
    ) -> ResultT:
        """Acquire the execution gate, mark use, and await one invocation."""
        execution_gate: asyncio.Semaphore = model.execution_gate
        async with execution_gate:
            model.mark_used()
            return await self._invoke(model.runtime, invocation)

    @abstractmethod
    async def _invoke(self, runtime: RuntimeT, invocation: InvocationT) -> ResultT:
        """Invoke one concrete provider runtime."""


class _OnnxModelExecutor(  # pyright: ignore[reportUnusedClass]
    ModelExecutor[_OnnxRuntime, object, object]
):
    """Fail closed until a real ONNX invocation boundary is implemented."""

    async def _invoke(self, runtime: _OnnxRuntime, invocation: object) -> object:
        """Reject unsupported ONNX invocation after lifecycle handling."""
        _ = runtime, invocation
        raise NotImplementedError
