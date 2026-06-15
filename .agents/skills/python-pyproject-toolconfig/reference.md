# reference.md — python-pyproject-toolconfig

## Placeholder 替換規則

templates 中使用兩種 placeholder，替換邏輯有嚴格的**順序依賴**：

### 兩種 placeholder

| Placeholder | 出現位置 | 預期輸出（以 `3.10` 為例）|
|---|---|---|
| `py${PYTHON_VERSION}` | ruff template 的 `target-version` | `py310`（去掉點） |
| `${PYTHON_VERSION}` | pyright template 的 `pythonVersion` | `3.10`（保留點） |
| `${PACKAGE_NAME}` | pyright template 的 `include` | `mylib` |

### 替換順序（必須依此順序）

```python
# 1. 先處理 py${PYTHON_VERSION} → py310（去掉點）
content = re.sub(r'py\$\{PYTHON_VERSION\}', f"py{python_version_nodot}", content)

# 2. 再處理剩餘的 ${PYTHON_VERSION} → 3.10（保留點）
content = content.replace("${PYTHON_VERSION}", python_version)

# 3. 最後處理 ${PACKAGE_NAME}
content = content.replace("${PACKAGE_NAME}", package_name)
```

**為什麼順序重要**：若先執行步驟 2，`py${PYTHON_VERSION}` 會變成 `py3.10`，步驟 1 的正則就再也匹配不到，ruff 的 `target-version` 會輸出錯誤的 `"py3.10"`（而非 `"py310"`）。

---

## tomllib 限制

Python 3.11+ 內建的 `tomllib` 是**唯讀**模組，只能讀取 TOML，不能寫入。

```python
import tomllib

# ✅ 可以讀取
with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

# ❌ tomllib 沒有 dump/write 功能
# tomllib.dump(data, f)  # AttributeError
```

因此本 script 採用**raw text append**（而非 TOML 序列化）來寫入新 section，這是刻意的設計選擇。

---

## Raw Text Append 安全性

直接對 `pyproject.toml` 做 `open("a")` append 是安全的，原因如下：

1. **TOML table 順序無關**：TOML 規範不要求 `[tool.*]` section 必須出現在檔案特定位置，parser 會正確處理任何順序。

2. **不會破壞現有內容**：只在檔案尾端新增，不修改既有行。

3. **重複 table 偵測**：script 在 append 前先用 `tomllib.load()` 讀取並確認目標 section 不存在，避免產生重複 table（重複 table 在 TOML 中是非法的）。

4. **最終驗證**：Process 第 5 步要求用 `tomllib.load()` 驗證結果，確保 append 後的 TOML 仍合法。

---

## Section 偵測邏輯

Script 只偵測**頂層** `[tool.*]` section 鍵，不偵測子 table（如 `[tool.ruff.lint]`）。

```python
# 偵測到的 key 集合示例
data = tomllib.load(f)
existing_tools = set(data.get("tool", {}).keys())
# → {"ruff", "pyright", "pytest"}  # 頂層 tool 鍵

# "ruff" 包含 lint、pydocstyle 等子 table，但偵測邏輯只看 "ruff" 這個鍵
```

**含義**：
- 若 `pyproject.toml` 中有 `[tool.ruff]`，無論 `[tool.ruff.lint]` 是否存在，整個 ruff section 都視為「已存在」，不會 append。
- 不存在「只有 `[tool.ruff.lint]` 沒有 `[tool.ruff]`」的情況（TOML 子 table 在父 table 鍵下必然可被偵測到）。

---

## 執行命令格式

### 從專案根目錄執行（標準用法）

```bash
uv run skills/python-pyproject-toolconfig/scripts/apply_toolconfig.py \
  --python-version 3.11 \
  --package-name mylib
```

### 驗證結果 TOML 合法

```bash
uv run -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('TOML valid')"
```

### 查看 script help

```bash
uv run --python 3.13 skills/python-pyproject-toolconfig/scripts/apply_toolconfig.py --help
```

### 執行 skill 單元測試

```bash
uv run --with pytest pytest skills/python-pyproject-toolconfig/tests/ -v
```

---

## Script 路徑解析

Script 使用 `Path(__file__).parent.parent` 定位 skill 根目錄，以便找到 `templates/` 目錄：

```
skills/python-pyproject-toolconfig/
├── scripts/
│   └── apply_toolconfig.py   ← __file__
│       parent → scripts/
│       parent.parent → python-pyproject-toolconfig/  ← skill_dir
└── templates/
    └── toolconfig-ruff.toml.tmpl
```

`pyproject.toml` 的路徑則使用 `Path("pyproject.toml")`（相對於 CWD），因此 script 必須從專案根目錄執行。
