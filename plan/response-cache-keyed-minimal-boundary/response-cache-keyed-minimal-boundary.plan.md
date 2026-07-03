# response-cache-keyed-minimal-boundary

## Goal / Outcome

- 凍結一個 repo-visible、最小且 keyed 的 response-cache boundary，使後續 Python implementation 能新增 `ResponseCacheKey`、`ResponseCacheKeyFactory` 與 bounded `FeatureHasher` collaborator，而不必重新打開更寬的 cache architecture。
- 當此 topic 完成時，repository 會擁有嚴格的 analysis layer 與 Python planning companions，明確鎖定 hash authority、精確 artifact paths，以及未來 `ResponseCache` runtime behavior 必須消費 `ResponseCacheKey`、而不是自行計算 hashes 的規則。

## Scope

- **In scope**:
  - 在 `analysis/response-cache-keyed-minimal-boundary/requirements.md` 與 `analysis/response-cache-keyed-minimal-boundary/technical-spec.md` 建立 analysis-layer baseline。
  - 在 `plan/response-cache-keyed-minimal-boundary/` 建立 repo-visible planning artifacts。
  - 規劃 `ResponseCacheKey`、`ResponseCacheKeyFactory`、`FeatureHasher` port，以及此 keyed boundary 所需最小文件對齊的 bounded Python implementation。
  - 凍結未來 implementation 會接觸的 source、tests 與 docs 路徑，但不引入 runtime cache storage behavior。

- **Out of scope**:
  - 任何 cache store、backend、persistence schema、TTL、eviction 或 cache-value representation。
  - 任何 `orchestrator` wiring、cache hit/miss flow 或 runtime response generation behavior。
  - 任何將 `features` 擴張超出 `Mapping[str, str]` 的行為，或 broader `feature-hash` authority 的擴張。
  - 任何對 `ModelPayloadHasher` ownership、signature 或 hashing semantics 的變更。
  - 任何 stable-library、release、tag 或 versioning work。

## Locked Decisions

- Analysis-layer strict mode 已啟用：`analysis/response-cache-keyed-minimal-boundary/technical-spec.md` 是 execution-facing source of truth，而 `analysis/response-cache-keyed-minimal-boundary/requirements.md` 是 business guardrail。chat-time scope 不覆蓋這兩份 artifact。
- 此 topic 明確採用 Python planning extension path，並要求 companion `*.spec.md` 與 `*.step.md` artifacts。
- D1 verdict: `non-trivial`。此 topic 會引入新的 public Python surfaces、新 tests，以及跨多個檔案的 bounded documentation updates。
- `ResponseCache` 不擁有 payload-hash 或 feature-hash authority。此 topic 凍結的規則是：任何未來 runtime `ResponseCache` surface 都只消費 `ResponseCacheKey`。
- `ResponseCacheKey` 欄位固定為：
  - `namespace: str`
  - `model_payload_hash: str`
  - `feature_hash: str`
- `ResponseCacheKeyFactory` 必須：
  - 在建構時持有 `FeatureHasher`
  - 在 `build(...)` 中顯式接收 `namespace`
  - 在 `build(...)` 中顯式接收 `model_payload_hash: str`
  - 在 `build(...)` 中顯式接收 `features: Mapping[str, str]`
- `features` 在此 topic 中凍結為 `Mapping[str, str]`。
- 此 topic 不引入 operational `ResponseCache` storage API，因為 store/backend/schema/TTL/eviction 明確不在範圍內。source-level minimum 只包含 key/factory/port package split，以及約束未來 cache ownership 的 docs。
- 此 topic 是 non-stable-library。`## Stable library metadata` 刻意省略，且不宣告 release workflow。

## Boundaries / Exclusions

- Planning actor 只負責此 topic 中 creator-owned 的 analysis 與 planning artifacts。
- Implementer 只能修改 `## Artifact Paths` 中列出的精確 doc、source、test 與 topic-artifact paths。
- Reviewer 提供獨立的 plan review 與後續 implementation-review evidence；reviewer 不撰寫 implementation steps，也不代替 human 關 gate。
- Human-owned 的 `human check` 與 `human merge` gates 仍然位於 creator-owned artifacts 之外，不能在此處預填。
- 未來任何需要 cache storage、backend lifecycles、runtime cache value semantics 或 orchestrator integration 的工作，都必須以新 topic 回到 `spec-and-plan-finalization`。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`; stop at `merged`，因為此 topic 不使用條件式 `release` workflow。
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`

