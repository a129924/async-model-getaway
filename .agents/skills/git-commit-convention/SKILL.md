---
name: git-commit-convention
description: Draft or review semantic commit messages from staged changes, including split signals, business-facing subjects, breaking-change markers, and repair commands such as `git add -p`, `git reset`, and `git commit --amend`.
complexity: medium
risk_profile:
  - ambiguity_sensitive   # partial staging or unclear intent changes the commit draft meaningfully
inputs:
  - staged files, staged hunks, and git status
  - business intent behind the change from recent conversation
  - repository's allowed commit types and scope mapping
  - related issue or PR identifiers if available
  - whether type-check, test, or pre-commit signals are already failing
  - whether the latest commit is a better candidate for --amend than a new commit
outputs:
  - one or more review-ready semantic commit drafts
  - split or composite-scope guidance when staged set crosses semantic boundaries
  - repair commands such as git add -p, git reset, or git commit --amend
  - warnings when testing, typing, or other quality gates are already failing
use_when:
  - user asks for a commit message or wants help before git commit
  - staged changes are ready and a compliant draft is needed
  - agent detects git commit intent and should intercept with a structured draft
  - a recent commit likely needs --amend due to typo, missed file, or footer fix
do_not_use_when:
  - main task is branch naming or release/tagging policy
  - no staged changes and user is not asking for general commit policy
  - main question is repository-wide CI, testing, or reviewer policy
---

# Purpose
Draft or review semantic commit messages that match the staged change set instead of merely restating code motion.

# Trigger / When to use
Use this skill when:
- the user asks for a commit message or wants help before `git commit`
- staged changes are ready and the agent should suggest one commit or several split commits
- the agent detects `git commit` intent and should intercept with a compliant draft
- a recent commit likely needs `--amend` because of a typo, missed file, or footer fix

Do not use this skill when:
- the main task is naming a branch or deciding release/tagging policy
- there are no staged changes and the user is not asking for general commit policy
- the main question is repository-wide CI, testing, or reviewer policy instead of the commit itself

# Inputs
- the staged files, staged hunks, and `git status`
- any recent conversation that explains the business intent behind the change
- the repository's allowed commit types and any scope mapping
- whether related issue or PR identifiers exist
- whether type-check, test, or pre-commit signals are already failing
- whether the latest commit is a better fit for `--amend` than a new commit

# Process
1. Start from staged content, not the whole working tree. If nothing is staged, stop and say so instead of inventing a commit.
2. If the staging is partial and the semantic intent is unclear, ask whether the commit message should describe only the staged subset.
3. Separate noise from business intent. If lockfiles, formatter rewrites, snapshots, or generated files are mixed into a business change, strongly recommend splitting them into a dedicated `chore:` or `style:` commit.
4. Detect multiple semantic boundaries. If one staged set mixes unrelated intentions, recommend split commits and provide repair commands such as `git reset`, `git add -p`, or `git restore --staged`.
5. Choose the commit `type` from business intent first: e.g. `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`, `perf`, `ci`, `build`, or `revert`.
6. Choose `scope` from the project's mapping when it exists. If the staged change truly spans multiple module boundaries in one intentional commit, allow a composite scope such as `feat(ui,api): ...`; otherwise prefer splitting.
7. Write the subject in business language. Name the user-visible or domain effect, not only the code action; e.g. `fix(錯誤處理): 修正語意派例外鏈結遺失` is better than `fix: add CustomException`.
8. Require a commit body when the subject alone cannot explain why, when the change is a refactor or multi-step fix, or when edge-case handling or migration detail matters.
9. Add a footer such as `Closes #123` or `Relates-to: #456` when an issue or PR identifier exists.
10. If the change is breaking, require `!` in the header and explain migration impact in the body.
11. Surface nearby quality failures early. If strict type-hint or test checks are already failing, include a warning in the commit recommendation instead of pretending the commit is release-safe.
12. Output the proposed message text, a short rationale, and a runnable `git commit` command, but never execute the commit without human confirmation.
13. If the latest commit only needs a narrow correction, prefer an `--amend` recommendation over creating an unnecessary follow-up commit.

# Examples
- **Positive**: Split formatter noise away from a business fix, then draft `fix(錯誤處理): 修正語意派例外鏈結遺失` with a body and `Relates-to` footer.
- **Negative**: Hide mixed lockfile and feature changes under one `feat: update files`, or describe only code motion such as `refactor: rename class` when the staged change actually fixes user-visible behavior.

# Validation
Main decision path:
1. **Staging check** — confirm `git status` shows staged changes before drafting; if nothing is staged AND the request is not a general commit-policy question, BLOCKED.
2. **Semantic boundary check** — identify whether staged set represents one intent or multiple; mixed-intent staging requires split recommendation before drafting a single commit.
3. **Type assignment** — verify chosen type (`feat`, `fix`, `refactor`, etc.) matches business intent, not code mechanics.
4. **Breaking change check** — if any public interface changes, require `!` marker and body explanation.
5. **Quality gate check** — if type-check or test failures are known, include explicit warning in the draft output.

PASS: staged changes form a coherent intent, type and subject are correctly assigned, any breaking change is marked.
SOFT FAIL: staging is partial or intent is ambiguous — continue with best-effort draft, flag the ambiguity explicitly, and ask the user to confirm scope.
BLOCKED: no staged changes exist AND the request is not a general commit-policy question AND no `--amend` candidate is identified.

# Failure Handling
- **Nothing staged**: stop immediately; state that no staged changes were found and ask the user to stage changes before proceeding.
- **Ambiguous intent**: produce a draft labelled `[DRAFT — scope unclear]` with the clearest interpretation, then list alternative interpretations and ask the user to confirm.
- **Mixed semantic boundaries**: produce split recommendations with repair commands rather than forcing one message; do not silently merge unrelated changes.
- **Repository type list unavailable**: fall back to the conventional-commits standard types; note the fallback in output.
- **Breaking change uncertain**: err toward requiring `!` and a body; explain reasoning so the user can override.

# Outputs
- one or more review-ready semantic commit drafts
- split or composite-scope guidance when the staged set crosses semantic boundaries
- repair commands such as `git add -p`, `git reset`, or `git commit --amend`
- warnings when testing, typing, or other linked quality gates are already failing

# Boundaries
- Do not auto-run `git commit`.
- Do not decide branch naming, PR approval, release tagging, or version synchronization.
- Do not bless a mixed-intent staged set as one commit when the semantic boundaries are clearly separate.
- Do not ignore breaking-change markers, missing issue footers, or body-needed cases just to keep the message short.

# Local references
- `examples.md`: semantic-style commit scenarios, split signals, anti-patterns, and repair-command playbooks
- `references/type-selection.md`: commit-type selection rules and business-language subject guidance
- `references/scope-alignment.md`: scope mapping, branch-to-scope alignment, and composite-scope rules
- `references/split-and-repair.md`: partial-staging checks, noise isolation, and amend/reset/add-p repair paths
