Analysis-layer routing: incomplete optional-analysis mode. Semantic warning: neither `analysis/response-cache-feature-identity/requirements.md` nor `analysis/response-cache-feature-identity/technical-spec.md` exists. The explicit human override recorded for this topic is therefore the execution baseline; this plan does not claim strict analysis mode. If either analysis artifact is introduced and conflicts with this locked baseline before implementation, return to `spec-and-plan-finalization`.

# response-cache-feature-identity

## Goal / Outcome

- Add one response-cache-internal concrete `FeatureHasher` that deterministically derives a lowercase SHA-256 feature identity from `Mapping[str, str]`, and can be injected into the existing `ResponseCacheKeyFactory` without changing its contract.
- When complete, equivalent key/value collections produce the same `feature_hash` regardless of insertion order, while representative key or value differences remain distinct and invalid runtime inputs fail closed.

## Scope

- **In scope**:
  - Add `CanonicalFeatureHasher` in the response-cache-internal module `src/async_model_gateway/response_cache/_canonical_feature_hasher.py`.
  - Add focused direct-import tests in `tests/response_cache/test_canonical_feature_hasher.py`, including factory injection and non-interference assertions.
  - Create this topic's plan, non-trivial behavior specification, and step tracker; declare the later reviewer, human-gate, RED-test, and implementation-review artifacts.

- **Out of scope**:
  - Changing the `FeatureHasher` port, `ResponseCacheKey`, `ResponseCacheKeyFactory`, their signatures, or the `ResponseCacheKey` field set.
  - Changing model-payload canonicalization or hash ownership, TTL/freshness/store behavior, persistence, eviction, settings, orchestrator flow, or response generation.
  - Adding package-root or `ports` re-exports, hash versioning/rotation/migration, dependencies, release/version metadata, or documentation claims beyond the already-true internal implementation boundary.

### Executable file inventory

| Classification | Exact paths | Contract |
| --- | --- | --- |
| Written now | `plan/response-cache-feature-identity/response-cache-feature-identity.plan.md`; `plan/response-cache-feature-identity/response-cache-feature-identity.spec.md`; `plan/response-cache-feature-identity/response-cache-feature-identity.step.md` | Planning actor creates only these repo-visible planning artifacts in this pass. |
| Written during implementation | `src/async_model_gateway/response_cache/_canonical_feature_hasher.py`; `tests/response_cache/test_canonical_feature_hasher.py` | Implementer/tester adds the one internal concrete hasher and its focused direct-import behavior coverage. |
| Planned future gate artifacts | `plan/response-cache-feature-identity/response-cache-feature-identity.plan-review.json`; `plan/response-cache-feature-identity/response-cache-feature-identity.human-check.json`; `plan/response-cache-feature-identity/response-cache-feature-identity.red-tests.yaml`; `plan/response-cache-feature-identity/response-cache-feature-identity.implementation-review.yaml` | Respectively Reviewer, Human, Tester, and Reviewer create these only at their workflow gates; this planning pass does not prefill them. |
| ReadOnly / preserve-and-validate | `README.md`; `docs/architecture.md`; `docs/specs/response-cache-boundary.md`; `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__version__.py`; `src/async_model_gateway/response_cache/__init__.py`; `src/async_model_gateway/response_cache/cache.py`; `src/async_model_gateway/response_cache/entry.py`; `src/async_model_gateway/response_cache/freshness_policy.py`; `src/async_model_gateway/response_cache/key.py`; `src/async_model_gateway/response_cache/key_factory.py`; `src/async_model_gateway/response_cache/ports/__init__.py`; `src/async_model_gateway/response_cache/ports/feature_hasher.py`; `src/async_model_gateway/response_cache/ports/store.py`; `src/async_model_gateway/response_cache/ttl_freshness_policy.py`; `tests/response_cache/test_cache.py`; `tests/response_cache/test_entry.py`; `tests/response_cache/test_in_memory_store.py`; `tests/response_cache/test_key.py`; `tests/response_cache/test_key_factory.py`; `tests/response_cache/test_response_cache_freshness_policy.py`; `tests/response_cache/test_response_cache_package_surface.py`; `tests/response_cache/test_ttl_freshness_policy.py` | Existing public surface, port, key/factory delegation, upstream payload identity, cache/store behavior, version/dependency metadata, documentation, and regression coverage must not drift. |
| Modify | None | This topic has no existing source, test, document, contract, export, or metadata modify path. |
| Deleted | None | This topic deletes no file, API, behavior, or planning artifact. |
| Out-of-scope / no path authorization | No additional repository paths | Any new production, test, document, public-surface, TTL/store, payload, or orchestrator path requires replanning. |

## Locked Decisions

