---
topic: model-registry-minimal-boundary
phase: plan-authoring
created: 2026-06-22
---

# model-registry-minimal-boundary — Step Tracking

> **Executor**: 完成後將每個步驟標記為 `[X]`。
> 在送交 `python-implementation-review` 之前，所有 Implementation Steps 都必須為 `[X]`。
> 請在 `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.step.md` 更新此檔。

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Gate Status

- Reviewer verdict: `approved`
- Human check: pending
- Current workflow position: `spec-and-plan-finalization` 仍在等待 repo-visible `human check`；`implement-plan`、`publish-in-progress` 與後續 workflow stages 尚未開始。

## Implementation Steps

- [ ] 1. 在 `tests/model_registry/test_package_surface.py`、`tests/model_registry/test_registry.py` 與 `tests/model_registry/test_freshness_policy.py` 補上非同步 RED coverage，並記錄 `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.red-tests.yaml`，使測試鎖定 async-only boundary、root re-export policy、僅限 `ports/` 的 abstract surface、`model_name + model_source_kind` lookup identity、未變更的 hasher contract，以及固定的 `RegistryFreshnessResult` shape。
- [ ] 2. 新增 `src/async_model_gateway/model_registry/registry.py`、`src/async_model_gateway/model_registry/entry.py`、`src/async_model_gateway/model_registry/freshness_policy.py`、`src/async_model_gateway/model_registry/freshness_result.py`、`src/async_model_gateway/model_registry/ports/__init__.py`、`src/async_model_gateway/model_registry/ports/store.py`，並更新 `src/async_model_gateway/model_registry/__init__.py`，使 source layout 維持一檔一概念、`RegistryStore` 仍是唯一 abstract collaborator、`ModelRegistry` 仍是唯一 root re-export，且 `ModelPayloadHasher` 以原樣被使用。
- [ ] 3. 更新 `README.md`、`docs/architecture.md`、`docs/specs/canonical-input-boundary.md` 與 `docs/specs/model-side-boundary.md`，使 repo-visible wording 正確反映最小 async-only `ModelRegistry` boundary、`ports/` store contract，以及受限的 freshness flow，且不擴張到 cache、gateway、pool 或 orchestrator implementation work。
- [ ] 4. 執行 `uv run pytest tests/model_registry/test_package_surface.py tests/model_registry/test_registry.py tests/model_registry/test_freshness_policy.py -v`、`uv run ruff check README.md docs src tests plan/model-registry-minimal-boundary` 與 `uv run pyright`，然後再更新 `plan/model-registry-minimal-boundary/model-registry-minimal-boundary.step.md`，以反映 implementer 擁有的工作已完成，之後才交給 reviewer 檢查。
