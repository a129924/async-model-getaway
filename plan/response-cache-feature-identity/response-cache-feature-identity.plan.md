Analysis-layer routing: incomplete optional-analysis mode. Semantic warning: neither `analysis/response-cache-feature-identity/requirements.md` nor `analysis/response-cache-feature-identity/technical-spec.md` exists. The explicit human override for this contract/error-policy replan is the execution baseline. If either analysis artifact is introduced and conflicts with this baseline before implementation, return to `spec-and-plan-finalization`.

# response-cache-feature-identity

## Goal / Outcome

- Correct the internal canonical feature identity contract so valid `str` subclasses contribute their base-string material without invoking an overridable `__str__`, canonical pairs sort by their complete base-string `(key, value)` tuple even when distinct emitted keys canonicalize to the same base key, and feature material that cannot strictly UTF-8 encode fails closed as `TypeError` chained from the original `UnicodeEncodeError`.
- Preserve the existing sorted pair-list JSON, `ensure_ascii=False`, compact separators, UTF-8, and lowercase SHA-256 digest representation while allowing the unchanged `ResponseCacheKeyFactory` to propagate the hasher failure unchanged.

## Scope

- **In scope**:
  - Revise this topic's plan, non-trivial behavior specification, and step tracker for the explicit contract/error-policy replan.
  - During a later approved implementation pass, modify only `src/async_model_gateway/response_cache/_canonical_feature_hasher.py` and `tests/response_cache/test_canonical_feature_hasher.py`.
  - Require direct-hasher and factory-integration regression tests for base-`str` material, an overridden `__str__`, complete-pair ordering for duplicate base keys with different values, strict UTF-8 rejection, `TypeError` chaining, and factory non-wrapping.

- **Out of scope**:
  - Changing the `FeatureHasher` port, `ResponseCacheKey`, `ResponseCacheKeyFactory`, their signatures, or the `ResponseCacheKey` field set.
  - Rejecting, deduplicating, or otherwise special-casing duplicate base keys; changing model-payload canonicalization or hash ownership, TTL/freshness/store behavior, persistence, eviction, settings, orchestrator flow, or response generation.
  - Adding package-root or `ports` re-exports, hash versioning/rotation/migration, dependencies, release/version metadata, or documentation claims beyond the already-true internal implementation boundary.

### Executable file inventory

| Classification | Exact paths | Contract |
| --- | --- | --- |
| Written now | `plan/response-cache-feature-identity/response-cache-feature-identity.plan.md`; `plan/response-cache-feature-identity/response-cache-feature-identity.spec.md`; `plan/response-cache-feature-identity/response-cache-feature-identity.step.md` | Planning actor updates only these repo-visible planning artifacts in this replan. |
| Modified during implementation | `src/async_model_gateway/response_cache/_canonical_feature_hasher.py`; `tests/response_cache/test_canonical_feature_hasher.py` | Implementer/tester corrects the sole internal hasher and its focused direct-import regression coverage. |
| Fresh future gate artifacts | `plan/response-cache-feature-identity/response-cache-feature-identity.plan-review.json`; `plan/response-cache-feature-identity/response-cache-feature-identity.human-check.json`; `plan/response-cache-feature-identity/response-cache-feature-identity.red-tests.yaml`; `plan/response-cache-feature-identity/response-cache-feature-identity.implementation-review.yaml` | Respectively Reviewer, Human, Tester, and independent Reviewer replace or update the historical evidence only at their new workflow gates; this planning pass does not prefill any of them. |
| ReadOnly / preserve-and-validate | `README.md`; `docs/architecture.md`; `docs/specs/response-cache-boundary.md`; `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__version__.py`; `src/async_model_gateway/response_cache/__init__.py`; `src/async_model_gateway/response_cache/cache.py`; `src/async_model_gateway/response_cache/entry.py`; `src/async_model_gateway/response_cache/freshness_policy.py`; `src/async_model_gateway/response_cache/key.py`; `src/async_model_gateway/response_cache/key_factory.py`; `src/async_model_gateway/response_cache/ports/__init__.py`; `src/async_model_gateway/response_cache/ports/feature_hasher.py`; `src/async_model_gateway/response_cache/ports/store.py`; `src/async_model_gateway/response_cache/ttl_freshness_policy.py`; `tests/response_cache/test_cache.py`; `tests/response_cache/test_entry.py`; `tests/response_cache/test_in_memory_store.py`; `tests/response_cache/test_key.py`; `tests/response_cache/test_key_factory.py`; `tests/response_cache/test_response_cache_freshness_policy.py`; `tests/response_cache/test_response_cache_package_surface.py`; `tests/response_cache/test_ttl_freshness_policy.py` | Existing public surface, port, key/factory delegation, upstream payload identity, cache/store behavior, version/dependency metadata, documentation, and regression coverage must not drift. |
| Deleted | None | This topic deletes no file, API, behavior, or planning artifact. |
| Out-of-scope / no path authorization | No additional repository paths | Any new production, test, document, public-surface, TTL/store, payload, or orchestrator path requires replanning. |

