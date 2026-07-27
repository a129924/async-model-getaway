"""Internal composition root for local runtime binding and execution."""

from __future__ import annotations

from async_model_gateway.model_runtime.model_artifact import ModelArtifact
from async_model_gateway.model_runtime.model_pool._runtime_binding import (
    RuntimeBinding,
    _RuntimeBindingResolver,  # pyright: ignore[reportPrivateUsage]
)
from async_model_gateway.model_runtime.model_pool.pool import ModelPool
from async_model_gateway.model_runtime.runtime_model._onnx_runtime import (
    OnnxRuntimeSession,
)


class _LocalRuntimeComposition:
    """Resolve one binding before acquiring and executing one local runtime."""

    def __init__(
        self,
        *,
        model_pool: ModelPool,
        binding_resolver: _RuntimeBindingResolver,
    ) -> None:
        """Store the internal dependencies for one composition root."""
        self._model_pool = model_pool
        self._binding_resolver = binding_resolver

    async def execute(
        self,
        artifact: ModelArtifact,
        invocation: dict[str, object],
    ) -> list[object]:
        """Resolve once, then acquire and execute through that same binding."""
        binding: RuntimeBinding[
            OnnxRuntimeSession, dict[str, object], list[object]
        ] = self._binding_resolver.resolve(artifact.loader_family)
        loaded_model = await self._model_pool.acquire(
            artifact,
            loader=binding.loader,
            max_concurrency=binding.max_concurrency,
        )
        return await binding.executor.execute(loaded_model, invocation)


def _create_local_runtime_composition(  # pyright: ignore[reportUnusedFunction]
) -> _LocalRuntimeComposition:
    """Create the private local runtime composition root."""
    return _LocalRuntimeComposition(
        model_pool=ModelPool(),
        binding_resolver=_RuntimeBindingResolver(),
    )
