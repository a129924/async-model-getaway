"""RED coverage for the model-artifact package surface contract."""

from __future__ import annotations

import importlib

import async_model_gateway as root_module
import async_model_gateway.model_runtime as model_runtime_root_module
import async_model_gateway.model_runtime.model_artifact as model_artifact_module
import async_model_gateway.model_runtime.model_artifact.artifact as artifact_module
import async_model_gateway.model_runtime.model_artifact.loader_family as loader_family_module
import async_model_gateway.model_registry as model_registry_module
import async_model_gateway.response_cache as response_cache_module

import pytest


def test_model_artifact_package_reexports_only_model_artifact_and_loader_family() -> None:
    """The topic-local package root must stay narrow and explicit."""
    assert model_artifact_module.__all__ == ["LoaderFamily", "ModelArtifact"]
    assert model_artifact_module.ModelArtifact is artifact_module.ModelArtifact
    assert model_artifact_module.LoaderFamily is loader_family_module.LoaderFamily


def test_model_artifact_types_stay_in_the_locked_single_concept_modules() -> None:
    """Each public concept must stay in the locked source-root modules."""
    assert artifact_module.ModelArtifact.__module__ == (
        "async_model_gateway.model_runtime.model_artifact.artifact"
    )
    assert loader_family_module.LoaderFamily.__module__ == (
        "async_model_gateway.model_runtime.model_artifact.loader_family"
    )


def test_model_artifact_package_does_not_expose_local_model_loader() -> None:
    """Deferred loader runtime behavior must stay outside this package surface."""
    assert not hasattr(model_artifact_module, "LocalModelLoader")


def test_existing_package_roots_do_not_reexport_model_artifact_surface() -> None:
    """The new boundary owner must not leak into other existing package roots."""
    for module in (
        root_module,
        model_runtime_root_module,
        model_registry_module,
        response_cache_module,
    ):
        assert not hasattr(module, "ModelArtifact")
        assert not hasattr(module, "LoaderFamily")


@pytest.mark.parametrize(
    "legacy_module_name",
    [
        "async_model_gateway.model_artifact",
        "async_model_gateway.model_artifact.artifact",
        "async_model_gateway.model_artifact.loader_family",
    ],
)
def test_legacy_model_artifact_import_paths_are_not_available(
    legacy_module_name: str,
) -> None:
    """The legacy package root must stay removed without a compatibility layer."""
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(legacy_module_name)
