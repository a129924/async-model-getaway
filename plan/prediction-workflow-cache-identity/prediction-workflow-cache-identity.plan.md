> Semantic warning: `analysis/prediction-workflow-cache-identity/requirements.md`
> and `analysis/prediction-workflow-cache-identity/technical-spec.md` do not
> exist. This docs-only topic is based on the human-approved architecture
> decisions recorded in the conversation; no analysis artifact is being
> silently substituted.

# prediction-workflow-cache-identity

## Goal / Outcome

- Establish one repo-visible target workflow for prediction identity, response
  reuse, model execution, and application-result representation.
- Make the current local/ONNX gateway's transitional status explicit without
  claiming that target Python surfaces already exist.

## Scope

- **In scope**:
  - Create the topic plan, specification, step tracker, plan-review verdict,
    and human-check evidence.
  - Add one detailed prediction-workflow boundary specification and align the
    architecture summary plus the existing core, canonical-input, model-side,
    orchestrator, and response-cache specifications.
  - Add a first-read link from `README.md` that distinguishes the target
    baseline from implemented runtime behavior.

- **Out of scope**:
  - Python implementation, public exports, request DTO changes, cache-key
    migration, concrete codecs, pandas integration, tests, version changes,
    persistence, eviction, retries, singleflight, table batching, or remote
    execution implementation.

## Locked Decisions

- This is a non-stable docs-only topic; no release workflow, `VERSION`, or
  release metadata change is required.
- Target canonical input adds `prediction_input`. It and `features` are deeply
  snapshotted before the first await, and their snapshots are shared by identity
  derivation and execution. All side-effect-free identity validation completes
  before registry freshness can write state.
- `ModelRegistry` remains the model identity and freshness authority. Its
  target result supplies `model_identity_hash`, derived from model name, source
  kind, and payload hash.
- `Predictor` owns stable base namespace declaration, a compatibility token,
  feature validation/execution projection, prediction-input identity projection,
  and raw-result-to-application-result projection. It does not own hashing, key
  construction, storage, or execution lifecycle.
- `FeatureIdentityHasher` owns `Mapping[str, str]` feature hashing;
  `PredictionInputHasher` owns JSON-like prediction-input hashing; both fail
  closed before cache lookup or execution.
- `CacheNamespaceDeriver` canonically hashes the predictor base namespace,
  predictor compatibility token, and `ResultCodec` compatibility token.
  `CacheKeyDeriver` only assembles the completed identity values.
- The target key is
  `CacheKey(namespace, model_identity_hash, feature_hash, prediction_input_hash)`.
  It is a future explicit breaking replacement for the current three-field
  public key, not a compatibility promise in this topic.
- `ResultCodec` belongs above `ResponseCache`: it maps application result to and
  from cache `str`. `CacheCodec` remains `str ↔ bytes`; `CacheStore` remains
  unaware of application result types. Result-codec encode or decode failure
  propagates unchanged and does not fall back to model execution or a write.
- `LocalResponseGateway` is a local/ONNX transition projection. Its opaque
  deriver and shallow `invocation` snapshot remain current behavior, not target
  conformance.

## Boundaries / Exclusions

- Planning artifacts and documentation are the only mutable surfaces in this
  topic. Any source, test, public-contract, or migration work returns to a new
  `spec-and-plan-finalization` topic.
- The implementer may not mark human gates on behalf of a human except for the
  explicit authorization recorded for this topic.
- `ResponseCache`, `CacheStore`, `CacheCodec`, `ModelPool`, `ModelGateway`, and
  `ModelExecution` retain their existing implementation boundaries; this topic
  only documents their target composition.

## Status / Allowed Transitions

- **Current**: `pr-open`
- **Execution model**: `spec-and-plan-finalization -> implement-plan ->
  pr-comment`; this topic stops at `merged` and has no release phase.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`

Routing notes:

- The plan-review artifact records an `approved` verdict after checking the
  shared workflow and topic-plan contracts.
- The human-check artifact records the explicit 2026-08-14 authorization to
  enter `implement-plan`; it is not inferred from earlier design discussion.
- All declared documentation implementation and validation work is complete.
  PR #28 has entered `pr-comment-review-pr-comments-and-fix`; all six current
  actionable review threads were addressed, committed, pushed, and resolved.
  The tracker records the validation and completed thread resolution.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/prediction-workflow-cache-identity/prediction-workflow-cache-identity.plan.md` | Planning actor | Execution contract |
| Topic specification | `plan/prediction-workflow-cache-identity/prediction-workflow-cache-identity.spec.md` | Planning actor | Frozen documentation acceptance contract |
| Step tracker | `plan/prediction-workflow-cache-identity/prediction-workflow-cache-identity.step.md` | Implementer | Progress and validation record |
| Plan review | `plan/prediction-workflow-cache-identity/prediction-workflow-cache-identity.plan-review.json` | Reviewer | Planning gate verdict |
| Human check | `plan/prediction-workflow-cache-identity/prediction-workflow-cache-identity.human-check.json` | Human | Execution authorization evidence |
| First-read summary | `README.md` | Implementer | Target-baseline reading link |
| Architecture summary | `docs/architecture.md` | Implementer | Current-versus-target overview |
| Core index | `docs/specs/core-abstractions-boundary.md` | Implementer | Vocabulary and dependency index |
| Canonical input spec | `docs/specs/canonical-input-boundary.md` | Implementer | Target input vocabulary |
| Model-side spec | `docs/specs/model-side-boundary.md` | Implementer | Registry target identity responsibility |
| Orchestrator spec | `docs/specs/orchestrator-boundary.md` | Implementer | Workflow coordination responsibility |
| Response-cache spec | `docs/specs/response-cache-boundary.md` | Implementer | Cache/result codec separation |
| Workflow spec | `docs/specs/prediction-workflow-boundary.md` | Implementer | Detailed target workflow and responsibility matrix |

`VERSION`, source, tests, and existing unrelated plan artifacts are not changed.
Any scope drift outside this table returns to planning.

## Implementation Steps

1. Create the detailed target workflow specification, including identity inputs,
   namespace compatibility, `ResultCodec`, failure behavior, and the local
   transition projection.
2. Align the architecture and spec index with the target workflow while clearly
   preserving implemented-versus-target distinctions.
3. Align canonical-input, model-side, orchestrator, and response-cache boundary
   wording with the shared owner matrix and dependency direction.
4. Add the concise README entry and run cross-document consistency validation.
5. Update the step tracker with completed implementation and validation facts.

## Validation / Acceptance Checks

- All declared documentation paths distinguish current implementation from
  target architecture.
- No document describes `features` as prediction input, `model-payload` as
  inference input, or `ResponseCache`/`CacheStore` as pandas-aware.
- The target workflow states the four identity dimensions, deep snapshot rule,
  result-codec compatibility namespace, and fail-closed codec behavior.
- `LocalResponseGateway` is documented as transitional and is not claimed to
  satisfy the target four-field key or deep-snapshot contract.
- The plan-review artifact uses the shared JSON-only shape and the human-check
  artifact records the explicit human authorization.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

No release workflow required. Future source implementation must open a new
topic that references this baseline.

## Open Questions / Unresolved Items

None. Concrete result serialization, Python surfaces, and cache-key migration
are explicitly deferred rather than unresolved within this topic.
