# prediction workflow boundary

## 定位

這份文件定義後續 application topic 必須共用的 **target architecture**。
它不是目前已完成的 Python runtime contract：generic `PredictionOrchestrator`、
四欄 `CacheKey`、`ResultCodec`、remote execution 與 `DataFrame` application flow
都尚未實作。現有 `LocalResponseGateway` 是 local/ONNX 的受限 transition
projection，不得被誤讀為本文件 target 的完整實作。

## Target workflow

外層 application 可以維持 `Mapping` input 到 `pandas.DataFrame` output 的使用
體驗；pandas 只停留在 application/workflow layer。

1. application 將外部 Mapping normalize 成 canonical input，並提供
   `model_name`、`model_source_kind`、`model-payload`、`features` 與
   `prediction_input`。
2. `PredictionOrchestrator` 在第一次 await 前，將 JSON-like
   `prediction_input` 與 `features` 建立深層 immutable snapshots。之後的 identity
   derivation 與 execution 都只消費各自的同一份 snapshot。
3. 在 `ModelRegistry.resolve_freshness` 可能更新 registry state 前，`Predictor`
   驗證 features vocabulary、投影 feature execution material 與 JSON-like
   `prediction_input_identity`；`FeatureIdentityHasher`、
   `PredictionInputHasher` 和 `CacheNamespaceDeriver` 完成全部無副作用的 identity
   work。任一 failure 都 fail closed，不能 resolve freshness、lookup、execute 或
   remember。
4. `ModelRegistry` resolve freshness，並交付完整 model identity 的
   `model_identity_hash`。
5. `CacheKeyDeriver` 僅組裝已完成的 identity，形成 target
   `CacheKey(namespace, model_identity_hash, feature_hash,
   prediction_input_hash)`。
6. `ResponseCache.lookup` 命中時交付 cache `str` value；`ResultCodec.decode`
   將它轉回 application result，例如 `DataFrame`，而不執行 model。
7. miss 時，`ModelExecution` 以 feature execution material、prediction-input
   snapshot，透過 local `ModelPool` 或 remote `ModelGateway` 路徑發生 invocation。
   `Predictor` 將 raw result 投影為 application result；
   `ResultCodec.encode` 將它轉成 cache `str`，再由 `ResponseCache.remember` 寫入。
   application result 本身才是回傳值。

## Responsibility matrix

| Role | Owns | Must not own |
| --- | --- | --- |
| `PredictionOrchestrator` | snapshot handoff、side-effect-free preflight 順序、hit/miss routing | hashing、key policy、model lifecycle、invocation semantics |
| `ModelRegistry` | model identity context、freshness、`model_identity_hash` target output | response cache、input identity、result representation |
| `Predictor` | fixed base namespace、predictor compatibility token、feature validation/execution projection、input identity projection、raw-result-to-application-result projection | hash、`CacheKey`、storage、execution lifecycle |
| `FeatureIdentityHasher` | validated feature snapshot 的 identity hash | feature vocabulary semantics、prediction input、model identity |
| `PredictionInputHasher` | JSON-like input identity hash | model identity、cache storage |
| `CacheNamespaceDeriver` | base namespace + predictor token + codec token 的 canonical namespace hash | input/model hashing、key assembly |
| `CacheKeyDeriver` | 四個已完成 identity 的 dumb assembly | registry lookup、canonicalization、execution |
| `ResultCodec` | application result `↔` cache `str` | `str ↔ bytes`、storage、raw model invocation |
| `ResponseCache` | `str` value reuse、record validation、TTL、whole-record write | pandas、Mapping、prediction semantics |
| `CacheCodec` / `CacheStore` | `str ↔ bytes` / whole-record primitives | application result types |
| `ModelExecution` | invocation semantics | cache identity、provider acquisition policy |
| `ModelPool` / `ModelGateway` | local acquisition / remote runtime access | response reuse、application results |

## Identity and compatibility

`model_identity_hash` represents complete model identity, not only payload
identity. Its target semantics cover `model_name`、`model_source_kind` 與
`model_payload_hash`; `ModelRegistry` is its authority.

`features` remains bounded capability / usage-mode material. It is not
prediction input and must not be used as a generic request bag. `Predictor`
validates its vocabulary and projects the validated feature snapshot into the
material that `ModelExecution` consumes; `FeatureIdentityHasher` only hashes
that same validated snapshot.

`prediction_input_identity` contains exactly the differences that can change the
application result. Correlation IDs, trace IDs, timestamps, and other
observability-only material do not belong in it.

The target four-field key is an explicit breaking replacement for the current
implemented three-field `CacheKey(namespace, model_payload_hash, feature_hash)`.
This docs topic creates no compatibility adapter and no storage migration.

`Predictor` must rotate its compatibility token whenever a change can alter
feature interpretation, prediction-input identity, or raw-result projection.
`CacheNamespaceDeriver` includes that token together with the result-codec
compatibility token, so an older predictor result cannot be reused by newer
prediction semantics.

## Result representation and failures

`ResponseCache` currently accepts and returns `str`; its `CacheCodec` persists
that value as bytes. `ResultCodec` deliberately sits above this boundary:

```text
application result --ResultCodec.encode--> cache str --CacheCodec.encode--> bytes
bytes --CacheCodec.decode--> cache str --ResultCodec.decode--> application result
```

Concrete `DataFrame` serialization, row-Mapping codecs, CAS, pickle, and format
selection are deferred. Every concrete codec must declare a compatibility token;
the token is part of namespace derivation, not stored as hidden interpretation
state.

- `ResultCodec.decode` failure on a cache hit propagates unchanged. It does not
  become a silent miss or trigger execution.
- `ResultCodec.encode` failure after a miss propagates unchanged. It does not
  write a fallback representation or return an unrepresentable result.
- Existing `ResponseCache` operational lookup/write semantics remain unchanged:
  known lookup failures close to miss, while `Skipped` / `Failed` writes remain
  fail-open after a valid cache string has been produced.

## Local transition projection

`LocalResponseGateway` currently guards local/ONNX use, shallow-copies its
`invocation` mapping before its first await, passes that snapshot to an opaque
private cache-key deriver and executor, and returns `str`. It already prevents
top-level invocation mutation from splitting its current key and execution
inputs. It does not yet provide deep JSON-like snapshots, standard hash owners,
the four-field key, `ResultCodec`, or application `DataFrame` results.

Any migration of this projection must be a separately planned source topic.

## Explicitly deferred

- Python packages, protocols, method signatures, exports, and dependency wiring
- target `CacheKey` implementation or old-key migration
- concrete result codecs or pandas dependency
- table/batch behavior, partial failures, ordering, retry, dedup, and concurrency
- persistence, eviction, invalidation policy changes, timeout, and singleflight
