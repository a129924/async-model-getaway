# model-registry-in-memory-store Specification

## Acceptance Criteria

1. Repository 提供 `async_model_gateway.model_registry.stores.InMemoryRegistryStore`
   作為 `RegistryStore` 的 concrete subclass，且 class name 維持為
   `InMemoryRegistryStore`。
2. `InMemoryRegistryStore.__init__()` 為 empty-only constructor，不接受 seed
   data、mapping、lock 或其他 collaborator injection。
3. `InMemoryRegistryStore.get_entry()` 與 `upsert_entry()` 維持 async-only
   contract，並明確使用 `typing_extensions.override`。
4. 同一 `InMemoryRegistryStore` instance 的讀寫由單一 `asyncio.Lock`
   序列化；本 topic 不擴張成 broader concurrency abstraction。
5. Store lookup identity 僅使用 `model_name + model_source_kind`；`payload_hash`
   不參與 lookup key。
6. `InMemoryRegistryStore` 只作為
   `async_model_gateway.model_registry.stores` submodule public surface；
   `async_model_gateway.model_registry` root package 不 re-export 它。
7. `README.md`、`docs/specs/model-side-boundary.md`、
   `docs/specs/canonical-input-boundary.md`、
   `docs/specs/core-abstractions-boundary.md` 以最小必要 wording 反映此 concrete
   store。
8. `src/async_model_gateway/__version__.py` 與 `pyproject.toml` 以 patch bump
   對齊 stable-library / release-facing topic contract。

## Behavioral Scenarios

### Scenario 1: First write and lookup on one store instance
- **Given**: 一個新建的 `InMemoryRegistryStore`，其內部 state 初始為空
- **When**: 呼叫 `upsert_entry()` 寫入一筆以 `model_name` 與
  `model_source_kind` 識別的 `RegistryEntry`，之後再以相同 lookup identity
  呼叫 `get_entry()`
- **Then**: `get_entry()` 回傳對應 entry，且 lookup contract 不需要
  `payload_hash`

### Scenario 2: Same model name, different model source kind
- **Given**: 一個 `InMemoryRegistryStore` instance
- **When**: 先後寫入兩筆擁有相同 `model_name` 但不同 `model_source_kind` 的
  `RegistryEntry`
- **Then**: 兩筆資料分別可被對應的 lookup identity 取回，不互相覆蓋

### Scenario 3: Package surface exposure stays bounded
- **Given**: repository 已新增 `InMemoryRegistryStore`
- **When**: 檢查 `async_model_gateway.model_registry.stores` 與
  `async_model_gateway.model_registry` 的 package surfaces
- **Then**: store 可由前者取得，但不會從後者 root package re-export

## Error / Edge Cases

- 對不存在的 `model_name + model_source_kind` lookup 呼叫 `get_entry()` 時，
  應回傳 `None`，而不是 raise custom exception。
- 以相同 lookup identity 再次 `upsert_entry()` 時，新 entry 應覆蓋舊 entry；
  topic 不定義 conflict exception。
- 同一 instance 上的並發 `get_entry()` / `upsert_entry()` 不得繞過單一
  `asyncio.Lock` 的序列化 contract。
- topic 不新增 sync helper、delete / clear / list APIs、seed constructor、
  persistence backend 或 broader architecture abstractions。
