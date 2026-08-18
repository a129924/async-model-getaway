"""Frozen request contract for bounded local response generation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TypeAlias

from async_model_gateway.model_registry.entry import ModelSourceKind
from async_model_gateway.model_runtime.model_artifact import ModelArtifact

__all__ = ["LocalResponseRequest"]

ModelPayloadValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | list["ModelPayloadValue"]
    | dict[str, "ModelPayloadValue"]
)


@dataclass(frozen=True, slots=True)
class LocalResponseRequest:
    """Keep caller-supplied local ONNX generation inputs together."""

    model_name: str
    model_source_kind: ModelSourceKind
    model_payload: dict[str, ModelPayloadValue]
    features: Mapping[str, str]
    model_artifact: ModelArtifact
    invocation: dict[str, ModelPayloadValue]
