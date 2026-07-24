"""Internal uncached acquisition for loaded provider runtimes."""

from __future__ import annotations

import asyncio
from typing import TypeGuard, TypeVar

from async_model_gateway.model_runtime.model_artifact import ModelArtifact
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    LoadedRuntimeModel,
)

from .loaders._model_loader import ModelLoader

RuntimeT = TypeVar("RuntimeT")


def _is_model_artifact(value: object) -> TypeGuard[ModelArtifact]:
    """Return whether an acquisition input is a model artifact."""
    return isinstance(value, ModelArtifact)


class ModelPool:
    """Create a fresh loaded resource from an injected loader."""

    async def acquire(
        self,
        artifact: ModelArtifact,
        *,
        loader: ModelLoader[RuntimeT],
        max_concurrency: int,
    ) -> LoadedRuntimeModel[RuntimeT]:
        """Load a raw runtime and wrap it with a per-acquisition execution gate."""
        if not _is_model_artifact(artifact):
            msg = "artifact must be a ModelArtifact"
            raise TypeError(msg)

        runtime: RuntimeT = await loader.load(artifact)
        return LoadedRuntimeModel(
            runtime=runtime,
            execution_gate=asyncio.Semaphore(max_concurrency),
        )
