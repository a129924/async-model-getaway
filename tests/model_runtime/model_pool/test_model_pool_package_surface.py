"""RED coverage for the internal model-pool package boundary."""

from __future__ import annotations

import inspect

import async_model_gateway.model_runtime.model_pool as model_pool_module
from async_model_gateway.model_runtime.model_pool import pool as pool_module


def test_model_pool_package_reexports_no_implementation_types() -> None:
    assert model_pool_module.__all__ == []
    assert not hasattr(model_pool_module, "ModelPool")
    assert not hasattr(model_pool_module, "ModelLoader")


def test_internal_pool_acquire_has_the_injected_generic_signature() -> None:
    acquire_signature = inspect.signature(pool_module.ModelPool.acquire)

    assert inspect.iscoroutinefunction(pool_module.ModelPool.acquire)
    assert tuple(acquire_signature.parameters) == (
        "self",
        "artifact",
        "loader",
        "max_concurrency",
    )
    assert acquire_signature.parameters["loader"].kind is inspect.Parameter.KEYWORD_ONLY
    assert acquire_signature.parameters["max_concurrency"].kind is inspect.Parameter.KEYWORD_ONLY
    assert acquire_signature.parameters["artifact"].annotation == "ModelArtifact"
    assert acquire_signature.parameters["loader"].annotation == "ModelLoader[RuntimeT]"
    assert acquire_signature.return_annotation == "LoadedRuntimeModel[RuntimeT]"
