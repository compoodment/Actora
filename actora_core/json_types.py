"""JSON value helpers used by transport-facing core contracts."""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, TypeAlias

from .errors import ContractValidationError

JSONScalar: TypeAlias = None | bool | int | float | str
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
JSONObject: TypeAlias = dict[str, JSONValue]

# Contract-v1 JSON crosses a JavaScript boundary. Integers outside this range
# cannot survive JSON.parse/stringify exactly, so accepting them would make a
# native save subtly different from the same save in a browser Worker.
MIN_SAFE_INTEGER = -(2**53 - 1)
MAX_SAFE_INTEGER = 2**53 - 1


def parse_json_safe_int(value: str, *, path: str) -> int:
    """Parses a JSON integer without triggering unbounded Python conversion."""
    digits = value[1:] if value.startswith("-") else value
    if not digits or len(digits) > 16:
        raise ContractValidationError(
            f"{path} must be a JavaScript-safe integer"
        )
    parsed = int(value)
    if not MIN_SAFE_INTEGER <= parsed <= MAX_SAFE_INTEGER:
        raise ContractValidationError(
            f"{path} must be a JavaScript-safe integer"
        )
    return parsed


def clone_json(value: Any, *, path: str = "$") -> JSONValue:
    """Returns a detached JSON-safe clone or raises with a useful path."""
    _assert_json_value(value, path)
    return deepcopy(value)


def clone_json_object(value: Any, *, path: str = "$") -> JSONObject:
    """Returns a detached JSON object clone."""
    if not isinstance(value, dict):
        raise ContractValidationError(f"{path} must be an object")
    cloned = clone_json(value, path=path)
    return cloned  # type: ignore[return-value]


def _assert_json_value(value: Any, path: str) -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int):
        if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
            raise ContractValidationError(
                f"{path} must be a JavaScript-safe integer"
            )
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractValidationError(f"{path} must not contain NaN or infinity")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _assert_json_value(child, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise ContractValidationError(f"{path} contains a non-string object key")
            _assert_json_value(child, f"{path}.{key}")
        return
    raise ContractValidationError(
        f"{path} contains unsupported value type {type(value).__name__}"
    )


def require_int(
    value: Any,
    *,
    path: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    """Validates an integer while rejecting booleans."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContractValidationError(f"{path} must be an integer")
    if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
        raise ContractValidationError(
            f"{path} must be a JavaScript-safe integer"
        )
    if minimum is not None and value < minimum:
        raise ContractValidationError(f"{path} must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise ContractValidationError(f"{path} must be at most {maximum}")
    return value


def require_nonempty_string(value: Any, *, path: str) -> str:
    """Validates a non-empty string."""
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{path} must be a non-empty string")
    return value
