"""Optimistic-concurrency dispatcher for the headless native engine."""

from __future__ import annotations

from .action_queue import queue_action, remove_action
from .advancement import advance_time
from .commands import CommandType, GameCommand
from .contracts import CommandError, CommandResult, SaveEnvelope
from .errors import (
    CommandRejectedError,
    ContractValidationError,
    IdentifierExhaustedError,
    InvariantError,
    NumericLimitError,
)
from .ids import DeterministicIdSource
from .json_types import MAX_SAFE_INTEGER
from .randomness import SeededRandomSource
from .serialization import (
    build_save_envelope,
    restore_save_envelope,
)
from .session import GameSession

SUPPORTED_ENGINE_KIND = "python-headless"
ENGINE_VERSION = "0.57.0"


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


def _create_game(command: GameCommand) -> CommandResult:
    """Builds a new deterministic world without importing terminal modules."""
    from game_setup import setup_initial_world_from_character

    character = command.payload["character"]
    seed = command.payload["seed"]
    if not isinstance(character, dict) or not isinstance(seed, str):
        raise ContractValidationError(
            "validated create_game payload changed before dispatch"
        )

    random_source = SeededRandomSource(int(seed, 16))
    id_source = DeterministicIdSource("actora")
    world, focused_actor_id = setup_initial_world_from_character(
        character,
        random_source=random_source,
        id_source=id_source,
    )

    session = GameSession.new(focused_actor_id, random_source)
    next_save = build_save_envelope(
        world,
        session,
        random_source,
        id_source,
        engine_version=ENGINE_VERSION,
        engine_kind=SUPPORTED_ENGINE_KIND,
        revision=1,
        metadata={},
    )
    return CommandResult(
        command_id=command.command_id,
        command_type=command.command_type,
        ok=True,
        revision=next_save.revision,
        save=next_save,
        effects=(
            {
                "kind": "game_created",
                "focused_actor_id": focused_actor_id,
            },
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
            return _failure(
                command,
                code="save_required",
                message="Start or load a game before using that command.",
                save=None,
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
        return _create_game(command)

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

    if command.command_type is CommandType.CREATE_GAME:
        return _failure(
            command,
            code="game_already_exists",
            message="A game already exists in this save.",
            save=save,
        )
    if command.command_type not in {
        CommandType.QUEUE_ACTION,
        CommandType.REMOVE_ACTION,
        CommandType.ADVANCE_TIME,
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
            effects = (
                {"kind": "action_queued", "action_id": action_id},
            )
            events = ()
            interruption = None
        elif command.command_type is CommandType.REMOVE_ACTION:
            remove_action_id = command.payload["action_id"]
            if not isinstance(remove_action_id, str):  # command-validated
                raise ContractValidationError(
                    "command.payload.action_id must be a string"
                )
            action_id = remove_action(
                restored.session,
                action_id=remove_action_id,
            )
            effects = (
                {"kind": "action_removed", "action_id": action_id},
            )
            events = ()
            interruption = None
        else:
            months = command.payload["months"]
            if not isinstance(months, int) or isinstance(months, bool):
                raise ContractValidationError(
                    "command.payload.months must be an integer"
                )
            advancement = advance_time(
                restored.world,
                restored.session,
                restored.random_source,
                restored.id_source,
                months,
            )
            raw_events = advancement["events"]
            raw_effects = advancement["effects"]
            if not isinstance(raw_events, list) or not isinstance(
                raw_effects,
                list,
            ):
                raise RuntimeError(
                    "advance_time returned an invalid result shape"
                )
            events = tuple(raw_events)
            effects = tuple(raw_effects)
            interruption = advancement["interruption"]
    except CommandRejectedError as exc:
        return _failure(
            command,
            code=exc.code,
            message=exc.message,
            save=save,
            details=exc.details,
        )
    except IdentifierExhaustedError:
        return _failure(
            command,
            code="identifier_limit",
            message="This save has reached its creation limit.",
            save=save,
        )

    try:
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
    except NumericLimitError:
        return _failure(
            command,
            code="state_limit",
            message="This save cannot safely apply that change.",
            save=save,
            details={"reason": "numeric_limit"},
        )
    except InvariantError as exc:
        numeric_limit_codes = {
            "invalid_money",
            "invalid_social_history",
        }
        if (
            exc.violations
            and all(
                violation.code in numeric_limit_codes
                for violation in exc.violations
            )
        ):
            return _failure(
                command,
                code="state_limit",
                message="This save cannot safely apply that change.",
                save=save,
                details={"reason": "numeric_limit"},
            )
        raise
    return CommandResult(
        command_id=command.command_id,
        command_type=command.command_type,
        ok=True,
        revision=next_save.revision,
        save=next_save,
        events=events,
        effects=effects,
        interruption=interruption,
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
