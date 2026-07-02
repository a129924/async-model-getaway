# response-cache-keyed-minimal-boundary Specification

## Acceptance Criteria

1. `async_model_gateway.response_cache` 在此 topic 中只 re-export `ResponseCacheKey` 與 `ResponseCacheKeyFactory`。
2. `ResponseCacheKey` 必須只包含 `namespace`、`model_payload_hash` 與 `feature_hash`，且三者型別都為 `str`。
3. `ResponseCacheKeyFactory` 在建構時持有 `FeatureHasher`，並暴露 `build(...)`，且該方法必須顯式接收 `namespace`、顯式 `model_payload_hash: str` 與顯式 `features: Mapping[str, str]`。
4. `ResponseCacheKeyFactory.build(...)` 必須將 feature hashing 委派給持有的 `FeatureHasher`，並將顯式傳入的 `model_payload_hash` 原樣放入回傳的 `ResponseCacheKey`。
5. `features` 必須維持為 `Mapping[str, str]`；factory 不得擴張、normalize 或重新解讀這個 boundary。
6. 此 topic 內任何 source file 都不得引入 cache store、backend、schema、TTL、eviction 或 orchestrator wiring 行為。
7. repo-visible docs 必須對齊這個最小 keyed boundary，且不得宣稱已經有完整 runtime response-cache implementation。

## Behavioral Scenarios

### Scenario 1: 由顯式 payload hash input 建立 keyed cache identity

- **Given**: 一個以 `FeatureHasher` 建構的 `ResponseCacheKeyFactory`
- **And**: 顯式 `namespace`、顯式 `model_payload_hash` 與顯式 `features: Mapping[str, str]`
- **When**: 呼叫 `build(...)`
- **Then**: `model_payload_hash` 會被原樣保留在回傳的 key 中
- **And**: features 會透過持有的 `FeatureHasher` 進行 hashing
- **And**: 回傳的 `ResponseCacheKey` 只包含提供的 `namespace` 與兩個 hashing 結果

### Scenario 2: feature hashing failure 會 fail closed

- **Given**: 一個會在 `FeatureHasher` 內失敗的 `features` input
- **When**: 呼叫 `build(...)`
- **Then**: 既有 feature-hash failure 會原樣往外傳播
- **And**: 不會回傳 `ResponseCacheKey`
- **And**: 此 topic 不加入 fallback coercion，也不新增 error taxonomy

### Scenario 3: Package surface 維持最小

- **Given**: `async_model_gateway.response_cache` package root
- **When**: caller 從 package root import
- **Then**: 只會 re-export `ResponseCacheKey` 與 `ResponseCacheKeyFactory`
- **And**: `FeatureHasher` 仍位於 `response_cache.ports`
- **And**: 此 topic 不暴露任何 operational `ResponseCache` storage API

## Error / Edge Cases

- `namespace` 在此 topic 中視為 literal keyed material；factory 不做 trim、normalize 或 synthesize。
- feature-hash semantics 仍由 `FeatureHasher` 擁有；factory 不得自行重排或 canonicalize features。
- 既有 `ModelPayloadHasher` semantics 仍是唯一 upstream payload-hash authority：dict-key canonicalization 不屬於新的 factory。
- 任何嘗試在此 topic 中加入 cache storage 或 orchestrator wiring 的行為，都屬於 scope violation，不是 edge-case extension。
