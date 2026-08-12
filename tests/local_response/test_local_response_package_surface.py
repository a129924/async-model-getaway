"""RED coverage for the exact public local-response package surface."""

from __future__ import annotations

from dataclasses import fields
import inspect
from collections.abc import Mapping
from typing import get_type_hints

import async_model_gateway
import async_model_gateway.local_response as local_response
import async_model_gateway.local_response.gateway as gateway_module
import async_model_gateway.local_response.request as request_module
from async_model_gateway.local_response import LocalResponseGateway, LocalResponseRequest
from async_model_gateway.model_registry.entry import ModelSourceKind
from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.response_cache import CacheKey


def test_local_response_exports_exactly_the_two_declared_public_types() -> None:
    """The direct-import package keeps helpers and existing owners internal."""
    assert local_response.__all__ == ["LocalResponseGateway", "LocalResponseRequest"]
    assert local_response.LocalResponseGateway is LocalResponseGateway
    assert local_response.LocalResponseRequest is LocalResponseRequest
    assert not hasattr(local_response, "ModelPayloadValue")
    assert all(
        not hasattr(local_response, name)
        for name in ("_CacheKeyDeriver", "_OnnxResultConverter", "_LocalResponseExecutor")
    )
    assert async_model_gateway.__all__ == ["__version__", "main"]
    assert not hasattr(async_model_gateway, "LocalResponseGateway")
    assert not hasattr(async_model_gateway, "LocalResponseRequest")


def test_request_is_frozen_slotted_and_has_the_exact_six_field_contract() -> None:
    """The request keeps caller input immutable and does not invent fields."""
    assert LocalResponseRequest.__dataclass_params__.frozen is True
    assert LocalResponseRequest.__slots__ == (
        "model_name",
        "model_source_kind",
        "model_payload",
        "features",
        "model_artifact",
        "invocation",
    )
    assert tuple(field.name for field in fields(LocalResponseRequest)) == (
        LocalResponseRequest.__slots__
    )
    annotations = get_type_hints(LocalResponseRequest)
    assert annotations["model_name"] is str
    assert annotations["model_source_kind"] is ModelSourceKind
    assert annotations["model_artifact"] is ModelArtifact
    assert annotations["invocation"] == dict[str, object]
    assert annotations["features"].__origin__.__name__ == "Mapping"
    assert hasattr(request_module, "ModelPayloadValue")
    assert "ModelPayloadValue" not in request_module.__all__


def test_gateway_constructor_and_generate_signature_are_the_locked_public_contract() -> None:
    """All constructor collaborators are keyword-only and generate is keyword-only async."""
    constructor = inspect.signature(LocalResponseGateway.__init__)
    generate = inspect.signature(LocalResponseGateway.generate)

    assert tuple(constructor.parameters) == (
        "self",
        "registry",
        "response_cache",
        "cache_key_deriver",
        "convert_onnx_result",
        "executor",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for name, parameter in constructor.parameters.items()
        if name != "self"
    )
    assert constructor.parameters["registry"].annotation == "ModelRegistry"
    assert constructor.parameters["response_cache"].annotation == "ResponseCache"
    assert constructor.parameters["cache_key_deriver"].annotation == "_CacheKeyDeriver"
    assert constructor.parameters["executor"].default is None
    assert inspect.iscoroutinefunction(LocalResponseGateway.generate)
    assert tuple(generate.parameters) == ("self", "request")
    assert generate.parameters["request"].kind is inspect.Parameter.KEYWORD_ONLY
    assert generate.parameters["request"].annotation == "LocalResponseRequest"
    assert generate.return_annotation == "str"
    assert hasattr(gateway_module, "_CacheKeyDeriver")
    assert not hasattr(gateway_module, "_FeatureHasher")
    assert hasattr(gateway_module, "_OnnxResultConverter")
    assert hasattr(gateway_module, "_LocalResponseExecutor")


def test_private_callable_protocols_have_the_frozen_annotations_without_becoming_exports() -> None:
    """The private seams retain their exact typed callable contracts."""
    deriver_hints = get_type_hints(gateway_module._CacheKeyDeriver.__call__)
    converter_hints = get_type_hints(gateway_module._OnnxResultConverter.__call__)
    executor_hints = get_type_hints(gateway_module._LocalResponseExecutor.__call__)

    assert deriver_hints["model_name"] is str
    assert deriver_hints["model_payload_hash"] is str
    assert deriver_hints["features"] == Mapping[str, str]
    assert deriver_hints["model_artifact"] is ModelArtifact
    assert deriver_hints["invocation"] == dict[str, object]
    assert deriver_hints["return"] is CacheKey
    assert converter_hints["return"] is str
    assert executor_hints["artifact"] is ModelArtifact
    assert executor_hints["invocation"] == dict[str, object]
    assert executor_hints["return"] == list[object]
    assert inspect.iscoroutinefunction(gateway_module._LocalResponseExecutor.__call__)
    assert LoaderFamily.ONNX.value == "onnx"
