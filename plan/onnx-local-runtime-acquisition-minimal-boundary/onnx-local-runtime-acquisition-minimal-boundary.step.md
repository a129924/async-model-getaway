---
topic: onnx-local-runtime-acquisition-minimal-boundary
phase: plan-authoring
created: 2026-07-18
---

# onnx-local-runtime-acquisition-minimal-boundary — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [ ] 1. Tester creates `test_onnx_local_runtime_acquisition.py` with a temporary ONNX model built by static `onnx` imports, updates `test_local_model_loader.py` so only PICKLE/TORCH default handlers remain fail-closed, adds the static type fixture and `pyrightconfig.json`, then records fresh RED evidence before production edits.
- [ ] 2. Implementer updates `pyproject.toml` and `uv.lock` with the locked `onnx` optional extra and dev `onnx` fixture dependency; no version/release metadata changes.
- [ ] 3. Implementer adds `_onnx_runtime_loader.py` with private lazy import, pre-load empty options validation, exact missing-extra translation, and CPU-only `asyncio.to_thread(...)` session creation.
- [ ] 4. Implementer updates `_local_model_loader.py` so `_load_onnx(...)` awaits the helper and calls `_create_loaded_runtime_model(...)`; it does not alter PICKLE/TORCH, explicit match/case routing, `assert_never`, or public annotations.
- [ ] 5. Implementer runs validation, verifies only `Written`/`Updated` paths changed, updates the actual step state, and hands the topic to independent implementation/code review.
