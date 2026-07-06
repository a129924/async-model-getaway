---
topic: response-cache-operational-minimal-boundary
phase: pr-comment-review-pr-comments-and-fix
created: 2026-07-03
---

# response-cache-operational-minimal-boundary — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [ ] code-review

## Gate Status

- Current workflow position: repo-visible `implementation-review` artifact 已是 `approved / COMPLETE`；此 topic 目前位於 `pr-comment-review-pr-comments-and-fix`，`code-review` 仍未開始。先前 repaired selected pytest suite、`uv run ruff check docs src tests plan/response-cache-operational-minimal-boundary` 與 `uv run pyright` 已於 2026-07-03 通過。

## Implementation Steps

- [X] 1. 在 `tests/response_cache/test_response_cache_package_surface.py`、`tests/response_cache/test_cache.py` 與 `tests/response_cache/test_entry.py` 補上 RED coverage，並記錄 `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.red-tests.yaml`，使新的 operational boundary 先以 tests 鎖定；同時把 `tests/response_cache/test_key.py` 與 `tests/response_cache/test_key_factory.py` 納入 preserve-and-validate regression matrix。
- [X] 2. 新增或更新 `src/async_model_gateway/response_cache/__init__.py`、`src/async_model_gateway/response_cache/cache.py`、`src/async_model_gateway/response_cache/entry.py`、`src/async_model_gateway/response_cache/ports/__init__.py` 與 `src/async_model_gateway/response_cache/ports/store.py`，使 package root re-export `ResponseCache`、`ResponseCacheEntry`、既有 `ResponseCacheKey` 與既有 `ResponseCacheKeyFactory`，並讓 `ResponseCacheStore` 維持 submodule-public。
- [X] 3. 更新 `docs/architecture.md` 與 `docs/specs/response-cache-boundary.md`，使 repo-visible wording 反映：既有 keyed boundary 已存在，而最小 operational `ResponseCache` 現在只透過 async store port 消費 `ResponseCacheKey` 與 `ResponseCacheEntry`。
- [X] 4. 執行 repo-consistent 的 selected pytest suite：`uv run pytest tests/response_cache/test_response_cache_package_surface.py tests/response_cache/test_cache.py tests/response_cache/test_entry.py tests/response_cache/test_key.py tests/response_cache/test_key_factory.py tests/model_registry/model_payload/test_canonical_hash.py tests/model_registry/stores/test_in_memory.py tests/model_registry/stores/test_stores_package_surface.py tests/model_registry/test_freshness_policy.py tests/model_registry/test_registry.py tests/test_package_entrypoint.py tests/test_local_path_guard.py -v`，再執行 `uv run ruff check docs src tests plan/response-cache-operational-minimal-boundary` 與 `uv run pyright`，更新 `plan/response-cache-operational-minimal-boundary/response-cache-operational-minimal-boundary.step.md`，並把 reviewer-owned artifacts 留給後續角色填寫。
