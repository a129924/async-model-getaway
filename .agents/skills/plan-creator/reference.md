# Plan Creator Reference

Overview of the stable rules that keep topic-plan authoring aligned with the repository workflow. Detailed rules for each topic are split into the `references/` files listed below.

- **Shared topic-plan contract**: `plan/topic-plan-contract.md` is the repo-level authority for required sections, fallback behavior, and contract-level blocking semantics. Local references in this skill must not redefine that authority.
- **Required section meaning**: what each mandatory topic-plan section means and what it must contain. See `references/required-section-meaning.md`.
- **Stable-library rule**: when and how to declare stable-library intent, `## Stable library metadata`, release timing, and VERSION/README decisions. See `references/stable-library-rule.md`.
- **Artifact path rule**: how to declare exact, role-labeled, executable artifact paths instead of vague descriptions. See `references/artifact-path-rule.md`.
- **Correction lifecycle rule**: when a topic uses correction / delta artifacts, keep the workflow body limited to lifecycle / routing contract, list parent and correction artifacts exactly, keep parent-sync closure explicit, and make `review-log` or equivalent handoff conditional on routing-controlling feedback rather than universal.
- **Minimum correction artifact contract**: put field-level requirements in reference / examples, not the workflow body. A repo-visible `*.correction-plan.md` should define at least the trigger / evidence, scope, what stays current, what changes, acceptance delta, affected artifacts, parent-sync note, and retention / closure intent. Add `*.correction-step.md` only when the repair or backfill is multi-step; it should name the ordered repair, backfill, review, and closure checkpoints.
- **Future extraction boundary**: correction-lifecycle refresh topics should update existing workflow / plan surfaces now, not create a standalone correction skill in the same topic. Defer standalone extraction to a later topic only if repeated authoring / review instability or cross-workflow reuse justifies it.
- **Role boundary rule**: how to keep planning actor, creator, reviewer, and Main Agent responsibilities distinct, including creator-owned `Implementation Steps`. See `references/role-boundary-rule.md`.
- **Examples**: use `examples.md` for field-level correction artifact samples, bounded-path examples, workflow-body versus reference-body separation, and future-extraction boundary examples. Do not embed long correction schemas directly in the workflow body.
- **Stop-and-ask triggers**: conditions that require stopping and asking before drafting or continuing. See `references/stop-and-ask-triggers.md`.
- **Template usage rule**: how to use and complete `templates/topic-plan-template.md` without leaving scaffolding in the final plan. See `references/template-usage-rule.md`.
