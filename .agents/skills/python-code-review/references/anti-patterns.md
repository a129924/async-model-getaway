# Complete anti-pattern list

## Hard-discouraged — always `blocking`

These patterns are flagged as `blocking` regardless of project configuration or context.

**Bare except:**
```python
# Blocking — catches KeyboardInterrupt, SystemExit, GeneratorExit
try:
    do_something()
except:
    pass
```

**`except Exception` with no re-raise or log:**
```python
# Blocking — silently swallows all exceptions
try:
    do_something()
except Exception:
    pass
```

**Bare `pass` in exception handler:**
```python
# Blocking — silently discards the exception; add a log, re-raise, or an explicit comment
try:
    connect()
except ConnectionError:
    pass
```

**Mutable default argument:**
```python
# Blocking — the list is created once and shared across all calls
def add_item(items=[], value=None):
    items.append(value)
    return items

# Fix:
def add_item(items: list[str] | None = None, value: str | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(value)
    return items
```

**`eval()` / `exec()` without sandboxing:**
```python
# Blocking unless an explicit sandboxing justification is documented inline
eval(user_input)
exec(generated_code)
```

**Implicit `Optional`:**
```python
# Blocking — None is a valid value but the type does not declare it
def greet(name: str = None) -> str:  # type: ignore — wrong approach
    ...

# Fix:
def greet(name: str | None = None) -> str:
    ...
```

**`__getattr__` / `__setattr__` for general attribute routing (not proxy/adapter):**
```python
# Blocking when used as a convenient dynamic lookup on a regular class
def __getattr__(self, name: str) -> str:
    return self._data.get(name, "")  # hides data flow, IDE cannot navigate
```
For the full escape-hatch conditions (proxy/adapter pattern), see `python-descriptors-attribute-access`.

---

## Flag with context — `warning` unless justified

These patterns are `warning` by default. They become `blocking` in strict-mode projects or
when no inline justification exists.

**`# type: ignore` without comment:**
```python
result = legacy_function(x)  # type: ignore  ← warning: why is this ignored?
result = legacy_function(x)  # type: ignore[attr-defined]  — third-party stub missing  ← acceptable
```

**`Any` in strict-mode projects:**
```python
# blocking in strict mode, warning otherwise
def process(data: Any) -> Any:
    ...
```

**Very long functions (>50 lines):**
- Flag as `warning`; do not auto-fail.
- Note the line range and suggest splitting at natural responsibility boundaries.

**Nested list comprehensions beyond 2 levels:**
```python
# warning: readability degrades beyond 2 levels
matrix = [[cell for cell in row] for row in grid]               # 2 levels — acceptable
cube = [[[v for v in row] for row in plane] for plane in cube]  # 3 levels — flag
```
