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


class _LocalLoadedRuntimeModel(LoadedRuntimeModel[RuntimeT]):
    """Keep local provider runtime state behind the abstract consumption boundary."""

    __slots__ = ("_loader_family", "_provider_model")

    def __init__(
        self,
        *,
        loader_family: LoaderFamily,
        provider_model: RuntimeT,
    ) -> None:
        """Store explicit provenance and the internal provider runtime."""
        self._loader_family = loader_family
        self._provider_model = provider_model

    @property
    def loader_family(self) -> LoaderFamily:
        """Return the explicit loader family that produced this runtime model."""
        return self._loader_family

    def _provider_runtime(self) -> RuntimeT:
        """Return the internal provider runtime for future model execution."""
        return self._provider_model


def _create_loaded_runtime_model(  # pyright: ignore[reportUnusedFunction]
    *,
    loader_family: LoaderFamily,
    provider_model: RuntimeT,
) -> LoadedRuntimeModel[RuntimeT]:
    """Create an opaque handle at the provider-object boundary."""
    return _LocalLoadedRuntimeModel(
        loader_family=loader_family,
        provider_model=provider_model,
    )
