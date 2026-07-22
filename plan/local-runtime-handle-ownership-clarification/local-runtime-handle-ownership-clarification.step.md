---
topic: local-runtime-handle-ownership-clarification
phase: pr-comment
created: 2026-07-21
baseline_branch: feat/andrew/onnx-local-runtime-acquisition
baseline_commit: 31a3d1d
---

# local-runtime-handle-ownership-clarification — Step Tracking

> **Executor**: Mark each step `[X]` only when complete.
> All Implementation Steps must be `[X]` before submitting for
> `python-implementation-review`.
> Update this file at:
> `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Gate Status

- All planning, RED, implementation, implementation-review, and independent code-review
  gates are complete. The code-review artifact records `verdict: approved`.
- Current workflow position: `pr-comment` is the next canonical phase, but no PR review
  surface exists yet.
- Pending human decision: commit, push, and PR creation are not authorized. Stop here
  until Human explicitly authorizes the publish/PR action; this step tracker does not
  treat completed reviews as permission to perform those actions.

## Implementation Steps

- [X] 1. Tester updates the six declared runtime-model/model-pool/model-execution test
  files, the two declared type fixtures, and topic `pyrightconfig.json`; it creates
  test-local concrete handles, adds the static production-tree ownership assertion, and
  records fresh RED evidence before production or docs changes.
- [X] 2. Implementer removes `_LocalLoadedRuntimeModel` and
  `_create_loaded_runtime_model(...)` from
  `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`, while
  retaining the public abstract generic `LoadedRuntimeModel` contract exactly.
- [X] 3. Implementer adds loader-local private concrete handle construction in
  `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`, makes
  `_load_onnx(...)` direct instantiate it after the unchanged helper await, and removes
  the runtime-model private-factory import/suppression without changing routing or
  ONNX/PICKLE/TORCH behavior.
- [X] 4. Implementer updates `docs/specs/model-side-boundary.md` to record opaque
  acquisition-handle semantics, loader-local construction, and unchanged
  `ModelExecution` invocation ownership without describing an executable adapter.
- [X] 5. Implementer runs declared focused/full validation, confirms no changes outside
  Artifact Paths, records only actual progress here, and hands evidence to independent
  implementation/code review.
