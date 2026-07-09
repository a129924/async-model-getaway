"""Concrete shared read contract for local model artifacts."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
import math
from types import MappingProxyType
from typing import NoReturn, SupportsIndex, TypeGuard, cast, overload

from collections.abc import Iterator, Mapping, Sequence

from .loader_family import LoaderFamily

__all__ = ["ModelArtifact"]

JSONScalar = None | bool | int | float | str
JSONLike = JSONScalar | list["JSONLike"] | dict[str, "JSONLike"]


def _raise_loader_options_immutable() -> NoReturn:
    """Fail closed on attempts to mutate loader_options content."""
    msg = "loader_options is immutable"
    raise TypeError(msg)


class _FrozenJSONList(Sequence["FrozenJSONLike"]):
    """List-like JSON container that rejects in-place mutation."""

    _values: tuple[FrozenJSONLike, ...]
    __slots__ = ("_values",)

    def __init__(self, values: Sequence[FrozenJSONLike]) -> None:
        object.__setattr__(self, "_values", tuple(values))

    def __delattr__(self, _name: str) -> NoReturn:
        _raise_loader_options_immutable()

    def __setattr__(self, _name: str, _value: object) -> NoReturn:
        _raise_loader_options_immutable()

    @overload
    def __getitem__(self, index: int) -> FrozenJSONLike: ...

    @overload
    def __getitem__(self, index: slice) -> tuple[FrozenJSONLike, ...]: ...

    def __getitem__(self, index: int | slice) -> FrozenJSONLike | tuple[FrozenJSONLike, ...]:
        return self._values[index]

    def __iter__(self) -> Iterator[FrozenJSONLike]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __repr__(self) -> str:
        return repr(list(self._values))

    def __eq__(self, other: object) -> bool:
        return _materialize_json_like(self) == _materialize_json_like(other)

    def __add__(self, _value: object) -> NoReturn:
        _raise_loader_options_immutable()

    def __radd__(self, _value: object) -> NoReturn:
        _raise_loader_options_immutable()

    def __delitem__(self, _key: object) -> None:
        _raise_loader_options_immutable()

    def __iadd__(self, _value: object) -> _FrozenJSONList:
        _raise_loader_options_immutable()

    def __imul__(self, _value: object) -> _FrozenJSONList:
        _raise_loader_options_immutable()

    def __setitem__(self, _key: object, _value: object) -> None:
        _raise_loader_options_immutable()

    def append(self, _value: FrozenJSONLike) -> None:
        _raise_loader_options_immutable()

    def clear(self) -> None:
        _raise_loader_options_immutable()

    def extend(self, _values: object) -> None:
        _raise_loader_options_immutable()

    def insert(self, _index: object, _value: FrozenJSONLike) -> None:
        _raise_loader_options_immutable()

    def pop(self, _index: object = -1) -> FrozenJSONLike:
        _raise_loader_options_immutable()

    def remove(self, _value: FrozenJSONLike) -> None:
        _raise_loader_options_immutable()

    def reverse(self) -> None:
        _raise_loader_options_immutable()

    def sort(self, *, key: object = None, reverse: bool = False) -> None:
        _ = key, reverse
        _raise_loader_options_immutable()


class _FrozenJSONDict(Mapping[str, "FrozenJSONLike"]):
    """Dict-like JSON container that rejects in-place mutation."""

    _values: Mapping[str, FrozenJSONLike]
    __slots__ = ("_values",)

    def __init__(self, values: Mapping[str, FrozenJSONLike]) -> None:
        object.__setattr__(self, "_values", MappingProxyType(dict(values)))

    def __delattr__(self, _name: str) -> NoReturn:
        _raise_loader_options_immutable()

    def __setattr__(self, _name: str, _value: object) -> NoReturn:
        _raise_loader_options_immutable()

    def __getitem__(self, key: str) -> FrozenJSONLike:
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __repr__(self) -> str:
        return repr(dict(self._values))

    def __eq__(self, other: object) -> bool:
        return _materialize_json_like(self) == _materialize_json_like(other)

    def __delitem__(self, _key: str) -> None:
        _raise_loader_options_immutable()

    def __ior__(self, _value: object) -> _FrozenJSONDict:
        _raise_loader_options_immutable()

    def __setitem__(self, _key: str, _value: FrozenJSONLike) -> None:
        _raise_loader_options_immutable()

    def clear(self) -> None:
        _raise_loader_options_immutable()

    def pop(self, _key: str, _default: object = None) -> FrozenJSONLike:
        _raise_loader_options_immutable()

    def popitem(self) -> tuple[str, FrozenJSONLike]:
        _raise_loader_options_immutable()

    def setdefault(self, _key: str, _default: FrozenJSONLike = None) -> FrozenJSONLike:
        _raise_loader_options_immutable()

    def update(self, *_args: object, **_kwargs: FrozenJSONLike) -> None:
        _raise_loader_options_immutable()


FrozenJSONLike = JSONScalar | _FrozenJSONList | _FrozenJSONDict


def _materialize_json_like(value: object) -> object:
    """Convert frozen JSON wrappers into plain built-in containers for comparisons."""
    if isinstance(value, _FrozenJSONDict):
        return {key: cast(JSONLike, _materialize_json_like(item)) for key, item in value.items()}
    if isinstance(value, _FrozenJSONList):
        return [cast(JSONLike, _materialize_json_like(item)) for item in value]
    return value


def _is_json_scalar(value: object) -> TypeGuard[JSONScalar]:
    """Return whether the runtime value is a supported JSON-like scalar."""
    return value is None or isinstance(value, str | bool | int | float)


def _is_json_list(value: object) -> TypeGuard[list[object]]:
    """Return whether the runtime value is a JSON-like list boundary candidate."""
    return isinstance(value, list)


def _is_json_dict(value: object) -> TypeGuard[dict[object, object]]:
    """Return whether the runtime value is a JSON-like dict boundary candidate."""
    return isinstance(value, dict)


def _normalize_json_like(
    value: object,
    *,
    active_container_ids: set[int] | None = None,
) -> FrozenJSONLike:
    """Validate runtime metadata and return a JSON-like copy."""
    if isinstance(value, float):
        if not math.isfinite(value):
            msg = "loader_options floats must be finite"
            raise ValueError(msg)
        return value

    if _is_json_scalar(value):
        return value

    if _is_json_list(value):
        if active_container_ids is None:
            active_container_ids = set()

        value_id = id(value)
        if value_id in active_container_ids:
            msg = "loader_options must not contain cyclic references"
            raise ValueError(msg)

        active_container_ids.add(value_id)
        try:
            return _FrozenJSONList(
                [
                    _normalize_json_like(
                        item,
                        active_container_ids=active_container_ids,
                    )
                    for item in value
                ]
            )
        finally:
            active_container_ids.remove(value_id)

    if _is_json_dict(value):
        if active_container_ids is None:
            active_container_ids = set()

        value_id = id(value)
        if value_id in active_container_ids:
            msg = "loader_options must not contain cyclic references"
            raise ValueError(msg)

        active_container_ids.add(value_id)
        normalized_dict: dict[str, FrozenJSONLike] = {}
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    msg = "loader_options dict keys must be strings"
                    raise TypeError(msg)
                normalized_dict[key] = _normalize_json_like(
                    item,
                    active_container_ids=active_container_ids,
                )
        finally:
            active_container_ids.remove(value_id)
        return _FrozenJSONDict(normalized_dict)

    msg = "loader_options values must be JSON-like scalars, lists, or dicts"
    raise TypeError(msg)


def _normalize_loader_options(value: object) -> _FrozenJSONDict:
    """Validate top-level loader options as dict[str, JSONLike]."""
    if not _is_json_dict(value):
        msg = "loader_options must be a dict[str, JSONLike]"
        raise TypeError(msg)

    normalized_value = _normalize_json_like(value)
    if not isinstance(normalized_value, _FrozenJSONDict):
        msg = "loader_options must be a dict[str, JSONLike]"
        raise TypeError(msg)
    return normalized_value


def _rebuild_model_artifact(
    loader_family: LoaderFamily,
    artifact_path: str,
    loader_options: dict[str, JSONLike],
) -> ModelArtifact:
    """Reconstruct the artifact through the public constructor contract."""
    return ModelArtifact(
        loader_family=loader_family,
        artifact_path=artifact_path,
        loader_options=loader_options,
    )


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
    loader_options: dict[str, JSONLike] = field(repr=False)
    __hash__ = None

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

    def __getattribute__(self, name: str) -> object:
        """Expose the public loader-options contract while storing frozen internals."""
        value = object.__getattribute__(self, name)
        if name == "loader_options":
            return cast(dict[str, JSONLike], _materialize_json_like(value))
        return value

    def __copy__(self) -> ModelArtifact:
        """Rebuild through validation so copied state stays frozen internally."""
        return type(self)(
            loader_family=self.loader_family,
            artifact_path=self.artifact_path,
            loader_options=self.loader_options,
        )

    def __deepcopy__(self, memo: dict[int, object]) -> ModelArtifact:
        """Rebuild through validation so deep-copied state stays frozen internally."""
        copied_artifact = type(self)(
            loader_family=self.loader_family,
            artifact_path=self.artifact_path,
            loader_options=copy.deepcopy(self.loader_options, memo),
        )
        memo[id(self)] = copied_artifact
        return copied_artifact

    def __reduce_ex__(
        self,
        protocol: SupportsIndex,
    ) -> tuple[object, tuple[LoaderFamily, str, dict[str, JSONLike]]]:
        """Force pickle-based reconstruction back through validation."""
        _ = protocol
        return (
            _rebuild_model_artifact,
            (self.loader_family, self.artifact_path, self.loader_options),
        )
