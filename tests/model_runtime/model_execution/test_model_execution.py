"""RED coverage for the minimal ModelExecution invocation boundary."""

from __future__ import annotations

import asyncio

import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily
from async_model_gateway.model_runtime.model_execution import ModelExecution
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel


class _FakeRuntime:
    """Represent a concrete provider runtime identity."""


class _FakeInvocation:
    """Represent a concrete invocation identity."""


class _FakeResult:
    """Represent a concrete invocation result identity."""


class _FakeLoadedRuntimeModel(LoadedRuntimeModel[_FakeRuntime]):
    """Expose one typed provider runtime through the existing private handoff."""

    def __init__(self, runtime: _FakeRuntime) -> None:
        self._runtime = runtime
        self.handoff_count = 0

    @property
    def loader_family(self) -> LoaderFamily:
        return LoaderFamily.TORCH

    def _provider_runtime(self) -> _FakeRuntime:
        self.handoff_count += 1
        return self._runtime


class _RecordingInvoker:
    """Record only calls whose returned coroutine is actually awaited."""

    def __init__(self, result: _FakeResult) -> None:
        self._result = result
        self.awaited_calls: list[tuple[_FakeRuntime, _FakeInvocation]] = []

    async def __call__(
        self,
        runtime: _FakeRuntime,
        invocation: _FakeInvocation,
    ) -> _FakeResult:
        self.awaited_calls.append((runtime, invocation))
        return self._result


class _RaisingInvoker:
    """Raise one caller-owned failure from the awaited invocation."""

    def __init__(self, error: BaseException) -> None:
        self._error = error
        self.await_count = 0

    async def __call__(
        self,
        _runtime: _FakeRuntime,
        _invocation: _FakeInvocation,
    ) -> _FakeResult:
        self.await_count += 1
        raise self._error


@pytest.mark.asyncio
async def test_execute_direct_awaits_once_and_preserves_all_identities() -> None:
    runtime = _FakeRuntime()
    invocation = _FakeInvocation()
    result = _FakeResult()
    model = _FakeLoadedRuntimeModel(runtime)
    invoker = _RecordingInvoker(result)
    execution = ModelExecution[_FakeRuntime, _FakeInvocation, _FakeResult](invoke=invoker)

    actual = await execution.execute(model, invocation)

    assert model.handoff_count == 1
    assert invoker.awaited_calls == [(runtime, invocation)]
    assert invoker.awaited_calls[0][0] is runtime
    assert invoker.awaited_calls[0][1] is invocation
    assert actual is result


@pytest.mark.asyncio
async def test_execute_propagates_the_same_invoker_exception_once() -> None:
    error = RuntimeError("sentinel invocation failure")
    invoker = _RaisingInvoker(error)
    execution = ModelExecution[_FakeRuntime, _FakeInvocation, _FakeResult](invoke=invoker)

    with pytest.raises(RuntimeError) as caught:
        await execution.execute(_FakeLoadedRuntimeModel(_FakeRuntime()), _FakeInvocation())

    assert caught.value is error
    assert invoker.await_count == 1


@pytest.mark.asyncio
async def test_execute_propagates_the_same_cancelled_error_once() -> None:
    cancellation = asyncio.CancelledError("sentinel cancellation")
    invoker = _RaisingInvoker(cancellation)
    execution = ModelExecution[_FakeRuntime, _FakeInvocation, _FakeResult](invoke=invoker)

    with pytest.raises(asyncio.CancelledError) as caught:
        await execution.execute(_FakeLoadedRuntimeModel(_FakeRuntime()), _FakeInvocation())

    assert caught.value is cancellation
    assert invoker.await_count == 1
