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

目前 package version baseline 為 `0.4.5`。repo 目前已落地最小
`ModelRegistry` boundary，並補齊最小 operational `ResponseCache`
boundary：`async_model_gateway.response_cache` 公開
`ResponseCache`、`ResponseCacheEntry`、`ResponseCacheKey` 與
`ResponseCacheKeyFactory`，而 `async_model_gateway.response_cache.ports`
提供 `FeatureHasher` port；`ResponseCacheStore` 仍維持為 submodule-only
surface。repo 也已把最小 `ModelArtifact` + `LoaderFamily` shared read
contract 納入 baseline：`async_model_gateway.model_artifact` 公開
`ModelArtifact` 與 `LoaderFamily`，用來表達 local artifact identity 與顯式
loader family。這不代表 `LocalModelLoader`、artifact I/O、`ModelPool`
runtime behavior 已完成。
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
model-registry boundary 與最小 operational response-cache boundary 已以狹義
public surface 落地。除此之外，較寬的 `features` semantics、response cache
architecture、`orchestrator` 與 `runtime-model` flow 仍不是已完成的 Python type
或 runtime feature。

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

- `async_model_gateway.model_artifact.ModelArtifact`
- `async_model_gateway.model_artifact.LoaderFamily`

其中 `ModelArtifact` 只負責 shared read contract；`LocalModelLoader`、artifact
I/O 與 `ModelPool` runtime behavior 仍 deferred。

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
- `LocalModelLoader`
- artifact I/O
- `ModelPool` runtime behavior
- broader response cache runtime logic
- `runtime-model` acquisition
- provider adapters
- infrastructure components
- framework-specific service surface

## Roadmap

接下來可能會處理的主題包含：

- settings baseline implementation
- core abstractions
- cache 與 model boundary
- persistence boundary
