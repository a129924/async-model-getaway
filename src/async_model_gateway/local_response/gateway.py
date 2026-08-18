"""Bounded local ONNX response generation with response-cache reuse."""

from __future__ import annotations

from typing import Protocol

from typing_extensions import assert_never

from async_model_gateway.model_registry import ModelRegistry
from async_model_gateway.model_registry.entry import ModelSourceKind
from async_model_gateway.model_runtime._local_runtime_composition import (
    _create_local_runtime_composition,  # pyright: ignore[reportPrivateUsage]
)
from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.response_cache import (
    CacheHit,
    CacheMiss,
    Failed,
    Remembered,
    ResponseCache,
    Skipped,
)

from ._identity_derivers import (
    _assemble_cache_key,  # pyright: ignore[reportPrivateUsage]
    _derive_feature_hash,  # pyright: ignore[reportPrivateUsage]
    _derive_namespace,  # pyright: ignore[reportPrivateUsage]
    _derive_prediction_input_hash,  # pyright: ignore[reportPrivateUsage]
)
from ._local_onnx_executor import _LocalOnnxExecutor  # pyright: ignore[reportPrivateUsage]
from .request import LocalResponseRequest, ModelPayloadValue

__all__ = ["LocalResponseGateway"]


class _OnnxResultConverter(Protocol):
    """Describe conversion of one ONNX invocation result into a response."""

    def __call__(self, result: list[object]) -> str: ...


class _LocalResponseExecutor(Protocol):
    """Describe one local ONNX invocation seam."""

    async def __call__(
        self,
        artifact: ModelArtifact,
        invocation: dict[str, ModelPayloadValue],
    ) -> list[object]: ...


class LocalResponseGateway:
    """Coordinate guarded local ONNX generation and response-cache reuse."""

    def __init__(
        self,
        *,
        registry: ModelRegistry,
        response_cache: ResponseCache,
        convert_onnx_result: _OnnxResultConverter,
        executor: _LocalResponseExecutor | None = None,
    ) -> None:
        """Bind the existing owners and optional local execution seam."""
        self._registry = registry
        self._response_cache = response_cache
        self._convert_onnx_result = convert_onnx_result
        self._executor: _LocalResponseExecutor = (
            _LocalOnnxExecutor(composition=_create_local_runtime_composition())
            if executor is None
            else executor
        )

    async def generate(self, *, request: LocalResponseRequest) -> str:
        """Reuse a cached response or invoke and remember one local ONNX result."""
        if request.model_source_kind is not ModelSourceKind.LOCAL:
            msg = "only local response generation is supported"
            raise NotImplementedError(msg)
        if request.model_artifact.loader_family is not LoaderFamily.ONNX:
            msg = "only ONNX local response generation is supported"
            raise NotImplementedError(msg)

        invocation_snapshot: dict[str, ModelPayloadValue] = dict(request.invocation)
        namespace = _derive_namespace()
        feature_hash = _derive_feature_hash(request.features)
        prediction_input_hash = _derive_prediction_input_hash(invocation_snapshot)
        freshness = await self._registry.resolve_freshness(
            model_name=request.model_name,
            model_source_kind=request.model_source_kind,
            model_payload=request.model_payload,
        )
        key = _assemble_cache_key(
            namespace=namespace,
            model_identity_hash=freshness.entry.model_identity_hash,
            feature_hash=feature_hash,
            prediction_input_hash=prediction_input_hash,
        )
        lookup_outcome = await self._response_cache.lookup(key=key, context=object())

        match lookup_outcome:
            case CacheHit(value=value):
                return value
            case CacheMiss():
                pass
            case _:
                assert_never(lookup_outcome)

        result = await self._executor(request.model_artifact, invocation_snapshot)
        response = self._convert_onnx_result(result)
        remember_outcome = await self._response_cache.remember(
            key=key,
            value=response,
            context=object(),
        )

        match remember_outcome:
            case Remembered() | Skipped() | Failed():
                return response
            case _:
                assert_never(remember_outcome)
