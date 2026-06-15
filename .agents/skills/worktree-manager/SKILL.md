---
name: worktree-manager
description: Manage Git worktree lifecycle operations with safe create, get-worktree, release, and remove routing.
complexity: high
risk_profile:
  - ambiguity_sensitive
  - destructive_action
  - external_tooling
inputs:
  - "requested operation: create, get-worktree, release worktree, or remove worktree"
  - "current repository context and target worktree selector when applicable"
  - "target branch or worktree name for create"
  - "explicit human approval for destructive removal or branch-collision resolution when required"
outputs:
  - create_result
  - get_worktree_result
  - release_evidence
  - routing_result
use_when:
  - an agent-driven workflow needs safe worktree lifecycle management for this repository
  - the operator needs worktree inspection, release, or removal guidance without collapsing lifecycle meanings
  - the agent must keep managed and unmanaged worktrees separate by path policy
do_not_use_when:
  - the task is implementation work inside an already selected worktree
  - the request is merge, push, branch deletion, release-tag, or environment setup work
  - the user expects `release worktree` to imply deletion
  - the user wants repository-internal worktree placement under the repo root
---

# Purpose
Manage Git worktree lifecycle operations safely without silently destroying state.

# Trigger / When to use
Use this skill when:
- the user asks to `create`, `get-worktree`, `release worktree`, or `remove worktree`
- the agent must create a managed task worktree at the canonical external path
- the operator needs a structured inspect result before deciding whether to keep, release, remove, or manually review a worktree

Do not use this skill when:
- the task is implementation work inside an already selected worktree
- the request is merge, push, branch deletion, release-tag, or environment setup work
- the user expects `release worktree` to imply deletion
- the user wants repository-internal worktree placement under the repo root

# Inputs
- requested operation: `create`, `get-worktree`, `release worktree`, or `remove worktree`
- repository root context for the target repo
- worktree selector when inspecting, releasing, or removing
- branch name or worktree name for create
- optional managed-path prefix override from the human; otherwise use `agent`
- explicit human destructive approval before any remove path
- explicit human choice when branch-name collision requires reuse or rename

# Process
1. Confirm the current directory belongs to the intended Git repository.
   - If repo-root validation fails, return `BLOCKED`, tell the operator to switch to the correct repository, and make no worktree mutation.
2. Resolve the requested lifecycle operation exactly as one of `create`, `get-worktree`, `release worktree`, or `remove worktree`.
   - If the intent is ambiguous (for example, "clean up this worktree"), stop and ask whether the user means `release worktree` or `remove worktree`.
3. Resolve the target worktree or branch selector.
   - Determine managed status from path policy first.
   - Surface a planner / observer coordination warning whenever shared planning, governance, or other cross-worktree files may be touched.
4. For `create`:
   - Build the managed path as `../<repo-name>.worktrees/<prefix>-YYYYMMDD-<worktree-name>`.
   - Keep the managed worktree outside the repository root.
   - If the target path already exists and is not the intended worktree, stop for human review instead of improvising.
   - If the preferred branch name already exists, stop for an explicit reuse-or-rename decision; do not silently reuse the lineage.
   - Create the branch and worktree only after the path and branch decisions are unambiguous.
   - Return at least this contract:
     ```yaml
     create_result:
       path: "../<repo-name>.worktrees/<prefix>-YYYYMMDD-<worktree-name>"
       branch: "<branch-name>"
       next_step: "cd <path> && continue work inside this worktree"
     ```
5. For `get-worktree`:
   - Inspect the requested worktree or the relevant known worktrees.
   - For every reported worktree, return `path`, `branch`, `status`, `dirty state`, `recommendation`, `reason`, and `next safe action`.
   - Route dirty, untracked, unpushed, detached, locked, unmanaged, or otherwise ambiguous states to `needs-human-decision`.
   - Route a missing path that Git still records as a worktree to `prune-candidate` with a reason and a safe follow-up action.
   - Do not auto-prune stale registrations.
6. For `release worktree`:
   - Treat release as non-destructive offboarding from the active working set.
   - Fill the fixed `release_evidence` schema before deciding whether release is safe.
   - Keep `destructive_action_allowed: false` by default.
   - Require a clean worktree, no untracked files, and merged or explicitly abandoned lineage before recommending release.
   - Never use release as a synonym for remove.
7. For `remove worktree`:
   - Require explicit human destructive approval.
   - Re-check safety signals before removal: clean state, no untracked files, no unresolved branch ambiguity, and no lock or unknown state.
   - Do not remove by default when state is dirty, untracked, unpushed, detached, locked, unmanaged without explicit authorization, or otherwise unclear.
   - If safety signals fail, return `needs-human-decision` instead of forcing deletion.
