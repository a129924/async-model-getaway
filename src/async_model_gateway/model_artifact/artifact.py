"""Concrete shared read contract for local model artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeGuard

from .loader_family import LoaderFamily

__all__ = ["ModelArtifact"]

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


def _normalize_json_like(value: object) -> JSONLike:
    """Validate runtime metadata and return a JSON-like copy."""
    if _is_json_scalar(value):
        return value

    if _is_json_list(value):
        return [_normalize_json_like(item) for item in value]

    if _is_json_dict(value):
        normalized_dict: dict[str, JSONLike] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                msg = "loader_options dict keys must be strings"
                raise TypeError(msg)
            normalized_dict[key] = _normalize_json_like(item)
        return normalized_dict

    msg = "loader_options values must be JSON-like scalars, lists, or dicts"
    raise TypeError(msg)


def _normalize_loader_options(value: object) -> dict[str, JSONLike]:
    """Validate top-level loader options as dict[str, JSONLike]."""
    if not _is_json_dict(value):
        msg = "loader_options must be a dict[str, JSONLike]"
        raise TypeError(msg)

    normalized_value = _normalize_json_like(value)
    if not isinstance(normalized_value, dict):
        msg = "loader_options must be a dict[str, JSONLike]"
        raise TypeError(msg)
    return normalized_value


def _require_loader_family(value: object) -> LoaderFamily:
    """Validate the explicit loader-family boundary."""
    if not isinstance(value, LoaderFamily):
        msg = "loader_family must be a LoaderFamily"
        raise TypeError(msg)
    return value


def _require_artifact_path(value: object) -> str:
    """Validate the explicit artifact-path boundary."""
    if not isinstance(value, str):
        msg = "artifact_path must be a string"
        raise TypeError(msg)

    if not value.strip():
        msg = "artifact_path must not be blank"
        raise ValueError(msg)
    return value


@dataclass(frozen=True, slots=True, init=False)
class ModelArtifact:
    """Immutable shared read contract for explicit local artifact metadata."""

    loader_family: LoaderFamily
    artifact_path: str
    loader_options: dict[str, JSONLike]

    def __init__(
        self,
        *,
        loader_family: LoaderFamily,
        artifact_path: str,
        loader_options: dict[str, JSONLike],
    ) -> None:
        """Enforce the minimal explicit read-contract invariants."""
        object.__setattr__(self, "loader_family", _require_loader_family(loader_family))
        object.__setattr__(self, "artifact_path", _require_artifact_path(artifact_path))
        object.__setattr__(
            self,
            "loader_options",
            _normalize_loader_options(loader_options),
        )
