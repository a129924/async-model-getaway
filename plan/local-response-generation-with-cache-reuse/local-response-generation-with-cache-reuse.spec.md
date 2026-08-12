# local-response-generation-with-cache-reuse Specification

## Acceptance Criteria

1. `gateway.py` defines the private, non-exported `_CacheKeyDeriver` protocol with
   keyword-only `model_name: str`, `model_payload_hash: str`,
   `features: Mapping[str, str]`, `model_artifact: ModelArtifact`, and
   `invocation: dict[str, object]` inputs, returning `CacheKey`.
2. `LocalResponseGateway.__init__` has keyword-only `registry`, `response_cache`,
   `cache_key_deriver`, `convert_onnx_result`, and optional `executor` parameters;
   it no longer accepts or retains `hash_features`. Package exports, request DTO,
   converter, executor, and default adapter contracts remain unchanged.
3. After the established local/ONNX guards and registry freshness, `generate()`
   calls the deriver with request model name, registry payload hash, features,
   artifact, and invocation. The returned `CacheKey` is handed unchanged to
   `lookup` and, on miss, `remember`.
4. The test deriver proves a changed invocation produces a different key and no
   cache cross-hit; it separately proves a changed model name produces a different
   key and no cache cross-hit. The artifact is an observed deriver identity input.
5. The gateway owns no canonicalization, hash, collision control, or namespace
   decision. Raw prompts, model names, and artifact paths appear neither in
   cache-facing namespace, context, nor record inputs.
6. Existing cache-context policy remains: lookup receives one fresh `object()`;
   miss remember receives another fresh `object()`; neither is retained, compared,
   exported, or request data.
7. Existing `CacheHit`/`CacheMiss` and `Remembered`/`Skipped`/`Failed` exhaustive
   `match/case` behavior, fail-open writes, direct await, and independent misses
   remain unchanged.
8. A deriver error propagates unchanged before lookup and causes no lookup,
   execution, converter call, or remember. Existing registry/executor/converter
   failures and cancellation propagation remain unchanged.
9. `ModelRegistry`, `ResponseCache`, `CacheKey`, `ModelPayloadHasher`, and
   `ModelArtifact` remain ReadOnly; no release/doc/version work is introduced.

## Behavioral Scenarios

### Scenario 1: opaque key supports a cache hit

- **Given**: a supported request, registry freshness, an injected deriver, and a
  `CacheHit`.
- **When**: `generate()` is awaited.
- **Then**: it calls Registry -> deriver -> lookup, returns the hit, and does not
  execute, convert, or remember; the lookup receives the deriver's same key and
  a fresh private context.

### Scenario 2: miss generates with unchanged key handoff

- **Given**: a supported request and `CacheMiss`.
- **When**: `generate()` is awaited.
- **Then**: it calls Registry -> deriver -> lookup -> executor -> converter ->
  remember -> return, and lookup/remember receive the exact same key object/value
  supplied by the deriver.

### Scenario 3: identity separation prevents cross-hit

- **Given**: two otherwise equivalent requests that differ only in invocation,
  and a second pair that differ only in model name.
- **When**: each pair is generated through a deriver whose canonical identity
  includes all five locked inputs.
- **Then**: each changed input derives a distinct key, lookup does not return the
  other request's cached response, and the artifact is observed by the deriver.

### Scenario 4: deriver failure stops before cache use

- **Given**: a supported request and a deriver that raises a sentinel exception.
- **When**: `generate()` is awaited.
- **Then**: the same exception propagates after registry freshness, and lookup,
  executor, converter, and remember are not called.

## Error / Edge Cases

- Non-local source and non-ONNX artifact still raise `NotImplementedError` before
  registry, deriver, cache, executor, or converter observation.
- The gateway does not catch deriver exceptions or cancellation and does not
  remember after any pre-remember failure.
- `Remembered`, `Skipped`, and `Failed` still return converted output; unexpected
  closed outcomes reach `assert_never`.
- Tests use static imports only; dynamic module loading is not authorized.
