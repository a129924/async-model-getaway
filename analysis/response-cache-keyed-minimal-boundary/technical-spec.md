# response-cache-keyed-minimal-boundary Technical Specification

## Translation Status

- Source baseline: `analysis/response-cache-keyed-minimal-boundary/requirements.md`
- Translation posture: pessimistic implementer
- Result: `ready-for-plan-authoring`

## Technical Summary

- 此 topic 最小且誠實的落地方式，是新增一個 `response_cache` package，擁有 `ResponseCacheKey`、`ResponseCacheKeyFactory` 與 bounded `FeatureHasher` port。
- 此 topic 不引入 operational `ResponseCache` storage API，因為 frozen scope 明確排除了 store、backend、schema、TTL、eviction 與 orchestrator wiring。相對地，它凍結的是：未來任何 `ResponseCache` runtime surface 都必須消費 `ResponseCacheKey`。
- 既有 `ModelPayloadHasher` 仍是 payload-hash owner，但 payload hashing 保持在 `ResponseCacheKeyFactory.build(...)` 之外；factory 只消費顯式傳入的 `model_payload_hash`。

## Requirement-to-Technical Mapping

| Requirement | Technical realization | Planned artifacts | Dependency notes |
| --- | --- | --- | --- |
| `ResponseCache` 必須消費已建好的 `ResponseCacheKey`，而不是自行計算 hashes | 凍結 source 與 docs，讓 key construction 位於 `ResponseCacheKeyFactory`，而未來 runtime cache behavior 則由 docs/spec wording 約束，而不是偷帶 store API | `src/async_model_gateway/response_cache/__init__.py`, `src/async_model_gateway/response_cache/key.py`, `src/async_model_gateway/response_cache/key_factory.py`, `docs/specs/response-cache-boundary.md`, `docs/architecture.md` | 依賴 upstream 已提供的 payload hash；不依賴 store/backend work |
| `ResponseCacheKey` 欄位固定為三個字串 | 新增 concrete key value surface，且只包含 `namespace`、`model_payload_hash`、`feature_hash` | `src/async_model_gateway/response_cache/key.py`, `tests/response_cache/test_key.py`, `plan/response-cache-keyed-minimal-boundary/response-cache-keyed-minimal-boundary.spec.md` | 不允許額外 metadata 或 cache payload ownership |
| `ResponseCacheKeyFactory` 持有 `FeatureHasher` 並接收顯式 build inputs | 新增 factory module 與 `FeatureHasher` port，使 `build(...)` 消費顯式 `model_payload_hash`，並將 feature hash 委派給持有的 `FeatureHasher` | `src/async_model_gateway/response_cache/key_factory.py`, `src/async_model_gateway/response_cache/ports/feature_hasher.py`, `tests/response_cache/test_key_factory.py` | payload hashing authority 維持在 upstream；factory 不得自行 canonicalize features |
| `features` 固定為 `Mapping[str, str]` | 將型別簽名、tests 與 docs 全部鎖到這個精確 shape | `src/async_model_gateway/response_cache/key_factory.py`, `tests/response_cache/test_key_factory.py`, `docs/specs/response-cache-boundary.md` | broader feature authority 延後處理 |
| backend、schema、TTL、eviction 與 orchestrator wiring 維持 out of scope | implementation path 嚴格限縮在 key/factory/docs/tests | topic `*.plan.md`, `*.step.md`, `docs/architecture.md` | 任何新增 store 或 wiring 檔案的行為都算 scope violation |
| creator-owned planning artifact set 必須存在 | 在 implementation 前先完成 analysis 與 plan companions | `analysis/.../requirements.md`, `analysis/.../technical-spec.md`, `plan/.../*.plan.md`, `plan/.../*.spec.md`, `plan/.../*.step.md` | 讓後續 execution 能走 strict analysis-layer routing |

## Proposed Source And Test Surface

### Source

- `src/async_model_gateway/response_cache/__init__.py`
- `src/async_model_gateway/response_cache/key.py`
- `src/async_model_gateway/response_cache/key_factory.py`
- `src/async_model_gateway/response_cache/ports/__init__.py`
- `src/async_model_gateway/response_cache/ports/feature_hasher.py`

### Tests

- `tests/response_cache/test_response_cache_package_surface.py`
- `tests/response_cache/test_key.py`
- `tests/response_cache/test_key_factory.py`

### Docs

- `docs/architecture.md`
- `docs/specs/response-cache-boundary.md`

## Technical Decisions

- `ResponseCacheKey` 應是小型、不可變、完整型別化的 value surface，且只包含三個已凍結的字串欄位。
- `ResponseCacheKeyFactory` 應維持同步。此 topic 不引入 async boundary、resource lifecycle、timeout policy 或 concurrency policy。
- `FeatureHasher` 應是此 topic 中唯一的新 abstract collaborator，並透過 `response_cache/ports/feature_hasher.py` 暴露，而不是 re-export 到 package root。
- package root 在此 topic 中只應 re-export `ResponseCacheKey` 與 `ResponseCacheKeyFactory`。`FeatureHasher` 保持 submodule-public。
- error handling 應維持 fail-closed 且不做翻譯：factory 內部的 feature hashing 例外原樣傳播，而 upstream payload hashing failure 仍由既有 payload-hash owner 負責。

## Feasibility And Cost

| Workstream | Complexity | Sequencing | Operational burden |
| --- | --- | --- | --- |
| Key 與 factory source surfaces | Medium | 必須排在 test authoring 之後 | Low；不引入 runtime resources |
| Package-surface 與 behavior tests | Medium | implementation 的第一個子階段 | Low；isolated pytest coverage |
| Docs 對齊 | Low | 在 source contracts 凍結後進行 | Low；純 wording 變更 |

## Architecture Compliance Check

- 符合目前架構：`ResponseCache` 仍是獨立 boundary，依賴 payload-hash 加上 features。
- 符合目前 ownership rules：`ModelPayloadHasher` 保持 upstream payload-hash owner；新 factory 只協調 literal `namespace`、顯式 `model_payload_hash` 與 feature-hash input。
- 符合目前 repo stage：不假設 backend、provider 或 orchestration implementation 已存在。
- 不需要 stable-library metadata：此 topic 明確是 non-stable-library。

## Conflict Notes And Rollback-to-Alignment Triggers

- 已避開的重大衝突：若引入 concrete operational `ResponseCache` API，就會需要 store/backend 假設，而 frozen scope 明確禁止。
  Handling：此 topic 僅限於 keyed source surfaces，加上約束未來 `ResponseCache` ownership 的 documentation。
- 出現下列任一情況時，必須回退到 alignment：
  - 引入 store、backend、schema、TTL、eviction 或 orchestrator 檔案
  - 將 `features` 擴張超出 `Mapping[str, str]`
  - 將 payload hashing authority 從 `ModelPayloadHasher` 移走
  - 在同一 slug 下新增 broader feature-hash authority topic

## Open Technical Questions

- 無。
