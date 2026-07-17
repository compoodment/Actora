"""Optimistic-concurrency dispatcher for the first headless action slice."""

from __future__ import annotations

from .action_queue import queue_action, remove_action
from .commands import CommandType, GameCommand
from .contracts import CommandError, CommandResult, SaveEnvelope
from .errors import CommandRejectedError, ContractValidationError
from .json_types import MAX_SAFE_INTEGER
from .serialization import (
    build_save_envelope,
    restore_save_envelope,
)

SUPPORTED_ENGINE_KIND = "python-headless"


def _copy_save(save: SaveEnvelope) -> SaveEnvelope:
    return SaveEnvelope.from_dict(save.to_dict())


def _failure(
    command: GameCommand,
    *,
    code: str,
    message: str,
    save: SaveEnvelope | None,
    details: dict[str, object] | None = None,
) -> CommandResult:
    stable_save = _copy_save(save) if save is not None else None
    return CommandResult(
        command_id=command.command_id,
        command_type=command.command_type,
        ok=False,
        revision=stable_save.revision if stable_save is not None else 0,
        save=stable_save,
        error=CommandError(
            code=code,
            message=message,
            details=details or {},
        ),
    )


def dispatch_command(
    save: SaveEnvelope | None,
    command: GameCommand,
) -> CommandResult:
    """Executes one validated command without mutating the supplied envelope."""
    if not isinstance(command, GameCommand):
        raise ContractValidationError("command must be a GameCommand")
    # Revalidate nested mutable command payloads before any state work.
    command.to_dict()

    if save is None:
        if command.command_type is not CommandType.CREATE_GAME:
            raise ContractValidationError(
                "an existing save is required for this command"
            )
        if command.expected_revision != 0:
            return _failure(
                command,
                code="revision_conflict",
                message="The command expected a different save revision.",
                save=None,
                details={
                    "actual_revision": 0,
                    "expected_revision": command.expected_revision,
                },
            )
        return _failure(
            command,
            code="command_not_implemented",
            message="Game creation is not implemented in this engine slice.",
            save=None,
        )

    if not isinstance(save, SaveEnvelope):
        raise ContractValidationError("save must be a SaveEnvelope or null")
    save.to_dict()

    if save.engine_kind != SUPPORTED_ENGINE_KIND:
        return _failure(
            command,
            code="engine_kind_mismatch",
            message="This dispatcher cannot execute that save engine kind.",
            save=save,
            details={
                "actual_engine_kind": save.engine_kind,
                "expected_engine_kind": SUPPORTED_ENGINE_KIND,
            },
        )
    if command.expected_revision != save.revision:
        return _failure(
            command,
            code="revision_conflict",
            message="The command expected a different save revision.",
            save=save,
            details={
                "actual_revision": save.revision,
                "expected_revision": command.expected_revision,
            },
        )

    if command.command_type not in {
        CommandType.QUEUE_ACTION,
        CommandType.REMOVE_ACTION,
    }:
        return _failure(
            command,
            code="command_not_implemented",
            message=(
                f"Command '{command.command_type.value}' is not implemented "
                "in this engine slice."
            ),
            save=save,
        )
    if save.revision >= MAX_SAFE_INTEGER:
        return _failure(
            command,
            code="revision_conflict",
            message="This save cannot accept another change.",
            save=save,
            details={"reason": "revision_limit"},
        )
    if (
        command.command_type is CommandType.QUEUE_ACTION
        and save.ids.next_value >= MAX_SAFE_INTEGER
    ):
        return _failure(
            command,
            code="action_not_available",
            message="That action is unavailable.",
            save=save,
            details={"reason": "identifier_limit"},
        )

    restored = restore_save_envelope(save)
    try:
        if command.command_type is CommandType.QUEUE_ACTION:
            action = command.payload["action"]
            if not isinstance(action, dict):  # guarded by command validation
                raise ContractValidationError(
                    "command.payload.action must be an object"
                )
            action_id = queue_action(
                restored.world,
                restored.session,
                restored.id_source,
                action,
            )
            effect = {"kind": "action_queued", "action_id": action_id}
        else:
            remove_action_id = command.payload["action_id"]
            if not isinstance(remove_action_id, str):  # command-validated
                raise ContractValidationError(
                    "command.payload.action_id must be a string"
                )
            action_id = remove_action(
                restored.session,
                action_id=remove_action_id,
            )
            effect = {"kind": "action_removed", "action_id": action_id}
    except CommandRejectedError as exc:
        return _failure(
            command,
            code=exc.code,
            message=exc.message,
            save=save,
            details=exc.details,
        )

    next_save = build_save_envelope(
        restored.world,
        restored.session,
        restored.random_source,
        restored.id_source,
        engine_version=restored.engine_version,
        engine_kind=restored.engine_kind,
        revision=restored.revision + 1,
        metadata=restored.metadata,
        format_version=restored.format_version,
        schema_version=restored.schema_version,
    )
    return CommandResult(
        command_id=command.command_id,
        command_type=command.command_type,
        ok=True,
        revision=next_save.revision,
        save=next_save,
        effects=(effect,),
    )


def dispatch_serialized_command(
    serialized_save: str | None,
    serialized_command: str,
) -> str:
    """Strict JSON bridge shared by native tests and a future Worker adapter."""
    from .serialization import loads_save_envelope
    from .transport import dumps_command_result, loads_game_command

    save = (
        loads_save_envelope(serialized_save)
        if serialized_save is not None
        else None
    )
    command = loads_game_command(serialized_command)
    return dumps_command_result(dispatch_command(save, command))