- D1 verdict: `non-trivial` — the topic adds a new internal identity owner, a behavior contract, focused tests, and Python workflow evidence while preserving an existing injected-port boundary.
- `CanonicalFeatureHasher` is internal-only: it lives only at `async_model_gateway.response_cache._canonical_feature_hasher`, implements the existing `FeatureHasher.hash_features(features: Mapping[str, str]) -> str` method, and is not re-exported by `async_model_gateway.response_cache` or `async_model_gateway.response_cache.ports`.
- Canonical representation is frozen as follows: validate every mapping key and value with `isinstance(..., str)`; sort entries by their unmodified string key using Python's normal string ordering; serialize the sorted sequence of two-string pairs with `json.dumps(..., ensure_ascii=False, separators=(",", ":"))`; encode that exact serialized text as UTF-8; return `hashlib.sha256(...).hexdigest()`.
- The digest is exactly a 64-character lowercase hexadecimal SHA-256 digest. The canonical representation of the empty mapping is `[]`, whose required golden digest is `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- Validation precedes sorting and serialization. A non-`str` key or value raises `TypeError`; implementation must not call `str(...)`, trim whitespace, casefold, normalize Unicode, insert defaults, swallow the exception, or return a cache-miss substitute.
- `ResponseCacheKeyFactory` remains a pure delegate: it receives literal `namespace` and upstream `model_payload_hash`, passes the original mapping to the injected hasher, and lets the hasher failure propagate before it can construct a `ResponseCacheKey`.
- The topic adopts the Python planning extension. RED test authoring is the first `implement-plan` subphase; `.spec.md`, `.step.md`, `.red-tests.yaml`, and `.implementation-review.yaml` are required evidence before PR routing.
- Async-planning status: exempt — cite exemption evidence: the only new behavior is synchronous, in-memory validation, sorting, serialization, and hashing; it adds no async boundary, lifecycle ownership, concurrency, timeout, cancellation, retry, or external I/O.
- Stable-library intent is explicitly absent. `README.md`, version metadata, and release timing are not changed; the conditional `## Stable library metadata` section is intentionally absent and the conditional `release` workflow does not apply.

## Boundaries / Exclusions

