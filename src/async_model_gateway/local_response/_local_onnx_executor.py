"""Private adapter from local response generation to local runtime composition."""

from __future__ import annotations

from typing import TypeAlias, TypeGuard

from async_model_gateway.model_runtime._local_runtime_composition import (
    _LocalRuntimeComposition,  # pyright: ignore[reportPrivateUsage]
)
from async_model_gateway.model_runtime.model_artifact import ModelArtifact

from .request import ModelPayloadValue

_RuntimeInvocation: TypeAlias = dict[str, object]


def _is_runtime_invocation(
    _invocation: dict[str, ModelPayloadValue],
) -> TypeGuard[_RuntimeInvocation]:
    """Refine the existing shallow snapshot for composition without copying it."""
    return True


class _LocalOnnxExecutor:  # pyright: ignore[reportUnusedClass]
    """Delegate one supported local ONNX invocation to existing composition."""

    def __init__(self, *, composition: _LocalRuntimeComposition) -> None:
        """Bind the existing internal composition owner."""
        self._composition = composition

    async def __call__(
        self,
        artifact: ModelArtifact,
        invocation: dict[str, ModelPayloadValue],
    ) -> list[object]:
        """Execute through the composition without adding lifecycle behavior."""
        if not _is_runtime_invocation(invocation):
            msg = "local ONNX invocation must be a string-keyed mapping"
            raise TypeError(msg)
        return await self._composition.execute(artifact, invocation)
