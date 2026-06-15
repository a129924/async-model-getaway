# Plan Reviewer Examples

Use these examples after `SKILL.md` has already narrowed the task to reviewing a repo-visible topic plan for this repository.

## Approved / non-stable topic

A plan that:
- lives at `plan/cache-key-auditor/cache-key-auditor.plan.md`
- includes all required sections
- uses canonical transitions
- lists exact artifact paths
- explicitly says stable-library metadata is absent
- keeps `Reviewer Handoff` as one JSON object

Typical verdict:

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Approved / correction-lifecycle topic

A plan that:
- lists exact parent and correction-related artifact paths with owner/role labels
- keeps workflow-body correction text limited to lifecycle / routing contract
- defines the minimum correction artifact contract in reference / example surfaces instead of the workflow body
- makes parent-sync closure explicit
- keeps `review-log` conditional on routing-controlling feedback
- leaves reviewer-owned work out of creator `Implementation Steps`
- refreshes existing workflow / plan surfaces now and defers any standalone correction skill to a later topic unless repeated instability or cross-workflow reuse justifies extraction

Typical verdict:

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Approved + ADDRESS / stable topic

A stable-library publish plan that:
- includes `## Stable library metadata`
- declares README row, VERSION bump, and timing
- keeps artifact paths exact
- is broadly correct
- but needs one direct contract fix, such as clarifying a README row position or adding a missing role label in `Artifact Paths`

Typical verdict:

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [
      {
        "comment": "Clarify the README row position in Stable library metadata.",
        "location": "plan/topic/topic.plan.md:140-150",
        "why": "The publish contract is usable, but the row placement should be explicit."
      }
    ],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Needs-rework / workflow-breaking

A plan that:
- skips canonical transitions
- routes `planned` directly to `review-ready`
- declares release before PR or merge
- or writes `Reviewer Handoff` as Markdown prose or a table

Typical verdict:

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Status transitions are non-canonical and skip required workflow phases.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Replace the status model with the canonical creator -> reviewer -> publish -> merge transitions."
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Needs-rework / correction-contract-breaking

A plan that:
- uses `merged implementation` or another vague evidence label instead of exact repo-visible paths
- puts reviewer verdict logging into creator `Implementation Steps`
- requires `review-log` for every review even when routing is unaffected
- turns a sample three-round cap into a repository-wide rule
- bloats the workflow body with field-by-field correction artifact schema
- or quietly broadens the topic into creating a standalone correction skill now

Typical verdict:

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Artifact Paths are too vague to support correction-lifecycle review.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Replace vague evidence labels with exact repo-visible parent/correction paths and explicit role labels."
    },
    {
      "issue": "Creator Implementation Steps contain reviewer-owned review-log work.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Keep reviewer logging in reviewer handoff or routing surfaces and leave creator steps creator-owned."
    },
    {
      "issue": "The plan universalizes review-log or round-cap policy instead of keeping it conditional or topic-specific.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Require review-log only when feedback controls routing or multi-round rework, and declare any round cap as topic policy only."
    },
    {
      "issue": "The plan creates a standalone correction skill even though this topic only refreshes existing workflow / plan surfaces.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Keep standalone correction skill extraction out of this topic and defer it to a later, separately scoped topic only if repeated instability or cross-workflow reuse justifies it."
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Needs-rework / scope-or-boundary-breaking

A plan that:
- lists artifact paths as `skill folder`, `docs`, or `maybe version files`
- mixes creator, reviewer, and Main Agent duties
- implies stable-library timing without explicit metadata
- leaves `TBD` where the workflow needs a real contract

Typical verdict:

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Artifact Paths are too vague to function as an executable contract.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Replace broad labels with exact repo-visible paths and explicit role labels."
    },
    {
      "issue": "Stable-library intent is implied but not explicitly declared.",
      "file": "plan/topic/topic.plan.md",
      "fix": "Either add Stable library metadata with timing and rationale, or explicitly state the topic is non-stable."
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Anti-pattern summary

- authoring the plan instead of reviewing it
- approving a plan with vague artifact paths because "the scope sounds right"
- treating a prose note as an acceptable reviewer handoff
- downgrading real contract failures into optional suggestions
- accepting workflow-body correction-schema bloat because the examples "might be useful later"
