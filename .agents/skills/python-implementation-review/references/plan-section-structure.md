# Plan Section Structure

Plans produced by `python-plan-authoring` contain 13 sections in this order:

1. `## Goal`
2. `## Non-goals`
3. `## Current Context`
4. `## Requirements`
5. `## Decisions`
6. `## Public Contract / API Changes`
7. `## Affected Files / Modules`
8. `## Implementation Steps`
9. `## Test Plan`
10. `## Validation Commands`
11. `## Risks`
12. `## Rollback Plan`
13. `## Open Questions`

`python-implementation-review` traces only four of these sections:

| Section | What this skill checks |
| --- | --- |
| `## Implementation Steps` | Is each numbered step present in the implementation? |
| `## Non-goals` | Has any "will not do" item been done anyway (scope creep)? |
| `## Public Contract / API Changes` | Does the implementation match the authorized signatures, return types, and exceptions? |
| `## Test Plan` | Are the specified test case types present in the specified test files? |

The other nine sections are informational context. They do not produce traceability findings.
