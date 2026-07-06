# response-cache-operational-minimal-boundary Specification

## Acceptance Criteria

1. `async_model_gateway.response_cache` package root 必須 re-export `ResponseCache`、`ResponseCacheEntry`、`ResponseCacheKey` 與 `ResponseCacheKeyFactory`。
2. `async_model_gateway.response_cache` package root 與 `async_model_gateway.response_cache.ports` 都不得 re-export `ResponseCacheStore`；store port 只允許維持在 `async_model_gateway.response_cache.ports.store`。
3. `ResponseCache` constructor 必須固定為 `ResponseCache(store: ResponseCacheStore)`。
4. `ResponseCache.get(...)` 必須固定為 `async def get(self, *, key: ResponseCacheKey) -> ResponseCacheEntry | None`，並將 `None` 保留為 cache miss surface。
5. `ResponseCache.set(...)` 必須固定為 `async def set(self, *, key: ResponseCacheKey, entry: ResponseCacheEntry) -> None`。
6. `ResponseCache` 不得在 `get(...)` 或 `set(...)` 內自行建立 `ResponseCacheKey`、重新計算 hash，或將 `ResponseCacheEntry` 展平成裸 `str`。
7. `ResponseCacheEntry` 必須是 immutable、完整型別化的 value type，且只有 `response: str` 一個欄位。
8. `ResponseCacheStore` 必須提供與 `ResponseCache` 對齊的 async `get` / `set` contract，以 `ResponseCacheKey` 與 `ResponseCacheEntry` 作為唯一 public data surfaces。
9. 既有 `tests/response_cache/test_key.py` 與 `tests/response_cache/test_key_factory.py` 的 keyed boundary guarantees 在此 topic 中必須保持有效。
10. repo-visible docs 必須對齊「既有 keyed boundary + 新增 minimal operational boundary」的描述，且不得宣稱已具備 concrete backend 或 broader runtime cache feature。
11. `ResponseCache` 不得建立、關閉或重置 `ResponseCacheStore` 底層 resources；store lifecycle 仍由 caller / store owner 擁有。
12. 此 topic 的 async boundary 只允許 direct await delegation；不得加入 timeout、retry、sync mirror、background task 或 fan-out behavior。

## Behavioral Scenarios

### Scenario 1: `ResponseCache.get(...)` 委派 store lookup 並保留 hit/miss semantics

- **Given**: 一個以 `ResponseCacheStore` 建構的 `ResponseCache`
- **And**: 一個既有的 `ResponseCacheKey`
- **And**: store 對該 key 回傳 `ResponseCacheEntry(response="cached response")`
- **When**: 呼叫 `await response_cache.get(key=key)`
- **Then**: `ResponseCache` 會以原樣 key 委派 store lookup
- **And**: 回傳值是同一個 `ResponseCacheEntry`
- **And**: `ResponseCache` 不會重新計算 hashes 或重建 key

### Scenario 2: `ResponseCache.get(...)` 將 miss 表達為 `None`

- **Given**: 一個以 `ResponseCacheStore` 建構的 `ResponseCache`
- **And**: store 對該 key 回傳 `None`
- **When**: 呼叫 `await response_cache.get(key=key)`
- **Then**: `ResponseCache` 會回傳 `None`
- **And**: 這個 `None` 只代表 cache miss，不代表 swallowed failure

### Scenario 3: `ResponseCache.set(...)` 原樣委派 key 與 entry

- **Given**: 一個 `ResponseCacheEntry(response="generated response")`
- **And**: 一個既有的 `ResponseCacheKey`
- **When**: 呼叫 `await response_cache.set(key=key, entry=entry)`
- **Then**: `ResponseCache` 會把同一個 key 與同一個 entry 原樣交給 store
- **And**: `set(...)` completion surface 為 `None`
- **And**: `ResponseCache` 不會修改 entry 或替 entry 加入 metadata

### Scenario 4: package surface 維持新增 owner、保留 keyed、隱藏 store port

- **Given**: `async_model_gateway.response_cache` package root
- **When**: caller 從 package root import
- **Then**: 可以取得 `ResponseCache`、`ResponseCacheEntry`、`ResponseCacheKey` 與 `ResponseCacheKeyFactory`
- **And**: 無法從 package root 直接取得 `ResponseCacheStore`
- **And**: 也不得把 `async_model_gateway.response_cache.ports` 視為 `ResponseCacheStore` 的可匯入 owner
- **And**: `ResponseCacheStore` 只能從 `async_model_gateway.response_cache.ports.store` 直接匯入

## Error / Edge Cases

- store failure 會原樣往外傳播；`ResponseCache` 不新增 fallback、wrapping 或 exception taxonomy。
- awaitable cancellation semantics 也必須原樣保留；此 topic 不新增 timeout 或 cancellation wrapper。
- `ResponseCacheEntry.response` 在此 topic 中視為 literal cached response；不做 trim、normalization 或 provider-specific parsing。
- `ResponseCache` 不擁有 key construction authority；任何需要新 key material 的需求都屬於 keyed boundary rework，而不是此 topic 的 edge-case extension。
- `ResponseCacheEntry` 不得在此 topic 中加入 timestamps、TTL、content type、model metadata 或 cache provenance 欄位。
- 此 topic 的 async baseline 只涵蓋 direct await delegation；任何 timeout、retry、batching、fan-out 或 cancellation orchestration 都屬於 scope violation。
