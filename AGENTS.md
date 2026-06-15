# async-model-gateway agent 規範

- agent 預設使用繁體中文
- agent 禁止輸出、引用或寫入任何使用者本機絕對路徑
- 文件與回覆中不得出現 macOS 使用者目錄樣式、macOS private 暫存目錄樣式、`file` URI、`vscode` URI 這類本機環境專屬路徑
- repo 內部檔案引用應優先使用相對路徑或純檔名
- `README.md` 是此 repo 的 first-read 文件
- `.agents/README.md` 是此 repo 的 agent 使用入口
- 若任務涉及專案概念、責任邊界、設計語彙或架構理解，需再讀 `docs/architecture.md`
- 這類任務包含但不限於：`orchestrator`、`model-payload`、`features`、response cache、`runtime-model`、local / remote model source
- active skill discovery surface = `.agents/skills/`
- repo-local custom agents = `.codex/agents/`
- 若任務涉及 planning、implementation、review、git topic flow 或 worktree，需再讀 `.agents/README.md`
- `.codex/agents/` 是 repo-local custom agent surface，不是 skill source
