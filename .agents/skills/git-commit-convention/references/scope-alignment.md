# Scope alignment

## Preferred source of truth

1. Use the repository's explicit scope map when it exists.
2. If no map exists, choose a short domain or module label that other commits in the repo would recognize.
3. If one commit truly spans two inseparable module contracts, allow a composite scope.

## Branch alignment

Branch naming and commit scope should reinforce the same semantic area.

- Branch: `feat/andrew/auth-session-timeout`
- Commit: `feat(auth): 實作 Session 逾時保護`

If the branch says `auth` but the commit says `ui` and the staged change is mostly UI, pause and ask whether the work belongs on another branch or whether the branch name should be repaired.

## Composite scopes

Composite scopes are allowed only when one intentional change crosses boundaries that cannot be meaningfully separated.

- Allowed: `feat(ui,api): 實作語意派錯誤提示與回傳格式`
- Prefer split instead of: one commit that mixes `ui`, `api`, and unrelated docs churn

Composite scopes are a fallback, not the default.
