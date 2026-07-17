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

目前 package version baseline 為 `0.6.0`。repo 目前已落地最小
`ModelRegistry` boundary，並補齊最小 operational `ResponseCache`
boundary：`async_model_gateway.response_cache` 公開
`ResponseCache`、`ResponseCacheEntry`、`ResponseCacheKey` 與
`ResponseCacheKeyFactory`，而 `async_model_gateway.response_cache.ports`
提供 `FeatureHasher` port；`ResponseCacheStore` 仍維持為 submodule-only
surface。repo 也已把最小 `ModelArtifact` + `LoaderFamily` shared read
contract 納入 baseline：
`async_model_gateway.model_runtime.model_artifact` 公開 `ModelArtifact` 與
`LoaderFamily`，並由 `model_runtime` 作為後續 model-runtime family layout 的
umbrella root，用來表達 shared read contract 的最小 artifact metadata 與顯式
loader family vocabulary。repo 也已落地最小 local acquisition boundary：
`async_model_gateway.model_runtime.model_pool.ModelPool` 以 async
`acquire(...)` 消費 `ModelArtifact`，並保有私有的 `LocalModelLoader`。該 loader
只依 `LoaderFamily` 的顯式 `pickle`、`torch`、`onnx` 分支路由，且以
`assert_never(...)` 收束 closed enum 的不可達 fallback；它不依 path 或內容猜測
family。repo 也已在
`async_model_gateway.model_runtime.runtime_model` 落地 abstract
`LoadedRuntimeModel` consumption contract：其唯一 public semantic 是
`loader_family`；provider runtime 只由私有 local implementation 保存，並透過
non-public internal handoff 交給最小 `ModelExecution` boundary。`ModelPool.acquire(...)`
與 private loader 的 return type 已收窄為這個 contract。repo 現在也已在
`async_model_gateway.model_runtime.model_execution` 公開 generic `ModelExecution`：
它以 injected typed async callable 消費 provider runtime 與 invocation，並 direct-await
單次呼叫；一般例外與 cancellation 會原樣傳播。這不代表 artifact I/O、真實 provider
invocation、provider framework、完整 orchestration、remote execution、lifecycle、
timeout 或 retry 已完成。
root package 目前只公開 `__version__` 與 `main`；`ModelRegistry` 由
`async_model_gateway.model_registry` 提供，
`async_model_gateway.model_registry.stores` 提供 submodule public 的
`InMemoryRegistryStore`，而 `model-payload` hashing 的 public owner 仍維持為
`ModelPayloadHasher`。這不代表 cache backend、TTL policy、`orchestrator`
flow 或 broader cache architecture 已完成。

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
model-registry boundary、最小 operational response-cache boundary，以及狹義的
model-artifact、local acquisition、runtime-model consumption 與 `ModelExecution`
boundary 已落地。除此之外，較寬的 `features` semantics、response cache
architecture、`orchestrator` 與完整 `runtime-model` flow 仍不是已完成的 Python
type 或 runtime feature。

目前已落地的最小 model-registry boundary 包含：

- `async_model_gateway.model_registry.ModelRegistry`
- `async_model_gateway.model_registry.stores.InMemoryRegistryStore`
- `async_model_gateway.model_registry.model_payload.ModelPayloadHasher`

其中 `ModelPayloadHasher`：

- 它的 public method `hash_model_payload(...)` 負責把 `model-payload` 作
  recursive canonicalization 後產生穩定的 SHA-256 hex digest
- nested dict 會 canonicalize
- list 順序保留
- scalar 不做 normalization
- unsupported type 會 fail closed 並 raise `TypeError`

目前已落地的最小 operational response-cache boundary 包含：

- `async_model_gateway.response_cache.ResponseCache`
- `async_model_gateway.response_cache.ResponseCacheEntry`
- `async_model_gateway.response_cache.ResponseCacheKey`
- `async_model_gateway.response_cache.ResponseCacheKeyFactory`
- `async_model_gateway.response_cache.ports.FeatureHasher`

其中 `ResponseCacheStore` 仍維持為 submodule-only surface。

目前已落地的最小 model-artifact shared read contract 包含：

- `async_model_gateway.model_runtime.model_artifact.ModelArtifact`
- `async_model_gateway.model_runtime.model_artifact.LoaderFamily`

其中 `ModelArtifact` 只負責 shared read contract。最小 `ModelPool` 只提供
async local acquisition；其私有 `LocalModelLoader` 消費這個 contract 並作 explicit
family dispatch，並以 `LoadedRuntimeModel` 作 typed return boundary。artifact I/O、
provider framework 與完整 lifecycle 仍 deferred。

目前已落地的最小 model-execution boundary 包含：

- `async_model_gateway.model_runtime.model_execution.ModelExecution`
- injected typed async callable seam
- 單次 invocation 的 direct-await
- 一般例外與 cancellation 原樣傳播

它只擁有最小 invocation semantics；真實 provider invocation、loader I/O、完整
orchestration、remote execution、lifecycle、timeout 與 retry 仍 deferred。

在目前階段，`model_source_kind` 只鎖 `local | remote`，而 capability 差異先收斂在 `features`，不先拆成多方法名公開介面。

## 責任摘要

在高層概念上，gateway side 預期聚焦在 orchestration 與 cache-oriented decision；model side 預期負責提供 `runtime-model`，而這個 `runtime-model` 可以來自 local 或 remote model source。

更詳細的說明整理在 [docs/architecture.md](docs/architecture.md)。

目前的 settings policy 邊界整理在 [docs/settings-policy.md](docs/settings-policy.md)。

core abstractions 的 boundary spec 入口整理在 [docs/specs/core-abstractions-boundary.md](docs/specs/core-abstractions-boundary.md)。

## 尚未實作

這個 repository 目前尚未實作：

- 更寬的 model-side architecture 與任何超出最小 boundary 的 registry behavior
- gateway execution flow
- artifact I/O
- cache、reuse、close/unload 與其他 `ModelPool` lifecycle behavior
- broader response cache runtime logic
- 真實 local `runtime-model` acquisition
- provider adapters
- infrastructure components
- framework-specific service surface

## Roadmap

接下來可能會處理的主題包含：

- settings baseline implementation
- core abstractions
- cache 與 model boundary
- persistence boundary
