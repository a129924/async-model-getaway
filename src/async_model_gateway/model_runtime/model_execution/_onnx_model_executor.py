"""Private ONNX provider invocation."""

from __future__ import annotations

import asyncio
from typing import TypeGuard

from async_model_gateway.model_runtime.runtime_model._onnx_runtime import (
    OnnxRuntimeSession,
)

from .execution import ModelExecutor


def _run_session(
    runtime: OnnxRuntimeSession,
    invocation: dict[str, object],
) -> list[object]:
    """Make the fixed provider call from a worker thread."""
    return runtime.run(None, invocation, None)


def _is_dict_invocation(value: object) -> TypeGuard[dict[str, object]]:
    """Narrow an untyped runtime value before validating its key contract."""
    return isinstance(value, dict)


def _validate_invocation(invocation: object) -> None:
    """Reject runtime-invalid container shapes before provider work."""
    if not _is_dict_invocation(invocation):
        msg = "ONNX invocation must be a dict with string keys"
        raise TypeError(msg)
    for key in invocation:
        if type(key) is not str:
            msg = "ONNX invocation must be a dict with string keys"
            raise TypeError(msg)


class _OnnxModelExecutor(ModelExecutor[OnnxRuntimeSession, dict[str, object], list[object]]):
    """Invoke one ONNX session without exposing provider details."""

    async def _invoke(
        self,
        runtime: OnnxRuntimeSession,
        invocation: dict[str, object],
    ) -> list[object]:
        """Run synchronous provider work without changing cancellation ownership."""
        _validate_invocation(invocation)
        return await asyncio.to_thread(_run_session, runtime, invocation)


def create_onnx_model_executor() -> ModelExecutor[
    OnnxRuntimeSession, dict[str, object], list[object]
]:
    """Create the executor used by the closed ONNX runtime binding."""
    return _OnnxModelExecutor()
