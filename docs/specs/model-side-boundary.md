# model side boundary

## 摘要

這份文件定義 model side 的正式共享詞彙與責任邊界。

目前 model side 固定由三個業務名詞構成：

- `ModelRegistry`
- `ModelPool`
- `ModelGateway`

`runtime-model` 則是 model side 對外暴露的 consumption boundary。

## `ModelRegistry`

`ModelRegistry` 是 identity context owner、`payload-hash` authority 與 freshness authority。

目前 repo 已落地這個 boundary 的最小 class-first 版本：
`async_model_gateway.model_registry.ModelRegistry`。

它透過位於 `async_model_gateway.model_registry.ports.store` 的 async-only
`RegistryStore` 做 lookup 與條件式 persistence，並持續以既有的
`async_model_gateway.model_registry.model_payload.ModelPayloadHasher`
作為 `payload-hash` owner。

它負責：

- 消費以下 identity context：
  - `model_name`
  - `model_source_kind`
  - `model-payload`
- 以 `model_name + model_source_kind` 作為 store lookup identity
- 從上述 identity context 派生穩定的 `payload-hash`
- 交付受限的 freshness decision：`first-seen`、`unchanged`、`changed`
- 在 freshness 不是 `unchanged` 時更新 registry state
- 提供與 payload identity 相關的決策資訊給 `orchestrator`

它不負責：

- model 下架
- local model lifecycle
- remote model execution
- response cache persistence

gateway / registry 不做語意等價判斷；只要 `model-payload` material 不同，就一律視為模型已更新。

目前已落地的 hashing core 也遵守這個原則：dict key order 會被 canonicalize，
但 list order 仍屬 identity material，`1` 與 `1.0` 也不會被視為同一份 payload。

目前這個最小 boundary 仍不擴張到 cache wiring、runtime-model acquisition、
`ModelPool`、`ModelGateway` 或更寬的 model-side orchestration。

## `ModelPool`

`ModelPool` 是 local model runtime and lifecycle owner。

它只屬於 `local` 路徑。

它負責：

- local model availability
- local model 上下架
- local `runtime-model` 的取得與生命週期責任
- 在內部消化 local runtime 種類、backend 差異與生命週期細節
- 透過 `LocalModelLoader` 完成 local acquisition，再交付統一的 `runtime-model`

它不負責：

- `payload-hash` authority
- registry freshness authority
- remote model side boundary
- 把 local runtime taxonomy 提前暴露成 canonical input 欄位

## `LocalModelLoader`

`LocalModelLoader` 是 `ModelPool` 內部的 local acquisition sub-boundary。

它的輸入是 `model_artifact`，而不是 `model-payload`。

它負責：

- 根據 `model_artifact` 選 loader family
- 定位要讀的 artifact
- 接收讀取所需的額外資訊
- 讀取 local artifact
- 轉成 Python object
- 再統一包裝成 `runtime-model`

它不負責：

- 依賴 `model-payload` 猜 loader
- 擁有 identity authority
- 對外暴露 top-level business owner 身分

## Fail-Closed 原則

若 `model_artifact` 缺失、矛盾或資訊不足，`LocalModelLoader` 應直接 fail。

猜副檔名、猜 pickle、猜 object shape 不能作為正式主路徑。

最多只能保留為 deferred fallback note，而不能寫成標準行為。

## `ModelGateway`

`ModelGateway` 是 remote model side boundary。

它只屬於 `remote` 路徑。

它負責：

- remote model source 路徑
- remote model side 的接取責任
- 對 `orchestrator` 暴露 remote path 可消費的 model-side boundary

remote 目前只有單一實際需求，不需要先做更細 provider 分類。

它與 `ModelPool` 並列，而不是被 `ModelPool` 吞進去。

## `runtime-model`

`runtime-model` 是 model side 對外暴露的 consumption boundary。

目前只固定其邊界角色，不定義最終 class、protocol 或 provider contract。

對外能力邊界在目前階段採統一入口；能力差異先收斂在 `features`，不先拆成多方法名公開 surface。
