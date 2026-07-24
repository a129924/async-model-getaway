# async-model-gateway agent 入口

## 讀取順序

1. 先讀 `AGENTS.md`
2. 再讀 `README.md`
3. 若任務涉及專案概念、責任邊界或設計語彙，再讀 `docs/architecture.md`
4. 若任務涉及 planning、implementation、review、git topic flow 或 worktree，再讀對應 `.agents/skills/`

## Surface 定位

- `.agents/skills/` 是 active discovery surface
- `.codex/agents/` 是 repo-local custom agent surface
- `.codex/agents/` 不是 skill source

## 已安裝 Skills

### Workflow / Planning

- `scope-draft-plan`
- `plan-creator`
- `plan-reviewer`
- `plan-step-tracker`
- `subagent-dispatch-policy`
- `python-plan-authoring`
- `python-plan-review`

### Python Core

- `python-async-planning`
- `python-async-await`
- `python-implementation-review`
- `python-code-review`
- `python-type-hints-strict`
- `python-testing-pytest`
- `python-tdd-test-authoring`
- `python-package-layout`
- `python-module-boundaries`
- `python-api-signature`
- `python-class-design`
- `python-error-handling`
- `python-library-architecture`

### Repo Tooling

- `python-pre-commit`
- `python-pyproject-toolconfig`

### Git / Workspace

- `git-commit-convention`
- `git-branch-naming`
- `worktree-manager`

## 使用原則

- 規劃 topic 時，優先讀 `plan-creator`、`python-plan-authoring`，必要時補 `python-async-planning`
- 審查或修正 plan 時，優先讀 `plan-reviewer`、`python-plan-review`
- 實作 Python 變更時，依需求讀對應 Python core skills，不把單一 skill 擴張成整套架構規則
- 做 implementation review 時，優先讀 `python-implementation-review`；若要做較廣的品質審查，再補 `python-code-review`
- 準備 commit 時，先讀 `git-commit-convention`
- 需要建立或修正 branch naming 時，讀 `git-branch-naming`
- 明確涉及 worktree lifecycle 時，才讀 `worktree-manager`

## Custom Agents

- `planner`：只做 topic plan 或 refine，不實作、不 commit、不 push
- `implementer`：只做已核准範圍內的 repo 變更，不 commit、不 push
- `reviewer`：只做 correctness、boundary 與 validation review，不 commit、不 push
