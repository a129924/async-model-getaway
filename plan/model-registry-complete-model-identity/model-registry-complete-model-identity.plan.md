> Semantic warning: `analysis/model-registry-complete-model-identity/requirements.md`
> and `analysis/model-registry-complete-model-identity/technical-spec.md` do not
> exist at authoring time. This plan relies only on repository exploration, the
> workflow contract, and the explicitly approved topic contract; the optional
> analysis layer is incomplete and is not evidence.

# model-registry-complete-model-identity

## Goal / Outcome

- Add a stable, complete, read-only `RegistryEntry.model_identity_hash` derived
  from `model_name`, `model_source_kind`, and existing `payload_hash`.
- Preserve lookup, freshness decisions, result shape, and upsert conditions.

## Scope

- **In scope**: the identity hasher submodule; the derived entry property; a
  pre-policy candidate identity read; bounded tests plus the single required
  `model_identity` test-package marker; and minimal accurate updates to
  `README.md`, `docs/architecture.md`, and
  `docs/specs/model-side-boundary.md`.
- **Out of scope**: CacheKey migration; `RegistryFreshnessResult`, lookup-key,
  freshness-policy, payload-hasher, or signature changes; predictor,
  orchestrator, runtime, provider, response-cache, persistence, dependency,
  lockfile, version, release, and broad documentation changes.

## Locked Decisions

- This is non-stable-library work: no `Stable library metadata`, version bump,
  or release workflow. The docs changes are explanatory only.
- D1 verdict is `non-trivial`; the topic adopts the Python planning extension.
- `ModelIdentityHasher` is public only from
  `async_model_gateway.model_registry.model_identity`. The registry root does
  not re-export it.
- The stateless public callable is
  `ModelIdentityHasher.hash_model_identity(*, model_name: str,
  model_source_kind: ModelSourceKind, model_payload_hash: str) -> str`.
- Concatenate exactly three frames, in order, for literal ASCII labels
  `model_name`, `model_source_kind`, `model_payload_hash`. Each is
  `label + NUL + 8-byte big-endian UTF-8-byte-length + UTF-8 value bytes`; hash
  the concatenation with SHA-256 and return lowercase hex. JSON, implicit
  conversion, Unicode normalization, and field reordering are forbidden.
- The golden vector `("demo", ModelSourceKind.LOCAL, "a" * 64)` must hash to
  `177653000e2e441856c1d22e3b2b0d02a1ba7c384f1029fb5b5c3464663b72b4`.
- Name and payload hash must be non-empty `str`: wrong type raises `TypeError`,
  empty string raises `ValueError`. Only existing `ModelSourceKind.LOCAL` and
  `.REMOTE` are accepted; raw strings and all other values raise `TypeError`.
- `RegistryEntry.model_identity_hash` is lazy-imported and calculated, never a
  dataclass field, stored value, cache, or constructor parameter.
- `resolve_freshness()` keeps its signature and existing lookup order. It reads
  candidate identity after construction and before policy evaluation; identity
  errors propagate unchanged and prevent policy evaluation/upsert, but do not
  remove the pre-existing lookup call.
- `RegistryFreshnessResult` stays `decision`, `entry`, `previous_payload_hash`;
  `CacheKey` stays three fields. Payload hashing and all existing signatures are
  unchanged.
- An independent plan-review `approved` verdict and repo-visible human-check
  pass are both required before implementation.
- `tests/model_registry/model_identity/__init__.py` is the only permitted new
  test marker. It prevents same-basename collection collision between the new
  identity `test_canonical_hash.py` and existing payload
  `test_canonical_hash.py`; do not modify pytest configuration/import mode, add
  another marker, or use dynamic loading. It changes no production contract.

## Boundaries / Exclusions

- Planning authoring creates only this topic's plan, step, and spec artifacts.
- The implementer may later modify only paths declared below; path or contract
  drift returns to `spec-and-plan-finalization`.
- Reviewers do not implement fixes or pass human gates.
- This amendment invalidates the current contents of the plan-review and
  human-check evidence paths for implementation entry. A reviewer must overwrite
  the declared plan-review path with its fresh verdict; after that approval, the
  human gate owner must overwrite the declared human-check path with fresh
  clearance. Planning authoring does neither.
