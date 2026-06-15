# Plan creator examples

Use these examples after `SKILL.md` has already narrowed the task to repository topic-plan authoring.

## Normal path

### Non-stable skill topic
```md
# Example topic intent
- create `skills/cache-key-auditor/`
- stop at `review-ready`

## Artifact Paths
| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/cache-key-auditor/cache-key-auditor.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Skill contract | `skills/cache-key-auditor/SKILL.md` | Creator | Main skill instructions under topic scope |
| Skill reference | `skills/cache-key-auditor/reference.md` | Creator | Local supporting guidance for the drafted skill |
| Skill examples | `skills/cache-key-auditor/examples.md` | Creator | Usage examples for the drafted skill |

Artifact path notes:
- This topic does **not** modify `README.md`, `VERSION`, or release notes.
- `Stable library metadata` is intentionally absent because this topic is not a
  stable-library publish topic.
```

- Good because the non-stable intent is explicit and the paths are exact.

### Stable-library publish topic
```md
## Locked Decisions
- This topic updates the stable library entry for `cache-key-auditor`.

## Stable library metadata
- README row: `| cache-key-auditor | validates cache-key rules for repo-visible APIs |`
- VERSION bump: `MINOR`
- Timing: `publish-in-progress`
- Rationale: new approved stable skill enters the public library table
```

- Good because stable-library impact is declared instead of implied.

### Correction-lifecycle contract topic
```md
## Scope
- **In scope**:
  - refresh `plan/agent-handoff-workflow.md`
  - refresh `skills/plan-reviewer/checklist.md`

## Locked Decisions
- The workflow body stays slim and keeps only correction lifecycle / routing rules.
- Detailed correction artifact content belongs in reference / examples, not the workflow body.
- This topic refreshes existing workflow surfaces only; it does **not** create a standalone correction skill now.
- A later standalone correction skill is only a future option if repeated authoring / review instability or cross-workflow reuse justifies extraction in a separate topic.

## Artifact Paths
| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/correction-refresh/correction-refresh.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Repo workflow contract | `plan/agent-handoff-workflow.md` | Creator | Slim lifecycle / routing contract |
| Reviewer checklist | `skills/plan-reviewer/checklist.md` | Creator | Review gate for correction-lifecycle contract topics |

Artifact path notes:
- This topic does **not** modify `README.md`, `VERSION`, or `.github/copilot-instructions.md`.
- No `review-log` artifact is listed because this authoring topic does not use reviewer feedback to control routing or multi-round rework.

## Implementation Steps
1. Refresh the workflow body so it keeps only correction lifecycle / routing rules.
2. Put field-level correction artifact guidance in reference / examples instead of the workflow body.

## Reference expectation
- Minimum `*.correction-plan.md` contract:
  - `Trigger / Evidence`
  - `Scope`
  - `What stays current`
  - `What changes`
  - `Acceptance delta`
  - `Affected artifacts`
  - `Parent sync note`
  - `Retention / closure intent`
- Minimum `*.correction-step.md` contract:
  - use only when the repair or backfill is multi-step
  - ordered repair / backfill steps
  - downstream review checkpoints
  - closure check that parent sync is complete before resolution
```

- Good because the workflow body stays slim, the field-level correction contract has a repo-visible home outside the workflow body, the artifact paths are exact and role-labeled, the conditional `review-log` rule is explicit, and future skill extraction stays deferred.

### Workflow-spec topic
```md
## Scope
- **In scope**:
  - update `plan/agent-handoff-workflow.md`
  - update `.github/guides/MAIN-AGENT-WORKFLOW.md` only if direct contradictions appear

## Artifact Paths
| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/workflow-spec-refresh/workflow-spec-refresh.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Repo workflow contract | `plan/agent-handoff-workflow.md` | Creator | Repo-level workflow wording being refreshed |

Artifact path notes:
- This topic treats `plan/agent-handoff-workflow.md` as the primary workflow contract surface.
- Update `.github/guides/MAIN-AGENT-WORKFLOW.md` only if direct contradictions are discovered.
- If the guide becomes an execution surface, add it explicitly to topic scope and artifact paths.
```

- Good because the topic stays process-focused, keeps the repo workflow contract primary, and treats the guide as conditional follow-up context instead of a default artifact surface.

### Small wording-only topic
```md
## Scope
- **In scope**:
  - clarify one misleading sentence in `skills/foo/SKILL.md`

## Artifact Paths
| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/foo-wording-fix/foo-wording-fix.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Skill contract | `skills/foo/SKILL.md` | Creator | Single wording fix target |
```

- Good because the plan stays small instead of pretending the topic is broader.

## Anti-patterns

### Mixed stable-library intent
```md
## Post-merge / release actions
- maybe update `README.md` and `VERSION` if this feels stable enough later
```

- Bad because stable-library timing is implied but not declared.

### Vague artifact paths
```md
## Artifact Paths
- skill folder
- docs
- maybe version files
```

- Bad because no one can reliably validate drift against vague path labels.

### Vague correction evidence path
```md
## Artifact Paths
| Artifact | Path | Owner | Role |
| Correction evidence | `merged implementation` | Creator | prove accepted drift |
```

- Bad because `merged implementation` is not an exact repo-visible path.

### Reviewer work inside creator steps
```md
## Implementation Steps
1. Refresh the correction workflow text.
2. Write `plan/topic/topic.review-log.md` with the reviewer verdict after approval.
```

- Bad because reviewer feedback logging is not creator-owned implementation work.

### Workflow-body bloat
```md
## Scope
- Add a field-by-field `correction-plan` schema directly inside `plan/agent-handoff-workflow.md`.
```

- Bad because the workflow body should carry lifecycle / routing contract only; detailed schema belongs in reference or examples.

### Premature standalone correction skill
```md
## Scope
- refresh `plan/agent-handoff-workflow.md`
- create `skills/correction-delta-lifecycle/`

## Locked Decisions
- Extract a standalone correction skill now so future topics must use it immediately.
```

- Bad because this topic is a contract refresh for existing workflow surfaces; standalone extraction belongs in a later, separately planned topic only if repeated instability or cross-workflow reuse justifies it.

### Unconditional review-log and global round cap
```md
## Routing notes
- Every review must create `plan/<topic>/<topic>.review-log.md`.
- Creator / reviewer loops stop after exactly three rounds in all topics.
```

- Bad because review logs are conditional and round caps are topic policy, not repository-wide law.

### Wrong reviewer handoff format
```md
## Reviewer Handoff
| Issue | Severity | Notes |
| --- | --- | --- |
| Missing examples | high | please add more |
```

- Bad because workflow requires a machine-consumable JSON object.

### Wrong phase timing
```md
## Post-merge / release actions
- after approval, release the change and then open a PR
```

- Bad because approval, PR, merge, and release are distinct workflow phases.

### Invalid status model or transition
```md
## Status / Allowed Transitions
- **Current**: `planned`
- **Allowed transitions**:
  - `planned` -> `review-ready`
  - `review-ready` -> `approved`
  - `approved` -> `merged`
```

- Bad because it skips required workflow phases, invents an impossible direct approval path, and does not preserve the canonical creator -> reviewer -> publish sequence required by the repository contract.

### Role-boundary confusion
```md
## Locked Decisions
- reviewer will finish any missing creator work during approval
```

- Bad because reviewer and creator are separate roles.
