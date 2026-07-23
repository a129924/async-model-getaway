---
topic: pr-18-remove-dynamic-onnx-import-test
phase: pr-comment
state: awaiting-human-merge-gate
next_state: merged
created: 2026-07-23
---

# pr-18-remove-dynamic-onnx-import-test — Step Tracking

> **Executor**: Mark each step `[X]` only when complete.
> All Implementation Steps must be `[X]` before submitting for
> `python-implementation-review`.
> Update this file at:
> `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review
- [X] pr-comment-review-and-pr-comment-fix
- [ ] human-merge-gate (Human)

## Completed Evidence

- Independent Plan-Reviewer 已核准
  `pr-18-remove-dynamic-onnx-import-test.plan-review.json`，Human gate 為
  `cleared_for: implement-plan`。
- Tester 的 fresh RED evidence 已記錄在
  `pr-18-remove-dynamic-onnx-import-test.red-tests.yaml`。
- Private typed importer seam 已完成於
  `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`；production
  default 仍是 lazy `onnxruntime.InferenceSession` import。
- Dynamic module-table setup 已由 focused test 移除，改用 injected callable。
- Validation passed:
  - focused ONNX acquisition pytest: 10 passed
  - model-pool/model-execution pytest: 35 passed
  - full pytest: 185 passed
  - Pyright: 0 errors, 0 warnings
  - Ruff: passed
  - pre-commit: passed
  - governance `rg`: no matches (expected exit 1)
  - `git diff --check`: passed

- Independent implementation review approved
  `pr-18-remove-dynamic-onnx-import-test.implementation-review.yaml`; it found no
  scope drift or contract drift.
- Independent code review approved
  `pr-18-remove-dynamic-onnx-import-test.code-review.yaml`; it found no Python
  quality, typing, lint, error-handling, anti-pattern, or test-quality finding.
- The bounded PR comment fix was committed and pushed as `354f466`
  (`fix(model-runtime): remove dynamic ONNX import tests`), updating PR #18.
- PR #18 thread `PRRT_kwDOS7D3Es6TIo9V` was replied to and resolved after the
  approved implementation was published.
- PR #18 CI completed successfully after the update.

## Human Merge Gate

- `pr-comment-review-and-pr-comment-fix` is complete: the named actionable
  thread is replied to and resolved, and the published PR update has green CI.
- The next state is the explicit Human `human-merge-gate`. No actor may merge
  PR #18, alter the PR state, or start a release without separate Human merge
  authorization.
- This topic has no release workflow. Only after a Human merge decision may its
  state become `merged`; it then stops.

下一步：等待 Human 明確決定是否 merge PR #18；不得自動 merge 或進行 release。

## Implementation Steps

- [X] 1. Tester adds fresh RED coverage in `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` using only ordinary static imports and injected typed callables: prove the existing source has no supported callable seam while preserving the named top-level/nested `ModuleNotFoundError` expectations; record the result in the declared RED artifact.
- [X] 2. Implementer updates only `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`: separate the real private lazy import into a fully typed zero-argument importer and accept a private test-only callable override at the helper boundary; centralize exact top-level-missing translation around that seam while retaining options validation, `asyncio.to_thread(...)`, and CPU-only construction unchanged.
- [X] 3. Implementer updates only `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`: delete `sys`/`ModuleType` imports and all module-table mutation; inject callable factories for real construction, provider failure, top-level missing dependency, nested missing dependency, thread-offload, and cancellation tests as needed, without weakening their assertions or adding dynamic module loading.
- [X] 4. Implementer runs the declared focused, full, typing, lint, governance-source, and diff checks; confirms only `Written`/`Updated` paths changed; updates the step tracker only with actual completed work; then hands the topic to independent implementation and code review.
