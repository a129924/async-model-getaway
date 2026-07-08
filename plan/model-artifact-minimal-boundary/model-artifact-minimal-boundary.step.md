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

- Current workflow position: 最新獨立 `code-review` verdict 仍是 `needs-rework`，但其唯一 blocker 已收斂為本檔 repo-visible state drift。current `HEAD` 已補上 `ModelArtifact.loader_options` 對 built-in `dict` / `list` bypass 的直接封鎖，並新增對應 regression coverage；exact validation evidence 也已到位：`uv run ruff check docs src tests plan/model-artifact-minimal-boundary`、`uv run pyright` 與 `uv run pytest -q` 皆已通過。repo-visible implementer state 現在對齊 current `HEAD`，後續 reviewer workflows 仍需各自更新 `implementation-review` / `code-review` gate，本檔不預先宣稱其完成。

## Implementation Steps

- [X] 1. 在 `tests/model_artifact/test_model_artifact_package_surface.py`、`tests/model_artifact/test_loader_family.py` 與 `tests/model_artifact/test_model_artifact.py` 新增 RED coverage，並記錄 `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.red-tests.yaml`；測試已先鎖定 public import surface、bounded `LoaderFamily` vocabulary、`ModelArtifact` 最小欄位、non-identity semantics、以及 `LocalModelLoader` 仍缺席的 boundary。
- [X] 2. 新增 `src/async_model_gateway/model_artifact/__init__.py`、`src/async_model_gateway/model_artifact/loader_family.py` 與 `src/async_model_gateway/model_artifact/artifact.py`，使 source layout 維持一檔一概念，而 `async_model_gateway.model_artifact` 只公開 `ModelArtifact` 與 `LoaderFamily`。
- [X] 3. 更新 `docs/architecture.md`、`docs/specs/canonical-input-boundary.md`、`docs/specs/core-abstractions-boundary.md` 與 `docs/specs/model-side-boundary.md`，讓 repo-visible wording 一致表達：`model_artifact` 是 shared read contract、`LoaderFamily` 必須顯式提供、`LoaderFamily` starter vocabulary 只允許 `pickle|torch|onnx`、`ModelArtifact` 只承載 `loader_family` / `artifact_path` / `loader_options`，且 `LocalModelLoader` 仍是 docs-level deferred boundary。
- [X] 4. 執行現行 validation contract：`uv run ruff check docs src tests plan/model-artifact-minimal-boundary`、`uv run pyright` 與 `uv run pytest -q` 已在 current `HEAD` 通過；本次 bounded rework 的 direct regression probes 亦已納入 suite。此步驟現已完成，後續只保留 reviewer-owned gate artifacts 由對應 workflow 更新。
