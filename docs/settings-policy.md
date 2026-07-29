# async-model-gateway settings policy

## 摘要

這份文件只固定 initialization 階段的 settings policy 邊界，不定義實作。

目前目標是避免 settings 在真正開始系統切片前，先被過度設計成完整 schema、完整 env surface 或完整 persistence config。

## 目前定位

- settings 以 developer-injected policy 為主
- internal response-cache TTL freshness 以 developer injection 提供，不形成 settings surface
- remote 或 provider-specific config 延後
- 不先把 settings 擴張成 runtime orchestration surface

## 近期預留概念

目前只預留或限定這類 policy 類型：

- process-local response-cache 的正 TTL freshness policy 由呼叫端明確注入；它不是
  settings loading、env var 或 persistence config
- eviction 類型設定
- 與 cache 行為有關的開關或策略

除上述 internal 注入式 TTL policy 外，其餘仍是概念層級，不代表已定案的 Python type、
env var 名稱或設定載入方式。

## 明確延後

這一輪明確不做：

- `pydantic` model
- `.env.example`
- env var 命名最終定案
- settings loading precedence
- `model-payload` schema
- response cache persistence schema
- remote/provider-specific config
- database、Redis 或 `SQLAlchemy` integration

## 原則

- 若後續某個 topic 只需要少量 policy，優先讓開發者以明確注入方式提供，而不是先做完整 global settings system
- 若某個設定需求其實隱含 persistence、provider contract 或 runtime-model acquisition 決策，應把它歸回對應系統 topic，而不是偽裝成 initialization settings
- 真正導入 `pydantic` 的時機，應是 settings baseline 已有明確 shape 與載入邊界之後，而不是為了提前佔位
