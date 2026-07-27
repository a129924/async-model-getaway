"""Private CPU-only ONNX Runtime acquisition."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import cast

from typing_extensions import override

from async_model_gateway.model_runtime.model_artifact import ModelArtifact
from async_model_gateway.model_runtime.runtime_model._onnx_runtime import (
    OnnxRuntimeSession,
)

from ._model_loader import ModelLoader

_InferenceSessionConstructor = Callable[..., object]
_InferenceSessionImporter = Callable[[], _InferenceSessionConstructor]


def _import_inference_session_constructor() -> _InferenceSessionConstructor:
    """Lazily import the optional ONNX Runtime session constructor."""
    # onnxruntime has no stubs; this optional provider import is isolated at its boundary.
    from onnxruntime import InferenceSession  # pyright: ignore[reportMissingTypeStubs]

    return InferenceSession


async def load_onnx_runtime(
    artifact: ModelArtifact,
    *,
    inference_session_importer: _InferenceSessionImporter = _import_inference_session_constructor,
) -> OnnxRuntimeSession:
    """Create a CPU-only ONNX Runtime session for an artifact."""
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

    # onnxruntime has no stubs: this is the sole provider-boundary session refinement.
    return cast(
        OnnxRuntimeSession,
        await asyncio.to_thread(
            inference_session,
            artifact.artifact_path,
            providers=["CPUExecutionProvider"],
        ),
    )


# This loader is instantiated only by the closed runtime-binding factory.
class _OnnxModelLoader(ModelLoader[OnnxRuntimeSession]):  # pyright: ignore[reportUnusedClass]
    """Load the raw ONNX provider session."""

    @override
    async def load(self, artifact: ModelArtifact) -> OnnxRuntimeSession:
        """Create the CPU-only provider session for an ONNX artifact."""
        return await load_onnx_runtime(artifact)
