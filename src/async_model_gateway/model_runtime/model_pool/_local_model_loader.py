"""Private explicit routing for local model-artifact acquisition."""

from __future__ import annotations

from typing_extensions import assert_never

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel

from ._onnx_runtime_loader import load_onnx_runtime


class _LocalLoadedRuntimeModel(LoadedRuntimeModel[object]):
    """Keep a locally acquired provider runtime behind the opaque handle contract."""

    __slots__ = ("_loader_family", "_provider_model")

    def __init__(
        self,
        *,
        loader_family: LoaderFamily,
        provider_model: object,
    ) -> None:
        """Store explicit provenance and the erased provider runtime."""
        self._loader_family = loader_family
        self._provider_model = provider_model

    @property
    def loader_family(self) -> LoaderFamily:
        """Return the explicit loader family that produced this runtime model."""
        return self._loader_family

    def _provider_runtime(self) -> object:
        """Return the provider runtime through the internal execution handoff."""
        return self._provider_model


class LocalModelLoader:
    """Dispatch a shared model artifact through its explicit loader family."""

    async def load(self, artifact: ModelArtifact) -> LoadedRuntimeModel[object]:
        """Await the route selected by the artifact's explicit loader family."""
        match artifact.loader_family:
            case LoaderFamily.PICKLE:
                return await self._load_pickle(artifact)
            case LoaderFamily.TORCH:
                return await self._load_torch(artifact)
            case LoaderFamily.ONNX:
                return await self._load_onnx(artifact)
            case _:
                assert_never(artifact.loader_family)

    async def _load_pickle(self, _artifact: ModelArtifact) -> LoadedRuntimeModel[object]:
        """Fail closed until pickle artifact I/O is implemented in a later topic."""
        raise NotImplementedError

    async def _load_torch(self, _artifact: ModelArtifact) -> LoadedRuntimeModel[object]:
        """Fail closed until torch artifact I/O is implemented in a later topic."""
        raise NotImplementedError

    async def _load_onnx(self, artifact: ModelArtifact) -> LoadedRuntimeModel[object]:
        """Acquire an ONNX runtime session through the private provider helper."""
        session = await load_onnx_runtime(artifact)
        return _LocalLoadedRuntimeModel(
            loader_family=LoaderFamily.ONNX,
            provider_model=session,
        )
