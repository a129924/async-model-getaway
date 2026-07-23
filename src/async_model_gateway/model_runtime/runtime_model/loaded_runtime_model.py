"""Opaque handle returned by runtime-model providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from async_model_gateway.model_runtime.model_artifact import LoaderFamily

__all__ = ["LoadedRuntimeModel"]

RuntimeT = TypeVar("RuntimeT", covariant=True)


class LoadedRuntimeModel(ABC, Generic[RuntimeT]):
    """Define the opaque consumption boundary for an acquired runtime model."""

    __slots__ = ()

    @property
    @abstractmethod
    def loader_family(self) -> LoaderFamily:
        """Return the explicit loader family that produced this runtime model."""

    @abstractmethod
    def _provider_runtime(self) -> RuntimeT:
        """Return the provider runtime through the model-side internal handoff."""
