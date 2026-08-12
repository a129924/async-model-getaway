"""Strict public typing witness for local response generation with cache reuse."""

from __future__ import annotations

from collections.abc import Mapping

from typing_extensions import assert_type

from async_model_gateway.local_response import LocalResponseGateway, LocalResponseRequest
from async_model_gateway.model_registry import ModelRegistry
from async_model_gateway.model_registry.entry import ModelSourceKind
from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.response_cache import ResponseCache


def _hash_features(features: Mapping[str, str]) -> str:
    """Supply the frozen feature-hashing callable shape."""
    return ";".join(f"{name}={value}" for name, value in sorted(features.items()))


def _convert_onnx_result(result: list[object]) -> str:
    """Supply the frozen ONNX conversion callable shape."""
    return str(result)


async def _execute_local_response(
    artifact: ModelArtifact,
    invocation: dict[str, object],
) -> list[object]:
    """Supply the frozen local-executor callable shape."""
    _ = artifact, invocation
    return []


def _request() -> LocalResponseRequest:
    """Exercise the recursive payload contract through the public request only."""
    return LocalResponseRequest(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        model_payload={"nested": [None, {"enabled": True, "weight": 0.5}]},
        features={"format": "text"},
        model_artifact=ModelArtifact(
            loader_family=LoaderFamily.ONNX,
            artifact_path="model.onnx",
            loader_options={},
        ),
        invocation={"prompt": "hello"},
    )


async def check_public_gateway_preserves_the_frozen_typed_surface(
    registry: ModelRegistry,
    response_cache: ResponseCache,
) -> None:
    """Prove public construction and async generation without private imports."""
    gateway = LocalResponseGateway(
        registry=registry,
        response_cache=response_cache,
        hash_features=_hash_features,
        convert_onnx_result=_convert_onnx_result,
        executor=_execute_local_response,
    )
    response = await gateway.generate(request=_request())

    assert_type(gateway, LocalResponseGateway)
    assert_type(response, str)
