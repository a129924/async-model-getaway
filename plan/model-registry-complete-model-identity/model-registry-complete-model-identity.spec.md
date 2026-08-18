# model-registry-complete-model-identity Specification

## Acceptance Criteria

1. `async_model_gateway.model_registry.model_identity` exports
   `ModelIdentityHasher`; the registry root still exports only `ModelRegistry`.
2. The static method uses exactly the ordered literal-label frames
   `model_name`, `model_source_kind`, `model_payload_hash` and SHA-256 hex.
3. `("demo", ModelSourceKind.LOCAL, "a" * 64)` returns
   `177653000e2e441856c1d22e3b2b0d02a1ba7c384f1029fb5b5c3464663b72b4`.
4. Name/hash are non-empty `str`; invalid types raise `TypeError`, empty values
   raise `ValueError`; only the two existing source-kind enum members are valid.
5. The entry property is read-only/derived and absent from dataclass fields,
   stored state, and constructor parameters.
6. Registry candidate identity is read before policy. Its failure propagates and
   prevents policy/upsert without changing the preceding lookup.
7. Result/CacheKey fields, lookup identity, payload hashing, public signatures,
   decisions, and upsert condition stay unchanged.
8. Docs claim only registry identity capability, never cache migration or flow.
9. `tests/model_registry/model_identity/__init__.py` is the sole added test
   marker, so full pytest collection includes both canonical-hash test modules
   without import mismatch; pytest config/import mode and production contracts
   remain unchanged.

## Behavioral Scenarios

### Scenario 1: Deterministic complete-model identity

- **Given**: `model_name="demo"`, `ModelSourceKind.LOCAL`, and `"a" * 64`
- **When**: the static method or the entry property derives identity
- **Then**: it returns the exact locked golden digest on every invocation

### Scenario 2: Literal framed UTF-8 material

- **Given**: valid Unicode or unframed-concatenation-sensitive identity values
- **When**: identity is derived
- **Then**: each labeled frame uses UTF-8 byte length and literal bytes
- **Then**: no JSON, normalization, coercion, or reordering occurs

### Scenario 3: Existing freshness path with enforced identity

- **Given**: first-seen, same-payload, and changed-payload registry calls
- **When**: each candidate property is read before policy
- **Then**: results remain first-seen, unchanged, changed; writes remain only
  first-seen/changed

### Scenario 4: Invalid identity stops policy and write

- **Given**: invalid derived identity material
- **When**: `resolve_freshness()` reads the property
- **Then**: the locked error propagates and neither policy nor upsert is called

### Scenario 5: Same-basename test modules collect safely

- **Given**: the existing payload and new identity test modules are both named
  `test_canonical_hash.py`
- **When**: pytest performs full collection
- **Then**: the sole `model_identity/__init__.py` marker gives the new module a
  distinct import path and both modules collect without import mismatch

## Error / Edge Cases

- Non-strings and raw `"local"` are not coerced; empty name/hash is rejected.
- One-field changes alter the digest; Unicode equivalent forms remain distinct
  when their literal UTF-8 bytes differ.
- The property cannot be assigned and does not alter equality/constructor shape.
- Existing lookup may occur before identity validation; the no-policy/no-upsert
  guarantee begins after candidate construction.
- No root export, result field, or CacheKey field may be added.
- Do not solve collection by changing pytest configuration/import mode, adding
  other markers, or dynamically loading modules.
- After this plan amendment, the current plan-review and human-check contents
  are stale. The reviewer overwrites the declared review path with current
  evidence; only then may the human gate owner overwrite the declared
  human-check path. Neither action is a production-contract change.
