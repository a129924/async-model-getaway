# prediction-workflow-cache-identity Specification

## Acceptance Criteria

1. A reader can locate one detailed target workflow that separates canonical
   input, identity derivation, cache reuse, execution, result projection, and
   result representation.
2. Target `CacheKey` identity has exactly namespace, model identity hash,
   feature hash, and prediction-input hash; it does not reuse the current
   three-field key contract by implication.
3. The target workflow makes `prediction_input` JSON-like, deeply snapshotted
   before the first await, and shared by identity derivation and execution.
4. `ResultCodec` is application-layer only; `ResponseCache` continues to own
   cache `str` values and `CacheCodec` continues to own `str ↔ bytes`.
5. Codec compatibility contributes to the namespace through the canonical hash
   of predictor base namespace and codec token. Codec encode/decode errors
   propagate without a fallback execution or write.
6. Every changed document states whether it describes current implementation or
   target architecture. `LocalResponseGateway` remains a transition projection.

## Behavioral Scenarios

### Cache hit

- Given a target-compatible key and a cache hit containing a `str` value,
- when `ResultCodec.decode` succeeds,
- then the application result, such as a `DataFrame`, is returned without model
  execution.

### Cache miss

- Given a cache miss,
- when execution and predictor result projection succeed,
- then `ResultCodec.encode` creates the cache `str`, `ResponseCache.remember`
  receives that string, and the application result is returned.

### Identity or codec failure

- Given a failed input projection, canonicalization, hash, codec decode, or
  codec encode,
- then the exact failure propagates and the workflow does not manufacture a
  fallback cache key, execution, or cache write.

## Deferred Items

- Concrete `DataFrame`/row-Mapping codecs, serialization formats, CAS/pickle,
  Python signatures, and the implementation/migration of the target key.
