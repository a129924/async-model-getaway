"""Strict witness for the unchanged private ONNX runtime protocol boundary."""

from __future__ import annotations

from async_model_gateway.model_runtime.model_artifact import ModelArtifact
from async_model_gateway.model_runtime.model_pool.loaders._onnx_model_loader import (
    _OnnxModelLoader,
)
from async_model_gateway.model_runtime.runtime_model._onnx_runtime import _OnnxRuntime


def _accept_onnx_runtime(runtime: _OnnxRuntime) -> None:
    """Accept only the existing minimum provider runtime protocol."""
    _ = runtime


async def check_loader_result_satisfies_minimum_protocol(artifact: ModelArtifact) -> None:
    """Keep the Loader return type at the private protocol boundary."""
    runtime = await _OnnxModelLoader().load(artifact)

    _accept_onnx_runtime(runtime)