## Locked Decisions

- D1 verdict: `non-trivial` — this correction changes the executable identity/error contract, requires a fresh plan review and human check, fresh RED evidence, implementation, and independent implementation review.
- `CanonicalFeatureHasher` remains internal-only at `async_model_gateway.response_cache._canonical_feature_hasher`, implements the unchanged `FeatureHasher.hash_features(features: Mapping[str, str]) -> str` method, and is not re-exported by `async_model_gateway.response_cache` or `async_model_gateway.response_cache.ports`.
- Canonical digest representation remains frozen: validate each mapping key/value with `isinstance(..., str)`; obtain each accepted key/value's identity material with the explicit base calls `str.__str__(key)` and `str.__str__(value)`, never polymorphic `str(...)` or a subclass override of `__str__`; sort the resulting base-string pairs lexicographically as complete `(base_key, base_value)` tuples with normal built-in string ordering; serialize the sorted pair list with `json.dumps(..., ensure_ascii=False, separators=(",", ":"))`; strictly encode that exact text as UTF-8; return `hashlib.sha256(...).hexdigest()`.
- A mapping-like input that emits multiple accepted keys whose base-string material is equal but whose base-string values differ remains valid feature material. It must be deterministic across emitted insertion order through complete-pair sorting; this topic must not reject, deduplicate, or otherwise choose a duplicate-key error policy.
- `ensure_ascii=True` is forbidden. The digest remains exactly a 64-character lowercase SHA-256 hexadecimal string. The empty mapping remains canonical `[]` with golden digest `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- Feature material is defined as text that can strictly UTF-8 encode. For a valid runtime `str` (including a `str` subclass) whose canonical serialized representation cannot encode because of an unpaired surrogate or equivalent encoding failure, `CanonicalFeatureHasher` must catch the original `UnicodeEncodeError` at the UTF-8 boundary and raise `TypeError` from that exact exception. It must not change JSON settings, coerce, normalize, skip, return a cache-miss substitute, or leak the raw encoding error as the contract result.
- Validation precedes material extraction, sorting, and serialization. A non-`str` key or value raises `TypeError`; implementation must not call polymorphic `str(...)`, trim whitespace, casefold, normalize Unicode, insert defaults, swallow an exception, or return a fallback digest.
- `ResponseCacheKeyFactory` remains a pure delegate: it receives literal `namespace` and upstream `model_payload_hash`, passes the original mapping to the injected hasher, constructs no key when hashing fails, and does not catch, translate, or wrap the concrete hasher's `TypeError` or its chained `UnicodeEncodeError` cause.
- The topic adopts the Python planning extension. After fresh plan review approval and a fresh repo-visible human check, RED test authoring is the first `implement-plan` subphase. Fresh `.red-tests.yaml` evidence is required before implementation; fresh independent `.implementation-review.yaml` evidence is required before PR routing.
- Async-planning status: exempt — cite exemption evidence: the correction is synchronous, in-memory string material extraction, validation, sorting, serialization, encoding, and hashing; it adds no async boundary, lifecycle ownership, concurrency, timeout, cancellation, retry, or external I/O.
- Stable-library intent is explicitly absent. `README.md`, version metadata, and release timing are not changed; the conditional `## Stable library metadata` section is intentionally absent and the conditional `release` workflow does not apply.

## Boundaries / Exclusions

- The planning actor writes only the three current planning artifacts; it does not implement source/tests, alter historic review evidence, create fresh reviewer verdicts, or close human gates.
- The implementer/tester may modify only the declared internal hasher and focused test, plus the declared fresh workflow evidence at its assigned gate. A need to edit a ReadOnly path, use a new import surface, or create another module/test path returns to `spec-and-plan-finalization`.
- Tests use ordinary direct imports only. Dynamic module loading is not authorized.
- Reviewer independently writes fresh plan-review and implementation-review verdicts; Human independently writes fresh human-check and human-merge gate evidence. Main Agent owns worktree, branch, publish/PR routing, and post-merge orchestration; none of that work belongs in creator steps.
- The existing plan-review, human-check, RED-test, and implementation-review artifacts record the pre-replan contract only. They are retained without modification as historical evidence, cannot satisfy any gate for this revised contract, and must not be prefilled by the planning actor.
- Representation choices outside the locked sorted pair-list JSON/UTF-8/SHA-256 form, including `ensure_ascii=True`, delimiter schemes, normalization, generic serializers, and versioning, belong to another topic.

## Status / Allowed Transitions

