# Strict typing reference

## Baseline
- Treat `pyright --strict` as the default compatibility target.
- Annotate public function and method parameters and return values.
- For Python 3.10+, use PEP 604 unions such as `User | None`; for Python 3.8/3.9 compatibility, use `Optional[User]` or `Union[...]`.
- For Python 3.9+, use built-in generics such as `list[str]` and `dict[str, int]`; for Python 3.8 compatibility, use `List[str]` and `Dict[str, int]`.
- For Python 3.10+, use `TypeAlias` for repeated or complex types; for older baselines, use `typing_extensions.TypeAlias` when available or keep the alias pattern explicit with compatible `typing` spellings.
- Annotate empty collections and mutable attributes when inference would be ambiguous.

## Preferred patterns
- Use `Literal` for small closed string choices.
- Narrow types with explicit checks before branching.
- Keep return types stable; prefer one clear output shape per function.

## `object` decision order
- Follow this preference order: `repo-owned type -> explicit refinement / alias -> boundary-only object`.
- Reuse an existing repo-owned alias, value type, model, protocol, or other concrete domain type for ordinary parameters, returns, and service-layer contracts.
- If no reusable repo-owned type exists yet, refine the contract explicitly or introduce a named alias before considering `object`.
- Do not use `object` to avoid understanding the domain model or to make strict type checking feel easier.

## Allowed `object` boundaries
- `object` is allowed only at true untrusted boundaries or narrowing-helper entry points.
- Keep the allowed list narrow: decoder output, validator input, type-guard input, and similar one-step narrowing helpers whose next action is to recover a precise type.
- Narrow accepted `object` values back to a precise repo-owned or explicitly refined type before normal business logic, storage, or public return paths.
- If a stronger repo-owned or domain contract already exists for the position, replacing it with `object` is invalid.

## Justification requirement for `object`
- Every surviving `object` annotation must include a short justification naming the boundary or narrowing role it serves, such as `boundary: JSON decoder output` or `narrowing helper input for TypeGuard[UserPayload]`.
- Missing justification is a review failure, not an optional style issue.
- `easier type checking`, `not sure of the type`, `avoid importing the model`, or `we will refine later` are not acceptable justifications.
- If the task turns into choosing whether the contract should be an `Enum`, `dataclass`, `ABC`, or `Protocol`, redirect to `python-model-selection` instead of leaving the site as `object`.

## Restricted escape hatches
- `Any`: only at dynamic boundaries or third-party edges; convert to precise types quickly.
- `cast(...)`: only after a runtime guarantee or trusted narrowing step.
- Ignore comments: only for isolated tool limitations, with the smallest possible scope and a justification note.
- Avoid file-wide suppression when a local fix is possible.

## Avoid
- Untyped public APIs.
- Legacy spellings like `Optional[X]`, `Union[A, B]`, `List[X]`, or `Dict[K, V]` when the supported Python version already allows modern syntax.
- Routine `cast` or ignore comments as a replacement for modeling the type correctly.
- Replacing a known repo-owned or domain type with `object` outside a true untrusted boundary or narrowing-helper input.
- Return signatures that bounce between unrelated types.
