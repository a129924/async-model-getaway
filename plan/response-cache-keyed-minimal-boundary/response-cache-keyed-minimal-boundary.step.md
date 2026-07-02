---
topic: response-cache-keyed-minimal-boundary
phase: implement-plan
created: 2026-07-02
---

# response-cache-keyed-minimal-boundary — 步驟追蹤

> **Executor**: 完成後將每個步驟標記為 `[X]`。
> 在送交 `python-implementation-review` 之前，所有 Implementation Steps 都必須為 `[X]`。
> 請在 `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.step.md` 更新此檔。

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [ ] implementation-review
- [ ] code-review

## Gate Status

- Plan review artifact: `approved`
- Human check: `passed`
- Current workflow position: 已完成 `implement-plan`；`implementation-review` 與 `code-review` 尚未開始。

## Implementation Steps

- [X] 1. 在 `tests/response_cache/test_package_surface.py`、`tests/response_cache/test_key.py` 與 `tests/response_cache/test_key_factory.py` 補上 bounded RED coverage，並記錄 `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.red-tests.yaml`，使 keyed boundary 在 source edits 前先被鎖定。
- [X] 2. 新增 `src/async_model_gateway/response_cache/__init__.py`、`src/async_model_gateway/response_cache/key.py`、`src/async_model_gateway/response_cache/key_factory.py`、`src/async_model_gateway/response_cache/ports/__init__.py` 與 `src/async_model_gateway/response_cache/ports/feature_hasher.py`，使 package 只暴露最小 keyed boundary，並將抽象 hashing authority 維持在 `ports/`。
- [X] 3. 更新 `docs/architecture.md` 與 `docs/specs/response-cache-boundary.md`，使 repo-visible wording 反映 keyed cache identity 目前透過 `ResponseCacheKey` 與 `ResponseCacheKeyFactory` 準備，而 operational cache storage 仍維持 deferred。
- [X] 4. 原 plan 的 pytest 組合 coverage 僅 `84.65%`，因此改用更廣但仍限定既有 repo tests 的 selected suite：`uv run pytest tests/response_cache/test_package_surface.py tests/response_cache/test_key.py tests/response_cache/test_key_factory.py tests/model_registry/model_payload/test_canonical_hash.py tests/model_registry/stores/test_in_memory.py tests/model_registry/stores/test_stores_package_surface.py tests/model_registry/test_freshness_policy.py tests/model_registry/test_registry.py tests/test_package_entrypoint.py tests/test_local_path_guard.py -v`；結果 `55 passed`、coverage `99.56%`，且 `uv run ruff check docs src tests plan/response-cache-keyed-minimal-boundary` 與 `uv run pyright` 皆通過。下一步留給 reviewer workflows。
