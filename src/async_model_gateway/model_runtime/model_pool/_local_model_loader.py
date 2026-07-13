"""Private explicit routing for local model-artifact acquisition."""

from __future__ import annotations

from typing_extensions import assert_never

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact


class LocalModelLoader:
    """Dispatch a shared model artifact through its explicit loader family."""

    async def load(self, artifact: ModelArtifact) -> object:
        """Await the route selected by the artifact's explicit loader family."""
        # TODO: Replace `object` with the agreed runtime-model contract
        # (tentatively `LoadedRuntimeModel`) once that boundary is defined.
        match artifact.loader_family:
            case LoaderFamily.PICKLE:
                return await self._load_pickle(artifact)
            case LoaderFamily.TORCH:
                return await self._load_torch(artifact)
            case LoaderFamily.ONNX:
                return await self._load_onnx(artifact)
            case _:
                assert_never(artifact.loader_family)

    async def _load_pickle(self, _artifact: ModelArtifact) -> object:
        """Fail closed until pickle artifact I/O is implemented in a later topic."""
        raise NotImplementedError

    async def _load_torch(self, _artifact: ModelArtifact) -> object:
        """Fail closed until torch artifact I/O is implemented in a later topic."""
        raise NotImplementedError

    async def _load_onnx(self, _artifact: ModelArtifact) -> object:
        """Fail closed until ONNX artifact I/O is implemented in a later topic."""
        raise NotImplementedError
