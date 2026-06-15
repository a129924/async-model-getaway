# Artifact Path Rule

Rules for declaring and maintaining the `Artifact Paths` section in a topic plan.

- Treat `Artifact Paths` as an executable contract, not a summary.
- Name concrete paths such as `skills/<skill-name>/SKILL.md`, not vague phrases such as `docs`, `skill files`, or `merged implementation`.
- Every artifact path must be role-labeled: state who owns the path and what role it plays in the topic.
- If a topic uses correction artifacts, list each parent artifact and each correction artifact separately with exact paths; do not collapse them into `correction files` or other catch-all wording.
- If reviewer feedback controls routing or multi-round rework, list the exact repo-visible `review-log` or equivalent handoff artifact too.
- Parent artifacts remain current truth after accepted backfill; correction artifacts remain historical truth. The artifact list should make that relationship obvious.
- If later work appears outside the listed paths, that is a plan-alignment problem, not a harmless detail.
- Do not use broad directory references when individual file paths can be named.
