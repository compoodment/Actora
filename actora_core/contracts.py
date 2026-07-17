"""Save and command-result contracts for the headless engine boundary."""

from __future__ import annotations

from dataclasses import dataclass, field

from .commands import CommandType
from .errors import ContractValidationError
from .ids import IdState
from .json_types import (
    JSONObject,
    JSONValue,
    clone_json,
    clone_json_object,
    require_int,
    require_nonempty_string,
)
from .randomness import RandomState
from .session import GameSession


def _reject_unknown_fields(
    data: dict[object, object],
    allowed_fields: set[str],
    *,
    path: str,
) -> None:
    unknown_fields = [
        field for field in data
        if not isinstance(field, str) or field not in allowed_fields
    ]
    if unknown_fields:
        rendered = ", ".join(sorted(str(field) for field in unknown_fields))
        raise ContractValidationError(
            f"{path} contains unknown fields: {rendered}"
        )


@dataclass(slots=True)
class SaveEnvelope:
    """Versioned state intended for the future deterministic runtime.

    The current TUI has not adopted the injected RNG/ID sources yet, so a
    schema-1 envelope proves lossless data transport but does not by itself
    make existing gameplay calls deterministically replayable.
    """

    engine_version: str
    world: JSONObject
    session: GameSession
    rng: RandomState
    ids: IdState
    revision: int = 0
    engine_kind: str = "python-headless"
    metadata: JSONObject = field(default_factory=dict)
    format_version: int = 1
    schema_version: int = 1

    def __post_init__(self) -> None:
        self.engine_version = require_nonempty_string(
            self.engine_version,
            path="save.engine_version",
        )
        self.engine_kind = require_nonempty_string(
            self.engine_kind,
            path="save.engine_kind",
        )
        # Parsing and execution authority are deliberately separate. A foreign
        # kind must remain parseable so the dispatcher can return a structured,
        # byte-preserving engine_kind_mismatch; only the dispatcher decides
        # which exact literal it is allowed to execute.
        self.world = clone_json_object(self.world, path="save.world")
        if not isinstance(self.session, GameSession):
            raise ContractValidationError("save.session must be a GameSession")
        self.session = GameSession.from_dict(self.session.to_dict())
        if not isinstance(self.rng, RandomState):
            raise ContractValidationError("save.rng must be a RandomState")
        if not isinstance(self.ids, IdState):
            raise ContractValidationError("save.ids must be an IdState")
        self.metadata = clone_json_object(self.metadata, path="save.metadata")
        self.revision = require_int(
            self.revision,
            path="save.revision",
            minimum=0,
        )
        self.format_version = require_int(
            self.format_version,
            path="save.format_version",
            minimum=1,
        )
        self.schema_version = require_int(
            self.schema_version,
            path="save.schema_version",
            minimum=1,
        )
        if self.format_version != 1:
            raise ContractValidationError(
                f"Unsupported save format_version {self.format_version}"
            )
        if self.schema_version != 1:
            raise ContractValidationError(
                f"Unsupported save schema_version {self.schema_version}"
            )

    @classmethod
    def from_dict(cls, data: object) -> "SaveEnvelope":
        if not isinstance(data, dict):
            raise ContractValidationError("save must be an object")
        allowed_fields = {
            "format_version",
            "schema_version",
            "engine_version",
            "engine_kind",
            "revision",
            "world",
            "session",
            "rng",
            "ids",
            "metadata",
        }
        unknown_fields = [
            field
            for field in data
            if not isinstance(field, str) or field not in allowed_fields
        ]
        if unknown_fields:
            rendered = ", ".join(
                sorted(str(field) for field in unknown_fields)
            )
            raise ContractValidationError(
                "save contains unknown fields: " + rendered
            )
        format_version = require_int(
            data.get("format_version", 1),
            path="save.format_version",
            minimum=1,
        )
        schema_version = require_int(
            data.get("schema_version", 1),
            path="save.schema_version",
            minimum=1,
        )
        if format_version != 1:
            raise ContractValidationError(
                f"Unsupported save format_version {format_version}"
            )
        if schema_version != 1:
            raise ContractValidationError(
                f"Unsupported save schema_version {schema_version}"
            )
        return cls(
            format_version=format_version,
            schema_version=schema_version,
            engine_version=data.get("engine_version"),
            engine_kind=data.get("engine_kind", "python-headless"),
            revision=data.get("revision", 0),
            world=data.get("world"),
            session=GameSession.from_dict(data.get("session")),
            rng=RandomState.from_dict(data.get("rng")),
            ids=IdState.from_dict(data.get("ids")),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, JSONValue]:
        require_nonempty_string(self.engine_version, path="save.engine_version")
        require_nonempty_string(self.engine_kind, path="save.engine_kind")
        require_int(self.revision, path="save.revision", minimum=0)
        format_version = require_int(
            self.format_version,
            path="save.format_version",
            minimum=1,
        )
        schema_version = require_int(
            self.schema_version,
            path="save.schema_version",
            minimum=1,
        )
        if format_version != 1:
            raise ContractValidationError(
                f"Unsupported save format_version {self.format_version}"
            )
        if schema_version != 1:
            raise ContractValidationError(
                f"Unsupported save schema_version {self.schema_version}"
            )
        if not isinstance(self.session, GameSession):
            raise ContractValidationError("save.session must be a GameSession")
        if not isinstance(self.rng, RandomState):
            raise ContractValidationError("save.rng must be a RandomState")
        if not isinstance(self.ids, IdState):
            raise ContractValidationError("save.ids must be an IdState")
        validated_session = GameSession.from_dict(self.session.to_dict())
        from .validation import assert_valid_save_envelope

        assert_valid_save_envelope(self)
        return {
            "format_version": format_version,
            "schema_version": schema_version,
            "engine_version": self.engine_version,
            "engine_kind": self.engine_kind,
            "revision": self.revision,
            "world": clone_json_object(self.world, path="save.world"),
            "session": validated_session.to_dict(),
            "rng": self.rng.to_dict(),
            "ids": self.ids.to_dict(),
            "metadata": clone_json_object(self.metadata, path="save.metadata"),
        }


