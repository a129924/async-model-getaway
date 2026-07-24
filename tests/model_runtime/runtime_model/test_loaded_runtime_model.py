"""RED coverage for the concrete internal loaded-runtime resource."""

from __future__ import annotations

import asyncio
import inspect
from dataclasses import fields, is_dataclass
from datetime import datetime, timezone

from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    LoadedRuntimeModel,
)
from async_model_gateway.model_runtime.runtime_model import (
    loaded_runtime_model as loaded_runtime_model_module,
)


def test_loaded_runtime_model_is_a_slots_generic_dataclass_with_runtime_state() -> None:
    runtime = object()
    gate = asyncio.Semaphore(1)
    loaded = LoadedRuntimeModel(runtime=runtime, execution_gate=gate)

    assert is_dataclass(LoadedRuntimeModel)
    assert LoadedRuntimeModel.__parameters__[0].__name__ == "RuntimeT"
    assert tuple(field.name for field in fields(LoadedRuntimeModel)) == (
        "runtime",
        "execution_gate",
        "loaded_at",
        "last_used_at",
    )
    assert loaded.runtime is runtime
    assert loaded.execution_gate is gate
    assert loaded.last_used_at is None
    assert loaded.loaded_at.tzinfo is timezone.utc
    assert not hasattr(loaded, "__dict__")


def test_mark_used_sets_an_aware_utc_timestamp_without_provider_behavior() -> None:
    loaded = LoadedRuntimeModel(runtime=object(), execution_gate=asyncio.Semaphore(1))

    loaded.mark_used()

    assert isinstance(loaded.loaded_at, datetime)
    assert isinstance(loaded.last_used_at, datetime)
    assert loaded.last_used_at >= loaded.loaded_at
    assert loaded.last_used_at.tzinfo is timezone.utc


def test_loaded_runtime_model_has_only_passive_resource_members() -> None:
    loaded = LoadedRuntimeModel(runtime=object(), execution_gate=asyncio.Semaphore(1))

    for forbidden_member in (
        "loader_family",
        "loader",
        "executor",
        "binding",
        "_provider_runtime",
        "execute",
        "invoke",
        "load",
        "unload",
        "close",
        "warm_up",
        "resolve_executor",
    ):
        assert not hasattr(loaded, forbidden_member)


def test_loaded_runtime_model_module_has_no_legacy_opaque_handle_abstractions() -> None:
    module_source = inspect.getsource(loaded_runtime_model_module)

    assert "class _LocalLoadedRuntimeModel" not in module_source
    assert "_provider_runtime" not in module_source
    assert "LoaderFamily" not in module_source
