# response-cache-contract-migration — Requirements Baseline

## Intent

將現有的最小 response-cache API 遷移為一個可長期維護的 async contract。遷移完成後，
`ResponseCache` 是唯一 package-root public facade；cache identity、context、儲存 envelope、
versioned cleanup 與 legacy compatibility 各自有明確且不可互相取代的責任。

本 baseline 由本 topic 的 planning actor 建立；`technical-spec.md` 是後續實作計畫的
execution-facing source of truth。

## Measurable Requirements

1. root facade 只提供以下兩個 async operations，且兩者都以 keyword-only `key` 與
   `context` 呼叫：
   - `async def lookup(self, *, key: CacheKey, context: ContextT) -> CacheHit | CacheMiss`
   - `async def remember(self, *, key: CacheKey, value: str, context: ContextT) -> Remembered | Skipped | Failed`
2. `CacheKey` 是 identity 與 hash material 的唯一 authority。它保留既有 namespace、
   model-payload hash 與 feature hash 的語意；`ContextT` 只能是單次 invocation 的
   generic input，不能進入 identity、hash、`StoredCacheRecord`、store key 或 persisted
   metadata。
3. `StoredCacheRecord` 是唯一 storage envelope，且 immutable。它必須含 schema version、
   codec identifier、encoded payload、aware-UTC `written_at` / `expires_at`、每次 successful
   write 產生的 opaque version token，以及受限 metadata；record 的 metadata 至多八組，
   每組 key/value 分別至多 64/256 UTF-8 bytes，所有 metadata 合計至多 2 KiB。
4. `CacheCodec` 只負責 `str` value 與 bytes payload 的 encode/decode；
   `VersionTokenFactory` 只負責每次 write 產生不可由 cache caller 解讀的 token；
   `CacheStore` 只負責 coherent per-key record I/O 與 atomic compare-delete。這三種 owner
   不得重算 identity、保存 context 或承擔 facade outcome policy。
5. `CacheStore.get` 必須交付 coherent record snapshot 或 absent；`set` 必須以整筆 record
   取代同一 key 的舊 record；`delete_if_version` 必須原子地比較 supplied token，再只在
   相同時刪除。這項保證不得以 read-then-unconditional-delete 模擬。
6. `lookup` 對 absent、expired、unsupported schema、decode/record/store 的已知 operational
   failure 都回傳 `CacheMiss`。expired/invalid record 的 best-effort cleanup 即使失敗仍是
   `CacheMiss`，且不得把較新的 replacement record 刪除。
7. `remember` 對 successful write 回傳 `Remembered`；已知 closed store condition 回傳
   `Skipped(reason=CLOSED)`；已知 store、codec 或 version-token operational failure 回傳
   封閉的 `Failed(kind=...)`。`asyncio.CancelledError` 與 programmer/configuration defects
   必須原樣傳播，不得轉成 miss 或 failed result。
8. invalidation 不屬於 `ResponseCache` facade。它必須經獨立 `CacheInvalidator` port，以
   supplied `CacheKey` 做 key-local deletion：存在時 `Invalidated`，不存在時 `NotFound`；
   known operational failure、cancellation 與 defect 都原樣傳播。
9. 現有 `ResponseCacheKey`、`ResponseCacheKeyFactory`、`ResponseCacheEntry` 與 facade
   `get`/`set`/`invalidate` 只能存在於 temporary compatibility adapter。adapter 會有
   明示 removal condition；到期後不得保留舊 root export、legacy type 或 legacy method。
10. 實作必須新增 direct-import tests，覆蓋 public exports、legacy migration、coherent
    replacement race、compare-delete race、cancellation 與 failure matrix；測試不得為了
    配合實作使用 dynamic module loading。

## Boundaries

- 不新增 orchestrator、application composition、model invocation 或 application wiring。
- 不引入 background task、queue、worker、timeout、retry、batching、cross-key fan-out、
  persistence backend、settings、admission、capacity 或 eviction policy。
- 不在本 planning topic 修改 `README.md`、`docs/architecture.md` 或
  `docs/specs/response-cache-boundary.md`；它們是後續 implementer 必須同步的 declared paths。

## Acceptance Signals

- 既有 API 與新 contract 的每一項都有 canonical reconciliation mapping，且 mapping 對
  current、target、migration 與 compatibility 四欄均有具體答案。
- public package surface 不再將 legacy facade 作為正常使用路徑；temporary adapter 的 import
  path、deprecation signal 與 terminal removal condition 都可由測試驗證。
- compare-delete race 中，stale lookup 的 cleanup 不會刪除在其 read 之後寫入的新 token record。
- 任何 context 值都無法透過 key equality/hash、stored record field、codec payload 或
  metadata 被觀測或重新取得。

## D1 Verdict

```json
{
  "verdict": "non-trivial",
  "reason": "The topic replaces a root-public async cache contract, introduces immutable stored-record and versioned store guarantees, changes failure translation, adds a compatibility lifecycle, and requires cancellation and concurrency race coverage."
}
```
