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

- The original handle-ownership implementation evidence remains historical truth, but
  all original source/docs/tests/type fixtures and the existing CI diff are now
  Historical ReadOnly preserve-and-verify context, not current Implementer targets.
- The exact authorized `.github/workflows/ci.yml` `--extra onnx` diff already exists in
  the worktree and has been preserved and verified without workflow rewrite.
- Fresh revised-scope Plan-Reviewer verdict is recorded as `approved` in the declared
  `local-runtime-handle-ownership-clarification.plan-review.json` artifact; the
  refreshed Human state `cleared_for: implement-plan` authorized this bounded work.
- Exactly one final LF has been added to each of the three declared human-check JSON
  targets. Raw diff inspection confirms no JSON text, semantics, ordering, indentation,
  or other non-final byte changed.
- CI-parity validation passes: `uv lock --check`, frozen dev-plus-ONNX sync, no-sync
  Pyright, pytest, `pre-commit run --all-files`, and `git diff --check` all pass.
- Validation-hygiene retrofit D1 is `trivial`: its existing CI workflow-line diff plus
  three final-LF normalizations require no fresh RED, test edit, or CI-specific spec.
  Existing RED/spec artifacts remain historical evidence for the completed original
  handle-ownership implementation.
- Current Implementer writable boundary is exact: only the three declared human-check
  JSON final-LF paths. Plan/step, plan-review, review, and human-gate artifacts remain
  separately owned by their declared actors.
- The declared implementation-review artifact records `verdict: approved` with no
  blocking, scope, or contract drift. The declared code-review artifact also records
  `verdict: approved` with no findings or code-quality rework.
- All validation-hygiene retrofit gates are complete. Current workflow position:
  `pr-comment` / Human handoff. No new commit, push, PR creation, or PR update has been
  performed; Human authorization is required before any publish or PR action.

## Implementation Steps

> Steps 1–5 are completed historical handle-ownership evidence and are ReadOnly for
> this retrofit. Step 6 preserves/verifies an existing Historical ReadOnly CI diff.
> Only step 8 writes files, and it may write only the three declared final-LF targets.

- [X] 1. Historical ReadOnly — Tester updated the six declared runtime-model/model-pool/model-execution test
  files, the two declared type fixtures, and topic `pyrightconfig.json`; it creates
  test-local concrete handles, adds the static production-tree ownership assertion, and
  records fresh RED evidence before production or docs changes.
- [X] 2. Historical ReadOnly — Implementer removed `_LocalLoadedRuntimeModel` and
  `_create_loaded_runtime_model(...)` from
  `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`, while
  retaining the public abstract generic `LoadedRuntimeModel` contract exactly.
- [X] 3. Historical ReadOnly — Implementer added loader-local private concrete handle construction in
  `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`, makes
  `_load_onnx(...)` direct instantiate it after the unchanged helper await, and removes
  the runtime-model private-factory import/suppression without changing routing or
  ONNX/PICKLE/TORCH behavior.
- [X] 4. Historical ReadOnly — Implementer updated `docs/specs/model-side-boundary.md` to record opaque
  acquisition-handle semantics, loader-local construction, and unchanged
  `ModelExecution` invocation ownership without describing an executable adapter.
- [X] 5. Historical ReadOnly — Implementer ran declared focused/full validation, confirmed no changes outside
  Artifact Paths, records only actual progress here, and hands evidence to independent
  implementation/code review.
- [X] 6. After fresh plan-review and refreshed human-check, Implementer preserved and
  verified the existing Historical ReadOnly `.github/workflows/ci.yml` `Sync dependencies`
  `uv sync --frozen --group dev --extra onnx` diff without rewriting the workflow.
- [X] 7. Implementer ran CI-parity validation without writing the Historical ReadOnly
  context: `uv lock --check`, frozen dev-plus-ONNX
  sync, no-sync Pyright, pytest, pre-commit all-files, and `git diff --check`; it
  confirmed the existing CI diff plus no dependency/API/source/test/lock/suppression or
  lazy-import-ignore change.
- [X] 8. Implementer appended exactly one final LF to each declared ONNX acquisition,
  handle-ownership, and documentation-consistency human-check JSON; no JSON text,
  value, key order, indentation, or other byte changed.
- [X] 9. Implementer ran all declared CI-parity and `pre-commit run --all-files`
  checks, then inspected each raw JSON diff to confirm only the missing-final-newline
  marker changed before independent review.
