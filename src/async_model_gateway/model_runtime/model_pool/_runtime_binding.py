"""Internal pre-acquisition loader and executor bindings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from typing_extensions import assert_never

from async_model_gateway.model_runtime.model_artifact import LoaderFamily
from async_model_gateway.model_runtime.model_execution.execution import (
    ModelExecutor,
    _OnnxModelExecutor,  # pyright: ignore[reportPrivateUsage]
)

from ._local_model_loader import ModelLoader, _OnnxModelLoader  # pyright: ignore[reportPrivateUsage]

RuntimeT = TypeVar("RuntimeT")
InvocationT = TypeVar("InvocationT")
ResultT = TypeVar("ResultT")


@dataclass(frozen=True, slots=True)
class RuntimeBinding(Generic[RuntimeT, InvocationT, ResultT]):
    """Keep a loader, executor, and concurrency policy paired."""

    loader: ModelLoader[RuntimeT]
    executor: ModelExecutor[RuntimeT, InvocationT, ResultT]
    max_concurrency: int


class _RuntimeBindingResolver:  # pyright: ignore[reportUnusedClass]
    """Resolve the closed local runtime family vocabulary before acquisition."""

    def resolve(
        self,
        loader_family: LoaderFamily,
    ) -> RuntimeBinding[object, object, object]:
        """Return the pre-paired internal binding for one explicit family."""
        match loader_family:
            case LoaderFamily.ONNX:
                return RuntimeBinding(
                    loader=_OnnxModelLoader(),
                    executor=_OnnxModelExecutor(),
                    max_concurrency=1,
                )
            case LoaderFamily.PICKLE | LoaderFamily.TORCH:
                raise NotImplementedError
            case _:
                assert_never(loader_family)
