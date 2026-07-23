"""Private ONNX Runtime session acquisition for local model artifacts."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from async_model_gateway.model_runtime.model_artifact import ModelArtifact


_InferenceSessionConstructor = Callable[..., object]
_InferenceSessionImporter = Callable[[], _InferenceSessionConstructor]


def _import_inference_session_constructor() -> _InferenceSessionConstructor:
    """Lazily import the optional ONNX Runtime session constructor."""
    # onnxruntime does not ship type stubs; keep this optional import lazy.
    from onnxruntime import InferenceSession  # pyright: ignore[reportMissingTypeStubs]

    return InferenceSession


async def load_onnx_runtime(
    artifact: ModelArtifact,
    *,
    inference_session_importer: _InferenceSessionImporter = _import_inference_session_constructor,
) -> object:
    """Create an opaque CPU-only ONNX Runtime session for an artifact."""
    if artifact.loader_options:
        msg = "ONNX loader_options are not supported"
        raise ValueError(msg)

    try:
        inference_session = inference_session_importer()
    except ModuleNotFoundError as error:
        if error.name == "onnxruntime":
            msg = "ONNX runtime support requires installing async-model-gateway[onnx]"
            raise RuntimeError(msg) from error
        raise

    return await asyncio.to_thread(
        inference_session,
        artifact.artifact_path,
        providers=["CPUExecutionProvider"],
    )