Routing notes:

- `approved` 需要 repo-visible plan-review artifact 為 `approved`，以及另一個獨立的 repo-visible `human check`。
- 此 topic 使用 Python planning extension path。在 `implement-plan` 期間，RED test authoring 是 source edits 之前的第一個必要 Python 子階段。
- `*.step.md`、`*.spec.md`、`*.red-tests.yaml` 與 `*.implementation-review.yaml` 都只是 workflow companion artifacts；在宣告 gate 真正通過前，它們本身不代表 approval。
- 因為主 worktree 與這個 managed worktree 都可能碰 planning/governance files，避免多個 worktree 平行修改此 topic 的 `analysis/` 與 `plan/` 路徑。
- 任何超出已宣告 keyed boundary、精確 artifact paths 或已凍結 input contracts 的 drift，都必須讓此 topic 回到 `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Requirements baseline | `analysis/response-cache-keyed-minimal-boundary/requirements.md` | Planning actor | keyed cache boundary 的 frozen business-intent baseline |
| Technical specification | `analysis/response-cache-keyed-minimal-boundary/technical-spec.md` | Planning actor | downstream planning 必須遵守的 execution-facing technical baseline |
| Topic plan | `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.plan.md` | Planning actor | 此 topic 的 repo-visible execution contract |
| Topic step tracking | `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.step.md` | Implementer | repo-visible implementation-progress companion artifact |
| Topic behavior spec | `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.spec.md` | Planning actor | non-trivial Python behavior contract，供 TDD 與後續 review 使用 |
| Plan review artifact | `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| RED test artifact | `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.red-tests.yaml` | Implementer | `implement-plan` 期間產出的 repo-visible TDD gate evidence |
| Implementation review artifact | `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.implementation-review.yaml` | Reviewer | repo-visible implementation-review gate evidence |
| Architecture summary | `docs/architecture.md` | Implementer | 對齊 minimal keyed response-cache boundary 的高層 wording |
| Response-cache boundary spec | `docs/specs/response-cache-boundary.md` | Implementer | 將 repo-visible cache-boundary wording 對齊 `ResponseCacheKey` 與 factory ownership |
| Response-cache package root | `src/async_model_gateway/response_cache/__init__.py` | Implementer | 最小 keyed response-cache package 的 root import surface |
| Response-cache key value surface | `src/async_model_gateway/response_cache/key.py` | Implementer | concrete `ResponseCacheKey` value object |
| Response-cache key factory | `src/async_model_gateway/response_cache/key_factory.py` | Implementer | 消費顯式 payload hash 並委派 feature hashing 的 concrete `ResponseCacheKeyFactory` |
| Response-cache ports package root | `src/async_model_gateway/response_cache/ports/__init__.py` | Implementer | bounded response-cache abstract collaborators 的 package surface |
| Feature hasher port | `src/async_model_gateway/response_cache/ports/feature_hasher.py` | Implementer | 此 topic 中 keyed boundary 擁有的唯一 abstract collaborator |
| Response-cache package-surface tests | `tests/response_cache/test_response_cache_package_surface.py` | Implementer | 驗證 root export policy 與 bounded submodule exposure |
| Response-cache key tests | `tests/response_cache/test_key.py` | Implementer | 驗證固定三欄位的 key surface |
| Response-cache factory tests | `tests/response_cache/test_key_factory.py` | Implementer | 驗證 explicit input routing、delegation 與 fail-closed behavior |

Artifact path notes:

- 此 topic 不修改 `README.md`、`VERSION`、`.github/copilot-instructions.md`，也不碰任何 `orchestrator` 或 backend paths。
- Treat listed paths as an executable contract.
- 若後續工作需要 concrete `ResponseCache` runtime API、cache-value schema 或 store integration path，必須停止並回到 `spec-and-plan-finalization`。

## Implementation Steps

