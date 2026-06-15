---
name: git-branch-naming
description: Name or repair development branches with semantic prefixes, `<type>/<username>/<short-description>` structure, and migration guidance when work has already started on the wrong branch.
complexity: medium
risk_profile:
  - ambiguity_sensitive   # task type, namespace token, or current branch state changes the recommendation meaningfully
inputs:
  - the task's business intent
  - the chosen development type such as `feat`, `fix`, `refactor`, `docs`, or `chore`
  - the username or approved namespace token
  - the current branch, including whether work or commits already exist there
  - any existing branch names that might conflict
  - the expected commit scope or dominant module
outputs:
  - one recommended branch name or a small set of tightly related alternatives
  - repair commands such as `git checkout -b ...` or `git branch -m ...`
  - split advice when one task name tries to cover multiple semantic boundaries
use_when:
  - the user asks for a branch name
  - the agent detects `git checkout -b` or `git switch -c` intent
  - a task has just been confirmed and the agent should suggest a branch before work starts
  - the current branch is clearly misnamed and the user needs a safe migration path
do_not_use_when:
  - the main task is drafting commit messages or deciding release/tagging policy
  - the branch is a release or hotfix branch whose lifecycle should be governed by `git-release-management`
  - the user only wants generic Git tutorials unrelated to branch naming
---

# Purpose
Choose or repair development branch names so the branch tells the same semantic story as the work.

# Trigger / When to use
Use this skill when:
- the user asks for a branch name
- the agent detects `git checkout -b` or `git switch -c` intent
- a task has just been confirmed and the agent should suggest a branch before work starts
- the current branch is clearly misnamed and the user needs a safe migration path

Do not use this skill when:
- the main task is drafting commit messages or deciding release/tagging policy
- the branch is a release or hotfix branch whose lifecycle should be governed by `git-release-management`
- the user only wants generic Git tutorials unrelated to branch naming

# Inputs
- the task's business intent
- the chosen development type such as `feat`, `fix`, `refactor`, `docs`, or `chore`
- the username or approved namespace token
- the current branch, including whether work or commits already exist there
- any existing branch names that might conflict
- the expected commit scope or dominant module

# Process
1. Decide whether the branch is a normal development branch or a release/hotfix case. Hand release/hotfix timing decisions to `git-release-management`.
2. Choose a semantic branch type that aligns with the same type system used by `git-commit-convention`.
3. Build the preferred development branch as `<type>/<username>/<short-description>`.
4. Keep `short-description` short, semantic, and lowercase; prefer about 2-4 words in kebab-case that match the dominant scope or business goal.
5. If the repo does not use personal usernames in branch names, stop and ask for the approved namespace token instead of inventing one.
6. If the current branch is wrong but the work has already started, provide an escape path: rename in place, create a new branch from the current state, or otherwise move the work with the least semantic damage.
7. If the description is too broad or crosses multiple semantic areas, recommend splitting into smaller branches or replacing the description with a more abstract but still truthful label.
8. If the preferred branch name already exists, check whether it is really the same task. If not, suggest a more precise suffix or a clear alternate description.
9. Output the recommended branch name plus the repair or creation command, but do not rename branches automatically.

# Examples
- **Positive**: Suggest `feat/andrew/auth-session-timeout` for a new authentication rule, or repair work on `main` with `git checkout -b feat/andrew/auth-session-timeout`.
- **Negative**: Approve `misc/update-stuff`, keep coding on `main` without a migration path, or let a `fix/...` branch carry a clearly feature-sized workflow change.

# Outputs
- one recommended branch name or a small set of tightly related alternatives
- repair commands such as `git checkout -b ...` or `git branch -m ...`
- split advice when one task name tries to cover multiple semantic boundaries

# Validation
1. **Scope gate** — confirm the request is about naming or repairing a development branch. Release or hotfix lifecycle decisions are BLOCKED and should be handed to `git-release-management`.
2. **Naming inputs check** — confirm branch type, namespace token, and a truthful short description are known. If the repository does not use personal usernames, require the approved replacement token instead of guessing.
3. **Current-state check** — determine whether the user needs a fresh branch, an in-place rename, or a branch move from the wrong starting point. Existing work on the current branch changes the recommended command path.
4. **Conflict check** — if the preferred branch name already exists, verify whether it represents the same task lineage before recommending reuse.

PASS: enough context exists to recommend a truthful branch name and the safest non-automated create / rename / rescue command.  
SOFT FAIL: task type, namespace token, current branch state, or dominant scope is incomplete or ambiguous; continue with a best-effort recommendation, label the assumptions explicitly, and ask the user to confirm the missing signal.  
BLOCKED: the request is actually about release or hotfix branch policy, or the branch lineage/state is too unclear to choose between reuse, rename, or split guidance without misleading the user.

# Failure Handling
- **Missing Context**: if the type, namespace token, or current branch state is unknown, ask for the missing signal first; if a provisional answer is still useful, label it as assumption-based.
- **Ambiguous Requirement**: if the request could describe multiple task scopes or both a rename and split path, surface the competing interpretations and state which signal decides the recommendation.
- **Execution Limitation**: do not inspect or mutate Git state automatically; when real branch state cannot be verified, provide safe manual commands and say that local verification is still required.

# Boundaries
- Do not draft commit bodies, PR gates, release tags, or version policy.
- Do not manage release/hotfix approval timing; hand that to `git-release-management`.
- Do not silently accept a vague or misleading branch name when a clearer semantic name is available.
- Do not auto-run branch creation or rename commands.

# Local references
- `examples.md`: branch naming scenarios, migration commands, conflict handling, and anti-patterns
- `references/naming-patterns.md`: preferred branch structure, type alignment, and short-description rules
- `references/migration-playbooks.md`: wrong-branch rescue paths and rename versus recreate guidance
- `references/conflict-and-fallbacks.md`: name-conflict handling, namespace fallback, and broad-task compression rules
