"""Bounded loader-family vocabulary for local model artifacts."""

from __future__ import annotations

from enum import Enum

__all__ = ["LoaderFamily"]


class LoaderFamily(str, Enum):
    """Allowed explicit loader families for the shared read contract."""

    PICKLE = "pickle"
    TORCH = "torch"
    ONNX = "onnx"
