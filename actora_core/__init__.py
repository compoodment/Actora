"""Curses-free contracts for Actora's headless runtime.

Importing it must never import the terminal shell.
"""

from .commands import CommandType, GameCommand
from .contracts import CommandError, CommandResult, SaveEnvelope
from .dispatcher import (
    ENGINE_VERSION,
    SUPPORTED_ENGINE_KIND,
    dispatch_command,
    dispatch_serialized_command,
)
from .errors import (
    CommandRejectedError,
    ContractValidationError,
    IdentifierExhaustedError,
    InvariantError,
    InvariantViolation,
    NumericLimitError,
)
from .ids import DeterministicIdSource, IdSource, IdState
from .randomness import RandomSource, RandomState, SeededRandomSource
from .serialization import (
    RestoredSave,
    build_save_envelope,
    deserialize_world,
    dumps_save_envelope,
    loads_save_envelope,
    restore_save_envelope,
    serialize_world,
)
from .session import GameSession
from .transport import (
    dumps_command_result,
    dumps_game_command,
    loads_command_result,
    loads_game_command,
)
from .validation import (
    assert_valid_save_envelope,
    assert_valid_world_state,
    collect_save_invariant_violations,
    collect_world_invariant_violations,
)

__all__ = [
    "CommandError",
    "CommandRejectedError",
    "CommandResult",
    "CommandType",
    "ContractValidationError",
    "DeterministicIdSource",
    "ENGINE_VERSION",
    "GameCommand",
    "GameSession",
    "IdSource",
    "IdState",
    "IdentifierExhaustedError",
    "InvariantError",
    "InvariantViolation",
    "NumericLimitError",
    "RandomSource",
    "RandomState",
    "RestoredSave",
    "SaveEnvelope",
    "SeededRandomSource",
    "SUPPORTED_ENGINE_KIND",
    "assert_valid_save_envelope",
    "assert_valid_world_state",
    "build_save_envelope",
    "collect_save_invariant_violations",
    "collect_world_invariant_violations",
    "deserialize_world",
    "dispatch_command",
    "dispatch_serialized_command",
    "dumps_command_result",
    "dumps_game_command",
    "dumps_save_envelope",
    "loads_command_result",
    "loads_game_command",
    "loads_save_envelope",
    "restore_save_envelope",
    "serialize_world",
]
