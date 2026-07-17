"""JSON serialization seam for current World/Human state and core contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .contracts import SaveEnvelope
from .errors import ContractValidationError
from .ids import DeterministicIdSource, IdSource
from .json_types import (
    JSONObject,
    JSONValue,
    clone_json,
    clone_json_object,
    parse_json_safe_int,
)
from .randomness import RandomSource, SeededRandomSource
from .session import GameSession
from .validation import assert_valid_save_envelope, assert_valid_world_state


def _serialize_human(actor: object) -> JSONObject:
    required_fields = (
        "species",
        "first_name",
        "last_name",
        "sex",
        "gender",
        "sexuality",
        "birth_year",
        "birth_month",
        "stats",
        "money",
        "appearance",
        "traits",
        "current_place_id",
        "residence_place_id",
        "jurisdiction_place_id",
        "temporary_occupancy_place_id",
        "structural_status",
        "death_year",
        "death_month",
        "death_reason",
    )
    missing_fields = [field_name for field_name in required_fields if not hasattr(actor, field_name)]
    if missing_fields:
        raise ContractValidationError(
            "Cannot serialize actor missing fields: " + ", ".join(missing_fields)
        )
    state: dict[str, Any] = {
        "actor_type": "human",
        **{
            field_name: getattr(actor, field_name)
            for field_name in required_fields
        },
    }
    return clone_json_object(state, path="world.actor")


def serialize_world(world: object) -> JSONObject:
    """Builds a detached, JSON-safe snapshot of the current World."""
    required_fields = (
        "current_year",
        "current_month",
        "actors",
        "links",
        "places",
        "records",
        "focused_actor_id",
    )
    missing_fields = [field_name for field_name in required_fields if not hasattr(world, field_name)]
    if missing_fields:
        raise ContractValidationError(
            "Cannot serialize world missing fields: " + ", ".join(missing_fields)
        )

    actors = getattr(world, "actors")
    if not isinstance(actors, dict):
        raise ContractValidationError("world.actors must be an object")
    state: JSONObject = {
        "current_year": getattr(world, "current_year"),
        "current_month": getattr(world, "current_month"),
        "actors": {
            actor_id: _serialize_human(actor)
            for actor_id, actor in actors.items()
        },
        "links": clone_json(getattr(world, "links"), path="world.links"),
        "places": clone_json(getattr(world, "places"), path="world.places"),
        "records": clone_json(getattr(world, "records"), path="world.records"),
        "focused_actor_id": getattr(world, "focused_actor_id"),
        "recent_event_ids_by_actor": clone_json(
            getattr(world, "recent_event_ids_by_actor"),
            path="world.recent_event_ids_by_actor",
        ),
        "used_npc_last_names": sorted(
            getattr(world, "_used_npc_last_names", set())
        ),
    }
    assert_valid_world_state(state)
    return state


def deserialize_world(world_state: object) -> object:
    """Restores a current ``World`` without constructors that create records."""
    state = clone_json_object(world_state, path="world")
    assert_valid_world_state(state)

    # These imports are deliberately local: the transport contracts stay
    # standard-library-only at package import time, and neither module imports
    # the curses shell.
    from human import Human
    from world import World

    world = World(
        start_year=state["current_year"],
        start_month=state["current_month"],
    )
    world.places = clone_json(state["places"], path="world.places")
    world.links = clone_json(state["links"], path="world.links")
    world.records = clone_json(state["records"], path="world.records")
    world.recent_event_ids_by_actor = clone_json(
        state["recent_event_ids_by_actor"],
        path="world.recent_event_ids_by_actor",
    )
    world.actors = {}

    actors = state["actors"]
    if not isinstance(actors, dict):  # guarded by invariant validation
        raise ContractValidationError("world.actors must be an object")
    for actor_id, actor_state_value in actors.items():
        actor_state = clone_json_object(
            actor_state_value,
            path=f"world.actors.{actor_id}",
        )
        # Restore through a side-effect-free allocation seam.  Human.__init__
        # is currently deterministic, but bypassing it here prevents future
        # constructor defaults or randomization from consuming a runtime trace.
        actor = Human.__new__(Human)
        actor.species = actor_state["species"]
        actor.first_name = actor_state["first_name"]
        actor.last_name = actor_state["last_name"]
        actor.sex = actor_state["sex"]
        actor.gender = actor_state["gender"]
        actor.sexuality = actor_state["sexuality"]
        actor.birth_year = actor_state["birth_year"]
        actor.birth_month = actor_state["birth_month"]
        actor.stats = clone_json(
            actor_state["stats"],
            path=f"world.actors.{actor_id}.stats",
        )
        actor.money = actor_state["money"]
        actor.appearance = clone_json(
            actor_state["appearance"],
            path=f"world.actors.{actor_id}.appearance",
        )
        actor.traits = clone_json(
            actor_state["traits"],
            path=f"world.actors.{actor_id}.traits",
        )
        actor.current_place_id = actor_state["current_place_id"]
        actor.residence_place_id = actor_state["residence_place_id"]
        actor.jurisdiction_place_id = actor_state["jurisdiction_place_id"]
        actor.temporary_occupancy_place_id = actor_state[
            "temporary_occupancy_place_id"
        ]
        actor.structural_status = actor_state["structural_status"]
        actor.death_year = actor_state["death_year"]
        actor.death_month = actor_state["death_month"]
        actor.death_reason = actor_state["death_reason"]
        world.actors[actor_id] = actor

    world.focused_actor_id = state["focused_actor_id"]
    world._used_npc_last_names = set(state["used_npc_last_names"])
    return world


def build_save_envelope(
    world: object,
    session: GameSession,
    random_source: RandomSource,
    id_source: IdSource,
    *,
    engine_version: str,
    revision: int = 0,
    engine_kind: str = "python-headless",
    metadata: JSONObject | None = None,
    format_version: int = 1,
    schema_version: int = 1,
) -> SaveEnvelope:
    """Captures world/session data plus the injected-source states.

    The headless dispatcher restores this exact state. Terminal compatibility
    paths continue using module-global sources until they adopt the same
    command boundary.
    """
    envelope = SaveEnvelope(
        engine_version=engine_version,
        engine_kind=engine_kind,
        revision=revision,
        world=serialize_world(world),
        session=GameSession.from_dict(session.to_dict()),
        rng=random_source.snapshot(),
        ids=id_source.snapshot(),
        metadata=metadata or {},
        format_version=format_version,
        schema_version=schema_version,
    )
    assert_valid_save_envelope(envelope)
    return envelope


@dataclass(frozen=True, slots=True)
class RestoredSave:
    """Complete runtime data and envelope provenance reconstructed from a save."""

    world: object
    session: GameSession
    random_source: SeededRandomSource
    id_source: DeterministicIdSource
    engine_version: str
    engine_kind: str
    revision: int
    metadata: JSONObject
    format_version: int
    schema_version: int


def restore_save_envelope(envelope: SaveEnvelope) -> RestoredSave:
    """Reconstructs state without running simulation or rewiring old globals."""
    envelope.to_dict()
    return RestoredSave(
        world=deserialize_world(envelope.world),
        session=GameSession.from_dict(envelope.session.to_dict()),
        random_source=SeededRandomSource.from_state(envelope.rng),
        id_source=DeterministicIdSource.from_state(envelope.ids),
        engine_version=envelope.engine_version,
        engine_kind=envelope.engine_kind,
        revision=envelope.revision,
        metadata=clone_json_object(envelope.metadata, path="save.metadata"),
        format_version=envelope.format_version,
        schema_version=envelope.schema_version,
    )


def _reject_json_constant(value: str) -> None:
    raise ContractValidationError(f"save JSON contains invalid constant {value}")


def _reject_duplicate_keys(pairs: list[tuple[str, JSONValue]]) -> JSONObject:
    result: JSONObject = {}
    for key, value in pairs:
        if key in result:
            raise ContractValidationError(f"save JSON contains duplicate key '{key}'")
        result[key] = value
    return result


def dumps_save_envelope(
    envelope: SaveEnvelope,
    *,
    indent: int | None = None,
) -> str:
    """Serializes one validated envelope using canonical key ordering."""
    data = envelope.to_dict()
    return json.dumps(
        data,
        allow_nan=False,
        ensure_ascii=False,
        indent=indent,
        separators=(",", ":") if indent is None else None,
        sort_keys=True,
    )


def loads_save_envelope(serialized: str) -> SaveEnvelope:
    """Parses strict JSON, validates contracts, and checks all invariants."""
    if not isinstance(serialized, str):
        raise ContractValidationError("serialized save must be a string")
    try:
        data = json.loads(
            serialized,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant,
            parse_int=lambda value: parse_json_safe_int(
                value,
                path="save JSON integer",
            ),
        )
    except ContractValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise ContractValidationError(f"Invalid save JSON: {exc.msg}") from exc
    envelope = SaveEnvelope.from_dict(data)
    assert_valid_save_envelope(envelope)
    return envelope
