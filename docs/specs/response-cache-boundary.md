# response cache boundary

## 摘要

`ResponseCache` 是受限的 async response reuse boundary。package root 只公開
`ResponseCache`、`CacheKey` 與封閉的 lookup/write outcomes；它不提供 orchestration、
backend selection、store lifecycle、persistence、settings、eviction 或 metrics。

## Identity 與 context

`CacheKey(namespace, model_payload_hash, feature_hash)` 是唯一 cache identity authority。
所有三個值都必須在 cache 之外導出；cache 不重新計算 payload 或 feature hash。
`lookup` 與 `remember` 接收 context 作為單次呼叫輸入，但不讀取、保存或序列化它；context
不影響 identity、record、metadata、expiry 或 version token。

## Facade 與 record ownership

`ResponseCache` 只提供 keyword-only async `lookup` 與 `remember`。它持有 store、codec、
version-token factory、write-time expiry policy 與 injected aware-UTC clock。remember 成功路徑
建立一個 immutable complete record：schema version、codec id、encoded payload、written/expiry
timestamps、new opaque version token 和空 metadata。已知 operational failure 轉為封閉 outcomes；
cancellation 和其他 defects 原樣傳播。

`CacheStore`、`CacheCodec`、`VersionTokenFactory` 與 `CacheInvalidator` 是 submodule-public
ports。store 只做 whole-record replacement、key-local delete 和 token-guarded atomic
compare-delete。lookup 的過期或不支援 record cleanup 絕不使用 unconditional delete，因此不會
刪除 concurrent replacement。invalidation 由獨立 `CacheInvalidator` 擁有，不是 facade method。

## Freshness 與 compatibility

internal `FreshnessPolicy` 只在 write 時從 aware-UTC `written_at` 衍生 `expires_at`；讀取不會
renew expiry。`TtlFreshnessPolicy` 保持 strict positive TTL。temporary deprecated legacy bridge
僅在 `async_model_gateway.response_cache.compat`；它提供舊 caller 的過渡 map 與 warning，且不會
由 package root re-export。後續經核准的 removal change 才能連同 adapter、legacy aliases、warnings
與 migration tests 一起移除。
