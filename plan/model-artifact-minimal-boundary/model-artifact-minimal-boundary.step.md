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
- [X] implementation-review
- [X] code-review

## Gate Status

- Current workflow position: reviewer-owned `implementation-review` artifact 現已為 `approved`；最新獨立 `code-review` verdict 為可直接前進。reviewer 端已重跑 exact validation 並通過：`uv run pytest -q` => `126 passed`, coverage `99.29%`；`uv run ruff check docs src tests plan/model-artifact-minimal-boundary` => passed；`uv run pyright` => passed。dispatcher 目前停在下一個 `human-check` 邊界。

## Implementation Steps

- [X] 1. 在 `tests/model_artifact/test_model_artifact_package_surface.py`、`tests/model_artifact/test_loader_family.py` 與 `tests/model_artifact/test_model_artifact.py` 新增 RED coverage，並記錄 `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.red-tests.yaml`；測試已先鎖定 public import surface、bounded `LoaderFamily` vocabulary、`ModelArtifact` 最小欄位、non-identity semantics、以及 `LocalModelLoader` 仍缺席的 boundary。
- [X] 2. 新增 `src/async_model_gateway/model_artifact/__init__.py`、`src/async_model_gateway/model_artifact/loader_family.py` 與 `src/async_model_gateway/model_artifact/artifact.py`，使 source layout 維持一檔一概念，而 `async_model_gateway.model_artifact` 只公開 `ModelArtifact` 與 `LoaderFamily`。
- [X] 3. 更新 `docs/architecture.md`、`docs/specs/canonical-input-boundary.md`、`docs/specs/core-abstractions-boundary.md` 與 `docs/specs/model-side-boundary.md`，讓 repo-visible wording 一致表達：`model_artifact` 是 shared read contract、`LoaderFamily` 必須顯式提供、`LoaderFamily` starter vocabulary 只允許 `pickle|torch|onnx`、`ModelArtifact` 只承載 `loader_family` / `artifact_path` / `loader_options`，且 `LocalModelLoader` 仍是 docs-level deferred boundary。
- [X] 4. 執行現行 validation contract：`uv run ruff check docs src tests plan/model-artifact-minimal-boundary`、`uv run pyright` 與 `uv run pytest -q` 已在 current `HEAD` 通過；本次 bounded rework 的 direct regression probes 亦已納入 suite。此步驟現已完成，後續只保留 reviewer-owned gate artifacts 由對應 workflow 更新。