- This capability must not imply cache migration, execution flow, or persistence.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: `spec-and-plan-finalization -> implement-plan ->
  pr-comment -> pr-comment-review-pr-comments-and-fix`; stop at `merged`.
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

Routing notes: this completed collection-safety amendment is ready for the
reviewer gate in `spec-and-plan-finalization`. The reviewer overwrites the
declared `.plan-review.json` path with current evidence. Only after its approved
verdict may the human gate owner overwrite the declared `.human-check.json` path
with current `implement-plan` clearance. RED tests are then first in
`implement-plan`; an approved implementation review is required before
`pr-comment`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.plan.md` | Planning actor | Execution contract |
| Step tracking | `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.step.md` | Implementer | Progress tracking |
| Behavior spec | `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.spec.md` | Planning actor | Non-trivial behavior contract |
| Plan review | `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.plan-review.json` | Reviewer | Current planning-gate verdict, overwritten after each plan amendment |
| Human check | `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.human-check.json` | Human | Current implementation-entry gate, overwritten after the current approved review |
| RED evidence | `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.red-tests.yaml` | Implementer | Future TDD evidence |
| Implementation review | `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.implementation-review.yaml` | Reviewer | Future pre-PR gate |
| Identity package | `src/async_model_gateway/model_registry/model_identity/__init__.py` | Implementer | Public submodule export |
| Identity core | `src/async_model_gateway/model_registry/model_identity/canonical_hash.py` | Implementer | Framed hashing/validation |
| Entry | `src/async_model_gateway/model_registry/entry.py` | Implementer | Derived property |
| Registry | `src/async_model_gateway/model_registry/registry.py` | Implementer | Pre-policy property read |
| Identity tests | `tests/model_registry/model_identity/test_canonical_hash.py` | Implementer | Hasher/property coverage |
| Identity test package marker | `tests/model_registry/model_identity/__init__.py` | Implementer | Only marker required for unambiguous pytest collection |
| Freshness tests | `tests/model_registry/test_freshness_policy.py` | Implementer | Result/policy regressions |
| Registry tests | `tests/model_registry/test_registry.py` | Implementer | Ordering/flow regressions |
| Package tests | `tests/model_registry/test_model_registry_package_surface.py` | Implementer | Root non-re-export |
| Project summary | `README.md` | Implementer | Minimal capability wording |
| Architecture | `docs/architecture.md` | Implementer | Minimal boundary wording |
| Model-side spec | `docs/specs/model-side-boundary.md` | Implementer | Minimal ownership wording |

`README.md` changes; VERSION, `pyproject.toml`, `uv.lock`, and
`.github/copilot-instructions.md` do not. Only plan, step, and spec are created
now. The current contents of review/human JSON are stale because of this
amendment; their declared paths are overwritten by their proper owners during
the fresh review and clearance sequence.

## Implementation Steps

1. Add `tests/model_registry/model_identity/__init__.py` as the sole test-package
   marker. Do not change pytest config/import mode, add markers elsewhere, or
   use dynamic loading.
2. Author RED coverage in the declared identity and registry test modules, then
   create the RED evidence mapping golden, framing, validation, property,
   result-shape, root-surface, and side-effect cases; no dynamic test loading.
3. Add `model_identity/__init__.py` and `canonical_hash.py`, exporting only the
   hasher and implementing the locked static API, frames, digest, and validation.
4. Add the lazy read-only property in `entry.py` without changing dataclass
   fields, constructor, equality, or storage.
5. Read candidate identity in `registry.py` before policy evaluation without
   changing lookup timing, payload hashing, decisions, or upsert condition.
6. Apply three bounded docs edits, run validation, and truthfully update step
   tracking for implementation review.

## Validation / Acceptance Checks

- Plan sections, paths, transitions, semantic warning, and the single JSON
  reviewer handoff obey repository workflow contracts.
- Step mirrors all six steps and shows only plan authoring complete; spec exists.
- Full collection must include both canonical-hash modules without import
  mismatch: `uv run pytest --collect-only` and full `uv run pytest` are required.
- The current review/human evidence contents are stale for this amendment. The
  reviewer and then human gate owner must overwrite their respective declared
  paths; planning authoring has not fabricated either gate.
- Golden hash, literal UTF-8 framing, fail-closed validation, read-only derived
  property, frozen shapes/signatures, no policy/upsert after identity failure,
  and first-seen/unchanged/changed regression behavior are verified.
- `uv run pytest`, `uv run pyright`, and `uv run ruff check src tests` pass in
  implementation validation.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {"ADDRESS": [], "DISCUSS": [], "SKIP": []}
}
```

