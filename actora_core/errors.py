"""Shared errors for headless-core contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


class ContractValidationError(ValueError):
    """Raised when a command or serialized contract has an invalid shape."""


class NumericLimitError(ContractValidationError):
    """Raised when an otherwise numeric JSON value exceeds its safe range."""


class IdentifierExhaustedError(ContractValidationError):
    """Raised when a valid deterministic ID source cannot allocate again."""


class CommandRejectedError(Exception):
    """Expected domain rejection converted into a structured command result."""

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message
        self.details = dict(details or {})
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class InvariantViolation:
    """One stable, machine-readable state invariant violation."""

    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} at {self.path}: {self.message}"


class InvariantError(ContractValidationError):
    """Raised when world or save state violates one or more invariants."""

    def __init__(self, violations: Iterable[InvariantViolation]):
        self.violations = tuple(violations)
        if not self.violations:
            raise ValueError("InvariantError requires at least one violation")
        super().__init__("; ".join(str(violation) for violation in self.violations))
