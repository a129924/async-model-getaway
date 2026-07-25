---
topic: onnx-minimal-model-loader-validation
phase: implementation
created: 2026-07-25
---

# onnx-minimal-model-loader-validation — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Implementation Steps

- [X] 1. Tester creates fresh RED coverage and the dedicated Protocol witness for the exact runtime/static evidence contract, then records only the declared RED evidence.
- [X] 2. Tester creates the deterministic Identity-model generator and committed ONNX asset, including non-writing byte-drift `--check` behavior.
- [X] 3. Implementer updates `tests/model_runtime/model_pool/test_onnx_model_loader.py` with real Loader session/provider/invalid-artifact evidence and no inference.
- [X] 4. Implementer updates `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` to use the committed asset while retaining existing async/error coverage.
- [X] 5. Tester creates the topic-local strict Pyright config and the no-provider Protocol witness without changing production/global typing.
- [X] 6. Implementer runs validation, verifies scope/path compliance, truthfully updates step state, and hands off for independent review.
