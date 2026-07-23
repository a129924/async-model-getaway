"""RED coverage for the private ONNX local-runtime acquisition boundary."""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path

import onnx
import onnxruntime
import pytest
from onnx import TensorProto, helper

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_execution import ModelExecution
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.model_pool._onnx_runtime_loader import (
    load_onnx_runtime,
)
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel

InferenceSessionConstructor = Callable[..., object]
InferenceSessionImporter = Callable[[], InferenceSessionConstructor]


def _return_constructor(
    constructor: InferenceSessionConstructor,
) -> InferenceSessionImporter:
    """Return a fully typed private-importer test double."""

    def importer() -> InferenceSessionConstructor:
        return constructor

    return importer


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
) -> None:
    """First-version ONNX loading must fail closed on all loader options."""
    importer_called = False

    def unexpected_importer() -> InferenceSessionConstructor:
        nonlocal importer_called
        importer_called = True
        raise AssertionError("session construction must not run")

    with pytest.raises(ValueError) as raised:
        await load_onnx_runtime(
            _artifact(onnx_model_path, loader_options={"providers": []}),
            inference_session_importer=unexpected_importer,
        )

    assert str(raised.value) == "ONNX loader_options are not supported"
    assert importer_called is False


@pytest.mark.asyncio
async def test_acquire_translates_only_a_missing_top_level_onnxruntime_dependency(
    onnx_model_path: Path,
) -> None:
    """The optional-extra guidance must preserve the missing import as its cause."""
    missing_dependency = ModuleNotFoundError(
        "No module named 'onnxruntime'",
        name="onnxruntime",
    )

    def raise_missing_dependency() -> InferenceSessionConstructor:
        raise missing_dependency

    with pytest.raises(RuntimeError) as raised:
        await load_onnx_runtime(
            _artifact(onnx_model_path),
            inference_session_importer=raise_missing_dependency,
        )

    assert str(raised.value) == (
        "ONNX runtime support requires installing async-model-gateway[onnx]"
    )
    assert raised.value.__cause__ is missing_dependency


@pytest.mark.asyncio
async def test_acquire_preserves_provider_failures_without_install_guidance(
    onnx_model_path: Path,
) -> None:
    """Provider construction errors must remain provider-owned failures."""
    provider_failure = RuntimeError("provider initialization failed")

    def fail_construction(*_args: object, **_kwargs: object) -> object:
        raise provider_failure

    with pytest.raises(RuntimeError) as raised:
        await load_onnx_runtime(
            _artifact(onnx_model_path),
            inference_session_importer=_return_constructor(fail_construction),
        )

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
) -> None:
    """A nested optional-runtime import failure must not become install guidance."""
    nested_failure = ModuleNotFoundError(
        "No module named 'onnxruntime.capi'",
        name="onnxruntime.capi",
    )

    def fail_transitive_import() -> InferenceSessionConstructor:
        raise nested_failure

    with pytest.raises(ModuleNotFoundError) as raised:
        await load_onnx_runtime(
            _artifact(onnx_model_path),
            inference_session_importer=fail_transitive_import,
        )

    assert raised.value is nested_failure


@pytest.mark.asyncio
async def test_acquire_moves_session_construction_off_the_event_loop_thread(
    onnx_model_path: Path,
) -> None:
    """A ready coroutine must advance while the synchronous factory is running."""
    progress = asyncio.Event()
    progress_seen_by_factory: list[bool] = []
    expected_session = object()

    async def advance_event_loop() -> None:
        await asyncio.sleep(0)
        progress.set()

    def blocking_factory(*_args: object, **_kwargs: object) -> object:
        time.sleep(0.1)
        progress_seen_by_factory.append(progress.is_set())
        return expected_session

    progress_task = asyncio.create_task(advance_event_loop())

    session = await load_onnx_runtime(
        _artifact(onnx_model_path),
        inference_session_importer=_return_constructor(blocking_factory),
    )
    await progress_task

    assert progress_seen_by_factory == [True]
    assert session is expected_session


@pytest.mark.asyncio
async def test_acquire_propagates_cancellation_and_releases_the_worker_fixture(
    onnx_model_path: Path,
) -> None:
    """Cancelling the caller must not be translated into a loader-specific failure."""
    factory_started = threading.Event()
    release_factory = threading.Event()

    def blocking_factory(*_args: object, **_kwargs: object) -> object:
        factory_started.set()
        release_factory.wait(timeout=2)
        return object()

    acquisition = asyncio.create_task(
        load_onnx_runtime(
            _artifact(onnx_model_path),
            inference_session_importer=_return_constructor(blocking_factory),
        )
    )

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