- **Current**: `review-ready` in `spec-and-plan-finalization` after the explicit human override for complete canonical-pair sorting.
- **Plan-authoring completeness**: `INCOMPLETE` only for the two explicitly absent optional analysis companions named in the routing warning. The override freezes all executable decisions; this status does not satisfy a review or human gate.
- **Execution model**: route the actionable PR feedback through `pr-comment-review-pr-comments-and-fix` back to `spec-and-plan-finalization`; then require fresh plan review approved -> fresh Human `human check` cleared -> fresh RED tests -> implementation -> fresh independent implementation review -> `pr-comment`. No historical gate is reusable or prefilled. Stop at `merged`; no conditional `release` workflow applies.
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

- A fresh Reviewer-owned `plan/response-cache-feature-identity/response-cache-feature-identity.plan-review.json` with verdict `approved`, authored against this revised complete-pair-sorting plan/spec/step contract, is required before a fresh Human-owned `plan/response-cache-feature-identity/response-cache-feature-identity.human-check.json` can explicitly clear `implement-plan`. Neither artifact may be prefilled.
- Neither the old `approved` review nor the old `cleared` human-check state is valid for this revised contract; chat consensus cannot replace either repo-visible gate.
- The Tester may write new RED tests/evidence only after both fresh planning gates clear. The Implementer may modify the two implementation paths only after fresh RED evidence. An independent Reviewer must produce new implementation-review evidence before the topic returns to `pr-comment`.
- Scope, path, public-contract, canonical-representation, identity-material, error-policy, or release-intent drift returns to `spec-and-plan-finalization`; PR discussion cannot replace planning or human-check gates.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Absent requirements companion | `analysis/response-cache-feature-identity/requirements.md` | Analysis producer | Optional business-intent guardrail; absent at authoring and not created by this topic. |
| Absent technical-spec companion | `analysis/response-cache-feature-identity/technical-spec.md` | Analysis producer | Optional execution source; absent at authoring and not created by this topic. |
| Topic plan | `plan/response-cache-feature-identity/response-cache-feature-identity.plan.md` | Planning actor | Revised canonical execution contract and locked Python decisions. |
| Topic behavior specification | `plan/response-cache-feature-identity/response-cache-feature-identity.spec.md` | Planning actor | Revised non-trivial behavior contract for fresh RED tests and review. |
| Topic step tracker | `plan/response-cache-feature-identity/response-cache-feature-identity.step.md` | Planning actor / Implementer | Reset workflow-stage and implementation-progress record for this replan. |
| Fresh plan review | `plan/response-cache-feature-identity/response-cache-feature-identity.plan-review.json` | Reviewer | Fresh single-object planning verdict for this revised contract; old content is historical only. |
| Fresh human check | `plan/response-cache-feature-identity/response-cache-feature-identity.human-check.json` | Human | Fresh explicit clearance after the fresh approved plan review; old content is historical only. |
| Fresh RED-test evidence | `plan/response-cache-feature-identity/response-cache-feature-identity.red-tests.yaml` | Tester | Fresh pre-implementation RED evidence mapped to this revised spec; old content is historical only. |
| Fresh implementation review | `plan/response-cache-feature-identity/response-cache-feature-identity.implementation-review.yaml` | Independent Reviewer | Fresh plan-conformance evidence required before PR routing; old content is historical only. |
| Internal concrete hasher | `src/async_model_gateway/response_cache/_canonical_feature_hasher.py` | Implementer | Sole response-cache-internal `FeatureHasher` implementation. |
| Focused concrete-hasher tests | `tests/response_cache/test_canonical_feature_hasher.py` | Tester | Direct-import identity, complete-pair duplicate-base-key ordering, strict-encoding failure, factory integration, and non-interference coverage. |

Artifact path notes:

- This topic does not modify `README.md`, `VERSION`, `.github/copilot-instructions.md`, `pyproject.toml`, `uv.lock`, or any existing source/test file other than the two declared implementation paths.
- Listed paths are exhaustive. Work outside them is plan misalignment, not an implementation detail; stop and replan before changing it.

## Implementation Steps

