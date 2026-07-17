"""RED coverage for the private ONNX local-runtime acquisition boundary."""

from __future__ import annotations

import asyncio
import sys
import threading
import time
from pathlib import Path
from contextlib import suppress
from types import ModuleType

import onnx
import onnxruntime
import pytest
from onnx import TensorProto, helper

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_execution import ModelExecution
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel


def _write_identity_model(path: Path) -> None:
    """Write a minimal, runtime-compatible ONNX identity graph to a temporary path."""
    graph = helper.make_graph(
        [helper.make_node("Identity", inputs=["input"], outputs=["output"])],
        "identity",
        [helper.make_tensor_value_info("input", TensorProto.FLOAT, [1])],
        [helper.make_tensor_value_info("output", TensorProto.FLOAT, [1])],
    )
    model = helper.make_model(
        graph,
        ir_version=10,
        opset_imports=[helper.make_operatorsetid("", 13)],
    )
    onnx.save_model(model, path)


def _artifact(path: Path, *, loader_options: dict[str, object] | None = None) -> ModelArtifact:
    """Build an explicitly routed ONNX artifact without suffix-based behavior."""
    return ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path=str(path),
        loader_options={} if loader_options is None else loader_options,
    )


@pytest.fixture
def onnx_model_path(tmp_path: Path) -> Path:
    """Create a valid model at a path that intentionally has no ONNX suffix."""
    path = tmp_path / "identity-runtime"
    _write_identity_model(path)
    return path


@pytest.mark.asyncio
async def test_acquire_returns_a_cpu_only_onnx_session_through_the_opaque_handle(
    onnx_model_path: Path,
) -> None:
    """An explicit ONNX artifact must acquire a real CPU session without inference."""
    loaded = await ModelPool().acquire(_artifact(onnx_model_path))
    seen_runtimes: list[object] = []
    invocation = object()
    result = object()

    async def record_runtime(runtime: object, received_invocation: object) -> object:
        seen_runtimes.append(runtime)
        assert received_invocation is invocation
        return result

    execution = ModelExecution[object, object, object](invoke=record_runtime)

    assert isinstance(loaded, LoadedRuntimeModel)
    assert loaded.loader_family is LoaderFamily.ONNX
    assert await execution.execute(loaded, invocation) is result
    assert len(seen_runtimes) == 1
    assert isinstance(seen_runtimes[0], onnxruntime.InferenceSession)
    assert seen_runtimes[0].get_providers() == ["CPUExecutionProvider"]


