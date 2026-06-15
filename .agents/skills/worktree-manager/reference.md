# worktree-manager reference

Use this file for stable operational details that would make `SKILL.md` too dense.

## Lifecycle terminology

- `create`: create a managed worktree and its intended branch lineage at the canonical path.
- `get-worktree`: inspect worktree state and return a structured recommendation.
- `release worktree`: non-destructive offboarding from the active working set.
- `remove worktree`: destructive removal of the worktree directory and Git registration after an explicit human gate.

Never collapse `release worktree` and `remove worktree` into one action.

## Selector notes

A selector should resolve to one worktree without guessing. Prefer, in order:

1. explicit path
2. explicit branch name
3. explicit worktree name / slug when it maps to one known worktree

If a selector matches more than one candidate or cannot be verified, stop at
inspection or ask for clarification instead of mutating state.

## Managed-path policy

Managed worktrees use this path family:

`../<repo-name>.worktrees/<prefix>-YYYYMMDD-<worktree-name>`

Rules:
- managed worktrees live outside the repository root
- default `<prefix>` is `agent`
- a human may explicitly override the prefix
- path policy decides managed vs unmanaged ownership in v1
- metadata or plan context may add notes, but they do not replace path policy

Examples:
- managed: `../agent-skills.worktrees/agent-20260507-worktree-skill`
- unmanaged: `../scratch/worktree-skill`
- unmanaged: `.github/worktrees/worktree-skill`

## Inspect output contract

Every reported worktree must include:

```yaml
path: "<absolute or repo-relative path>"
branch: "<branch-name|detached|unknown>"
status: "<summary status>"
dirty state: "clean|dirty|untracked|dirty+untracked|unknown"
recommendation: "keep|release|remove|needs-human-decision|prune-candidate"
reason: "<why this recommendation fits the observed state>"
next safe action: "<concrete next step>"
```

Notes:
- `status` is a concise summary of the current condition; it should not replace the `reason`
- `dirty state` must stay explicit even when the recommendation is already `needs-human-decision`
- `prune-candidate` is reserved for missing-path-but-still-registered worktrees

## Recommendation matrix detail

| Condition | Recommendation | Required reasoning |
| --- | --- | --- |
| clean + branch still active + task ongoing | `keep` | active workspace still in use |
| clean + task done + merged or explicitly abandoned | `release` | safe to leave active working set, not yet delete |
| clean + already released or no longer needed + destructive approval handled separately | `remove` | destructive cleanup may be appropriate only on the explicit remove path |
| dirty tracked changes | `needs-human-decision` | tracked edits may still matter |
| untracked files | `needs-human-decision` | local state may still matter |
| unpushed commits | `needs-human-decision` | unpublished commits may be lost |
| detached HEAD or branch not found | `needs-human-decision` | lineage is ambiguous |
| unmanaged path | `needs-human-decision` | ownership cannot be assumed |
| missing path but still registered | `prune-candidate` | registration appears stale |
| locked worktree | `needs-human-decision` | another process or policy may own the state |

## Release evidence schema

Use this exact field set before recommending `release worktree`:

```yaml
release_evidence:
  task_status: completed | paused | abandoned | unknown
  worktree_clean: true | false | unknown
  untracked_files: true | false | unknown
  branch_status: merged | unmerged | no_branch | unknown
  pr_status: merged | closed | open | none | unknown
  push_status: pushed | unpushed | no_remote | unknown
  user_intent: release | remove | keep | unknown
  destructive_action_allowed: true | false
  evidence_notes:
    - "<short note>"
```

Minimum release gate:
- `worktree_clean: true`
- `untracked_files: false`
- `branch_status: merged` or `pr_status: merged`, unless the human explicitly says the task is abandoned or does not need merge
- `destructive_action_allowed: false` by default

## Safety routing notes

- Outside a valid Git repository: `BLOCKED`
- Branch collision during create: stop for explicit reuse-or-rename decision
- Dirty, untracked, unpushed, detached, locked, or unknown state: `needs-human-decision`
- Shared planning or governance files across worktrees: surface a planner / observer coordination warning
- Stale registration during `get-worktree`: `prune-candidate`, never auto-prune as part of inspection
- Unmanaged worktrees: inspect-only by default; destructive paths require explicit human authorization plus the full remove gate
