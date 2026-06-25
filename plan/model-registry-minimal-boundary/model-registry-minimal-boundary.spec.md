# model-registry-minimal-boundary Specification

## Acceptance Criteria

1. `async_model_gateway.model_registry` 在 package root 只能 re-export
   `ModelRegistry`。
2. `ModelRegistry.resolve_freshness(...)` 必須是 async-only，且只能接受
   `model_name`、`model_source_kind` 與 `model_payload`。
3. `RegistryStore` 必須是唯一的 abstract collaborator，位於
   `async_model_gateway.model_registry.ports.store`，並提供 async lookup
   與 async upsert methods。
4. `RegistryStore` 的 lookup identity 必須精確為
   `model_name + model_source_kind`。
5. `RegistryFreshnessResult` 必須只包含 `decision`、`entry` 與
   `previous_payload_hash`。
6. `RegistryFreshnessPolicy` 必須只回傳 `first-seen`、`unchanged` 或
   `changed`，且 `changed` 必須攜帶前一個 payload hash。
7. `ModelRegistry` 必須持續以原樣使用
   `ModelPayloadHasher.hash_model_payload(...) -> str`，不得重新安置或包裝
   該 contract。
8. Source files 必須維持一檔一概念；abstract types 必須放在 `ports/`
   之下；implementation 不得保留 multi-concept registry blob。

## Behavioral Scenarios

### Scenario 1: First-seen payload creates a new registry entry
- **Given**: `ModelRegistry` 收到 `model_name`、`model_source_kind` 與合法的
  `model_payload`
- **And**: `await RegistryStore.get_entry(...)` 回傳 `None`
- **When**: 呼叫 `await ModelRegistry.resolve_freshness(...)`
- **Then**: `ModelPayloadHasher.hash_model_payload(...)` 會在不改變 contract
  的前提下產生 candidate payload hash
- **And**: `RegistryFreshnessPolicy.evaluate(...)` 回傳
  `decision = "first-seen"`
- **And**: `await RegistryStore.upsert_entry(...)` 會以 candidate
  `RegistryEntry` 被呼叫一次
- **And**: 回傳的 `RegistryFreshnessResult` 包含 candidate `entry`，且
  `previous_payload_hash = None`

### Scenario 2: Unchanged payload does not trigger a write
- **Given**: `RegistryStore` 已持有相同 `model_name` 與
  `model_source_kind` 的 `RegistryEntry`
- **And**: 新的 `model_payload` 產生相同的 payload hash
- **When**: 呼叫 `await ModelRegistry.resolve_freshness(...)`
- **Then**: `RegistryFreshnessPolicy.evaluate(...)` 回傳
  `decision = "unchanged"`
- **And**: `RegistryStore.upsert_entry(...)` 不會被 await
- **And**: 回傳結果仍會攜帶 candidate `entry`

### Scenario 3: Changed payload updates the stored entry
- **Given**: `RegistryStore` 已持有相同 `model_name` 與
  `model_source_kind` 的 `RegistryEntry`
- **And**: 新的 `model_payload` 產生不同的 payload hash
- **When**: 呼叫 `await ModelRegistry.resolve_freshness(...)`
- **Then**: `RegistryFreshnessPolicy.evaluate(...)` 回傳
  `decision = "changed"`
- **And**: `await RegistryStore.upsert_entry(...)` 會以新的 candidate
  `RegistryEntry` 被呼叫一次
- **And**: 回傳結果中的 `previous_payload_hash` 會來自先前的 entry

### Scenario 4: Lookup identity ignores payload hash
- **Given**: 兩個 request 共享相同的 payload hash
- **And**: 兩個 request 在 `model_name` 或 `model_source_kind` 其中之一不同
- **When**: 分別對每個 request 呼叫
  `await ModelRegistry.resolve_freshness(...)`
- **Then**: `RegistryStore.get_entry(...)` 只使用
  `model_name + model_source_kind` 作為 lookup identity
- **And**: 相同的 payload hash 不會讓不同 lookup identity 被折疊為同一筆

### Scenario 5: Invalid payload fails before any write
- **Given**: `model_payload` 內含不被既有 hasher contract 支援的內容
- **When**: 呼叫 `await ModelRegistry.resolve_freshness(...)`
- **Then**: 呼叫會 raise `TypeError`
- **And**: `RegistryStore.upsert_entry(...)` 不會被 await
- **And**: 此 topic 不會新增 timeout wrapper、fallback coercion 或新的
  error taxonomy

## Error / Edge Cases

- 巢狀 dict 的順序仍由既有 hasher 做 canonicalize，因此只有順序不同的情況
  不得產生 `decision = "changed"`。
- list 順序仍屬於 identity material，因此只差在 list 排序的 payload
  必須產生 `decision = "changed"`。
- `1` 與 `1.0` 仍是不同的 identity material，因為既有 hasher 不會對 scalar
  values 做 normalization。
- Store lookup 與 upsert failures 必須以原樣向外傳播。
- `asyncio.CancelledError` 不得被 `ModelRegistry` 吞掉或轉譯。
- `RegistryStore`、`RegistryEntry`、`RegistryFreshnessPolicy` 與
  `RegistryFreshnessResult` 都不得從 package root 被 re-export。
