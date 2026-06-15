# worktree-manager checklist

Use this checklist for repeatable safety checks. It is operational, not a policy
summary.

## Pre-create checks

- [ ] Current directory resolves to the intended Git repository root or a child of it.
- [ ] Requested operation is clearly `create`, not `get-worktree`, `release worktree`, or `remove worktree`.
- [ ] Managed path follows `../<repo-name>.worktrees/<prefix>-YYYYMMDD-<worktree-name>`.
- [ ] Managed path stays outside the repository root.
- [ ] Preferred branch name is known.
- [ ] If the preferred branch name already exists, the human has made an explicit reuse-or-rename decision.
- [ ] Target path does not already exist as an unrelated directory or conflicting worktree.
- [ ] Shared planning or governance files that may be edited across worktrees are called out with a coordination warning.
- [ ] Planned output includes `path`, `branch`, and `next_step`.

## Pre-release checks

- [ ] Requested operation is clearly `release worktree`.
- [ ] Target worktree selector resolves to the intended worktree.
- [ ] Worktree is managed, or the operator has been told that unmanaged worktrees are inspect-only by default.
- [ ] `release_evidence.task_status` is filled.
- [ ] `release_evidence.worktree_clean` is filled and currently `true`.
- [ ] `release_evidence.untracked_files` is filled and currently `false`.
- [ ] `release_evidence.branch_status`, `pr_status`, and `push_status` are filled or explicitly marked `unknown`.
- [ ] Lineage is merged, or the human explicitly states the task is abandoned / does not need merge.
- [ ] `release_evidence.user_intent` is `release`.
- [ ] `release_evidence.destructive_action_allowed` remains `false`.
- [ ] Output explains that release does not imply deletion.

## Pre-remove checks

- [ ] Requested operation is clearly `remove worktree`.
- [ ] Explicit human destructive approval is present in the current request or restated confirmation.
- [ ] Target worktree selector resolves to exactly one worktree.
- [ ] Latest state check shows no tracked changes.
- [ ] Latest state check shows no untracked files.
- [ ] Latest state check shows no unpushed commits, detached HEAD, unknown branch state, or lock that would require human review.
- [ ] The request does not rely on a previous `release worktree` as implied delete permission.
- [ ] If the worktree is unmanaged, the response restates that ownership is not assumed and uses the same destructive gate.

## Unmanaged-worktree checks

- [ ] Path classification is based on canonical managed-path family first.
- [ ] Unmanaged worktrees are limited to inspection and status reporting by default.
- [ ] No automatic release, remove, delete, prune, rename, or branch deletion is implied for unmanaged paths.
- [ ] Recommendation and next safe action tell the operator what human decision is still required.

## Non-repo and ambiguous-state checks

- [ ] If repo-root validation fails, the result is `BLOCKED` and no mutation occurs.
- [ ] If the user says "clean up" or similar ambiguous wording, the response asks whether they mean `release worktree` or `remove worktree`.
- [ ] Dirty, untracked, unpushed, detached, locked, or unknown states route to `needs-human-decision`.
- [ ] Missing-path-but-registered worktrees route to `prune-candidate` and are not auto-pruned.
- [ ] Every `get-worktree` entry includes `path`, `branch`, `status`, `dirty state`, `recommendation`, `reason`, and `next safe action`.
