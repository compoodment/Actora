"""Injected and serializable identifier seams."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .errors import ContractValidationError
from .json_types import MAX_SAFE_INTEGER, require_int

_ID_SEGMENT_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def _validate_segment(value: object, *, path: str) -> str:
    if not isinstance(value, str) or not _ID_SEGMENT_PATTERN.fullmatch(value):
        raise ContractValidationError(
            f"{path} must use lowercase letters, digits, and single underscores"
        )
    return value


@dataclass(frozen=True, slots=True)
class IdState:
    """Serializable state for deterministic sequential identifiers."""

    namespace: str
    next_value: int = 1
    algorithm: str = "sequential-v1"

    def __post_init__(self) -> None:
        if self.algorithm != "sequential-v1":
            raise ContractValidationError(
                f"Unsupported ID-state algorithm '{self.algorithm}'"
            )
        _validate_segment(self.namespace, path="ids.namespace")
        require_int(self.next_value, path="ids.next_value", minimum=1)

    @classmethod
    def from_dict(cls, data: object) -> "IdState":
        if not isinstance(data, dict):
            raise ContractValidationError("ids must be an object")
        allowed_fields = {"algorithm", "namespace", "next_value"}
        unknown_fields = sorted(
            str(field)
            for field in data
            if not isinstance(field, str) or field not in allowed_fields
        )
        if unknown_fields:
            raise ContractValidationError(
                "ids contains unknown fields: " + ", ".join(unknown_fields)
            )
        return cls(
            namespace=_validate_segment(data.get("namespace"), path="ids.namespace"),
            next_value=require_int(
                data.get("next_value"),
                path="ids.next_value",
                minimum=1,
            ),
            algorithm=data.get("algorithm", "sequential-v1"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "algorithm": self.algorithm,
            "namespace": self.namespace,
            "next_value": self.next_value,
        }


@runtime_checkable
class IdSource(Protocol):
    """Minimum identifier API required by simulation code."""

    def next_id(self, role: str) -> str:
        ...

    def snapshot(self) -> IdState:
        ...


class DeterministicIdSource:
    """Monotonic identifier generator that survives save/reload exactly."""

    def __init__(self, namespace: str = "actora", next_value: int = 1):
        state = IdState(namespace=namespace, next_value=next_value)
        self._namespace = state.namespace
        self._next_value = state.next_value

    @classmethod
    def from_state(cls, state: IdState) -> "DeterministicIdSource":
        return cls(namespace=state.namespace, next_value=state.next_value)

    def next_id(self, role: str) -> str:
        normalized_role = _validate_segment(role, path="role")
        if self._next_value >= MAX_SAFE_INTEGER:
            raise ContractValidationError(
                "ids.next_value cannot advance beyond the JavaScript-safe range"
            )
        value = self._next_value
        self._next_value += 1
        return f"{self._namespace}_{normalized_role}_{value:08d}"

    def snapshot(self) -> IdState:
        return IdState(namespace=self._namespace, next_value=self._next_value)
