# async-model-gateway

`async-model-gateway` 是一個以 async-first、typed-first 為方向的 model gateway 專案基礎。

## 專案目的

這個專案目前聚焦在兩個目標：

- 降低 model 使用成本
- 降低 response 產生成本

## 目前階段

目前 repository 仍處於 project initialization 階段。

在這個階段，repo 先建立後續工作的基線：

- Python `3.10`
- `uv` 專案與環境管理
- async-first 專案方向
- typed-first dependency baseline
- GitHub Actions CI baseline
- packaged application scaffold
- 最小 CLI entrypoint

目前 package version baseline 為 `0.7.0`。repo 目前已落地最小
`ModelRegistry` boundary，並補齊受限的 `ResponseCache` boundary：
`async_model_gateway.response_cache` 只公開 `ResponseCache`、`CacheKey` 與封閉的
lookup/write outcomes。facade 只提供 async `lookup` / `remember`；context 僅為單次
呼叫輸入，不會進入 identity 或 stored record。internal TTL policy 在 write 時衍生
aware-UTC expiry，process-local store 只保存完整 versioned record；過期 cleanup 使用
token-guarded compare-delete。`CacheInvalidator`、store、codec 與 token factory 都維持
submodule-only，temporary deprecated adapter 只存在於 `response_cache.compat`，不屬於
正常 public surface。這些都不代表 persistence、settings、eviction 或 orchestration 已落地。
repo 也已把最小 `ModelArtifact` + `LoaderFamily` shared read
contract 納入 baseline：
`async_model_gateway.model_runtime.model_artifact` 公開 `ModelArtifact` 與
`LoaderFamily`，並由 `model_runtime` 作為後續 model-runtime family layout 的
umbrella root，用來表達 shared read contract 的最小 artifact metadata 與顯式
loader family vocabulary。repo 也已落地 internal-only local runtime binding：私有
composition 會在 pool acquisition 前，依顯式 `LoaderFamily` 解析同一組 Loader、
Executor 與 concurrency policy；ONNX route 才 lazy 建立 CPU-only provider session。
`ModelPool` 以注入的 generic Loader 建立 concrete generic
`LoadedRuntimeModel`，後者只保存 runtime、execution gate 與 aware-UTC 使用時間。
Executor 在取得 gate 後更新時間並直接 await invocation；一般例外與 cancellation
原樣傳播。這些 runtime composition、pool、loader、executor 與 loaded model 都沒有
public package entrypoint，provider session 亦不會穿透 application / orchestrator
boundary。PICKLE 與 TORCH 仍 fail closed；真實 provider invocation / ONNX invoker、
provider framework、完整 orchestration、remote execution、lifecycle、timeout 與 retry
仍未完成。
root package 目前只公開 `__version__` 與 `main`；`ModelRegistry` 由
`async_model_gateway.model_registry` 提供，
`async_model_gateway.model_registry.stores` 提供 submodule public 的
`InMemoryRegistryStore`，而 `model-payload` hashing 的 public owner 仍維持為
`ModelPayloadHasher`。`RegistryEntry` 也提供由 model name、source kind 與
payload hash 組成的唯讀 `model_identity_hash`，其 public hashing owner 只在
`async_model_gateway.model_registry.model_identity.ModelIdentityHasher`。這不代表
cache migration、broader cache backend/policy、`orchestrator` flow 或 broader cache
architecture 已完成。

## 核心概念

以下詞彙是目前專案共享的核心語彙：

- `model_name`
- `model_source_kind`
- `orchestrator`
- `model-payload`
- `features`
- response cache
- `runtime-model`
- local / remote model source

這些詞彙大多數仍屬設計層級，用來做規劃與對齊；目前只有最小
model-registry boundary、最小 operational response-cache boundary，以及 internal
model-artifact / local runtime binding slice 已落地。除此之外，較寬的 `features`
semantics、response cache architecture、`orchestrator` 與完整 `runtime-model` flow
仍不是已完成的 Python type 或 runtime feature。

目前已落地的最小 model-registry boundary 包含：

