"""Public ModelPool owner for local runtime-model acquisition."""

from __future__ import annotations

from typing import TypeGuard

from async_model_gateway.model_runtime.model_artifact import ModelArtifact

from ._local_model_loader import LocalModelLoader


def _create_local_model_loader() -> LocalModelLoader:
    """Create the private local loader retained by one ModelPool instance."""
    return LocalModelLoader()


def _is_model_artifact(value: object) -> TypeGuard[ModelArtifact]:
    """Return whether a public acquisition input is a model artifact."""
    return isinstance(value, ModelArtifact)


class ModelPool:
    """Provide the minimal public local runtime-model acquisition boundary."""

    def __init__(self) -> None:
        """Create and retain this pool's private local loader."""
        self._local_model_loader = _create_local_model_loader()

    async def acquire(self, artifact: ModelArtifact) -> object:
        """Acquire a runtime model through the retained private local loader."""
        if not _is_model_artifact(artifact):
            msg = "artifact must be a ModelArtifact"
            raise TypeError(msg)

        return await self._local_model_loader.load(artifact)
