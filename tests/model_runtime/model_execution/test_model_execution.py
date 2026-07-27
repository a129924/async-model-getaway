"""RED coverage for internal executor lifecycle behavior."""

from __future__ import annotations

import asyncio
import threading
from datetime import timezone

import pytest

from async_model_gateway.model_runtime.model_execution.execution import (
    ModelExecutor,
)
from async_model_gateway.model_runtime.model_execution._onnx_model_executor import (
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


class _RecordingOnnxRuntime:
    """Record the provider call made by the private ONNX executor."""

    def __init__(self) -> None:
        self.calls: list[tuple[list[str] | None, dict[str, object], object | None]] = []
        self.result: list[object] = [object()]

    def get_providers(self) -> list[str]:
        return ["CPUExecutionProvider"]

    def run(
        self,
        output_names: list[str] | None,
        input_feed: dict[str, object],
        run_options: object | None,
    ) -> list[object]:
        self.calls.append((output_names, input_feed, run_options))
        return self.result


class _FailingOnnxRuntime:
    """Preserve the provider-owned failure identity."""

    def __init__(self, error: RuntimeError) -> None:
        self.error = error

    def get_providers(self) -> list[str]:
        return ["CPUExecutionProvider"]

    def run(
        self,
        _output_names: list[str] | None,
        _input_feed: dict[str, object],
        _run_options: object | None,
    ) -> list[object]:
        raise self.error


class _BlockingOnnxRuntime:
    """Keep provider work blocked until the test releases it."""

    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()

    def get_providers(self) -> list[str]:
        return ["CPUExecutionProvider"]

    def run(
        self,
        _output_names: list[str] | None,
        _input_feed: dict[str, object],
        _run_options: object | None,
    ) -> list[object]:
        self.started.set()
        self.release.wait(timeout=2)
        return []


class _InputName(str):
    """Represent a valid provider input-name subtype."""


@pytest.mark.asyncio
async def test_onnx_executor_rejects_invalid_invocations_before_provider_work() -> None:
    runtime = _RecordingOnnxRuntime()
    model = LoadedRuntimeModel(runtime=runtime, execution_gate=asyncio.Semaphore(1))
    executor = _OnnxModelExecutor()

    with pytest.raises(TypeError):
        await executor.execute(model, object())
    with pytest.raises(TypeError):
        await executor.execute(model, ["not a mapping"])
    with pytest.raises(TypeError):
        await executor.execute(model, {1: object()})

    assert runtime.calls == []
    assert model.execution_gate.locked() is False


@pytest.mark.asyncio
async def test_onnx_executor_preserves_provider_result_and_call_shape() -> None:
    runtime = _RecordingOnnxRuntime()
    invocation = {"input": object()}
    model = LoadedRuntimeModel(runtime=runtime, execution_gate=asyncio.Semaphore(1))

    result = await _OnnxModelExecutor().execute(model, invocation)

    assert result is runtime.result
    assert runtime.calls == [(None, invocation, None)]


@pytest.mark.asyncio
async def test_onnx_executor_accepts_string_subclasses_as_input_names() -> None:
    runtime = _RecordingOnnxRuntime()
    invocation = {_InputName("input"): object()}
    model = LoadedRuntimeModel(runtime=runtime, execution_gate=asyncio.Semaphore(1))

    result = await _OnnxModelExecutor().execute(model, invocation)

    assert result is runtime.result
    assert runtime.calls == [(None, invocation, None)]


@pytest.mark.asyncio
async def test_onnx_executor_preserves_provider_failure_identity() -> None:
    failure = RuntimeError("provider failure")
    model = LoadedRuntimeModel(
        runtime=_FailingOnnxRuntime(failure),
        execution_gate=asyncio.Semaphore(1),
    )

    with pytest.raises(RuntimeError) as caught:
        await _OnnxModelExecutor().execute(model, {"input": object()})

    assert caught.value is failure


@pytest.mark.asyncio
async def test_onnx_executor_propagates_cancellation_without_waiting_for_worker() -> None:
    runtime = _BlockingOnnxRuntime()
    model = LoadedRuntimeModel(runtime=runtime, execution_gate=asyncio.Semaphore(1))
    execution = asyncio.create_task(_OnnxModelExecutor().execute(model, {"input": object()}))

    try:
        assert await asyncio.to_thread(runtime.started.wait, 1)
        execution.cancel()
        with pytest.raises(asyncio.CancelledError):
            await execution

        assert model.execution_gate.locked() is False
    finally:
        runtime.release.set()
