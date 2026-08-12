"""Private adapter from local response generation to local runtime composition."""

from __future__ import annotations

from async_model_gateway.model_runtime._local_runtime_composition import (
    _LocalRuntimeComposition,  # pyright: ignore[reportPrivateUsage]
)
from async_model_gateway.model_runtime.model_artifact import ModelArtifact


class _LocalOnnxExecutor:  # pyright: ignore[reportUnusedClass]
    """Delegate one supported local ONNX invocation to existing composition."""

    def __init__(self, *, composition: _LocalRuntimeComposition) -> None:
        """Bind the existing internal composition owner."""
        self._composition = composition

    async def __call__(
        self,
        artifact: ModelArtifact,
        invocation: dict[str, object],
    ) -> list[object]:
        """Execute through the composition without adding lifecycle behavior."""
        return await self._composition.execute(artifact, invocation)
