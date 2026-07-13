"""Private explicit routing for local model-artifact acquisition."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import TypeGuard

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact

Route = Callable[[ModelArtifact], Awaitable[object]]


def _is_route_mapping(value: object) -> TypeGuard[Mapping[LoaderFamily, Route]]:
    """Return whether a test seam value is a route-mapping candidate."""
    return isinstance(value, Mapping)


async def _load_pickle(_artifact: ModelArtifact) -> object:
    """Fail closed until pickle artifact I/O is implemented in a later topic."""
    raise NotImplementedError


async def _load_torch(_artifact: ModelArtifact) -> object:
    """Fail closed until torch artifact I/O is implemented in a later topic."""
    raise NotImplementedError


async def _load_onnx(_artifact: ModelArtifact) -> object:
    """Fail closed until ONNX artifact I/O is implemented in a later topic."""
    raise NotImplementedError


class LocalModelLoader:
    """Dispatch a shared model artifact through its explicit loader family."""

    def __init__(self, *, _route_mapping: Mapping[LoaderFamily, Route] | None = None) -> None:
        if _route_mapping is None:
            self._route_mapping: Mapping[LoaderFamily, Route] = {
                LoaderFamily.PICKLE: _load_pickle,
                LoaderFamily.TORCH: _load_torch,
                LoaderFamily.ONNX: _load_onnx,
            }
            return

        if not _is_route_mapping(_route_mapping):
            msg = "_route_mapping must be a Mapping"
            raise TypeError(msg)

        if set(_route_mapping) != set(LoaderFamily):
            msg = "_route_mapping must contain exactly all LoaderFamily keys"
            raise ValueError(msg)

        if not all(callable(route) for route in _route_mapping.values()):
            msg = "_route_mapping values must be callable"
            raise TypeError(msg)

        self._route_mapping = _route_mapping

    async def load(self, artifact: ModelArtifact) -> object:
        """Await the route selected by the artifact's explicit loader family."""
        return await self._route_mapping[artifact.loader_family](artifact)
