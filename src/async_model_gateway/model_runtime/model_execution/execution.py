"""Minimal typed execution boundary for loaded runtime models."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel

RuntimeT = TypeVar("RuntimeT")
InvocationT = TypeVar("InvocationT")
ResultT = TypeVar("ResultT")


class ModelExecution(Generic[RuntimeT, InvocationT, ResultT]):
    """Invoke one loaded provider runtime through an injected async callable."""

    def __init__(
        self,
        *,
        invoke: Callable[[RuntimeT, InvocationT], Awaitable[ResultT]],
    ) -> None:
        """Store the caller-provided async invoker."""
        self._invoke = invoke

    async def execute(
        self,
        model: LoadedRuntimeModel[RuntimeT],
        invocation: InvocationT,
    ) -> ResultT:
        runtime = model._provider_runtime()  # pyright: ignore[reportPrivateUsage]
        return await self._invoke(runtime, invocation)