## Post-merge / release actions

No release workflow required. After merge, do not change version, tags,
lockfile, or release state.

## Open Questions / Unresolved Items

None.

## Goal

Provide deterministic complete-model identity for existing registry entries
without changing established registry behavior outside the derived capability.

## Non-goals

- No CacheKey change or cache-record migration.
- No registry persistence, store API, or lookup-key change.
- No `ModelPayloadHasher` behavior change.
- No orchestrator, provider, runtime, or execution wiring.
- No dependency, root re-export, compatibility adapter, release, or version bump.

## Current Context

`RegistryEntry` is a frozen slotted three-field dataclass in `entry.py`.
`resolve_freshness()` looks up by name/source kind, derives `payload_hash` via
the existing hasher, evaluates the synchronous policy, and upserts only if not
unchanged. The registry root exports only `ModelRegistry`.

## Requirements

1. The new submodule exports only `ModelIdentityHasher`; no root re-export.
2. Exact locked frames produce the exact golden digest.
3. Identity input validation fails closed without coercion or normalization.
4. The entry property is calculated/read-only and excluded from dataclass state.
5. Identity read occurs before policy; failure prevents policy/upsert, not lookup.
6. Signatures, result/CacheKey fields, payload hashing, policy, and upsert stay
   unchanged.
7. Docs describe only the identity capability.
8. The sole new test-package marker lets full pytest collect both canonical-hash
   modules without import mismatch; pytest config/import mode, other markers,
   dynamic loading, and all production contracts remain unchanged.

## Decisions

- Async-planning status: exempt — cite exemption evidence: this adds synchronous
  pure hashing and a synchronous property only; it changes no async boundary,
  lifecycle, concurrency, cancellation, timeout, or failure ownership.
- Module/package placement: hasher in `model_identity/canonical_hash.py` and
  submodule `__init__.py`; property in `entry.py`; ordering read in `registry.py`.
- New public API: yes — static `ModelIdentityHasher.hash_model_identity(...)`
  and read-only `RegistryEntry.model_identity_hash: str`.
- Interface changes: no signature change; only a derived property and internal
  synchronous read are added.
- Breaking changes allowed: no — existing public contracts remain frozen.
- New dependencies: no — standard-library `hashlib` only.
- Error handling strategy: locked `TypeError`/`ValueError` propagate unchanged
  through the property before policy evaluation/upsert.
- Typing strategy: strict Python 3.10 annotations, existing `ModelSourceKind`,
  no `Any`, no coercion, and no protocol.

## Public Contract / API Changes

```python
class ModelIdentityHasher:
    @staticmethod
    def hash_model_identity(
        *, model_name: str, model_source_kind: ModelSourceKind,
        model_payload_hash: str,
    ) -> str: ...
```

The static method returns lowercase SHA-256 hex, raises locked errors, and is
submodule-public only. `RegistryEntry.model_identity_hash` has no setter, field,
stored representation, or constructor parameter. Existing signatures/root
exports remain backward-compatible.

## Affected Files / Modules

Likely affected files:

- `src/async_model_gateway/model_registry/model_identity/__init__.py`
- `src/async_model_gateway/model_registry/model_identity/canonical_hash.py`
- `src/async_model_gateway/model_registry/entry.py`
- `src/async_model_gateway/model_registry/registry.py`
- `tests/model_registry/model_identity/test_canonical_hash.py`
- `tests/model_registry/model_identity/__init__.py`
- `tests/model_registry/test_freshness_policy.py`
- `tests/model_registry/test_registry.py`
- `tests/model_registry/test_model_registry_package_surface.py`
- `README.md`, `docs/architecture.md`, `docs/specs/model-side-boundary.md`

Candidate files to inspect:

- `src/async_model_gateway/model_registry/freshness_result.py`
- `src/async_model_gateway/model_registry/freshness_policy.py`
- `src/async_model_gateway/model_registry/ports/store.py`
- `src/async_model_gateway/response_cache/key.py`

## Implementation Steps

1. Add the sole `model_identity` test-package marker; keep pytest config/import
   mode and all other test-package markers unchanged.