@pytest.mark.asyncio
async def test_acquire_rejects_non_empty_options_before_constructing_a_session(
    onnx_model_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """First-version ONNX loading must fail closed on all loader options."""
    construction_called = False

    def unexpected_construction(*_args: object, **_kwargs: object) -> object:
        nonlocal construction_called
        construction_called = True
        raise AssertionError("session construction must not run")

    monkeypatch.setattr(onnxruntime, "InferenceSession", unexpected_construction)

    with pytest.raises(ValueError) as raised:
        await ModelPool().acquire(_artifact(onnx_model_path, loader_options={"providers": []}))

    assert str(raised.value) == "ONNX loader_options are not supported"
    assert construction_called is False


@pytest.mark.asyncio
async def test_acquire_translates_only_a_missing_top_level_onnxruntime_dependency(
    onnx_model_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The optional-extra guidance must preserve the missing import as its cause."""
    monkeypatch.setitem(sys.modules, "onnxruntime", None)

    with pytest.raises(RuntimeError) as raised:
        await ModelPool().acquire(_artifact(onnx_model_path))

    assert str(raised.value) == (
        "ONNX runtime support requires installing async-model-gateway[onnx]"
    )
    assert isinstance(raised.value.__cause__, ModuleNotFoundError)
    assert raised.value.__cause__.name == "onnxruntime"


@pytest.mark.asyncio
async def test_acquire_preserves_provider_failures_without_install_guidance(
    onnx_model_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Provider construction errors must remain provider-owned failures."""
    provider_failure = RuntimeError("provider initialization failed")

    def fail_construction(*_args: object, **_kwargs: object) -> object:
        raise provider_failure

    monkeypatch.setattr(onnxruntime, "InferenceSession", fail_construction)

    with pytest.raises(RuntimeError) as raised:
        await ModelPool().acquire(_artifact(onnx_model_path))

    assert raised.value is provider_failure


@pytest.mark.asyncio
async def test_acquire_preserves_missing_artifact_path_failure_without_translation(
    tmp_path: Path,
) -> None:
    """A missing provider path must retain its native ONNX Runtime failure."""
    missing_path = tmp_path / "missing-runtime-model"

    with pytest.raises(Exception) as raised:
        await ModelPool().acquire(_artifact(missing_path))

    assert str(raised.value) != (
        "ONNX runtime support requires installing async-model-gateway[onnx]"
    )
    assert raised.value.__cause__ is None


@pytest.mark.asyncio
async def test_acquire_preserves_invalid_onnx_model_failure_without_translation(
    tmp_path: Path,
) -> None:
    """An invalid provider artifact must retain its native ONNX Runtime failure."""
    invalid_model = tmp_path / "invalid-runtime-model"
    invalid_model.write_text("not an ONNX model", encoding="utf-8")

    with pytest.raises(Exception) as raised:
        await ModelPool().acquire(_artifact(invalid_model))

    assert str(raised.value) != (
        "ONNX runtime support requires installing async-model-gateway[onnx]"
    )
    assert raised.value.__cause__ is None


@pytest.mark.asyncio
async def test_acquire_preserves_nested_optional_import_failure_unchanged(
    onnx_model_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A nested optional-runtime import failure must not become install guidance."""
    nested_failure = ModuleNotFoundError(
        "No module named 'onnxruntime.capi'",
        name="onnxruntime.capi",
    )
    fake_onnxruntime = ModuleType("onnxruntime")

    def fail_transitive_import(_name: str) -> object:
        raise nested_failure

    fake_onnxruntime.__getattr__ = fail_transitive_import  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "onnxruntime", fake_onnxruntime)

    with pytest.raises(ModuleNotFoundError) as raised:
        await ModelPool().acquire(_artifact(onnx_model_path))

    assert raised.value is nested_failure


@pytest.mark.asyncio
async def test_acquire_moves_session_construction_off_the_event_loop_thread(
    onnx_model_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A ready coroutine must advance while the synchronous factory is running."""
    progress = asyncio.Event()
    progress_seen_by_factory: list[bool] = []
    session = object()

    async def advance_event_loop() -> None:
        await asyncio.sleep(0)
        progress.set()

    def blocking_factory(*_args: object, **_kwargs: object) -> object:
        time.sleep(0.1)
        progress_seen_by_factory.append(progress.is_set())
        return session

    monkeypatch.setattr(onnxruntime, "InferenceSession", blocking_factory)
    progress_task = asyncio.create_task(advance_event_loop())

    loaded = await ModelPool().acquire(_artifact(onnx_model_path))
    await progress_task

    assert progress_seen_by_factory == [True]
    seen_runtimes: list[object] = []

    async def record_runtime(runtime: object, _invocation: object) -> None:
        seen_runtimes.append(runtime)

    await ModelExecution[object, object, None](invoke=record_runtime).execute(loaded, object())
    assert seen_runtimes == [session]


@pytest.mark.asyncio
async def test_acquire_propagates_cancellation_and_releases_the_worker_fixture(
    onnx_model_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cancelling the caller must not be translated into a loader-specific failure."""
    factory_started = threading.Event()
    release_factory = threading.Event()

    def blocking_factory(*_args: object, **_kwargs: object) -> object:
        factory_started.set()
        release_factory.wait(timeout=2)
        return object()

    monkeypatch.setattr(onnxruntime, "InferenceSession", blocking_factory)
    acquisition = asyncio.create_task(ModelPool().acquire(_artifact(onnx_model_path)))

    try:
        assert await asyncio.to_thread(factory_started.wait, 1)
        acquisition.cancel()
        with pytest.raises(asyncio.CancelledError):
            await acquisition
    finally:
        release_factory.set()
        if acquisition.done():
            with suppress(asyncio.CancelledError, NotImplementedError):
                acquisition.result()


@pytest.mark.asyncio
async def test_pickle_path_appearance_does_not_route_into_onnx_acquisition(
    onnx_model_path: Path,
) -> None:
    """Explicit PICKLE routing remains fail closed even for an ONNX-looking path."""
    artifact = ModelArtifact(
        loader_family=LoaderFamily.PICKLE,
        artifact_path=f"{onnx_model_path}.onnx",
        loader_options={},
    )

    with pytest.raises(NotImplementedError):
        await ModelPool().acquire(artifact)
