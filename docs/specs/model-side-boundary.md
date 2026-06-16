# model side boundary

## 摘要

這份文件定義 model side 的正式共享詞彙與責任邊界。

目前 model side 固定由三個業務名詞構成：

- `ModelRegistry`
- `ModelPool`
- `ModelGateway`

`runtime-model` 則是 model side 對外暴露的 consumption boundary。

## `ModelRegistry`

`ModelRegistry` 是 payload identity 與 freshness authority。

它負責：

- 從 canonical input 派生穩定的 `payload-hash`
- 判斷 registry state 是否需要更新
- 提供與 payload identity 相關的決策資訊給 `orchestrator`

它不負責：

- model 下架
- local model lifecycle
- remote model execution
- response cache persistence

## `ModelPool`

`ModelPool` 是 local model runtime and lifecycle owner。

它負責：

- local model availability
- local model 上下架
- local `runtime-model` 的取得與生命週期責任

它不負責：

- `payload-hash` authority
- registry freshness authority
- remote model side boundary

## `ModelGateway`

`ModelGateway` 是 remote model side boundary。

它負責：

- remote model source 路徑
- remote model side 的接取責任
- 對 `orchestrator` 暴露 remote path 可消費的 model-side boundary

它與 `ModelPool` 並列，而不是被 `ModelPool` 吞進去。

## `runtime-model`

`runtime-model` 是 model side 對外暴露的 consumption boundary。

目前只固定其邊界角色，不定義最終 class、protocol 或 provider contract。
