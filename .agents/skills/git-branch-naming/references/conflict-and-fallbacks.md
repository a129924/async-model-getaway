# Conflict and fallback rules

## Existing branch conflict

If the preferred branch name already exists:

1. verify whether it is truly the same task lineage
2. if yes, reuse or continue on that branch deliberately
3. if not, choose a more precise suffix or semantic tail

Examples:

- `feat/andrew/auth-session-timeout-v2`
- `fix/andrew/api-error-mapping-null-case`

## Username fallback

If the repository does not use personal usernames in branch names, do not invent a token. Ask for the approved namespace replacement.

## Broad task compression

If the task name is too long, keep:

1. the dominant business area
2. the dominant action
3. the smallest honest abstraction

If that still requires too many words, split the task instead of cramming everything into one branch name.
