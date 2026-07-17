"""Private ONNX Runtime session acquisition for local model artifacts."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from async_model_gateway.model_runtime.model_artifact import ModelArtifact


def _get_inference_session_constructor() -> Callable[..., object]:
    """Lazily import the optional ONNX Runtime session constructor."""
    try:
        # onnxruntime does not ship type stubs; keep this optional import lazy.
        from onnxruntime import InferenceSession  # pyright: ignore[reportMissingTypeStubs]
    except ModuleNotFoundError as error:
        if error.name == "onnxruntime":
            msg = "ONNX runtime support requires installing async-model-gateway[onnx]"
            raise RuntimeError(msg) from error
        raise

    return InferenceSession


async def load_onnx_runtime(artifact: ModelArtifact) -> object:
    """Create an opaque CPU-only ONNX Runtime session for an artifact."""
    if artifact.loader_options:
        msg = "ONNX loader_options are not supported"
        raise ValueError(msg)

    inference_session = _get_inference_session_constructor()
    return await asyncio.to_thread(
        inference_session,
        artifact.artifact_path,
        providers=["CPUExecutionProvider"],
    )
