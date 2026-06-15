# Git commit convention examples

Use these examples after `SKILL.md` has already narrowed the job to drafting or reviewing semantic commit messages from staged changes.

## Semantic subjects over code-motion subjects

### Prefer business-facing language
```text
fix(錯誤處理): 修正語意派例外鏈結遺失

當 API 驗證失敗時，保留原始例外鏈結，避免 CLI 報告失去根因。
Relates-to: #456
```

- The subject describes the business or operator-visible effect.
- The body explains why the fix matters, not merely which class changed.

### Avoid code-motion-only subjects
```text
fix: add CustomException class
```

- This says what code moved, not what user or business failure changed.
- Treat this as a rewrite signal, not as a final commit message.

## Noise isolation

### Split formatter or lockfile noise away from a feature
```bash
git reset
git add -p src/
git commit -m "feat(auth): 實作登入節流規則"

git add poetry.lock
git commit -m "chore(build): 更新鎖定依賴"
```

- Lockfiles, snapshots, generated files, and wide formatter churn should not dilute a semantic `feat:` or `fix:` commit.
- If the user staged everything already, prefer repair guidance over silently accepting the mixed set.

### Avoid mixed business and noise commits
```text
feat(auth): 實作登入節流規則
```
with:
- `src/auth/service.py`
- `poetry.lock`
- 400-line formatter rewrite in unrelated modules

- This is a split-required case unless the lockfile change is the direct result of the same intentional unit and the noise is trivial.

## Partial staging

### Ask whether the message should describe only the staged subset
```text
You staged only the validation hunk from `user_service.py`.
Should this commit describe only that validation fix, or do you intend to stage the remaining refactor before committing?
```

- Partial staging is valid, but the semantic contract must match the staged subset.
- Do not assume the unstaged context belongs in the commit title.

### Repair with `git add -p`
```bash
git add -p src/user_service.py
git commit -m "fix(驗證): 修正空白使用者名稱未被拒絕"
```

- Patch staging is a semantic-cleanup tool, not just a low-level Git trick.

## Monorepo and multi-scope changes

### Use a composite scope only when one business change truly spans both modules
```text
feat(ui,api): 實作語意派錯誤提示與對應回傳格式
```

- This passes only when the UI and API changes are one inseparable business capability.

### Prefer split commits when module intent differs
```bash
git reset
git add frontend/src/error_banner.tsx
git commit -m "feat(ui): 顯示語意派驗證錯誤提示"

git add backend/app/error_mapping.py
git commit -m "fix(api): 修正語意派錯誤碼映射"
```

- Crossing module boundaries is not, by itself, proof that one commit should stay whole.

## Breaking changes

### Mark incompatible API changes explicitly
```text
feat!(api): 改用顯式 keyword-only 參數建立 Session

移除舊的 positional `timeout` 呼叫方式，避免語意不明的參數排列。

Migration:
- 將 `create_session("fast", 30)` 改為 `create_session("fast", timeout=30)`
Closes #812
```

- `!` belongs in the header when callers must change behavior or call shape.
- The body should show the migration, not merely mention that one exists.

## Amend instead of noisy follow-up commits

### Suggest `--amend` for tiny fixes to the latest commit
```bash
git add README.md
git commit --amend
```

- Use this when the last commit only missed a footer, typo, or one closely related file.
- Do not create `docs: fix typo` immediately after a just-made feature commit when the typo is part of the same change set.

## Cross-skill warnings

### Warn when testing or strict typing already failed
```text
Recommended commit:
fix(型別): 修正 Result[T] 分支回傳不一致

Warning:
- `python-type-hints-strict` is currently failing on `service/result.py`
- `python-testing-pytest` still reports one failing behavior test
```

- Commit drafting still helps, but the agent should not pretend the change is ready for PR or release.

## Anti-pattern summary

- `feat: update files`
- one huge commit that mixes feature work, dependency churn, and formatter output
- a subject that mentions only renamed classes or moved files
- no body for a breaking or edge-case-heavy change
- no footer even though the change clearly tracks an issue or bug ticket
