> Semantic warning: `analysis/model-payload-canonical-hash-core/requirements.md`
> and `analysis/model-payload-canonical-hash-core/technical-spec.md` were not
> found at authoring time. This plan is authored from repo exploration and the
> explicit topic request only.

# model-payload-canonical-hash-core

## Goal / Outcome

- Define a bounded Python implementation topic that adds a canonical
  `model-payload` hashing core under `async_model_gateway.model_registry` with
  one public callable:
  `hash_model_payload(model_payload: dict[str, JSONLike]) -> str`.
- When this topic is complete, the repository has a cross-process-stable
  SHA-256 hex hashing surface for JSON-like `model-payload` identity material,
  with strict runtime type rejection and no broader registry, cache, or
  orchestration changes.

## Scope

- **In scope**:
  - Add the bounded topic plan, step tracking artifact, behavior spec, and
    repo-visible review artifact for `model-payload-canonical-hash-core`.
  - Plan implementation only in:
    `src/async_model_gateway/model_registry/__init__.py`,
    `src/async_model_gateway/model_registry/model_payload/__init__.py`,
    `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`,
    and `tests/model_registry/model_payload/test_canonical_hash.py`.
  - Freeze the public contract, canonicalization rules, error behavior, and
    import-surface boundary for the hashing core.

- **Out of scope**:
  - Any change to `ResponseCache`, `orchestrator`, `ModelPool`, `ModelGateway`,
    or broader runtime flow wiring.
  - Any freshness policy, registry state machine, or payload-hash consumption
    outside the bounded hashing surface.
  - Any loader, `model_artifact`, provider, cache-key, or release-facing work.

## Locked Decisions

- This topic is not a stable-library topic and does not declare release-facing
  timing. `## Stable library metadata` is intentionally absent.
- This topic explicitly adopts the Python planning extension path.
- D1 verdict: `non-trivial` — the topic introduces a new public callable,
  creates a new package surface under `model_registry/model_payload`, freezes
  recursive canonicalization behavior, and requires companion `*.step.md` and
  `*.spec.md` artifacts before implementation.
- The only public callable added by this topic is
  `hash_model_payload(model_payload: dict[str, JSONLike]) -> str`.
- The output contract is a SHA-256 lowercase hex string.
- The top-level `model_payload` input must be `dict[str, JSONLike]`.
- Nested dict keys are accepted only when every key is `str`.
- Values accept only JSON-like scalar, list, or dict content; unsupported types
  raise `TypeError`.
- Canonicalization is recursive for nested dicts, list order is preserved, and
  scalar values are not normalized.
- The canonicalization helper stays internal and is not a public API.
- Cross-process stability is required.
- Public import surface is allowed only from
  `async_model_gateway.model_registry.model_payload`; topic-local re-export from
  `model_payload/__init__.py` is allowed, but `model_registry/__init__.py` must
  not re-export the hashing callable.
- Typing must follow the repository strict baseline from `pyproject.toml`.

## Boundaries / Exclusions

- The planning actor only authors repo-visible planning artifacts for this
  topic.
- The implementer may only change the exact implementation and test paths
  declared in `## Artifact Paths`; drift outside those paths returns the topic
  to `spec-and-plan-finalization`.
- The reviewer validates bounded contract adherence and later gate evidence; the
  reviewer does not expand scope or rewrite implementation goals.
- Architecture and spec files provide boundary context only; this topic does not
  rewrite architecture text, broaden canonical-input semantics, or invent
  registry behavior beyond payload hashing.

## Status / Allowed Transitions