8. For unmanaged worktrees:
   - Allow inspect and status reporting.
   - Do not automatically release, remove, delete, prune, rename a branch, or assume the task is done.
   - If the human explicitly authorizes a destructive path, restate that the worktree is unmanaged and require the full remove safety gate before proceeding.

# Examples
- Positive: Create a managed task worktree, return the managed path, attached branch, and the immediate next step to continue work inside that worktree.
- Negative: Treat "release worktree" as permission to delete the directory, silently reuse an existing branch, or clean up an unmanaged worktree without an explicit destructive gate.

# Outputs
- `create_result`: managed `path`, attached `branch`, and immediate `next_step`
- `get_worktree_result`: entries with `path`, `branch`, `status`, `dirty state`, `recommendation`, `reason`, and `next safe action`
- `release_evidence`: recorded evidence plus the release recommendation that keeps destructive action separate
- `routing_result`: `BLOCKED`, `needs-human-decision`, or `prune-candidate` routing when safety rules require escalation
- a shared-file coordination warning when multiple worktrees may touch the same planning or governance files

# Validation

## Required Checks
- repo-root validation passes before any create, get-worktree, release, or remove action
- `create` uses the canonical managed path family and keeps the worktree outside the repository root
- `create_result` includes `path`, `branch`, and `next_step`
- `get-worktree` output includes `path`, `branch`, `status`, `dirty state`, `recommendation`, `reason`, and `next safe action` for every reported worktree
- `release worktree` records the full `release_evidence` schema and keeps `destructive_action_allowed: false` unless a separate remove path is explicitly authorized
- `release worktree` and `remove worktree` remain distinct operations
- risky states route to `needs-human-decision` instead of destructive automation
- missing-path-but-registered worktrees route to `prune-candidate` and are not auto-pruned
- unmanaged worktrees stay inspect-only by default
- branch collisions stop for an explicit reuse-or-rename decision

## Quality Checks (best effort)
- selector resolution is explicit enough that another agent could inspect the same target without guessing
- `reason` explains why the recommendation was chosen instead of only naming the status
- `next safe action` is concrete and non-destructive when the state is ambiguous
- the shared-file coordination warning names the planner / observer responsibility when shared files are present or likely

## On Soft Fail
- mark the result as `INCOMPLETE`
- continue with the safest best-effort inspection or guidance that does not mutate state
- list the missing information, blocked checks, or execution limits explicitly

# Failure Handling

## Missing Context
- mark the result as `INCOMPLETE`
- state which selector, branch name, release evidence field, or destructive approval is missing
- do not guess missing branch lineage or destructive intent

## Ambiguous Requirement
- if the ambiguity changes whether the path is `create`, `release worktree`, or `remove worktree`, return `BLOCKED` and ask for clarification
- if the ambiguity is non-destructive, proceed with inspection-only guidance and list the assumption explicitly

## Execution Limitation
- state the limitation explicitly in the result
- do not fabricate Git state, branch status, or release evidence
- prefer `get-worktree` style inspection guidance over risky mutation when commands or selectors cannot be verified

# Verification
- After `create`, verify the worktree path exists, the branch is attached as intended, and the returned `next_step` points into that worktree.
- After `get-worktree`, verify each reported worktree includes the full fixed field set.
- Before `release worktree` or `remove worktree`, verify that the evidence and safety gates still match the latest observed state.

# Red Flags
- the user says "clean up" without specifying `release worktree` or `remove worktree`
- the preferred branch name already exists
- the worktree path sits outside the canonical managed family but the request assumes the skill owns it
- Git still records a worktree whose path is missing
- multiple active worktrees may edit the same planning or governance files

# Common Rationalizations
- "Release and remove are basically the same."
- "The branch already exists, so just reuse it."
- "This unmanaged path looks close enough to the managed convention."
- "A stale registration can be auto-pruned without asking."

# Boundaries
- Do not perform feature implementation, merge, push, branch deletion, PR management, or release-tag handling.
- Do not place managed worktrees inside the repository root.
- Do not silently convert `release worktree` into `remove worktree`.
- Do not auto-prune stale registrations during `get-worktree`.
- Do not assume unmanaged worktrees are safe to modify or delete.
- Do not bypass the reuse-or-rename gate when a branch name collides.

# Local references
- `reference.md`: stable terminology, selector rules, managed-path policy, recommendation matrix detail, and release evidence schema
- `examples.md`: detailed positive, negative, and edge-case scenarios for create, get-worktree, release, and remove
- `checklist.md`: repeatable pre-create, pre-release, pre-remove, unmanaged-worktree, and non-repo safety checks