1. 在 `tests/response_cache/test_response_cache_package_surface.py`、`tests/response_cache/test_key.py` 與 `tests/response_cache/test_key_factory.py` 補上 bounded RED coverage，並記錄 `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.red-tests.yaml`，使 keyed boundary 在 source edits 前先被鎖定。
2. 新增 `src/async_model_gateway/response_cache/__init__.py`、`src/async_model_gateway/response_cache/key.py`、`src/async_model_gateway/response_cache/key_factory.py`、`src/async_model_gateway/response_cache/ports/__init__.py` 與 `src/async_model_gateway/response_cache/ports/feature_hasher.py`，使 package 只暴露最小 keyed boundary，並將抽象 hashing authority 維持在 `ports/`。
3. 更新 `docs/architecture.md` 與 `docs/specs/response-cache-boundary.md`，使 repo-visible wording 反映 keyed cache identity 現在透過 `ResponseCacheKey` 與 `ResponseCacheKeyFactory` 準備，而 operational cache storage 仍維持 deferred。
4. 執行 repo-consistent 的 selected pytest suite：`uv run pytest tests/response_cache/test_response_cache_package_surface.py tests/response_cache/test_key.py tests/response_cache/test_key_factory.py tests/model_registry/model_payload/test_canonical_hash.py tests/model_registry/stores/test_in_memory.py tests/model_registry/stores/test_stores_package_surface.py tests/model_registry/test_freshness_policy.py tests/model_registry/test_registry.py tests/test_package_entrypoint.py tests/test_local_path_guard.py -v`，再執行 `uv run ruff check docs src tests plan/response-cache-keyed-minimal-boundary` 與 `uv run pyright`，然後更新 `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.step.md`，再把 topic 交給 reviewer workflows。

## Validation / Acceptance Checks

- Canonical topic-plan sections、status names、transitions 與 reviewer handoff shape 必須持續符合 `plan/topic-plan-contract.md` 與 `plan/agent-handoff-workflow.md`。
- analysis layer 必須完整：`requirements.md` 與 `technical-spec.md` 兩者都存在，且 plan 採 strict analysis routing。
- `response-cache-keyed-minimal-boundary.spec.md` 存在，因為此 topic 被鎖為 `non-trivial`。
- `response-cache-keyed-minimal-boundary.step.md` 必須 mirror 每個編號 implementation step，且在實際到達後續 phases 前，不得預先完成後續 workflow stages。
- 不得有任何 artifact path 或 implementation step 引入 store、backend、schema、TTL、eviction、broader feature-hash authority 或 orchestrator wiring。
- pytest validation evidence 必須使用已宣告的 selected suite，並在 repository coverage gate 下通過；不得以未回寫到 creator-owned contract 的替代命令取代。
- validation evidence 必須證明 `ResponseCacheKeyFactory` 接受 `model_payload_hash: str` 與 `features: Mapping[str, str]`、將 feature hashing 委派給持有的 `FeatureHasher`，且不會在 factory 或任何未來 `ResponseCache` runtime owner 內自行計算 payload hash。
- package-surface validation 必須證明 root exports 仍限於最小 keyed package surface，而 `FeatureHasher` port 維持在 package root 之外。

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- No release workflow required.
- merge 後停止；不要在此 topic 下新增 version bumps、tags、release notes 或 stable-library publication work。

## Open Questions / Unresolved Items

- None.

## Non-goals

- 此 topic 不引入 runtime cache backend 或 cache-value storage semantics。
- 此 topic 不加入 `ResponseCache` 的 orchestrator wiring 或 hit/miss runtime flow。
- 此 topic 不將 `features` 擴張超出 `Mapping[str, str]`。
- 此 topic 不重新打開 `ModelPayloadHasher` ownership 或 hashing semantics。
- 此 topic 不在同一 slug 下建立更寬的 `feature-hash` authority topic。

## Current Context

- repository 目前在 `README.md`、`docs/architecture.md` 與 `docs/specs/response-cache-boundary.md` 中已有 response-cache wording，但尚未存在 `src/async_model_gateway/response_cache/` package。
- 目前架構已說明 `ResponseCache` 依賴 payload-hash 加上 features，而 `ModelPayloadHasher` 是既有的 payload hashing public owner。
- 目前尚無 response-cache source 或 tests，因此這個 topic 必須先凍結最小 keyed boundary，之後才能誠實地新增任何 cache runtime behavior。
- frozen topic contract 明確禁止 backend、schema、TTL、eviction 與 orchestrator wiring work，因此 source-level minimum 必須比完整 operational cache API 更窄。

## Requirements

