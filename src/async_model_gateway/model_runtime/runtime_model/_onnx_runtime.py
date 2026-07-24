"""Private minimum protocol for an ONNX provider runtime."""

from __future__ import annotations

from typing import Protocol


class _OnnxRuntime(Protocol):  # pyright: ignore[reportUnusedClass]
    """Describe the ONNX session capability used by this runtime boundary."""

    def get_providers(self) -> list[str]:
        """Return the provider names configured for this session."""
        ...
