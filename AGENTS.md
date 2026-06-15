# async-model-gateway agent 規範

- agent 預設使用繁體中文
- agent 禁止輸出、引用或寫入任何使用者本機絕對路徑
- 文件與回覆中不得出現 `/Users/...`、`/private/...`、`file://...`、`vscode://...` 這類本機環境專屬路徑
- repo 內部檔案引用應優先使用相對路徑或純檔名
- `README.md` 是此 repo 的 first-read 文件
- 若任務涉及專案概念、責任邊界、設計語彙或架構理解，需再讀 `docs/architecture.md`
- 這類任務包含但不限於：`orchestrator`、`model-payload`、`features`、response cache、`runtime-model`、local / remote model source
