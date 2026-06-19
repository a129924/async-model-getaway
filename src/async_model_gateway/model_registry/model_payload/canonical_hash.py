"""Canonical hashing for model-payload identity material."""

from __future__ import annotations

from hashlib import sha256
import json
from typing import TypeGuard

JSONScalar = None | bool | int | float | str
JSONLike = JSONScalar | list["JSONLike"] | dict[str, "JSONLike"]


def _is_json_scalar(value: object) -> TypeGuard[JSONScalar]:
    """Return whether the runtime value is a supported JSON-like scalar."""
    return value is None or isinstance(value, str | bool | int | float)


def _is_json_list(value: object) -> TypeGuard[list[object]]:
    """Return whether the runtime value is a JSON-like list boundary candidate."""
    return isinstance(value, list)


def _is_json_dict(value: object) -> TypeGuard[dict[object, object]]:
    """Return whether the runtime value is a JSON-like dict boundary candidate."""
    return isinstance(value, dict)


def _canonicalize_json_like(value: object) -> JSONLike:
    """Validate a runtime JSON-like value and return its canonical form."""
    if _is_json_scalar(value):
        return value

    if _is_json_list(value):
        return [_canonicalize_json_like(item) for item in value]

    if _is_json_dict(value):
        keys: list[str] = []
        for key in value:
            if not isinstance(key, str):
                msg = "model_payload dict keys must be strings"
                raise TypeError(msg)
            keys.append(key)

        canonical_dict: dict[str, JSONLike] = {}
        for key in sorted(keys):
            canonical_dict[key] = _canonicalize_json_like(value[key])
        return canonical_dict

    msg = "model_payload values must be JSON-like scalars, lists, or dicts"
    raise TypeError(msg)


def hash_model_payload(model_payload: dict[str, JSONLike]) -> str:
    """Return a deterministic SHA-256 hex digest for model-payload content."""
    runtime_payload: object = model_payload
    if not _is_json_dict(runtime_payload):
        msg = "model_payload must be a dict[str, JSONLike]"
        raise TypeError(msg)

    canonical_payload = _canonicalize_json_like(runtime_payload)
    serialized_payload = json.dumps(
        canonical_payload,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return sha256(serialized_payload.encode("utf-8")).hexdigest()
