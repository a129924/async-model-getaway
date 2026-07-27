"""Strict witness for the internal ONNX invocation pairing."""

from __future__ import annotations

from typing_extensions import assert_type

from async_model_gateway.model_runtime.model_execution.execution import ModelExecutor
from async_model_gateway.model_runtime.model_pool._runtime_binding import RuntimeBinding
from async_model_gateway.model_runtime.model_pool.loaders._model_loader import ModelLoader
from async_model_gateway.model_runtime.runtime_model._onnx_runtime import (
    OnnxRuntimeSession,
)


class _FakeSession:
    """Satisfy the frozen internal ONNX session Protocol."""

    def get_providers(self) -> list[str]:
        return ["CPUExecutionProvider"]

    def run(
        self,
        output_names: list[str] | None,
        input_feed: dict[str, object],
        run_options: object | None,
    ) -> list[object]:
        _ = output_names, input_feed, run_options
        return []


def check_onnx_runtime_binding_stays_precise(
    loader: ModelLoader[OnnxRuntimeSession],
    executor: ModelExecutor[OnnxRuntimeSession, dict[str, object], list[object]],
) -> None:
    """Prove the loader, executor and binding share one exact chain."""
    binding = RuntimeBinding[OnnxRuntimeSession, dict[str, object], list[object]](
        loader=loader,
        executor=executor,
        max_concurrency=1,
    )

    _accept_onnx_runtime(_FakeSession())
    assert_type(binding.loader, ModelLoader[OnnxRuntimeSession])
    assert_type(
        binding.executor,
        ModelExecutor[OnnxRuntimeSession, dict[str, object], list[object]],
    )


def _accept_onnx_runtime(runtime: OnnxRuntimeSession) -> None:
    """Require structural compatibility with the internal session Protocol."""
    _ = runtime