- **Current**: `approved`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`;
  stop at `merged` because this topic does not use the conditional `release`
  workflow.
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

- Independent reviewer work is complete and the repo-visible plan-review
  artifact records an `approved` verdict.
- `approved` requires both the repo-visible plan-review artifact with an
  `approved` verdict and an explicit repo-visible `human check`.
- Explicit repo-visible `human check` is now recorded as passed, so
  `spec-and-plan-finalization` is complete and this topic may enter
  `implement-plan`.
- This topic uses the Python extension path. During `implement-plan`, RED test
  authoring is the first mandatory Python subphase before production-code
  changes.
- This topic declares `*.step.md`, `*.spec.md`, `*.red-tests.yaml`, and
  `*.implementation-review.yaml` as companion artifacts for later workflow
  phases. They do not imply approval by themselves.
- Any scope change to the public callable, canonicalization rules, import
  surface, or implementation artifact paths must return to
  `spec-and-plan-finalization`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-payload-canonical-hash-core/model-payload-canonical-hash-core.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracking | `plan/model-payload-canonical-hash-core/model-payload-canonical-hash-core.step.md` | Planning actor | Repo-visible implementation-progress companion artifact |
| Topic behavior spec | `plan/model-payload-canonical-hash-core/model-payload-canonical-hash-core.spec.md` | Planning actor | Non-trivial Python behavior contract for TDD and later review |
| Plan review artifact | `plan/model-payload-canonical-hash-core/model-payload-canonical-hash-core.plan-review.json` | Reviewer | Repo-visible planning gate verdict |
| RED test artifact | `plan/model-payload-canonical-hash-core/model-payload-canonical-hash-core.red-tests.yaml` | Implementer | Repo-visible TDD gate evidence produced during `implement-plan` |
| Implementation review artifact | `plan/model-payload-canonical-hash-core/model-payload-canonical-hash-core.implementation-review.yaml` | Reviewer | Repo-visible implementation-review gate evidence |
| Model registry package boundary | `src/async_model_gateway/model_registry/__init__.py` | Implementer | Package boundary that must not re-export the hashing callable |
| Public model-payload import surface | `src/async_model_gateway/model_registry/model_payload/__init__.py` | Implementer | Topic-local public import surface for `hash_model_payload` |
| Canonical hashing core | `src/async_model_gateway/model_registry/model_payload/canonical_hash.py` | Implementer | Internal recursive canonicalization and SHA-256 hashing implementation |
| Canonical hash tests | `tests/model_registry/model_payload/test_canonical_hash.py` | Implementer | Bounded pytest coverage for hashing behavior and type rejection |

Artifact path notes:

- This topic does not modify `README.md`, `VERSION`, or
  `.github/copilot-instructions.md`.
- Treat listed paths as an executable contract.
- If later work needs new registry modules, cache integration, or broader tests
  outside the listed file, stop and route back through
  `spec-and-plan-finalization`.

## Implementation Steps

1. Add bounded pytest coverage in
   `tests/model_registry/model_payload/test_canonical_hash.py` for the happy
   path: equal nested payload content with different dict insertion order must
   hash to the same SHA-256 hex string, while preserving the public import
   surface from `async_model_gateway.model_registry.model_payload`.
2. Extend
   `tests/model_registry/model_payload/test_canonical_hash.py` with invalid,
   edge, regression, and backward-compatibility coverage: unsupported nested
   types raise `TypeError`, nested non-`str` dict keys raise `TypeError`, empty
   nested containers are accepted, list order affects the hash, and scalar
   values such as `1` and `1.0` are not normalized to the same digest.
3. Add
   `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`
   with the internal recursive canonicalization helper and the public
   `hash_model_payload` function so the implementation accepts only
   `dict[str, JSONLike]` at the top level, canonicalizes nested dicts
   recursively, preserves list order, rejects unsupported types with
   `TypeError`, and returns a SHA-256 hex digest.
4. Add `src/async_model_gateway/model_registry/model_payload/__init__.py` and
   `src/async_model_gateway/model_registry/__init__.py` so the allowed public
   import surface is `async_model_gateway.model_registry.model_payload`,
   `model_payload/__init__.py` may re-export `hash_model_payload`, and
   `model_registry/__init__.py` does not re-export it.

## Validation / Acceptance Checks

- Canonical topic-plan sections, status names, artifact paths, and reviewer
  handoff shape remain compatible with the repo workflow contracts.
- `model-payload-canonical-hash-core.spec.md` exists because this topic is
  locked as `non-trivial`.
- `model-payload-canonical-hash-core.step.md` mirrors every numbered
  implementation step and keeps only `plan-authoring` marked complete at plan
  creation time.
- Later TDD work can produce a repo-visible
  `model-payload-canonical-hash-core.red-tests.yaml` artifact before any
  production-code edits.
- Later implementation review can verify that only the four locked
  implementation artifact paths changed, that the only public callable is
  `hash_model_payload(model_payload: dict[str, JSONLike]) -> str`, and that
  `model_registry/__init__.py` still does not re-export the hashing surface.
- The eventual implementation must show dict-order-insensitive hashing, stable
  list-order sensitivity, explicit `TypeError` rejection for unsupported
  values, and SHA-256 hex output without relying on broader registry or cache
  changes.

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

- No release workflow required.
- After merge, stop; do not change README, VERSION, tags, or release state
  under this topic.

## Open Questions / Unresolved Items

- None.

## Non-goals

- This topic does not wire payload hashing into registry freshness decisions,
  cache identity, orchestrator flow, or runtime-model acquisition.
- This topic does not introduce semantic equivalence rules, scalar coercion, or
  loader inference from `model-payload`.
- This topic does not expose the canonicalization helper as a public callable
  or broaden the public import surface beyond
  `async_model_gateway.model_registry.model_payload`.
- This topic does not add new dependencies, release metadata, or documentation
  rewrites.

## Current Context

- `src/async_model_gateway/__init__.py` currently contains only the minimal
  package entrypoint scaffold; there is no existing `model_registry` package or
  `model_payload` hashing implementation yet.
- `pyproject.toml` already defines the repository strict typing baseline through
  `pyright` `typeCheckingMode = "strict"` and the existing `pytest` / `ruff`
  validation surfaces.
- `docs/specs/canonical-input-boundary.md` states that `model-payload` is
  strict identity material, must not receive semantic-equivalence handling, and
  can be consumed by `ModelRegistry` for `payload-hash` derivation.
- `docs/specs/model-side-boundary.md` assigns `payload-hash` authority to
  `ModelRegistry` while keeping loader, pool, gateway, and cache work outside
  this boundary.

## Requirements

1. The topic must add exactly one public callable,
   `hash_model_payload(model_payload: dict[str, JSONLike]) -> str`, under the
   import surface `async_model_gateway.model_registry.model_payload`.
2. The hashing result must be a SHA-256 lowercase hex string that is stable
   across processes for equivalent JSON-like payload structure.
3. Nested dicts must be canonicalized recursively, nested dict keys must be
   accepted only when they are `str`, and list order must remain significant.
4. Scalar values must not be normalized; payloads that differ only by scalar
   representation, such as `1` versus `1.0`, must remain distinguishable.
5. Unsupported runtime input types anywhere in the payload tree must raise
   `TypeError`.
6. `model_payload/__init__.py` may provide the topic-local re-export, but
   `model_registry/__init__.py` must not re-export the hashing callable.
7. The implementation must stay bounded to the four locked implementation
   artifact paths and must not touch `ResponseCache`, `orchestrator`,
   `ModelPool`, or `ModelGateway`.

## Decisions

- Async-planning status: exempt — cite exemption evidence: the topic is a
  synchronous hashing helper with no async boundary, resource lifecycle,
  concurrency, timeout, cancellation, or external I/O behavior.
- Module/package placement: add the bounded source surface under
  `src/async_model_gateway/model_registry/model_payload/` and keep
  `src/async_model_gateway/model_registry/__init__.py` as a non-re-exporting
  package boundary.
- New public API: yes — add exactly one public callable,
  `hash_model_payload(model_payload: dict[str, JSONLike]) -> str`, exposed only
  from `async_model_gateway.model_registry.model_payload`.
- Interface changes: yes — introduce a new `model_registry.model_payload`
  package surface and its matching test module without modifying unrelated
  package entrypoints.
- Breaking changes allowed: no — this topic only adds a new bounded surface and
  must not change existing behavior elsewhere in the package.
- New dependencies: no.
- Error handling strategy: reject unsupported runtime input with `TypeError`,
  including non-`str` nested dict keys and non-JSON-like values encountered at
  any depth.
- Typing strategy: fully typed under the repository strict baseline, using a
  recursive `JSONLike` type alias or equivalent internal typing surface without
  introducing `Any`.

## Public Contract / API Changes

- `async_model_gateway.model_registry.model_payload.hash_model_payload`
  - Signature:
    `def hash_model_payload(model_payload: dict[str, JSONLike]) -> str`
  - Input contract: the top-level value must be `dict[str, JSONLike]`; nested
    dict keys must all be `str`; values may contain only JSON-like scalar,
    `list`, or `dict` content.
  - Output contract: returns a SHA-256 lowercase hex string.
  - Failure behavior: raises `TypeError` when the payload tree contains an
    unsupported type or a nested dict key that is not `str`.
  - Stability contract: dict key order does not affect the result, nested dict
    canonicalization is recursive, list order remains significant, and scalar
    representations are not normalized.
- No other public callable is added by this topic.
- `src/async_model_gateway/model_registry/model_payload/__init__.py` may
  re-export `hash_model_payload` for the allowed import surface.
- `src/async_model_gateway/model_registry/__init__.py` must not re-export the
  hashing callable.

## Affected Files / Modules

Likely affected files:
- `src/async_model_gateway/model_registry/__init__.py`
- `src/async_model_gateway/model_registry/model_payload/__init__.py`
- `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`
- `tests/model_registry/model_payload/test_canonical_hash.py`

Candidate files to inspect:
- `docs/specs/canonical-input-boundary.md`
- `docs/specs/model-side-boundary.md`
- `pyproject.toml`

## Test Plan

- Happy path:
  `tests/model_registry/model_payload/test_canonical_hash.py` verifies that two
  payloads with identical nested content but different dict insertion order
  produce the same 64-character SHA-256 hex digest, and that the callable is
  importable from `async_model_gateway.model_registry.model_payload`.
- Invalid input:
  `tests/model_registry/model_payload/test_canonical_hash.py` verifies that
  unsupported nested values such as `object()` and nested dicts with non-`str`
  keys raise `TypeError`.
- Edge case:
  `tests/model_registry/model_payload/test_canonical_hash.py` verifies empty
  dict / list containers, nested empty structures, and list-order-sensitive
  payloads.
- Regression:
  `tests/model_registry/model_payload/test_canonical_hash.py` verifies that
  scalar representations are not normalized by asserting different digests for
  payloads containing `1` versus `1.0`, while nested dict key ordering remains
  digest-invariant.
- Backward compatibility:
  `tests/model_registry/model_payload/test_canonical_hash.py` verifies that the
  supported public import path is
  `async_model_gateway.model_registry.model_payload` and that no broader
  `model_registry` re-export is required by this topic contract.

## Validation Commands

```bash
uv run pytest tests/model_registry/model_payload/test_canonical_hash.py -v
uv run pyright src
uv run ruff check src tests
```

## Risks

- Cross-process stability can drift if the implementation accidentally depends
  on non-canonical Python object rendering instead of a deterministic
  canonicalization path.
- The public surface can widen unintentionally if
  `model_registry/__init__.py` re-exports `hash_model_payload` or if the helper
  function becomes public.

## Rollback Plan

- Revert the bounded implementation files:
  `src/async_model_gateway/model_registry/__init__.py`,
  `src/async_model_gateway/model_registry/model_payload/__init__.py`,
  `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`, and
  `tests/model_registry/model_payload/test_canonical_hash.py`.
- If the planning artifacts themselves must be withdrawn, revert the topic
  directory under `plan/model-payload-canonical-hash-core/` and return the
  topic to `planned`.

## Open Questions

- None.
