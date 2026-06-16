# canonical input boundary

## 摘要

這份文件定義 core abstractions 的輸入邊界。

在目前階段，正式共享的 canonical input 只有：

- `model-payload`
- `features`

## `model-payload`

`model-payload` 是進入核心 orchestration 邊界前，已完成 normalization 的 payload 概念。

它的責任是承載與 model response generation 直接相關的 canonical payload 資訊，而不是保留原始 external request shape。

目前只固定其概念角色，不定義最終 Python type、schema 或序列化形式。

## `features`

`features` 是與 `model-payload` 並列進入 canonical input boundary 的概念。

它承載會影響 response reuse 或 model selection 的特徵訊號，但目前不被定義為最終的 settings object、provider option 或 execution contract。

## Boundary

這一層負責：

- 固定 `model-payload` 與 `features` 作為正式共享輸入詞彙
- 聲明 external request shape 仍 deferred
- 固定它們是進入核心 orchestration boundary 前的 canonical input

這一層不負責：

- 產生 `payload-hash`
- 決定 cache identity
- 決定 registry freshness
- 決定 local / remote model 路徑
- 定義 Python class / protocol

## 依賴方向

`orchestrator` 消費這一層提供的 canonical input。

`ModelRegistry` 可以依賴這一層的 canonical input 來產生 `payload-hash`，但 hashing authority 不屬於這一層。
