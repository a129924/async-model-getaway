# local-response-generation-with-cache-reuse Specification

## Acceptance Criteria

1. `async_model_gateway.local_response` exports exactly `LocalResponseGateway` and
   `LocalResponseRequest`; root package exports stay unchanged.
2. `LocalResponseRequest` is frozen and slotted, with the six locked field names
   and annotations: `model_name`, `model_source_kind`, `model_payload`, `features`,
   `model_artifact`, and `invocation`. `request.py` defines the non-exported
   `ModelPayloadValue: TypeAlias = None | bool | int | float | str |
   list["ModelPayloadValue"] | dict[str, "ModelPayloadValue"]`; neither that alias
   nor the private callable protocols is re-exported.
3. `gateway.py` defines `_FeatureHasher.__call__(features: Mapping[str, str]) ->
   str`, `_OnnxResultConverter.__call__(result: list[object]) -> str`, and async
   `_LocalResponseExecutor.__call__(artifact: ModelArtifact, invocation:
   dict[str, object]) -> list[object]`. `LocalResponseGateway` has keyword-only
   `registry`, `response_cache`, `hash_features`, `convert_onnx_result`, and
   `executor: _LocalResponseExecutor | None = None`; `None` binds the private
   `_local_onnx_executor.py` default adapter, which only delegates to existing
   composition with no export or lifecycle change.
4. `generate(*, request)` rejects non-local source and non-ONNX artifact before
   registry, hasher, cache, executor, or converter observation, using
   `NotImplementedError`.
5. For supported input, it awaits registry freshness, derives feature hash, builds
   `CacheKey("local-response-v1", freshness.entry.payload_hash, feature_hash)`,
   then calls `lookup(..., context=object())` in that exact order. The lookup
   sentinel is private, fresh at the call site, is not request data, and does not
   enter identity or a record.
6. `CacheHit(value=value)` returns `value` immediately. `CacheMiss()` performs one
   direct executor await, one converter call, one remember call, then returns the
   converted response for `Remembered`, `Skipped`, or `Failed`. That remember call
   receives another call-site-created `context=object()` which is distinct from
   the lookup sentinel; neither sentinel is retained, compared, exported, or
   reused.
7. Lookup outcomes and remember outcomes use the locked exhaustive `match/case`
   shapes with `assert_never` fallback; gateway code adds no broad cache catch.
8. Registry, hasher, executor, converter, unexpected defects, and cancellation
   propagate unchanged. No remember occurs after any pre-remember failure.
9. Concurrent same-key misses are independent direct-await calls; no singleflight,
   lock, task, retry, timeout, or background policy is added.

## Behavioral Scenarios

### Scenario 1: cache hit returns before local execution

- **Given**: a local ONNX request, registry freshness result, feature hash, and a
  `CacheHit` from the response-cache facade.
- **When**: `LocalResponseGateway.generate()` is awaited.
- **Then**: it returns the hit string after registry/hash/lookup, where lookup
  received one fresh private `object()` context; neither executor, converter, nor
  remember is invoked.

### Scenario 2: cache miss generates and records a response

- **Given**: a local ONNX request and a `CacheMiss` from lookup.
- **When**: `generate()` is awaited with recording collaborators.
- **Then**: calls occur in Registry -> feature hash -> lookup -> executor ->
  converter -> remember order, the key has namespace `local-response-v1`, and the
  converted string is returned for each supported remember outcome. Fake cache
  observations prove that lookup and remember each received a fresh call-site
  `object()` context, that the two are identity-distinct, and that neither is the
  request or one of its fields.

### Scenario 3: supported concurrent misses do not share execution

- **Given**: two concurrent equivalent local ONNX requests and lookup misses.
- **When**: both `generate()` calls are awaited.
- **Then**: each call uses its own direct awaited executor/convert/remember path;
  neither call joins, locks, cancels, or retries the other.

### Scenario 4: default execution seam preserves existing ownership

- **Given**: a gateway created without the optional executor seam.
- **When**: a local ONNX cache miss reaches execution.
- **Then**: `_local_onnx_executor.py`'s private adapter delegates only to existing
  local runtime composition; no pool/executor/composition public export or
  lifecycle behavior is introduced.

## Error / Edge Cases

- `ModelSourceKind.REMOTE` fails closed with `NotImplementedError` before every
  collaborator call.
- `LoaderFamily.PICKLE` and `LoaderFamily.TORCH` fail closed with
  `NotImplementedError` before every collaborator call.
- Existing cache lookup operational failures remain facade-produced `CacheMiss`;
  they are not recaught at the gateway.
- `Remembered`, `Skipped`, and `Failed` are fail-open write results and return the
  converted response; an unexpected union member reaches `assert_never`.
- Registry/hasher/executor/converter errors and `CancelledError` propagate by
  identity and leave no later collaborator call or cache write.
- Static type validation rejects a widened/`Any` public request or callable seam;
  the strict witness uses `from async_model_gateway.local_response import
  LocalResponseGateway, LocalResponseRequest` and supplies typed callable
  collaborators matching the frozen constructor while leaving private protocols
  and `ModelPayloadValue` non-exported. Tests must use static imports and cannot
  use dynamic module loading.
