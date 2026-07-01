---
topic: model-registry-in-memory-store
phase: plan-authoring
created: 2026-07-01
---

# model-registry-in-memory-store — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/model-registry-in-memory-store/model-registry-in-memory-store.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [ ] 1. 在 `tests/model_registry/stores/test_in_memory.py` 撰寫 RED coverage，鎖定 `InMemoryRegistryStore` 的 empty-only constructor、`model_name + model_source_kind` lookup identity、first upsert / overwrite behavior、missing-entry return path，以及相同 instance 上以單一 `asyncio.Lock` 序列化讀寫的 contract。
- [ ] 2. 在 `tests/model_registry/stores/test_stores_package_surface.py` 與 `tests/model_registry/test_package_surface.py` 撰寫或更新 package-surface coverage，鎖定 store 只透過 `model_registry.stores` submodule public surface 暴露，且 `async_model_gateway.model_registry` root package 不得 re-export `InMemoryRegistryStore`。
- [ ] 3. 新增 `src/async_model_gateway/model_registry/stores/in_memory.py` 與 `src/async_model_gateway/model_registry/stores/__init__.py`，讓 `InMemoryRegistryStore` 成為 `RegistryStore` concrete subclass，維持 empty-only `__init__()`、單一 `asyncio.Lock`、以及 `typing_extensions.override` 標註的 async `get_entry()` / `upsert_entry()`。
- [ ] 4. 更新 `README.md`、`docs/specs/model-side-boundary.md`、`docs/specs/canonical-input-boundary.md` 與 `docs/specs/core-abstractions-boundary.md`，以最小必要 wording 反映新的 in-memory store、submodule public surface、以及未變更的 lookup identity boundary。
- [ ] 5. 在 `src/async_model_gateway/__version__.py` 與 `pyproject.toml` 規劃並實作 patch bump，讓 release-facing metadata 與 topic scope 對齊；不得擴張成 major/minor release work。
- [ ] 6. 執行本 topic 的 bounded validation，更新 `plan/model-registry-in-memory-store/model-registry-in-memory-store.step.md`，並在後續 workflow 需要時產出 implementer-owned 的 `model-registry-in-memory-store.red-tests.yaml` 與其他 implementer-owned bounded evidence，確認本 topic 的 repo-visible validation evidence 已完成並可供後續 gate 檢查。
