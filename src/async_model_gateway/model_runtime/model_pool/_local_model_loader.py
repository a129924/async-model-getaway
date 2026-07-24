"""Internal generic loaders for provider-native runtimes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from async_model_gateway.model_runtime.model_artifact import ModelArtifact

from ._onnx_runtime_loader import load_onnx_runtime

RuntimeT = TypeVar("RuntimeT")


class ModelLoader(ABC, Generic[RuntimeT]):
    """Load one provider-native runtime from a model artifact."""

    @abstractmethod
    async def load(self, artifact: ModelArtifact) -> RuntimeT:
        """Return the raw provider runtime for an artifact."""


class _OnnxModelLoader(ModelLoader[object]):  # pyright: ignore[reportUnusedClass]
    """Load the raw ONNX provider session."""

    async def load(self, artifact: ModelArtifact) -> object:
        """Create the CPU-only provider session for an ONNX artifact."""
        return await load_onnx_runtime(artifact)
