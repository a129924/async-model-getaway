"""Internal pre-acquisition loader and executor bindings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, cast

from typing_extensions import assert_never

from async_model_gateway.model_runtime.model_artifact import LoaderFamily
from async_model_gateway.model_runtime.model_execution.execution import (
    ModelExecutor,
    # The ONNX executor is an internal member of this closed binding factory.
    _OnnxModelExecutor,  # pyright: ignore[reportPrivateUsage]
)
from async_model_gateway.model_runtime.runtime_model._onnx_runtime import (
    # The precise runtime marker remains internal to runtime-binding composition.
    _OnnxRuntime,  # pyright: ignore[reportPrivateUsage]
)

from .loaders._model_loader import ModelLoader

# The ONNX loader is an internal member of this closed binding factory.
from .loaders._onnx_model_loader import _OnnxModelLoader  # pyright: ignore[reportPrivateUsage]

RuntimeT = TypeVar("RuntimeT")
InvocationT = TypeVar("InvocationT")
ResultT = TypeVar("ResultT")


@dataclass(frozen=True, slots=True)
class RuntimeBinding(Generic[RuntimeT, InvocationT, ResultT]):
    """Keep a loader, executor, and concurrency policy paired."""

    loader: ModelLoader[RuntimeT]
    executor: ModelExecutor[RuntimeT, InvocationT, ResultT]
    max_concurrency: int


# This resolver is constructed only by the local-runtime composition owner.
class _RuntimeBindingResolver:  # pyright: ignore[reportUnusedClass]
    """Resolve the closed local runtime family vocabulary before acquisition."""

    def resolve(
        self,
        loader_family: LoaderFamily,
    ) -> RuntimeBinding[object, object, object]:
        """Return the pre-paired internal binding for one explicit family."""
        match loader_family:
            case LoaderFamily.ONNX:
                onnx_binding = RuntimeBinding[_OnnxRuntime, object, object](
                    loader=_OnnxModelLoader(),
                    executor=_OnnxModelExecutor(),
                    max_concurrency=1,
                )
                # This is the sole LoaderFamily dynamic-routing erasure; the ONNX factory above
                # already establishes the precise loader/executor/runtime pairing.
                return cast(RuntimeBinding[object, object, object], onnx_binding)
            case LoaderFamily.PICKLE | LoaderFamily.TORCH:
                raise NotImplementedError
            case _:
                assert_never(loader_family)
