# Plan Creator Checklist

Use this checklist when drafting or sanity-checking a topic plan before handing it to a reviewer or the Main Agent for execution.

- [ ] The topic plan is repo-visible at `plan/<topic>/<topic>.plan.md`.
- [ ] `Goal / Outcome`, `Scope`, `Locked Decisions`, and `Boundaries / Exclusions` are explicit.
- [ ] `Status / Allowed Transitions` uses canonical workflow transitions only.
- [ ] The current status matches the actual workflow phase.
- [ ] `Artifact Paths` are exact, repo-visible, and role-labeled, not catch-all labels.
- [ ] If correction artifacts are used, each parent artifact, correction artifact, and any review-log / equivalent handoff artifact is listed with an exact path, owner, and role.
- [ ] If correction artifacts are used, the minimum correction artifact contract is defined in reference / examples: `correction-plan` covers trigger, scope, what stays / changes, acceptance delta, affected artifacts, parent sync, and retention intent; `correction-step` appears only when multi-step repair / backfill is needed.
- [ ] `Implementation Steps` stay creator-owned; reviewer verdict logging, reviewer acceptance work, and main-agent routing work are not written into creator steps.
- [ ] When correction lifecycle text appears in the plan, the workflow body stays slim and does not become a field-by-field correction artifact schema dump.
- [ ] Parent-sync closure is explicit when correction artifacts are used: parent artifacts return to current truth only after backfill.
- [ ] `review-log` or equivalent handoff is required only when reviewer feedback controls routing or multi-round rework.
- [ ] Any round cap is declared as topic policy, not as a repository-wide default.
- [ ] Correction-lifecycle refresh topics explicitly defer any standalone correction skill to a later topic unless repeated instability or cross-workflow reuse justifies extraction.
- [ ] Stable-library intent is explicit:
  - [ ] clearly absent for non-stable topics, or
  - [ ] declared with timing when stable-library surfaces are involved
- [ ] `Reviewer Handoff` is a single JSON object contract.
- [ ] `Post-merge / release actions` match the actual topic scope and timing.
- [ ] Planning actor, creator, reviewer, and Main Agent roles are not mixed.
- [ ] No placeholder wording remains where workflow needs a real contract.
