# Python API-signature examples

Use these examples after `SKILL.md` narrows the task to public function and method signatures.

## Mutable defaults

### Ban mutable shared defaults
```py
def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    current_tags = [] if tags is None else list(tags)
    current_tags.append(tag)
    return current_tags
```

- `None` is the missing signal.
- A fresh list is created per call.
- The default state is not shared across callers.

### Avoid mutable default values
```py
def add_tag(tag: str, tags: list[str] = []) -> list[str]:
    tags.append(tag)
    return tags
```

- This leaks state across calls.
- Public APIs should not hide shared mutable defaults in their signature.

### Safe immutable defaults are acceptable
```py
from enum import Enum


class UploadMode(Enum):
    STANDARD = "standard"
    RETRY = "retry"


def plan_upload(
    *,
    mode: UploadMode = UploadMode.STANDARD,
    labels: tuple[str, ...] = (),
    retries: int = 0,
) -> tuple[UploadMode, tuple[str, ...], int]:
    return mode, labels, retries
```

- Immutable defaults such as enum members, tuples, and numbers are safe.
- Use immutable defaults when they already match the contract.

## `None` vs explicit sentinel

### Default to `None` when `None` is not a legal business value
```py
def create_user(*, roles: list[str] | None = None) -> list[str]:
    return [] if roles is None else list(roles)
```

- `None` is enough here because callers do not need to pass `None` as a real value.

### Use a private sentinel when `None` is a real input
```py
_NOT_SET = object()


def update_display_name(*, display_name: str | None | object = _NOT_SET) -> str:
    if display_name is _NOT_SET:
        return "leave unchanged"
    if display_name is None:
        return "clear display name"
    return f"set display name to {display_name}"
```

- The API can now distinguish omitted input from explicit `None`.
- Keep the sentinel private and semantic.

## Parameter ordering and keyword-only clarity

### Keep signatures readable and force keywords where intent matters
```py
def export_report(
    report_id: str,
    destination: str,
    *,
    send_notify: bool = False,
    include_summary: bool = True,
) -> None:
    ...
```

- Required positional parameters come first.
- The boolean options are keyword-only so the call site stays explicit.

### Avoid mixed positional ambiguity
```py
def export_report(
    report_id: str,
    destination: str,
    send_notify: bool = False,
    include_summary: bool = True,
) -> None:
    ...
```

- `export_report("r1", "/tmp", True, False)` is harder to read and review.
- Flags that survive should not hide in positional calls.

## Boolean flags as signature smells

### One flag can be tolerated if it stays explicit
```py
def send_receipt(order_id: str, *, send_notify: bool = False) -> None:
    ...
```

- A single boolean is still a caution case.
- Keyword-only at least keeps the contract visible.

### Prefer semantic methods over behavior-switch flags
```py
def process_standard_order(order_id: str) -> None:
    ...


def process_urgent_order(order_id: str) -> None:
    ...
```

- Distinct behaviors are often clearer as distinct APIs.

### Prefer a richer mode parameter when the flag means "mode"
```py
from enum import Enum


class UploadMode(Enum):
    STANDARD = "standard"
    RETRY = "retry"


def upload(path: str, *, mode: UploadMode = UploadMode.STANDARD) -> None:
    ...
```

- A mode parameter scales better than `is_retry`.

### Two or more boolean flags should trigger refactoring
```py
def publish(
    content: str,
    *,
    send_notify: bool = False,
    dry_run: bool = False,
    is_urgent: bool = False,
) -> None:
    ...
```

- This signature is carrying too many behavior paths.
- Split the behavior, introduce a clearer model, or extract a parameter object.

## Broad `*args` / `**kwargs`

### Allow narrow forwarding wrappers
```py
def traced_call(*args: object, **kwargs: object) -> object:
    return _call_with_trace(*args, **kwargs)
```

- A wrapper or adapter may need transparent forwarding.
- This is an exception, not the default public API style.

### Avoid hiding the contract in `**kwargs`
```py
def create_user(**kwargs: object) -> None:
    ...
```

- Callers cannot see the real contract from the signature.
- Reviewers and static tooling lose useful shape information.

## Fat signatures and parameter objects

### Extract a parameter object when related values crowd the signature
```py
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DateRange:
    start_date: date
    end_date: date


def generate_report(
    account_id: str,
    date_range: DateRange,
    *,
    include_archived: bool = False,
) -> None:
    ...
```

- The related values gain a name.
- The public call site becomes easier to read.
- The question of whether `DateRange` should be a dataclass belongs to `python-model-selection`.

### Refactor crowded same-shape parameters
```py
def generate_report(
    account_id: str,
    start_date: str,
    end_date: str,
    currency: str,
    locale: str,
    *,
    include_archived: bool = False,
) -> None:
    ...
```

- The signature is getting wide and semantically crowded.
- Repeated same-shape values are easy to mix up.

## Positional-only parameters are out of scope

```py
def clamp(value: int, lower: int, upper: int, /) -> int:
    return max(lower, min(value, upper))
```

- First draft does not try to make policy for this shape.
- Treat positional-only as out of scope except for rare builtin-like compatibility cases.

## Split signals

Stop and hand off to another skill when the main question becomes:

- concrete type-annotation syntax or strict typing exceptions
- whether a parameter object should be an `Enum`, `dataclass`, `ABC`, or `Protocol`
- ordinary class internals, constructor logic, or attribute lifecycle
- naming policy for parameters, modules, or files
