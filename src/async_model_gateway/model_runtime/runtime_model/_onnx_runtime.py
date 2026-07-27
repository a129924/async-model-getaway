"""Private minimum protocol for an ONNX provider runtime."""

from __future__ import annotations

from typing import Protocol


class OnnxRuntimeSession(Protocol):
    """Describe the ONNX session capability used by this runtime boundary."""

    def get_providers(self) -> list[str]:
        """Return the provider names configured for this session."""
        ...

    def run(
        self,
        output_names: list[str] | None,
        input_feed: dict[str, object],
        run_options: object | None,
    ) -> list[object]:
        """Run one provider invocation."""
        ...