- `async_model_gateway.model_registry.ModelRegistry`
- `async_model_gateway.model_registry.stores.InMemoryRegistryStore`
- `async_model_gateway.model_registry.model_payload.ModelPayloadHasher`
- `async_model_gateway.model_registry.model_identity.ModelIdentityHasher`

其中 `ModelPayloadHasher`：

- 它的 public method `hash_model_payload(...)` 負責把 `model-payload` 作
  recursive canonicalization 後產生穩定的 SHA-256 hex digest
- nested dict 會 canonicalize
- list 順序保留
- scalar 不做 normalization
- unsupported type 會 fail closed 並 raise `TypeError`

`RegistryEntry.model_identity_hash` 則以 model name、source kind 與既有 payload
hash 產生完整且唯讀的 registry identity；它不變更 store lookup key、freshness
decision 或 response-cache key。

目前已落地的受限 response-cache boundary 包含：

- `async_model_gateway.response_cache.ResponseCache`
- `async_model_gateway.response_cache.CacheKey`
- `CacheHit` / `CacheMiss` 與 `Remembered` / `Skipped` / `Failed` outcomes

其中 `CacheStore`、`CacheCodec`、`VersionTokenFactory` 與 `CacheInvalidator` 都是
submodule-only surface。`ResponseCache` 單獨建立完整 record，internal process-local store
只做 whole-record replacement 與 token-guarded cleanup；它們不代表 persistence、settings、
eviction 或 orchestration 已落地。

目前已落地的最小 model-artifact shared read contract 包含：

- `async_model_gateway.model_runtime.model_artifact.ModelArtifact`
- `async_model_gateway.model_runtime.model_artifact.LoaderFamily`

其中 `ModelArtifact` 只負責 shared read contract。internal composition 會在 pool
acquisition 前，依顯式 family 解析配對的 Loader 與 Executor；ONNX route 會 lazy 建立
provider session，並由 pool 建立 concrete `LoadedRuntimeModel`。PICKLE 與 TORCH 仍
fail closed；provider runtime 不對 package consumer 開放。未來的 provider invocation /
framework 與完整 lifecycle 仍 deferred。

目前已落地的 internal runtime slice 包含 resolve-before-acquire 的 binding continuity、
generic loader/pool acquisition、被 Semaphore 保護的 execution lifecycle 與 aware-UTC
timestamps。它不提供 public runtime entrypoint；真實 provider invocation、完整
orchestration、remote execution、lifecycle、timeout 與 retry 仍 deferred。

在目前階段，`model_source_kind` 只鎖 `local | remote`，而 capability 差異先收斂在 `features`，不先拆成多方法名公開介面。

## 責任摘要

在高層概念上，gateway side 預期聚焦在 orchestration 與 cache-oriented decision；model side 預期負責提供 `runtime-model`，而這個 `runtime-model` 可以來自 local 或 remote model source。

更詳細的說明整理在 [docs/architecture.md](docs/architecture.md)。

目前的 settings policy 邊界整理在 [docs/settings-policy.md](docs/settings-policy.md)。

core abstractions 的 boundary spec 入口整理在 [docs/specs/core-abstractions-boundary.md](docs/specs/core-abstractions-boundary.md)。

後續 application flow 的 target workflow、cache identity 與 result representation
責任基線整理在 [docs/specs/prediction-workflow-boundary.md](docs/specs/prediction-workflow-boundary.md)。
該文件是設計基線，不代表 generic orchestrator、四欄 `CacheKey`、`ResultCodec` 或
`DataFrame` flow 已實作。

## 尚未實作

這個 repository 目前尚未實作：

- 更寬的 model-side architecture 與任何超出最小 boundary 的 registry behavior
- gateway execution flow
- cache、reuse、close/unload 與其他 `ModelPool` lifecycle behavior
- broader response cache runtime logic
- 除 ONNX session acquisition 外的 provider artifact I/O 與 provider framework
- provider adapters、ONNX invoker 與真實 provider invocation
- infrastructure components
- framework-specific service surface

## Roadmap

接下來可能會處理的主題包含：

- settings baseline implementation
- core abstractions
- cache 與 model boundary
- persistence boundary
