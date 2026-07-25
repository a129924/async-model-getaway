"""RED regression coverage for private ONNX raw-runtime acquisition."""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path

import onnxruntime
import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_pool.loaders._onnx_model_loader import (
    _OnnxModelLoader,
    load_onnx_runtime,
)
from async_model_gateway.model_runtime.model_pool.pool import ModelPool

InferenceSessionConstructor = Callable[..., object]
InferenceSessionImporter = Callable[[], InferenceSessionConstructor]
_MINIMAL_IDENTITY_MODEL_PATH = Path(__file__).with_name("fixtures") / "minimal_identity.onnx"


def _return_constructor(
    constructor: InferenceSessionConstructor,
) -> InferenceSessionImporter:
    def importer() -> InferenceSessionConstructor:
        return constructor

    return importer


def _artifact(path: Path, *, loader_options: dict[str, object] | None = None) -> ModelArtifact:
    return ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path=str(path),
        loader_options={} if loader_options is None else loader_options,
    )


@pytest.fixture
def onnx_model_path() -> Path:
    return _MINIMAL_IDENTITY_MODEL_PATH


@pytest.mark.asyncio
async def test_pool_wraps_a_cpu_only_onnx_session_from_the_injected_raw_loader(
    onnx_model_path: Path,
) -> None:
    loaded = await ModelPool().acquire(
        _artifact(onnx_model_path),
        loader=_OnnxModelLoader(),
        max_concurrency=1,
    )

    assert isinstance(loaded.runtime, onnxruntime.InferenceSession)
    assert loaded.runtime.get_providers() == ["CPUExecutionProvider"]
    assert loaded.execution_gate.locked() is False


@pytest.mark.asyncio
async def test_onnx_loader_rejects_options_before_constructing_a_session(
    onnx_model_path: Path,
) -> None:
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
async def test_onnx_loader_preserves_provider_failure_without_translation(
    onnx_model_path: Path,
) -> None:
    failure = RuntimeError("provider initialization failed")

    def fail_construction(*_args: object, **_kwargs: object) -> object:
        raise failure

    with pytest.raises(RuntimeError) as raised:
        await load_onnx_runtime(
            _artifact(onnx_model_path),
            inference_session_importer=_return_constructor(fail_construction),
        )

    assert raised.value is failure


@pytest.mark.asyncio
async def test_onnx_loader_moves_session_construction_off_the_event_loop_thread(
    onnx_model_path: Path,
) -> None:
    progress = asyncio.Event()
    progress_seen_by_factory: list[bool] = []

    async def advance_event_loop() -> None:
        await asyncio.sleep(0)
        progress.set()

    def blocking_factory(*_args: object, **_kwargs: object) -> object:
        time.sleep(0.1)
        progress_seen_by_factory.append(progress.is_set())
        return object()

    progress_task = asyncio.create_task(advance_event_loop())
    await load_onnx_runtime(
        _artifact(onnx_model_path),
        inference_session_importer=_return_constructor(blocking_factory),
    )
    await progress_task

    assert progress_seen_by_factory == [True]


@pytest.mark.asyncio
async def test_onnx_loader_propagates_cancellation_without_translation(
    onnx_model_path: Path,
) -> None:
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
