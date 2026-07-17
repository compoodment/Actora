"""Strict canonical JSON transport for commands and command results."""

from __future__ import annotations

import json
from collections.abc import Callable

from .commands import GameCommand
from .contracts import CommandResult
from .errors import ContractValidationError
from .json_types import JSONObject, JSONValue, parse_json_safe_int


def _strict_loads(
    serialized: str,
    *,
    contract_name: str,
) -> object:
    if not isinstance(serialized, str):
        raise ContractValidationError(
            f"serialized {contract_name} must be a string"
        )

    def reject_constant(value: str) -> None:
        raise ContractValidationError(
            f"{contract_name} JSON contains invalid constant {value}"
        )

    def reject_duplicate_keys(
        pairs: list[tuple[str, JSONValue]],
    ) -> JSONObject:
        result: JSONObject = {}
        for key, value in pairs:
            if key in result:
                raise ContractValidationError(
                    f"{contract_name} JSON contains duplicate key '{key}'"
                )
            result[key] = value
        return result

    try:
        return json.loads(
            serialized,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_constant,
            parse_int=lambda value: parse_json_safe_int(
                value,
                path=f"{contract_name} JSON integer",
            ),
        )
    except ContractValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise ContractValidationError(
            f"Invalid {contract_name} JSON: {exc.msg}"
        ) from exc


def _canonical_dumps(
    value_factory: Callable[[], dict[str, JSONValue]],
) -> str:
    return json.dumps(
        value_factory(),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def loads_game_command(serialized: str) -> GameCommand:
    """Parses strict JSON into one validated game command."""
    return GameCommand.from_dict(
        _strict_loads(serialized, contract_name="command")
    )


def dumps_game_command(command: GameCommand) -> str:
    """Serializes one command with canonical key ordering and spacing."""
    if not isinstance(command, GameCommand):
        raise ContractValidationError("command must be a GameCommand")
    return _canonical_dumps(command.to_dict)


def loads_command_result(serialized: str) -> CommandResult:
    """Parses strict JSON into one fully validated command result."""
    return CommandResult.from_dict(
        _strict_loads(serialized, contract_name="result")
    )


def dumps_command_result(result: CommandResult) -> str:
    """Serializes one result with canonical key ordering and spacing."""
    if not isinstance(result, CommandResult):
        raise ContractValidationError("result must be a CommandResult")
    return _canonical_dumps(result.to_dict)
