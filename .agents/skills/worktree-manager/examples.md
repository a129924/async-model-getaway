# worktree-manager examples

Use this file for concrete lifecycle scenarios. It expands the concise `SKILL.md`
examples without redefining the core contract.

## Scenario 1: create a managed worktree

User intent:
- "Create a worktree for the `worktree-skill` topic from the current repo."

Correct handling:
- validate that the current directory belongs to the target Git repository
- construct a managed path such as `../agent-skills.worktrees/agent-20260507-worktree-skill`
- create or attach the intended branch only after confirming there is no branch collision
- return the path, branch, and immediate next step

Example output:

```yaml
create_result:
  path: "../agent-skills.worktrees/agent-20260507-worktree-skill"
  branch: "feat/andrew/worktree-skill"
  next_step: "cd ../agent-skills.worktrees/agent-20260507-worktree-skill && continue work inside this worktree"
notes:
  - "Coordinate planner / observer owned files if multiple worktrees may touch them."
```

## Scenario 2: branch collision during create

User intent:
- "Create a worktree for `feat/andrew/worktree-skill`."

Observed condition:
- the preferred branch already exists

Correct handling:
- stop before creating the worktree
- ask whether to reuse the existing branch lineage or choose a new branch name
- do not silently attach a new worktree to the existing branch

Incorrect handling:
- automatically create the worktree on the existing branch without an explicit reuse decision

## Scenario 3: clean managed worktree ready for release

User intent:
- "Release this completed worktree."

Observed condition:
- managed path
- clean working tree
- no untracked files
- merged PR or explicit statement that the task is abandoned and does not need merge

Correct handling:
- produce `release_evidence`
- keep `destructive_action_allowed: false`
- recommend `release`
- explain that release removes the worktree from the active working set but does not imply deletion

Example output:

```yaml
release_evidence:
  task_status: completed
  worktree_clean: true
  untracked_files: false
  branch_status: merged
  pr_status: merged
  push_status: pushed
  user_intent: release
  destructive_action_allowed: false
  evidence_notes:
    - "Task merged; safe to offboard from active working set."
recommendation: release
reason: "Managed worktree is clean and the lineage is complete."
next safe action: "Mark the worktree as released; use remove worktree later only if explicit destructive cleanup is requested."
```

## Scenario 4: dirty or untracked worktree

User intent:
- "Release this worktree."

Observed condition:
- modified tracked files or untracked files are present

Correct handling:
- return `needs-human-decision`
- explain that the current state could still matter
- recommend reviewing, committing, shelving, or explicitly abandoning the remaining state before any release or remove decision

Incorrect handling:
- release or remove automatically because the task sounds finished

## Scenario 5: unmanaged worktree

User intent:
- "Clean up `/some/other/path/my-worktree`."

Observed condition:
- the path does not match `../<repo-name>.worktrees/<prefix>-YYYYMMDD-<worktree-name>`

Correct handling:
- classify it as unmanaged
- allow inspection only by default
- report status, recommendation, reason, and next safe action
- if the human later asks for destructive cleanup, restate that the worktree is unmanaged and require the full remove gate

Example output:

```yaml
path: "/some/other/path/my-worktree"
branch: "unknown"
status: "unmanaged"
dirty state: "unknown"
recommendation: "needs-human-decision"
reason: "Path is outside the managed worktree family, so ownership cannot be assumed."
next safe action: "Inspect the worktree manually and obtain explicit destructive approval before any remove path."
```

## Scenario 6: stale registration during get-worktree

User intent:
- "Get worktree status."

Observed condition:
- `git worktree list` still reports a worktree, but the path no longer exists

Correct handling:
- report the worktree as a stale registration
- set the recommendation to `prune-candidate`
- explain that the registration appears stale
- do not auto-prune during `get-worktree`

## Scenario 7: explicit destructive remove confirmation

User intent:
- "Remove this worktree. Destructive cleanup is approved."

Observed condition:
- selector resolves clearly
- clean state
- no untracked files
- no lock or detached / unknown branch state

Correct handling:
- restate that `remove worktree` is destructive
- confirm the explicit human approval is present
- proceed only if the latest safety checks still pass

Incorrect handling:
- treat an earlier release request as implied permission to delete now

## Scenario 8: request outside the repository

User intent:
- "Create a worktree here."

Observed condition:
- current directory is not the intended Git repository

Correct handling:
- return `BLOCKED`
- tell the operator to switch to the correct repository first
- make no worktree mutation