1. 此 topic 的 package root 必須暴露一個最小 keyed response-cache surface，使 downstream code 可以 import，而不需觸及未來 backend 或 orchestration concerns。
2. `ResponseCacheKey` 必須只包含 `namespace`、`model_payload_hash` 與 `feature_hash`，且三者型別都為 `str`。
3. `ResponseCacheKeyFactory` 必須要求顯式 `namespace`、顯式 `model_payload_hash: str` 與顯式 `features: Mapping[str, str]`，且在建構時持有 `FeatureHasher`。
4. Payload hashing authority 必須維持在既有 `ModelPayloadHasher` 的 upstream owner；feature hashing authority 必須維持在 bounded `FeatureHasher` collaborator；factory 只負責協調這些 inputs。
5. 此 topic 必須維持在此 plan 宣告的精確 docs、source、test 與 planning paths 之內。
6. 此 topic 不得引入 store、backend、schema、TTL、eviction、runtime cache-value semantics 或 orchestrator integration。
7. 在 implementation 開始前，此 topic 必須提供可供 review 的 Python companion artifacts 與 validation commands。

## Decisions

- Async-planning status: exempt — cite exemption evidence: 此 topic 只引入同步的 value、factory 與 hashing-port surfaces；不包含 async boundary、resource lifecycle、timeout、cancellation 或 concurrency 決策，而且 operational `ResponseCache` storage behavior 因為 store/backend work 不在範圍內而明確延後。
- Module/package placement: 在 `src/async_model_gateway/response_cache/` 下新增 package，包含 `key.py`、`key_factory.py` 與 `ports/feature_hasher.py`；docs 更新則限於 `docs/architecture.md` 與 `docs/specs/response-cache-boundary.md`。
- New public API: yes — 此 topic 在 package root 新增 `ResponseCacheKey` 與 `ResponseCacheKeyFactory`，且只新增這兩個 public surfaces。
- Interface changes: yes — `async_model_gateway.response_cache` 會成為真實 package root，而 `FeatureHasher` 保持為 `response_cache.ports` 下的 submodule-public surface。
- Breaking changes allowed: no — 此 topic 只新增 bounded surfaces 與 docs alignment；不修改既有 public contracts。
- New dependencies: no — 重用現有 repository toolchain 與既有 upstream payload-hash contract。
- Error handling strategy: feature hashing failures原樣傳播；factory 不新增 fallback coercion、normalization 或新的 exception taxonomy，upstream payload hashing failure 仍由既有 owner 負責。
- Typing strategy: 在 repository 的 strict baseline 下完整型別化；`features` 使用 `Mapping[str, str]`，`model_payload_hash` 凍結為 `str`。

## Public Contract / API Changes

- `async_model_gateway.response_cache.ResponseCacheKey`
  - concrete value surface，且只包含：
    - `namespace: str`
    - `model_payload_hash: str`
    - `feature_hash: str`
  - Contract:
    提供未來 `ResponseCache` 消費者使用的不可變 keyed cache identity material。
- `async_model_gateway.response_cache.ResponseCacheKeyFactory`
  - Constructor:
    `def __init__(self, feature_hasher: FeatureHasher) -> None`
  - Public method:
    `def build(self, *, namespace: str, model_payload_hash: str, features: Mapping[str, str]) -> ResponseCacheKey`
  - Contract:
    將 feature hashing 委派給持有的 `feature_hasher`，並回傳 `ResponseCacheKey`；payload hashing 保持在 factory 外部的 upstream owner，任何 cache owner 都不得在自身內部自行計算 hashes。
- `async_model_gateway.response_cache.ports.feature_hasher.FeatureHasher`
  - Abstract method:
    `def hash_features(self, features: Mapping[str, str]) -> str`
  - Contract:
    此 topic 中 feature-hash authority 的唯一 abstract collaborator。
- Backward compatibility:
  - 不修改任何既有 package root。
  - 此 topic 不引入 operational `ResponseCache` class 或 storage API。
  - 既有 `ModelPayloadHasher` ownership 與 hashing semantics 維持不變。

## Affected Files / Modules

Likely affected files:
- `docs/architecture.md`
- `docs/specs/response-cache-boundary.md`
- `src/async_model_gateway/response_cache/__init__.py`
- `src/async_model_gateway/response_cache/key.py`
- `src/async_model_gateway/response_cache/key_factory.py`
- `src/async_model_gateway/response_cache/ports/__init__.py`
- `src/async_model_gateway/response_cache/ports/feature_hasher.py`
- `tests/response_cache/test_response_cache_package_surface.py`
- `tests/response_cache/test_key.py`
- `tests/response_cache/test_key_factory.py`

