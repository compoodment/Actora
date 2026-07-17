"""Versionable JSON command contract for the headless dispatcher."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from geography import WORLD_GEOGRAPHY_BY_COUNTRY_ID
from mechanics import TRAIT_DEFINITIONS

from .errors import ContractValidationError
from .json_types import (
    JSONObject,
    JSONValue,
    clone_json_object,
    require_int,
    require_nonempty_string,
)

MAX_ADVANCE_MONTHS = 120
_CREATE_SEED_PATTERN = re.compile(r"^[0-9a-f]{16}$")
_CREATE_CHARACTER_FIELDS = {
    "first_name",
    "last_name",
    "sex",
    "gender",
    "country_id",
    "city_id",
    "appearance",
    "traits",
    "stats",
}
_CREATE_APPEARANCE_FIELDS = {"eye_color", "hair_color", "skin_tone"}
_CREATE_STAT_FIELDS = {
    "health",
    "happiness",
    "intelligence",
    "strength",
    "charisma",
    "imagination",
    "memory",
    "wisdom",
    "stress",
    "discipline",
    "willpower",
    "looks",
    "fertility",
}
_SIGNED_CREATE_STAT_FIELDS = {"memory", "stress"}
_CREATE_SEX_TO_GENDER = {
    "Male": "Male",
    "Female": "Female",
    "Intersex": "Non-binary",
}


class CommandType(str, Enum):
    """Initial command vocabulary shared by terminal and web runtimes."""

    CREATE_GAME = "create_game"
    QUEUE_ACTION = "queue_action"
    REMOVE_ACTION = "remove_action"
    ADVANCE_TIME = "advance_time"
    RESOLVE_CHOICE = "resolve_choice"
    CONTINUE_AS = "continue_as"


def _require_object_key(
    payload: JSONObject,
    key: str,
    *,
    path: str = "command.payload",
) -> JSONObject:
    if key not in payload or not isinstance(payload[key], dict):
        raise ContractValidationError(f"{path}.{key} must be an object")
    return clone_json_object(payload[key], path=f"{path}.{key}")


def _reject_unknown_fields(
    value: JSONObject,
    allowed_fields: set[str],
    *,
    path: str,
) -> None:
    unknown_fields = sorted(
        str(field)
        for field in value
        if not isinstance(field, str) or field not in allowed_fields
    )
    if unknown_fields:
        raise ContractValidationError(
            f"{path} contains unknown fields: " + ", ".join(unknown_fields)
        )


def _require_trimmed_string(value: object, *, path: str) -> str:
    normalized = require_nonempty_string(value, path=path)
    if normalized != normalized.strip():
        raise ContractValidationError(
            f"{path} must not start or end with whitespace"
        )
    return normalized


def _validate_create_character(character: JSONObject) -> None:
    _reject_unknown_fields(
        character,
        _CREATE_CHARACTER_FIELDS,
        path="command.payload.character",
    )
    missing_fields = sorted(_CREATE_CHARACTER_FIELDS - set(character))
    if missing_fields:
        raise ContractValidationError(
            "command.payload.character is missing fields: "
            + ", ".join(missing_fields)
        )

    for field_name in (
        "first_name",
        "last_name",
        "country_id",
        "city_id",
    ):
        _require_trimmed_string(
            character.get(field_name),
            path=f"command.payload.character.{field_name}",
        )

    country_id = character["country_id"]
    city_id = character["city_id"]
    country = WORLD_GEOGRAPHY_BY_COUNTRY_ID.get(country_id)
    if country is None:
        raise ContractValidationError(
            "command.payload.character.country_id is unknown"
        )
    if city_id not in {
        city["city_id"] for city in country["cities"]
    }:
        raise ContractValidationError(
            "command.payload.character.city_id must belong to "
            "command.payload.character.country_id"
        )

    sex = _require_trimmed_string(
        character.get("sex"),
        path="command.payload.character.sex",
    )
    if sex not in _CREATE_SEX_TO_GENDER:
        raise ContractValidationError(
            "command.payload.character.sex must be Male, Female, or Intersex"
        )
    gender = _require_trimmed_string(
        character.get("gender"),
        path="command.payload.character.gender",
    )
    expected_gender = _CREATE_SEX_TO_GENDER[sex]
    if gender != expected_gender:
        raise ContractValidationError(
            "command.payload.character.gender must match the current "
            f"creation default for {sex}: {expected_gender}"
        )

    appearance = _require_object_key(
        character,
        "appearance",
        path="command.payload.character",
    )
    _reject_unknown_fields(
        appearance,
        _CREATE_APPEARANCE_FIELDS,
        path="command.payload.character.appearance",
    )
    missing_appearance = sorted(
        _CREATE_APPEARANCE_FIELDS - set(appearance)
    )
    if missing_appearance:
        raise ContractValidationError(
            "command.payload.character.appearance is missing fields: "
            + ", ".join(missing_appearance)
        )
    for field_name in sorted(_CREATE_APPEARANCE_FIELDS):
        _require_trimmed_string(
            appearance.get(field_name),
            path=f"command.payload.character.appearance.{field_name}",
        )

    traits = character.get("traits")
    if not isinstance(traits, list):
        raise ContractValidationError(
            "command.payload.character.traits must be an array"
        )
    if (
        len(traits) != 4
        or any(not isinstance(trait, str) for trait in traits)
        or len(set(traits)) != 4
        or any(trait not in TRAIT_DEFINITIONS for trait in traits)
    ):
        raise ContractValidationError(
            "command.payload.character.traits must contain exactly 4 "
            "unique canonical human traits"
        )

    stats = _require_object_key(
        character,
        "stats",
        path="command.payload.character",
    )
    _reject_unknown_fields(
        stats,
        _CREATE_STAT_FIELDS,
        path="command.payload.character.stats",
    )
    missing_stats = sorted(_CREATE_STAT_FIELDS - set(stats))
    if missing_stats:
        raise ContractValidationError(
            "command.payload.character.stats is missing fields: "
            + ", ".join(missing_stats)
        )
    for stat_name in sorted(_CREATE_STAT_FIELDS):
        stat_value = stats.get(stat_name)
        if (
            isinstance(stat_value, bool)
            or not isinstance(stat_value, (int, float))
            or not math.isfinite(stat_value)
        ):
            raise ContractValidationError(
                "command.payload.character.stats."
                f"{stat_name} must be a finite number"
            )
        minimum, maximum = (
            (-50, 50)
            if stat_name in _SIGNED_CREATE_STAT_FIELDS
            else (0, 100)
        )
        if not minimum <= stat_value <= maximum:
            raise ContractValidationError(
                "command.payload.character.stats."
                f"{stat_name} must be between {minimum} and {maximum}"
            )


def _validate_create_game(payload: JSONObject) -> None:
    _reject_unknown_fields(
        payload,
        {"character", "seed"},
        path="command.payload",
    )
    character = _require_object_key(payload, "character")
    _validate_create_character(character)
    seed = require_nonempty_string(
        payload.get("seed"),
        path="command.payload.seed",
    )
    if _CREATE_SEED_PATTERN.fullmatch(seed) is None:
        raise ContractValidationError(
            "command.payload.seed must be 16 lowercase hexadecimal characters"
        )


def _validate_queue_action(payload: JSONObject) -> None:
    _reject_unknown_fields(payload, {"action"}, path="command.payload")
    action = _require_object_key(payload, "action")
    action_type = require_nonempty_string(
        action.get("action_type"),
        path="command.payload.action.action_type",
    )
    if action_type == "personal":
        _reject_unknown_fields(
            action,
            {"action_type", "subtype_id"},
            path="command.payload.action",
        )
        require_nonempty_string(
            action.get("subtype_id"),
            path="command.payload.action.subtype_id",
        )
    elif action_type == "spend_time":
        _reject_unknown_fields(
            action,
            {"action_type", "target_actor_id"},
            path="command.payload.action",
        )
        require_nonempty_string(
            action.get("target_actor_id"),
            path="command.payload.action.target_actor_id",
        )
    else:
        # Unsupported action families are a domain rejection, not a malformed
        # command. They may carry no unversioned fields into contract v1.
        _reject_unknown_fields(
            action,
            {"action_type"},
            path="command.payload.action",
        )


def _validate_remove_action(payload: JSONObject) -> None:
    _reject_unknown_fields(payload, {"action_id"}, path="command.payload")
    require_nonempty_string(
        payload.get("action_id"),
        path="command.payload.action_id",
    )


def _validate_advance_time(payload: JSONObject) -> None:
    _reject_unknown_fields(payload, {"months"}, path="command.payload")
    require_int(
        payload.get("months"),
        path="command.payload.months",
        minimum=1,
        maximum=MAX_ADVANCE_MONTHS,
    )


def _validate_resolve_choice(payload: JSONObject) -> None:
    _reject_unknown_fields(
        payload,
        {"choice_id", "option_id"},
        path="command.payload",
    )
    require_nonempty_string(
        payload.get("choice_id"),
        path="command.payload.choice_id",
    )
    if "option_id" not in payload:
        raise ContractValidationError(
            "command.payload.option_id is required and may be null"
        )
    option_id = payload["option_id"]
    if option_id is not None:
        require_nonempty_string(
            option_id,
            path="command.payload.option_id",
        )


def _validate_continue_as(payload: JSONObject) -> None:
    _reject_unknown_fields(payload, {"actor_id"}, path="command.payload")
    require_nonempty_string(
        payload.get("actor_id"),
        path="command.payload.actor_id",
    )


_PAYLOAD_VALIDATORS: dict[CommandType, Callable[[JSONObject], None]] = {
    CommandType.CREATE_GAME: _validate_create_game,
    CommandType.QUEUE_ACTION: _validate_queue_action,
    CommandType.REMOVE_ACTION: _validate_remove_action,
    CommandType.ADVANCE_TIME: _validate_advance_time,
    CommandType.RESOLVE_CHOICE: _validate_resolve_choice,
    CommandType.CONTINUE_AS: _validate_continue_as,
}


@dataclass(frozen=True, slots=True)
class GameCommand:
    """One optimistic-concurrency command sent to the simulation engine."""

    command_id: str
    command_type: CommandType
    payload: JSONObject
    expected_revision: int
    contract_version: int = 1

    def __post_init__(self) -> None:
        require_nonempty_string(self.command_id, path="command.command_id")
        if isinstance(self.command_type, str) and not isinstance(
            self.command_type,
            CommandType,
        ):
            try:
                object.__setattr__(self, "command_type", CommandType(self.command_type))
            except ValueError as exc:
                raise ContractValidationError(
                    f"Unsupported command type '{self.command_type}'"
                ) from exc
        if not isinstance(self.command_type, CommandType):
            raise ContractValidationError("command.command_type is invalid")
        object.__setattr__(
            self,
            "payload",
            clone_json_object(self.payload, path="command.payload"),
        )
        require_int(
            self.expected_revision,
            path="command.expected_revision",
            minimum=0,
        )
        if require_int(
            self.contract_version,
            path="command.contract_version",
            minimum=1,
        ) != 1:
            raise ContractValidationError(
                f"Unsupported command contract_version {self.contract_version}"
            )
        _PAYLOAD_VALIDATORS[self.command_type](self.payload)

    @classmethod
    def create(
        cls,
        command_type: CommandType | str,
        payload: JSONObject,
        *,
        command_id: str,
        expected_revision: int,
    ) -> "GameCommand":
        """Builds a caller-identified command.

        Command IDs belong to the request transport. They must never consume
        the simulation-owned ID source stored inside a save envelope.
        """
        try:
            normalized_type = CommandType(command_type)
        except (TypeError, ValueError) as exc:
            raise ContractValidationError(
                f"Unsupported command type '{command_type}'"
            ) from exc
        return cls(
            command_id=command_id,
            command_type=normalized_type,
            payload=payload,
            expected_revision=expected_revision,
        )

    @classmethod
    def from_dict(cls, data: object) -> "GameCommand":
        if not isinstance(data, dict):
            raise ContractValidationError("command must be an object")
        _reject_unknown_fields(
            data,
            {
                "contract_version",
                "command_id",
                "command_type",
                "expected_revision",
                "payload",
            },
            path="command",
        )
        command_type = data.get("command_type")
        try:
            normalized_type = CommandType(command_type)
        except (TypeError, ValueError) as exc:
            raise ContractValidationError(
                f"Unsupported command type '{command_type}'"
            ) from exc
        return cls(
            command_id=data.get("command_id"),
            command_type=normalized_type,
            payload=data.get("payload"),
            expected_revision=data.get("expected_revision"),
            contract_version=data.get("contract_version", 1),
        )

    def to_dict(self) -> dict[str, JSONValue]:
        # Frozen dataclasses can still contain caller-mutated dictionaries.
        # Re-run all validation before serialization so mutated commands cannot
        # bypass the contract after construction.
        require_nonempty_string(self.command_id, path="command.command_id")
        require_int(
            self.expected_revision,
            path="command.expected_revision",
            minimum=0,
        )
        if self.contract_version != 1:
            raise ContractValidationError(
                f"Unsupported command contract_version {self.contract_version}"
            )
        payload = clone_json_object(self.payload, path="command.payload")
        _PAYLOAD_VALIDATORS[self.command_type](payload)
        return {
            "contract_version": self.contract_version,
            "command_id": self.command_id,
            "command_type": self.command_type.value,
            "expected_revision": self.expected_revision,
            "payload": payload,
        }
