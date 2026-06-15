# examples.md — python-pyproject-toolconfig

## 正面範例 1：空白 pyproject.toml → 三個 section 全部 append

**情境**：全新專案，`pyproject.toml` 只有 `[project]` section。

**輸入 pyproject.toml：**
```toml
[project]
name = "mylib"
version = "0.1.0"
requires-python = ">=3.11"
```

**執行命令：**
```bash
uv run skills/python-pyproject-toolconfig/scripts/apply_toolconfig.py \
  --python-version 3.11 \
  --package-name mylib
```

**預期 stdout：**
```
✅ Will append [tool.ruff]
✅ Will append [tool.pyright]
✅ Will append [tool.pytest.ini_options]

✅ Appended 3 section(s) to pyproject.toml
```

**結果**：`pyproject.toml` 新增三個 section，原有 `[project]` 內容完全不變。

---

## 正面範例 2：已有 `[tool.ruff]` → 只 append 缺少的 pyright + pytest

**情境**：專案已有自訂 ruff 設定，只缺 pyright 和 pytest 配置。

**輸入 pyproject.toml：**
```toml
[project]
name = "mylib"

[tool.ruff]
line-length = 88
target-version = "py311"
```

**執行命令：**
```bash
uv run skills/python-pyproject-toolconfig/scripts/apply_toolconfig.py \
  --python-version 3.11 \
  --package-name mylib
```

**預期 stdout：**
```
ℹ️  [tool.ruff] already exists — skipping
✅ Will append [tool.pyright]
✅ Will append [tool.pytest.ini_options]

✅ Appended 2 section(s) to pyproject.toml
```

**結果**：既有 `[tool.ruff]` 的 `line-length = 88` 保持不變；pyright 和 pytest section 被 append。

---

## 反面範例 1：不應直接手動編輯 pyproject.toml 插入 tool section

**錯誤做法**：
```bash
# ❌ 手動複製貼上 TOML 內容到 pyproject.toml
cat >> pyproject.toml << 'EOF'
[tool.ruff]
line-length = 100
EOF
```

**為什麼錯**：
- 可能意外覆蓋既有 `[tool.ruff]` section（TOML 不允許重複 table，會導致解析錯誤）
- 無法自動填入正確的 `target-version`（需要依 Python 版本計算）
- 無法自動填入 `pythonVersion` 和 `include` 路徑
- 跳過了 section 偵測保護，不具冪等性

**正確做法**：使用 `apply_toolconfig.py` script，它會自動偵測、替換 placeholder、並只 append 缺少的 section。

---

## 反面範例 2：`--python-version` 不應傳入 ruff 格式

**錯誤做法**：
```bash
# ❌ 傳入 "py311" 或 "311"
uv run skills/python-pyproject-toolconfig/scripts/apply_toolconfig.py \
  --python-version py311 \
  --package-name mylib

# ❌ 傳入不含點號的純數字
uv run skills/python-pyproject-toolconfig/scripts/apply_toolconfig.py \
  --python-version 311 \
  --package-name mylib
```

**為什麼錯**：

| 傳入值 | ruff target-version | pyright pythonVersion |
|---|---|---|
| `py311` (錯) | `"pypy311"` ❌ | `"py311"` ❌ |
| `311` (錯) | `"py311"` 看似對 | `"311"` ❌ |
| `3.11` (正確) | `"py311"` ✅ | `"3.11"` ✅ |

**正確做法**：
```bash
# ✅ 傳入含點號的版本字串
uv run skills/python-pyproject-toolconfig/scripts/apply_toolconfig.py \
  --python-version 3.11 \
  --package-name mylib
```