@dataclass(frozen=True, slots=True)
class CommandError:
    """Structured engine error suitable for any presentation layer."""

    code: str
    message: str
    details: JSONObject = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_nonempty_string(self.code, path="result.error.code")
        require_nonempty_string(self.message, path="result.error.message")
        object.__setattr__(
            self,
            "details",
            clone_json_object(self.details, path="result.error.details"),
        )

    @classmethod
    def from_dict(cls, data: object) -> "CommandError":
        if not isinstance(data, dict):
            raise ContractValidationError("result.error must be an object")
        _reject_unknown_fields(
            data,
            {"code", "message", "details"},
            path="result.error",
        )
        return cls(
            code=data.get("code"),
            message=data.get("message"),
            details=data.get("details", {}),
        )

    def to_dict(self) -> dict[str, JSONValue]:
        require_nonempty_string(self.code, path="result.error.code")
        require_nonempty_string(self.message, path="result.error.message")
        return {
            "code": self.code,
            "message": self.message,
            "details": clone_json_object(
                self.details,
                path="result.error.details",
            ),
        }


def _clone_object_sequence(
    value: object,
    *,
    path: str,
) -> tuple[JSONObject, ...]:
    if not isinstance(value, (list, tuple)):
        raise ContractValidationError(f"{path} must be an array")
    return tuple(
        clone_json_object(item, path=f"{path}[{index}]")
        for index, item in enumerate(value)
    )


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Structured result returned by the future engine dispatcher."""

    command_id: str
    command_type: CommandType
    ok: bool
    revision: int
    save: SaveEnvelope | None
    events: tuple[JSONObject, ...] = ()
    effects: tuple[JSONObject, ...] = ()
    interruption: JSONObject | None = None
    error: CommandError | None = None
    contract_version: int = 1

    def __post_init__(self) -> None:
        require_nonempty_string(self.command_id, path="result.command_id")
        if isinstance(self.command_type, str) and not isinstance(
            self.command_type,
            CommandType,
        ):
            try:
                object.__setattr__(self, "command_type", CommandType(self.command_type))
            except ValueError as exc:
                raise ContractValidationError(
                    f"Unsupported result command type '{self.command_type}'"
                ) from exc
        if not isinstance(self.command_type, CommandType):
            raise ContractValidationError("result.command_type is invalid")
        if not isinstance(self.ok, bool):
            raise ContractValidationError("result.ok must be a boolean")
        require_int(self.revision, path="result.revision", minimum=0)
        require_int(
            self.contract_version,
            path="result.contract_version",
            minimum=1,
        )
        if self.contract_version != 1:
            raise ContractValidationError(
                f"Unsupported result contract_version {self.contract_version}"
            )
        object.__setattr__(
            self,
            "events",
            _clone_object_sequence(self.events, path="result.events"),
        )
        object.__setattr__(
            self,
            "effects",
            _clone_object_sequence(self.effects, path="result.effects"),
        )
        if self.interruption is not None:
            object.__setattr__(
                self,
                "interruption",
                clone_json_object(
                    self.interruption,
                    path="result.interruption",
                ),
            )
        if self.ok:
            if self.save is None:
                raise ContractValidationError("successful result must contain save")
            if self.error is not None:
                raise ContractValidationError("successful result must not contain error")
        elif self.error is None:
            raise ContractValidationError("failed result must contain error")
        if self.save is not None and not isinstance(self.save, SaveEnvelope):
            raise ContractValidationError("result.save must be a SaveEnvelope or null")
        if self.error is not None and not isinstance(self.error, CommandError):
            raise ContractValidationError("result.error must be a CommandError or null")
        if self.save is not None and self.save.revision != self.revision:
            raise ContractValidationError(
                "result.revision must match result.save.revision"
            )
        if self.save is not None:
            self.save.to_dict()

    @classmethod
    def from_dict(cls, data: object) -> "CommandResult":
        if not isinstance(data, dict):
            raise ContractValidationError("result must be an object")
        _reject_unknown_fields(
            data,
            {
                "contract_version",
                "command_id",
                "command_type",
                "ok",
                "revision",
                "save",
                "events",
                "effects",
                "interruption",
                "error",
            },
            path="result",
        )
        try:
            command_type = CommandType(data.get("command_type"))
        except (TypeError, ValueError) as exc:
            raise ContractValidationError(
                f"Unsupported result command type '{data.get('command_type')}'"
            ) from exc
        save_data = data.get("save")
        error_data = data.get("error")
        return cls(
            contract_version=data.get("contract_version", 1),
            command_id=data.get("command_id"),
            command_type=command_type,
            ok=data.get("ok"),
            revision=data.get("revision"),
            save=SaveEnvelope.from_dict(save_data) if save_data is not None else None,
            events=data.get("events", []),
            effects=data.get("effects", []),
            interruption=data.get("interruption"),
            error=CommandError.from_dict(error_data) if error_data is not None else None,
        )

    def to_dict(self) -> dict[str, JSONValue]:
        # Revalidate nested mutable values immediately before crossing the
        # transport boundary.
        require_nonempty_string(self.command_id, path="result.command_id")
        require_int(self.revision, path="result.revision", minimum=0)
        if self.contract_version != 1:
            raise ContractValidationError(
                f"Unsupported result contract_version {self.contract_version}"
            )
        save_data: dict[str, JSONValue] | None = None
        if self.save is not None:
            save_data = self.save.to_dict()
            if self.save.revision != self.revision:
                raise ContractValidationError(
                    "result.revision must match result.save.revision"
                )
        return {
            "contract_version": self.contract_version,
            "command_id": self.command_id,
            "command_type": self.command_type.value,
            "ok": self.ok,
            "revision": self.revision,
            "save": save_data,
            "events": clone_json(list(self.events), path="result.events"),
            "effects": clone_json(list(self.effects), path="result.effects"),
            "interruption": (
                clone_json_object(
                    self.interruption,
                    path="result.interruption",
                )
                if self.interruption is not None
                else None
            ),
            "error": self.error.to_dict() if self.error is not None else None,
        }