2. Write RED tests and future RED evidence for all locked identity cases.
3. Implement the new submodule and static framed hasher.
4. Add the lazy derived entry property without state changes.
5. Force the pre-policy identity read and verify failure ordering.
6. Update bounded docs, validate, and update the step artifact.

## Test Plan

Test files: `tests/model_registry/model_identity/test_canonical_hash.py`,
`tests/model_registry/test_freshness_policy.py`,
`tests/model_registry/test_registry.py`, and
`tests/model_registry/test_model_registry_package_surface.py`.

- Happy path: fixed golden digest and matching entry property.
- Invalid input: non-strings, empty strings, raw source strings, invalid source.
- Edge case: Unicode/framing-sensitive input and each independent field change.
- Regression: first-seen, unchanged, changed lookup/policy/previous-hash/upsert.
- Backward compatibility: dataclass/result/CacheKey shapes, frozen signatures,
  root non-re-export, and successful collection of both canonical-hash modules.

## Validation Commands

```sh
uv run pytest
uv run pytest --collect-only
uv run pyright
uv run ruff check src tests
```

## Risks

Incorrect labels, byte-length framing, source conversion, or read ordering could
break the golden contract or existing freshness side effects. A field or root
export change could silently widen public behavior.

## Rollback Plan

Revert only declared source, test, docs, and topic artifacts; remove the new
`model_identity` directory. Do not change the handoff's read-only surfaces.

## Open Questions

None.

## Implementation Python Handoff Metadata

### Goal

Provide deterministic complete-model identity for existing registry entries
without changing established registry behavior outside the derived capability.

### Non-Goal

Do not change CacheKey, registry persistence or lookup keys, payload hashing,
orchestrator/provider/runtime behavior, dependencies, release metadata, or the
registry-root import surface.

### In-Scope

The exact declared source, test, documentation, and topic-evidence paths; pure
identity hashing, derived property, pre-policy read, bounded tests, docs, and
the reviewer/human-owned overwrite sequence for current gate evidence.

### Out-Of-Scope

Everything in `## Non-goals`, especially CacheKey work and broader model-side
execution or persistence.

### ReadOnly

- `src/async_model_gateway/model_registry/__init__.py`
- `src/async_model_gateway/model_registry/freshness_result.py`
- `src/async_model_gateway/model_registry/freshness_policy.py`
- `src/async_model_gateway/model_registry/ports/__init__.py`
- `src/async_model_gateway/model_registry/ports/store.py`
- `src/async_model_gateway/model_registry/stores/in_memory.py`
- `src/async_model_gateway/model_registry/model_payload/__init__.py`
- `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`
- `tests/model_registry/model_payload/test_canonical_hash.py`
- `src/async_model_gateway/response_cache/`
- `pyproject.toml`, `uv.lock`, and version source. Planning authoring reads but
  does not modify current review/human evidence; only the declared reviewer or
  human gate owner overwrites that evidence at its workflow phase.

### Written

- `src/async_model_gateway/model_registry/model_identity/__init__.py`
- `src/async_model_gateway/model_registry/model_identity/canonical_hash.py`
- `tests/model_registry/model_identity/test_canonical_hash.py`
- `tests/model_registry/model_identity/__init__.py`
- `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.red-tests.yaml`

### Deleted

- None.

### Modify

- `src/async_model_gateway/model_registry/entry.py`
- `src/async_model_gateway/model_registry/registry.py`
- `tests/model_registry/test_freshness_policy.py`
- `tests/model_registry/test_registry.py`
- `tests/model_registry/test_model_registry_package_surface.py`
- `README.md`, `docs/architecture.md`, `docs/specs/model-side-boundary.md`
- `plan/model-registry-complete-model-identity/model-registry-complete-model-identity.step.md`

### TestCase

- Golden/stability and independent name/source/payload changes.
- Full pytest collection includes both canonical-hash modules without import
  mismatch, while pytest configuration/import mode and all other markers remain
  unchanged.
- Literal UTF-8 Unicode and frame-sensitive values without normalization/JSON.
- Invalid name/payload/source behavior.
- Read-only non-field property; frozen result/CacheKey/signature surfaces.
- Identity failure before policy/upsert but after the unchanged lookup.
- First-seen/unchanged/changed regression and root non-re-export.
