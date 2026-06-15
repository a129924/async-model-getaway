# Git branch naming examples

Use these examples after `SKILL.md` has already narrowed the task to naming or repairing development branches.

## New branch from a fresh task

### Prefer a semantic development branch
```bash
git switch -c feat/andrew/auth-session-timeout
```

- `feat` matches the development intent.
- `auth-session-timeout` is short, scoped, and business-facing.

### Avoid vague catch-all names
```bash
git switch -c misc/update-stuff
```

- This hides scope, type, and business intent.
- Treat it as a rename-required branch, not as a harmless shortcut.

## Started work on the wrong branch

### Move uncommitted work off `main` safely
```bash
git checkout -b fix/andrew/api-error-mapping
```

- Existing uncommitted changes move with the new branch.
- This is the default rescue path when the user started on `main` or `master`.

### Repair a misnamed current branch
```bash
git branch -m feat/andrew/auth-session-timeout
```

- Use rename when the current branch already represents the right task but carries the wrong name.

## Branch name conflict

### Check whether the existing branch is truly the same task
```text
Existing branch: feat/andrew/auth-session-timeout
Current task: new timeout policy for partner sessions
Recommended rename: feat/andrew/auth-session-timeout-v2
```

- Reuse the exact name only for the same task lineage.
- Otherwise choose a more precise suffix or a clearer semantic tail.

## Broad or overloaded task names

### Split multi-scope work into separate branches
```text
Instead of:
feat/andrew/auth-ui-api-cleanup

Prefer:
feat/andrew/auth-session-timeout
fix/andrew/ui-error-banner
```

- If one branch name tries to carry several scopes, that is usually a task-splitting signal.

### Compress to one honest abstraction when the task is truly one thing
```text
refactor/andrew/session-contract-cleanup
```

- This is acceptable when the underlying work is one cleanup that spans several files but one semantic goal.

## Type alignment with commit semantics

### Keep branch type and commit family coherent
```text
Branch: fix/andrew/query-null-handling
Commit: fix(查詢): 修正 null 條件造成查詢漏資料
```

- Branch type and commit type should not tell opposite stories.

### Repair a mismatch
```bash
git branch -m feat/andrew/query-null-handling
```

- If the branch says `fix` but the change is clearly a new capability, rename the branch rather than living with semantic drift.

## Namespace fallback

### Ask for an approved namespace token instead of inventing one
```text
This repository does not appear to use personal usernames in branch names.
Which namespace token should replace `<username>` here?
```

- Do not silently substitute `team`, `shared`, or another token without repo approval.

## Anti-pattern summary

- coding on `main` and pretending branch naming can wait forever
- names like `tmp/fix`, `misc/stuff`, or `feature/everything`
- overloaded descriptions that really describe two or more task branches
- name-conflict handling that reuses another task's branch without checking lineage
