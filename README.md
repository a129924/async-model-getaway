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

這些目前都屬於設計層級的概念，用來做規劃與對齊，還不是已實作的 Python type 或 runtime feature。

目前唯一已落地的最小核心，是
`async_model_gateway.model_registry.model_payload.hash_model_payload`：

- 它負責把 `model-payload` 作 recursive canonicalization 後產生穩定的
  SHA-256 hex digest
- nested dict 會 canonicalize
- list 順序保留
- scalar 不做 normalization
- unsupported type 會 fail closed 並 raise `TypeError`

在目前階段，`model_source_kind` 只鎖 `local | remote`，而 capability 差異先收斂在 `features`，不先拆成多方法名公開介面。

## 責任摘要

在高層概念上，gateway side 預期聚焦在 orchestration 與 cache-oriented decision；model side 預期負責提供 `runtime-model`，而這個 `runtime-model` 可以來自 local 或 remote model source。

更詳細的說明整理在 [docs/architecture.md](docs/architecture.md)。

目前的 settings policy 邊界整理在 [docs/settings-policy.md](docs/settings-policy.md)。

core abstractions 的 boundary spec 入口整理在 [docs/specs/core-abstractions-boundary.md](docs/specs/core-abstractions-boundary.md)。

## 尚未實作

這個 repository 目前尚未實作：

- `ModelRegistry` 的 freshness decision 與完整 registry behavior
- gateway execution flow
- model pool behavior
- response cache logic
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