1. After fresh plan review and fresh human check, revise direct-import RED tests in `tests/response_cache/test_canonical_feature_hasher.py` and record fresh `plan/response-cache-feature-identity/response-cache-feature-identity.red-tests.yaml` evidence. Cover base-`str` identity material for key/value subclasses that override `__str__`, safe built-in ordering under custom comparison subclasses, a mapping-like duplicate-base-key regression whose `.items()` emits equal base keys with different values in opposite orders, direct hasher and factory integration equality for those orders, strict UTF-8 rejection for an unpaired surrogate, direct `TypeError` whose `__cause__` is the original `UnicodeEncodeError`, and factory propagation of that same error policy without a key.
2. Modify `src/async_model_gateway/response_cache/_canonical_feature_hasher.py` only: after `isinstance` validation, obtain accepted subclass material with `str.__str__(key)` and `str.__str__(value)`, sort every resulting base-string pair lexicographically as a complete `(base_key, base_value)` tuple, retain the locked JSON representation, and translate only the UTF-8 `UnicodeEncodeError` into chained `TypeError`. Do not reject or deduplicate duplicate base keys, and do not modify the factory, port, exports, or any other behavior owner.
3. Make the fresh RED tests green and run `uv run pytest tests/response_cache/test_canonical_feature_hasher.py -v --no-cov`, `uv run pytest`, `uv run ruff check src tests plan/response-cache-feature-identity`, `uv run pyright`, and `uv run pre-commit run --all-files`. Record implementation progress only in `plan/response-cache-feature-identity/response-cache-feature-identity.step.md`; leave fresh reviewer and human artifacts to their independent owners.

## Validation / Acceptance Checks

- The plan preserves canonical sections/order, exact role-labeled paths, canonical transitions, the analysis warning, and the single JSON-object reviewer handoff required by `plan/topic-plan-contract.md` and `plan/agent-handoff-workflow.md`.
- `CanonicalFeatureHasher.hash_features` accepts `Mapping[str, str]`, returns a lowercase 64-character SHA-256 hex digest, preserves the frozen empty digest, and derives material for a valid string subclass through the base `str` implementation without calling the subclass's `__str__`.
- Two equivalent mappings containing `str` subclasses with hostile `__str__` or `__lt__` overrides have the same digest as equivalent built-in strings; distinct base-string material remains distinct even when the subclass override would present identical text.
- A mapping-like input that emits two pairs with equal base keys but different base values has the same direct-hasher and factory-produced digest in either emitted order, because canonicalization sorts the complete `(base_key, base_value)` tuples. It remains valid input and is not rejected or deduplicated.
- A surrogate-containing accepted `str` whose canonical JSON cannot strictly UTF-8 encode raises `TypeError`; its direct `__cause__` is the original `UnicodeEncodeError`. Valid Unicode remains raw material under `ensure_ascii=False` and no representation setting changes.
- Factory use with the concrete hasher raises the same `TypeError` contract with chained `UnicodeEncodeError`, returns no `ResponseCacheKey`, and demonstrates no factory-side catch, translation, or fallback.
- Non-`str` keys and values continue to raise `TypeError` before a digest or cache key is produced; no coercion/fallback happens.
- Package root and `ports` exports, the `FeatureHasher` port, factory interface/implementation, payload-hash owner, key fields, TTL/freshness/store behavior, dependencies, version metadata, docs, and orchestrator behavior remain unchanged.
- Fresh RED evidence is captured after the new planning gates and before production correction. Fresh independent implementation-review evidence records conformance before PR routing; all focused tests use direct imports and no dynamic module loading. Full validation passes the configured coverage gate.

### TestCase

1. `test_hash_features_uses_base_string_material_for_str_subclasses_with_overridden_str` proves hostile key/value `__str__` overrides neither change nor collapse identity relative to built-in strings.
2. `test_hash_features_normalizes_string_subclasses_before_sorting` retains the reverse-insertion/custom-`__lt__` regression and proves sorting uses built-in string material.
3. A new direct-hasher duplicate-base-key regression uses a mapping-like `.items()` source with two equal base keys and different values in opposite emitted orders, then proves full `(base_key, base_value)` ordering produces one digest without rejection or deduplication.
4. A new factory-integration duplicate-base-key regression proves `ResponseCacheKeyFactory(CanonicalFeatureHasher())` preserves the same deterministic feature digest in either emitted order.
5. `test_hash_features_rejects_unpaired_surrogate_as_chained_type_error` asserts direct fail-closed `TypeError` and its `UnicodeEncodeError` cause.
6. `test_factory_propagates_unpaired_surrogate_type_error_without_constructing_a_key` asserts the unchanged factory exposes the chained error contract and returns no key.
7. Existing golden digest, insertion-order, raw Unicode/whitespace/case, changed key/value, non-`str` `TypeError`, internal-only export, and factory injection tests remain as backward-compatibility regression coverage.
8. The full response-cache regression suite preserves package-surface, factory delegation, payload-hash isolation, TTL/freshness/store, and key/entry contracts without modifying their tests.

Validation commands:

```text
uv run pytest tests/response_cache/test_canonical_feature_hasher.py -v --no-cov
uv run pytest
uv run ruff check src tests plan/response-cache-feature-identity
uv run pyright
uv run pre-commit run --all-files
```

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
- After merge, do not create a version bump, release note, tag, migration, or stable-library publication for this internal capability.

## Open Questions / Unresolved Items

- None. The optional analysis layer is absent but explicitly warned and superseded by the human override; it does not leave an executable implementation decision unresolved.