Candidate files to inspect:
- `src/async_model_gateway/model_registry/model_payload/__init__.py`
- `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`
- `docs/specs/canonical-input-boundary.md`
- `pyproject.toml`

## Test Plan

Test files:
- `tests/response_cache/test_response_cache_package_surface.py`
- `tests/response_cache/test_key.py`
- `tests/response_cache/test_key_factory.py`

Test cases:
- Happy path:
  `tests/response_cache/test_key_factory.py` 驗證 `build(...)` 會回傳一個 `ResponseCacheKey`，其三個欄位分別是 literal `namespace` input、顯式 `model_payload_hash`，以及持有的 feature hash owner 回傳的 digest。
- Invalid input:
  `tests/response_cache/test_key_factory.py` 驗證 feature hashing failure 會原樣往外傳播，且不產生 key。
- Edge case:
  `tests/response_cache/test_key.py` 驗證 key surface 只維持三個字串欄位，沒有 hidden defaults 或額外 metadata。
- Regression:
  `tests/response_cache/test_response_cache_package_surface.py` 驗證 package root 只 export `ResponseCacheKey` 與 `ResponseCacheKeyFactory`，而 `FeatureHasher` 仍只在 submodule-public。
- Backward compatibility:
  `tests/response_cache/test_key_factory.py` 驗證 `features` 會以 `Mapping[str, str]` 原樣交給持有的 `FeatureHasher`，且 factory 不會 mutate 或擴張 feature input semantics；`model_payload_hash` 會作為 literal upstream identity material 被保留。
- Validation-only selected suite support:
  為了符合 repo-wide coverage gate，validation command 另外固定重跑 `tests/model_registry/model_payload/test_canonical_hash.py`、`tests/model_registry/stores/test_in_memory.py`、`tests/model_registry/stores/test_stores_package_surface.py`、`tests/model_registry/test_freshness_policy.py`、`tests/model_registry/test_registry.py`、`tests/test_package_entrypoint.py` 與 `tests/test_local_path_guard.py`；這些額外測試只用於 repo-consistent validation，並不擴張此 topic 的 source、docs 或 behavior scope。

## Validation Commands

```text
uv run pytest tests/response_cache/test_response_cache_package_surface.py tests/response_cache/test_key.py tests/response_cache/test_key_factory.py tests/model_registry/model_payload/test_canonical_hash.py tests/model_registry/stores/test_in_memory.py tests/model_registry/stores/test_stores_package_surface.py tests/model_registry/test_freshness_policy.py tests/model_registry/test_registry.py tests/test_package_entrypoint.py tests/test_local_path_guard.py -v
uv run ruff check docs src tests plan/response-cache-keyed-minimal-boundary
uv run pyright
```

## Risks

- 後續 implementation 可能會不小心引入 operational `ResponseCache` API，將 store semantics 偷帶進此 topic；因此必須嚴格執行精確 artifact paths 與 non-goals。
- 若 `FeatureHasher` 或未來 cache-runtime types 被 re-export 到 `response_cache/__init__.py`，新的 package root 可能會意外擴張。
- 文件可能過度宣稱 runtime cache support，而不是清楚說明目前只落地最小 keyed boundary。

## Rollback Plan

- 只回滾此 topic 宣告的 keyed-boundary files：
  - `docs/architecture.md`
  - `docs/specs/response-cache-boundary.md`
  - `src/async_model_gateway/response_cache/__init__.py`
  - `src/async_model_gateway/response_cache/key.py`
  - `src/async_model_gateway/response_cache/key_factory.py`
  - `src/async_model_gateway/response_cache/ports/__init__.py`
  - `src/async_model_gateway/response_cache/ports/feature_hasher.py`
  - `tests/response_cache/test_response_cache_package_surface.py`
  - `tests/response_cache/test_key.py`
  - `tests/response_cache/test_key_factory.py`
- 即使 implementation 變更在 merge 前被回滾，`analysis/response-cache-keyed-minimal-boundary/` 與 `plan/response-cache-keyed-minimal-boundary/` 仍保留作為 planning history。