- The planning actor writes only the three current planning artifacts; it does not implement source/tests, create reviewer verdicts, or close human gates.
- The implementer/tester may write only the declared internal hasher and focused test, plus their declared workflow evidence. A need to edit any ReadOnly path, use a new import surface, or create another module/test path returns to `spec-and-plan-finalization`.
- Tests use ordinary direct imports only. Dynamic module loading is not authorized.
- Reviewer independently writes plan-review and implementation-review verdicts; Human independently writes human-check and human-merge gate evidence. Main Agent owns worktree, branch, publish/PR routing, and post-merge orchestration; none of that work belongs in creator steps.
- Representation choices outside the locked sorted pair-list JSON/UTF-8/SHA-256 form, including delimiter schemes, normalization, generic serializers, and versioning, belong to another topic.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Plan-authoring completeness**: `INCOMPLETE` only for the two explicitly absent optional analysis companions named in the routing warning. The human override and all executable implementation decisions are otherwise frozen for independent review.
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`; stop at `merged`. No conditional `release` workflow applies.
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

- `approved` requires a Reviewer-owned `plan/response-cache-feature-identity/response-cache-feature-identity.plan-review.json` with verdict `approved` and a Human-owned `plan/response-cache-feature-identity/response-cache-feature-identity.human-check.json` that explicitly clears the plan for `implement-plan`.
- The absent analysis files remain a semantic warning. If reviewer or human judges either is required, route to `creator-in-progress`; do not infer strict analysis mode.
- Scope, path, public-contract, canonical-representation, error-policy, or release-intent drift returns to `spec-and-plan-finalization`; PR discussion cannot replace the planning or human-check gates.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Absent requirements companion | `analysis/response-cache-feature-identity/requirements.md` | Analysis producer | Optional business-intent guardrail; absent at authoring and not created by this topic. |
| Absent technical-spec companion | `analysis/response-cache-feature-identity/technical-spec.md` | Analysis producer | Optional execution source; absent at authoring and not created by this topic. |
| Topic plan | `plan/response-cache-feature-identity/response-cache-feature-identity.plan.md` | Planning actor | Canonical execution contract and locked Python implementation decisions. |
| Topic behavior specification | `plan/response-cache-feature-identity/response-cache-feature-identity.spec.md` | Planning actor | Required non-trivial behavior contract for RED tests and review. |
| Topic step tracker | `plan/response-cache-feature-identity/response-cache-feature-identity.step.md` | Implementer | Workflow-stage and implementation-progress record. |
| Plan review | `plan/response-cache-feature-identity/response-cache-feature-identity.plan-review.json` | Reviewer | Single-object planning verdict. |
| Human check | `plan/response-cache-feature-identity/response-cache-feature-identity.human-check.json` | Human | Explicit repo-visible clearance after approved plan review. |
| RED-test evidence | `plan/response-cache-feature-identity/response-cache-feature-identity.red-tests.yaml` | Tester | Pre-implementation RED evidence, test-to-requirement mapping, and static-import confirmation. |
| Implementation review | `plan/response-cache-feature-identity/response-cache-feature-identity.implementation-review.yaml` | Reviewer | Plan-conformance evidence required before PR routing. |
| Internal concrete hasher | `src/async_model_gateway/response_cache/_canonical_feature_hasher.py` | Implementer | Sole response-cache-internal `FeatureHasher` implementation. |
| Focused concrete-hasher tests | `tests/response_cache/test_canonical_feature_hasher.py` | Tester | Direct-import identity, failure, factory-injection, and non-interference coverage. |

Artifact path notes:

- This topic does not modify `README.md`, `VERSION`, `.github/copilot-instructions.md`, `pyproject.toml`, `uv.lock`, or any existing source/test file.
- Listed paths are exhaustive. Work outside them is plan misalignment, not an implementation detail; stop and replan before changing it.

## Implementation Steps

1. As the first `implement-plan` Python subphase, add direct-import RED tests in `tests/response_cache/test_canonical_feature_hasher.py` and record `plan/response-cache-feature-identity/response-cache-feature-identity.red-tests.yaml`. Cover the frozen canonical JSON pair-list form, fixed UTF-8/SHA-256 lowercase digest, insertion-order independence, value/key distinction, non-normalization, `TypeError` failures, and factory injection without changing existing regression tests.
2. Add `src/async_model_gateway/response_cache/_canonical_feature_hasher.py` with internal `CanonicalFeatureHasher(FeatureHasher)`. Validate runtime keys and values before sorting, serialize the sorted two-string pair list using the locked JSON settings, UTF-8 encode it, and return `sha256(...).hexdigest()`; do not add exports, fallback behavior, or other interfaces.
3. Make the RED tests green and run the declared focused, full-suite, lint, type, and pre-commit validation. Update `plan/response-cache-feature-identity/response-cache-feature-identity.step.md` only for creator-owned completed work; leave reviewer and human artifacts to their owners.

## Validation / Acceptance Checks

- The plan preserves canonical sections/order, exact role-labeled paths, canonical transitions, the analysis warning, and the single JSON-object reviewer handoff required by `plan/topic-plan-contract.md` and `plan/agent-handoff-workflow.md`.
- `CanonicalFeatureHasher.hash_features` accepts `Mapping[str, str]`, returns a lowercase 64-character SHA-256 hex digest, and makes `{"mode": "chat", "safety": "strict"}` match the digest for the same collection inserted in reverse order.
- The empty mapping produces the frozen golden digest `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`, proving the exact `[]` canonical representation rather than an accidental delimiter or serializer variant.
- A representative changed key and a representative changed value each produce a digest distinct from the baseline; whitespace, case, and Unicode differences are retained as raw identity material rather than normalized.
- Non-`str` mapping keys and values raise `TypeError`; no digest/cache key is produced, no coercion/fallback happens, and factory construction is not reached when the hasher fails.
- Injection into the unchanged factory preserves literal namespace and upstream `model_payload_hash`, uses the concrete hasher digest, and keeps the existing factory's mapping pass-through and failure propagation contract intact.
- Package root and `ports` exports, the `FeatureHasher` port, payload-hash owner, key fields, TTL/freshness/store behavior, dependencies, version metadata, docs, and orchestrator behavior remain unchanged.
- RED evidence is captured before production implementation; focused tests use direct imports and no dynamic module loading. Full validation passes the configured coverage gate.

### TestCase

1. `test_hash_features_is_insertion_order_independent` hashes two equivalent mappings inserted in opposite orders and asserts one digest.
2. `test_hash_features_matches_golden_empty_mapping_digest` asserts the frozen SHA-256 digest for canonical `[]`.
3. `test_hash_features_distinguishes_representative_key_and_value_changes` asserts distinct digests for one changed key and one changed value.
4. `test_hash_features_preserves_raw_whitespace_case_and_unicode_material` asserts raw-string differences are not normalized into a shared digest.
5. `test_hash_features_rejects_non_string_keys_or_values` parametrizes invalid keys and values, expects `TypeError`, and observes no digest.
6. `test_factory_uses_concrete_hasher_without_rewriting_identity_material` asserts the unchanged factory retains literal namespace/upstream payload hash and uses the concrete digest; its invalid-input companion asserts `TypeError` propagates and no key returns.
7. The full response-cache regression suite preserves package-surface, factory delegation, payload-hash isolation, TTL/freshness/store, and key/entry contracts without modifying their tests.

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
