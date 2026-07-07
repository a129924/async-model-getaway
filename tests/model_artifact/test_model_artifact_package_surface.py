"""RED coverage for the model-artifact package surface contract."""

from __future__ import annotations

import importlib


def test_model_artifact_package_reexports_only_model_artifact_and_loader_family() -> None:
    """The topic-local package root must stay narrow and explicit."""
    model_artifact_module = importlib.import_module("async_model_gateway.model_artifact")
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    assert model_artifact_module.__all__ == ["LoaderFamily", "ModelArtifact"]
    assert model_artifact_module.ModelArtifact is artifact_module.ModelArtifact
    assert model_artifact_module.LoaderFamily is loader_family_module.LoaderFamily


def test_model_artifact_types_stay_in_the_locked_single_concept_modules() -> None:
    """Each public concept must stay in the locked source-root modules."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    assert artifact_module.ModelArtifact.__module__ == (
        "async_model_gateway.model_artifact.artifact"
    )
    assert loader_family_module.LoaderFamily.__module__ == (
        "async_model_gateway.model_artifact.loader_family"
    )


def test_model_artifact_package_does_not_expose_local_model_loader() -> None:
    """Deferred loader runtime behavior must stay outside this package surface."""
    model_artifact_module = importlib.import_module("async_model_gateway.model_artifact")

    assert not hasattr(model_artifact_module, "LocalModelLoader")


def test_existing_package_roots_do_not_reexport_model_artifact_surface() -> None:
    """The new boundary owner must not leak into other existing package roots."""
    root_module = importlib.import_module("async_model_gateway")
    model_registry_module = importlib.import_module("async_model_gateway.model_registry")
    response_cache_module = importlib.import_module("async_model_gateway.response_cache")

    for module in (root_module, model_registry_module, response_cache_module):
        assert not hasattr(module, "ModelArtifact")
        assert not hasattr(module, "LoaderFamily")
