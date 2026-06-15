---
name: python-pyproject-toolconfig
description: Append missing ruff, pyright, and pytest configuration sections to an existing pyproject.toml without overwriting existing settings.
complexity: medium
risk_profile:
  - code_modification
inputs:
  - "--python-version: Python 版本字串，必須向人類詢問（例如 3.10、3.12）"
  - "--package-name: 套件/模組名稱，用於 pyright include 路徑，必須向人類詢問"
  - "pyproject.toml: 執行前必須已存在於當前工作目錄"
outputs:
  - "修改後的 pyproject.toml，補充了缺少的 [tool.ruff]、[tool.pyright]、[tool.pytest.ini_options] section"
  - "stdout 報告，列出每個 append 或跳過的 section"
  - "若所有 section 已存在，則不做任何修改"
use_when:
  - "Python 專案有 pyproject.toml，但缺少一個或多個 tool 配置 section"
  - "為新專案或現有專案建立 linting、型別檢查、測試配置"
  - "跨專案標準化工具設定，同時保留現有客製化設定"
do_not_use_when:
  - "專案使用 setup.cfg、tox.ini 或個別工具配置檔，而非 pyproject.toml"
  - "需要修改或更新現有工具配置（本 skill 只做 append）"
  - "需要配置 [tool.coverage]、[tool.mypy] 等本 skill 範圍外的工具"
---

# Purpose

為 Python 專案的 `pyproject.toml` 補充標準 `[tool.ruff]`、`[tool.pyright]`、`[tool.pytest.ini_options]` 配置 section。只新增缺少的 section；已存在的 section 一律不修改。

# Trigger / When to use

**使用時機：**
- Python 專案有 `pyproject.toml`，但缺少一個或多個 tool 配置 section
- 為新專案或現有專案建立 linting、型別檢查、測試配置
- 跨專案標準化工具設定，同時保留現有客製化設定

**不使用時機：**
- 專案使用 `setup.cfg`、`tox.ini` 或個別工具配置檔，而非 `pyproject.toml`
- 需要修改或更新現有工具配置（本 skill 只做 append）
- 需要配置 `[tool.coverage]`、`[tool.mypy]` 等本 skill 範圍外的工具

# Inputs

| 輸入 | 來源 | 說明 |
|---|---|---|
| `--python-version` | **必須詢問人類** | Python 版本字串，含點號，例如 `3.10`、`3.12` |
| `--package-name` | **必須詢問人類** | 套件/模組名稱，用於 pyright include 路徑，例如 `mylib` |
| `pyproject.toml` | 當前工作目錄 | 執行前必須已存在 |

**重要**：`--python-version` 和 `--package-name` 必須向人類詢問，不得自行推斷或猜測。

# Process

1. **確認** 當前工作目錄中 `pyproject.toml` 存在。

2. **詢問人類** 兩個必要值：
   - `--python-version`：專案 Python 目標版本，格式含點號（例如 `3.10`）
   - `--package-name`：位於 `src/` 下的可匯入套件名稱（例如 `mylib`）

3. **執行 script**（從專案根目錄）：
   ```bash
   uv run skills/python-pyproject-toolconfig/scripts/apply_toolconfig.py \
     --python-version 3.10 \
     --package-name mylib
   ```

4. **確認 stdout 輸出**：確認哪些 section 被 append（`✅ Will append`），哪些因已存在而跳過（`ℹ️ already exists`）。

5. **驗證** `pyproject.toml` 仍為合法 TOML：
   ```bash
   uv run -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('TOML valid')"
   ```

# Examples

- **Positive**: Run from project root with `--python-version 3.11 --package-name mypackage`; script detects no existing `[tool.*]` sections and appends ruff, pyright, and pytest blocks. See `examples.md` for full expected stdout.
- **Negative**: Passing `--python-version py311` instead of `3.11`; this produces `target-version = "pypy311"` in the ruff section. Always pass bare version strings such as `3.10` or `3.11`.

# Outputs

- 修改後的 `pyproject.toml`，補充了缺少的 `[tool.ruff]`、`[tool.pyright]`、`[tool.pytest.ini_options]` section
- stdout 報告，列出每個 append 或跳過的 section
- 若所有 section 已存在，則不做任何修改

# Boundaries

- **不修改** `[project]`、`[build-system]` 或任何非 `[tool.*]` section
- **不覆蓋**也不合併現有 `[tool.*]` section，只 append 缺少的
- **不管理** `[tool.ruff] exclude` patterns，由使用者自行維護
- **不支援** `[tool.coverage]`、`[tool.mypy]` 或其他本 skill 範圍外的工具
- 需要 `uv` 已安裝並可在 `PATH` 中存取
- 執行前 `pyproject.toml` 必須已存在於當前工作目錄
- **不負責更新**現有 `[tool.*]` section 的內容；修改現有設定的維護責任由 human 承擔

# Validation

## Required Checks
- pyproject.toml must exist in target directory before appending

## Quality Checks
- verify appended sections do not duplicate existing sections

## On Soft Fail
- If required inputs (python-version, package-name) are missing, stop and ask before proceeding

# Failure Handling

## Missing Context
- BLOCKED — if pyproject.toml does not exist or python-version / package-name not provided, stop and ask

## Ambiguous Requirement
- If package name is ambiguous, ask for clarification; do not guess

## Execution Limitation
- If pyproject.toml cannot be parsed, report the parse error and stop

# Local references

| 項目 | 用途 |
|---|---|
| `scripts/apply_toolconfig.py` | 可執行 script：偵測現有 section，append 缺少的 section |
| `templates/toolconfig-ruff.toml.tmpl` | `[tool.ruff]` 與 `[tool.ruff.lint]` section 範本，含 placeholder |
| `templates/toolconfig-pyright.toml.tmpl` | `[tool.pyright]` section 範本，含 placeholder |
| `templates/toolconfig-pytest.toml.tmpl` | `[tool.pytest.ini_options]` section 範本 |
| `tests/` | 單元測試：section 偵測、placeholder 替換、冪等性、既有設定保留 |
