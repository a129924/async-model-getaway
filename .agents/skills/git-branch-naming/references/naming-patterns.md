# Naming patterns

## Preferred development branch shape

Use:

```text
<type>/<username>/<short-description>
```

Examples:

- `feat/andrew/auth-session-timeout`
- `fix/andrew/api-error-mapping`
- `docs/andrew/release-guide-update`

## Type family

Keep development branch types aligned with commit semantics:

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

Release and hotfix timing decisions belong to `git-release-management`, even if naming style later stays compatible.

## Short-description rule

- prefer about 2-4 words
- use lowercase kebab-case
- describe one semantic target
- avoid filler such as `update`, `stuff`, `misc`, or `temp`
