---
topic: model-artifact-minimal-boundary
phase: implement-plan
created: 2026-07-07
---

# model-artifact-minimal-boundary — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [ ] implementation-review
- [ ] code-review

## Gate Status

- Current workflow position: `implement-plan` 已完成；`ModelArtifact` public constructor typing 已對齊 locked contract，topic tests 已補齊合法空 dict 與合法巢狀 JSON-like `loader_options` 正向 edge cases，且現行 validation contract `uv run pytest -q`、`uv run ruff check docs src tests plan/model-artifact-minimal-boundary` 與 `uv run pyright` 皆已通過，等待 reviewer 重跑 implementation review verdict。

## Implementation Steps

- [X] 1. 在 `tests/model_artifact/test_model_artifact_package_surface.py`、`tests/model_artifact/test_loader_family.py` 與 `tests/model_artifact/test_model_artifact.py` 新增 RED coverage，並記錄 `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.red-tests.yaml`；測試已先鎖定 public import surface、bounded `LoaderFamily` vocabulary、`ModelArtifact` 最小欄位、non-identity semantics、以及 `LocalModelLoader` 仍缺席的 boundary。
- [X] 2. 新增 `src/async_model_gateway/model_artifact/__init__.py`、`src/async_model_gateway/model_artifact/loader_family.py` 與 `src/async_model_gateway/model_artifact/artifact.py`，使 source layout 維持一檔一概念，而 `async_model_gateway.model_artifact` 只公開 `ModelArtifact` 與 `LoaderFamily`。
- [X] 3. 更新 `docs/architecture.md`、`docs/specs/canonical-input-boundary.md`、`docs/specs/core-abstractions-boundary.md` 與 `docs/specs/model-side-boundary.md`，讓 repo-visible wording 一致表達：`model_artifact` 是 shared read contract、`LoaderFamily` 必須顯式提供、`LoaderFamily` starter vocabulary 只允許 `pickle|torch|onnx`、`ModelArtifact` 只承載 `loader_family` / `artifact_path` / `loader_options`，且 `LocalModelLoader` 仍是 docs-level deferred boundary。
- [X] 4. 執行現行 validation contract：`uv run pytest -q`、`uv run ruff check docs src tests plan/model-artifact-minimal-boundary` 與 `uv run pyright`；三者皆已通過，full-suite pytest 為 92 passed，repo-wide coverage 為 97.22%，因此 implementer-owned execution evidence 已完成，後續只待 reviewer 產出新的 implementation-review verdict。
