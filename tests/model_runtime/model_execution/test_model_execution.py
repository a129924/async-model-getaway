"""RED coverage for internal executor lifecycle behavior."""

from __future__ import annotations

import asyncio
from datetime import timezone

import pytest

from async_model_gateway.model_runtime.model_execution.execution import (
    ModelExecutor,
    _OnnxModelExecutor,
)
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    LoadedRuntimeModel,
)


class _Runtime:
    """Represent one provider-runtime identity."""


class _Invocation:
    """Represent one invocation identity."""


class _Result:
    """Represent one result identity."""


class _RecordingExecutor(ModelExecutor[_Runtime, _Invocation, _Result]):
    """Record the concrete invocation supplied by the base lifecycle."""

    def __init__(self, result: _Result) -> None:
        self.result = result
        self.calls: list[tuple[_Runtime, _Invocation]] = []

    async def _invoke(self, runtime: _Runtime, invocation: _Invocation) -> _Result:
        self.calls.append((runtime, invocation))
        return self.result


class _FailureExecutor(ModelExecutor[_Runtime, _Invocation, _Result]):
    """Raise exactly the caller-owned error after gate acquisition."""

    def __init__(self, error: BaseException) -> None:
        self.error = error

    async def _invoke(self, _runtime: _Runtime, _invocation: _Invocation) -> _Result:
        raise self.error


@pytest.mark.asyncio
async def test_executor_marks_used_after_gate_acquisition_and_preserves_result_identity() -> None:
    runtime = _Runtime()
    invocation = _Invocation()
    result = _Result()
    model = LoadedRuntimeModel(runtime=runtime, execution_gate=asyncio.Semaphore(1))
    executor = _RecordingExecutor(result)
    actual = await executor.execute(model, invocation)

    assert actual is result
    assert executor.calls == [(runtime, invocation)]
    assert model.last_used_at is not None
    assert model.last_used_at.tzinfo is timezone.utc
    assert model.execution_gate.locked() is False


@pytest.mark.asyncio
async def test_executor_does_not_mark_queued_request_before_its_gate_is_acquired() -> None:
    gate = asyncio.Semaphore(1)
    await gate.acquire()
    model = LoadedRuntimeModel(runtime=_Runtime(), execution_gate=gate)
    executor = _RecordingExecutor(_Result())
    task = asyncio.create_task(executor.execute(model, _Invocation()))

    await asyncio.sleep(0)

    assert model.last_used_at is None
    gate.release()
    await task


@pytest.mark.asyncio
async def test_executor_preserves_failure_and_cancellation_identity_and_releases_gate() -> None:
    model = LoadedRuntimeModel(runtime=_Runtime(), execution_gate=asyncio.Semaphore(1))
    failure = RuntimeError("sentinel failure")

    with pytest.raises(RuntimeError) as caught_failure:
        await _FailureExecutor(failure).execute(model, _Invocation())

    assert caught_failure.value is failure
    assert model.last_used_at is not None
    assert model.execution_gate.locked() is False

    cancellation = asyncio.CancelledError("sentinel cancellation")
    with pytest.raises(asyncio.CancelledError) as caught_cancellation:
        await _FailureExecutor(cancellation).execute(model, _Invocation())

    assert caught_cancellation.value is cancellation
    assert model.execution_gate.locked() is False


@pytest.mark.asyncio
async def test_onnx_executor_marks_used_then_fails_closed_and_releases_gate() -> None:
    gate = asyncio.Semaphore(1)
    await gate.acquire()
    model = LoadedRuntimeModel(runtime=object(), execution_gate=gate)
    task = asyncio.create_task(_OnnxModelExecutor().execute(model, object()))

    await asyncio.sleep(0)

    assert model.last_used_at is None
    gate.release()

    with pytest.raises(NotImplementedError):
        await task

    assert model.last_used_at is not None
    assert model.last_used_at.tzinfo is timezone.utc
    assert model.execution_gate.locked() is False
