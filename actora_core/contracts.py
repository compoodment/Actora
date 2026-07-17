"""Save and command-result contracts for the headless engine boundary."""

from __future__ import annotations

from dataclasses import dataclass, field

from .commands import MAX_ADVANCE_MONTHS, CommandType
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
    """Versioned state for the deterministic native runtime boundary.

    The headless dispatcher owns injected RNG/ID sources. The terminal still
    uses compatibility adapters and legacy global sources outside that
    boundary.
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


_CONTINUITY_STATE_FIELDS = {
    "actor_id",
    "focus_actor_name",
    "focus_actor_structural_status",
    "focus_actor_death_year",
    "focus_actor_death_month",
    "focus_actor_death_reason",
    "is_dead",
    "universe_continues",
    "continuity_candidates",
    "continuity_candidate_ids",
    "had_continuity_candidates",
}


def _validate_continuity_state(value: object) -> JSONObject:
    state = clone_json_object(
        value,
        path="result.interruption.continuity_state",
    )
    _reject_unknown_fields(
        state,
        _CONTINUITY_STATE_FIELDS,
        path="result.interruption.continuity_state",
    )
    missing_fields = sorted(_CONTINUITY_STATE_FIELDS - set(state))
    if missing_fields:
        raise ContractValidationError(
            "result.interruption.continuity_state is missing fields: "
            + ", ".join(missing_fields)
        )

    for field_name in (
        "actor_id",
        "focus_actor_structural_status",
        "focus_actor_death_reason",
    ):
        require_nonempty_string(
            state.get(field_name),
            path=f"result.interruption.continuity_state.{field_name}",
        )
    if not isinstance(state.get("focus_actor_name"), str):
        raise ContractValidationError(
            "result.interruption.continuity_state."
            "focus_actor_name must be a string"
        )
    require_int(
        state.get("focus_actor_death_year"),
        path="result.interruption.continuity_state.focus_actor_death_year",
    )
    require_int(
        state.get("focus_actor_death_month"),
        path="result.interruption.continuity_state.focus_actor_death_month",
        minimum=1,
        maximum=12,
    )
    if state.get("focus_actor_structural_status") != "dead":
        raise ContractValidationError(
            "result.interruption.continuity_state."
            "focus_actor_structural_status must be dead"
        )
    if state.get("is_dead") is not True:
        raise ContractValidationError(
            "result.interruption.continuity_state.is_dead must be true"
        )
    if state.get("universe_continues") is not True:
        raise ContractValidationError(
            "result.interruption.continuity_state."
            "universe_continues must be true"
        )

    candidates = state.get("continuity_candidates")
    candidate_ids = state.get("continuity_candidate_ids")
    if not isinstance(candidates, list) or any(
        not isinstance(candidate, dict) for candidate in candidates
    ):
        raise ContractValidationError(
            "result.interruption.continuity_state."
            "continuity_candidates must be an object array"
        )
    if not isinstance(candidate_ids, list) or any(
        not isinstance(candidate_id, str) or not candidate_id
        for candidate_id in candidate_ids
    ):
        raise ContractValidationError(
            "result.interruption.continuity_state."
            "continuity_candidate_ids must be a string array"
        )
    candidate_actor_ids = [
        candidate.get("actor_id") for candidate in candidates
    ]
    if (
        any(
            not isinstance(candidate_id, str) or not candidate_id
            for candidate_id in candidate_actor_ids
        )
        or candidate_actor_ids != candidate_ids
        or len(set(candidate_ids)) != len(candidate_ids)
    ):
        raise ContractValidationError(
            "result.interruption.continuity_state candidate IDs must match"
        )
    had_candidates = state.get("had_continuity_candidates")
    if (
        not isinstance(had_candidates, bool)
        or had_candidates is not bool(candidates)
    ):
        raise ContractValidationError(
            "result.interruption.continuity_state."
            "had_continuity_candidates must match the candidate array"
        )
    return state


def _validate_interruption(value: object) -> JSONObject:
    interruption = clone_json_object(
        value,
        path="result.interruption",
    )
    kind = require_nonempty_string(
        interruption.get("kind"),
        path="result.interruption.kind",
    )
    if kind == "choice_required":
        _reject_unknown_fields(
            interruption,
            {"kind", "choice_id", "remaining_months"},
            path="result.interruption",
        )
        if set(interruption) != {
            "kind",
            "choice_id",
            "remaining_months",
        }:
            raise ContractValidationError(
                "result.interruption.choice_required must contain "
                "kind, choice_id, and remaining_months"
            )
        choice_id = require_nonempty_string(
            interruption.get("choice_id"),
            path="result.interruption.choice_id",
        )
        remaining_months = require_int(
            interruption.get("remaining_months"),
            path="result.interruption.remaining_months",
            minimum=0,
            maximum=MAX_ADVANCE_MONTHS,
        )
        return {
            "kind": kind,
            "choice_id": choice_id,
            "remaining_months": remaining_months,
        }
    if kind == "continuation_required":
        _reject_unknown_fields(
            interruption,
            {"kind", "continuity_state"},
            path="result.interruption",
        )
        if set(interruption) != {"kind", "continuity_state"}:
            raise ContractValidationError(
                "result.interruption.continuation_required must contain "
                "kind and continuity_state"
            )
        return {
            "kind": kind,
            "continuity_state": _validate_continuity_state(
                interruption.get("continuity_state")
            ),
        }
    raise ContractValidationError(
        f"Unsupported result interruption kind '{kind}'"
    )


def _saved_actor_full_name(actor: JSONObject) -> str:
    return (
        f"{actor.get('first_name', '')} "
        f"{actor.get('last_name', '')}"
    ).strip()


def _strict_json_equal(left: object, right: object) -> bool:
    """Compares JSON values without Python's bool/int numeric coercion."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (
            left.keys() == right.keys()
            and all(
                _strict_json_equal(left[key], right[key])
                for key in left
            )
        )
    if isinstance(left, list):
        return (
            len(left) == len(right)
            and all(
                _strict_json_equal(left_item, right_item)
                for left_item, right_item in zip(left, right)
            )
        )
    return left == right


def _saved_actor_lifecycle(
    actor: JSONObject,
    *,
    current_year: int,
    current_month: int,
) -> tuple[int, str]:
    birth_year = actor["birth_year"]
    birth_month = actor["birth_month"]
    age_years = current_year - birth_year
    if current_month < birth_month:
        age_years -= 1
    age_years = max(0, age_years)
    if age_years < 3:
        life_stage = "Infant"
    elif age_years < 10:
        life_stage = "Child"
    elif age_years < 18:
        life_stage = "Teenager"
    elif age_years < 25:
        life_stage = "Young Adult"
    elif age_years < 65:
        life_stage = "Adult"
    else:
        life_stage = "Elder"
    return age_years, life_stage


def _saved_parent_ids(
    world: JSONObject,
    actor_id: str,
) -> tuple[str | None, str | None]:
    links = world["links"]

    def targets(
        role: str,
        *,
        require_origin: bool,
    ) -> list[str]:
        result: list[str] = []
        for link in links:
            if (
                link.get("source_id") != actor_id
                or link.get("type") != "family"
                or link.get("role") != role
            ):
                continue
            if (
                require_origin
                and link.get("metadata", {}).get("is_origin_family")
                is not True
            ):
                continue
            target_id = link.get("target_id")
            if isinstance(target_id, str) and target_id not in result:
                result.append(target_id)
        return result

    origin_mothers = targets("mother", require_origin=True)
    origin_fathers = targets("father", require_origin=True)
    if origin_mothers or origin_fathers:
        return (
            origin_mothers[0] if origin_mothers else None,
            origin_fathers[0] if origin_fathers else None,
        )
    mothers = targets("mother", require_origin=False)
    fathers = targets("father", require_origin=False)
    return (
        mothers[0] if mothers else None,
        fathers[0] if fathers else None,
    )


def _saved_sibling_ids(
    world: JSONObject,
    actor_id: str,
) -> set[str]:
    mother_id, father_id = _saved_parent_ids(world, actor_id)
    parent_ids = {
        parent_id
        for parent_id in (mother_id, father_id)
        if parent_id is not None
    }
    if not parent_ids:
        return set()

    sibling_ids: set[str] = set()
    for other_actor_id in sorted(world["actors"]):
        if other_actor_id == actor_id:
            continue
        other_mother_id, other_father_id = _saved_parent_ids(
            world,
            other_actor_id,
        )
        other_parent_ids = {
            parent_id
            for parent_id in (other_mother_id, other_father_id)
            if parent_id is not None
        }
        if parent_ids.intersection(other_parent_ids):
            sibling_ids.add(other_actor_id)
    return sibling_ids


def _continuity_link_sort_key(link: JSONObject) -> tuple[object, ...]:
    role_priority = {
        "child": 0,
        "sibling": 1,
        "mother": 2,
        "father": 2,
    }
    return (
        link.get("type") or "",
        role_priority.get(link.get("role"), 9),
        link.get("role") or "",
        link.get("source_id") or "",
        link.get("target_id") or "",
    )


def _saved_family_branch_label(
    focused_actor_id: str,
    links: list[JSONObject],
) -> str | None:
    outgoing_roles = {
        link.get("role")
        for link in links
        if (
            link.get("source_id") == focused_actor_id
            and link.get("type") == "family"
        )
    }
    incoming_roles = {
        link.get("role")
        for link in links
        if (
            link.get("target_id") == focused_actor_id
            and link.get("type") == "family"
        )
    }
    if "mother" in outgoing_roles:
        return "Maternal"
    if "father" in outgoing_roles:
        return "Paternal"
    if "child" in incoming_roles:
        return "Descendant"
    return None


def _canonical_continuity_state(
    save: SaveEnvelope,
    focused_actor_id: str,
) -> JSONObject:
    """Rebuilds the world-owned continuity snapshot from saved JSON only."""
    world = save.world
    actors = world["actors"]
    places = world["places"]
    focused_actor = actors[focused_actor_id]
    grouped_links: dict[str, list[JSONObject]] = {}
    for link in world["links"]:
        source_id = link.get("source_id")
        target_id = link.get("target_id")
        if source_id == focused_actor_id:
            candidate_id = target_id
        elif target_id == focused_actor_id:
            candidate_id = source_id
        else:
            continue
        if (
            not isinstance(candidate_id, str)
            or candidate_id == focused_actor_id
            or candidate_id not in actors
        ):
            continue
        grouped_links.setdefault(candidate_id, []).append(link)

    sibling_ids = _saved_sibling_ids(world, focused_actor_id)
    candidates: list[JSONObject] = []
    family_role_labels = {
        "mother": "Mother",
        "father": "Father",
        "child": "Child",
        "sibling": "Sibling",
    }
    for candidate_id, related_links in grouped_links.items():
        candidate_actor = actors[candidate_id]
        if candidate_actor.get("structural_status") != "active":
            continue
        valid_links: list[JSONObject] = []
        for link in related_links:
            if link.get("type") == "social":
                metadata = link.get("metadata", {})
                if (
                    metadata.get("status", "active") != "active"
                    and metadata.get("ended_reason") != "death"
                ):
                    continue
            valid_links.append(link)
        if not valid_links:
            continue

        actor_perspective_links = [
            link
            for link in valid_links
            if (
                link.get("source_id") == focused_actor_id
                and link.get("target_id") == candidate_id
            )
        ]
        defining_link = sorted(
            actor_perspective_links or valid_links,
            key=_continuity_link_sort_key,
        )[0]
        link_type = defining_link.get("type")
        link_role = defining_link.get("role")
        if candidate_id in sibling_ids:
            if candidate_actor.get("sex") == "Female":
                relationship_label = "Sister"
            elif candidate_actor.get("sex") == "Male":
                relationship_label = "Brother"
            else:
                relationship_label = "Sibling"
        elif link_type == "family" and link_role in family_role_labels:
            relationship_label = family_role_labels[link_role]
        else:
            relationship_label = (
                f"{link_type}/{link_role}"
                if link_role
                else str(link_type)
            )

        if candidate_id in sibling_ids:
            relationship_priority = 1
        elif link_type == "family" and link_role == "child":
            relationship_priority = 0
        elif (
            link_type == "family"
            and link_role in {"mother", "father"}
        ):
            relationship_priority = 2
        elif link_type == "family":
            relationship_priority = 3
        else:
            relationship_priority = 9

        age, life_stage = _saved_actor_lifecycle(
            candidate_actor,
            current_year=world["current_year"],
            current_month=world["current_month"],
        )
        place = places.get(candidate_actor.get("current_place_id"))
        candidates.append(
            {
                "actor_id": candidate_id,
                "full_name": _saved_actor_full_name(candidate_actor),
                "link_type": link_type,
                "link_role": link_role,
                "relationship_label": relationship_label,
                "relationship_priority": relationship_priority,
                "family_branch_label": _saved_family_branch_label(
                    focused_actor_id,
                    related_links,
                ),
                "structural_status": candidate_actor[
                    "structural_status"
                ],
                "is_alive": True,
                "age": age,
                "life_stage": life_stage,
                "current_place_name": (
                    place.get("name")
                    if isinstance(place, dict)
                    else None
                ),
            }
        )

    candidates.sort(
        key=lambda candidate: (
            candidate.get("relationship_priority", 9),
            str(candidate.get("full_name", "")).casefold(),
            candidate.get("link_type") or "",
            candidate.get("link_role") or "",
            candidate.get("actor_id") or "",
        )
    )
    return {
        "actor_id": focused_actor_id,
        "focus_actor_name": _saved_actor_full_name(focused_actor),
        "focus_actor_structural_status": focused_actor[
            "structural_status"
        ],
        "focus_actor_death_year": focused_actor["death_year"],
        "focus_actor_death_month": focused_actor["death_month"],
        "focus_actor_death_reason": focused_actor["death_reason"],
        "is_dead": focused_actor["structural_status"] != "active",
        "universe_continues": True,
        "continuity_candidates": candidates,
        "continuity_candidate_ids": [
            candidate["actor_id"] for candidate in candidates
        ],
        "had_continuity_candidates": bool(candidates),
    }


def _assert_interruption_matches_result(
    interruption: JSONObject | None,
    *,
    command_type: CommandType,
    ok: bool,
    save: SaveEnvelope | None,
) -> None:
    if interruption is None:
        if (
            ok
            and command_type is CommandType.ADVANCE_TIME
            and save is not None
        ):
            if save.session.pending_choice is not None:
                raise ContractValidationError(
                    "advance result must surface its saved pending choice"
                )
            focused_actor = save.world.get("actors", {}).get(
                save.session.focused_actor_id
            )
            if (
                isinstance(focused_actor, dict)
                and focused_actor.get("structural_status") == "dead"
            ):
                raise ContractValidationError(
                    "advance result must surface its dead saved focus"
                )
        return
    if not ok:
        raise ContractValidationError(
            "failed result must not contain an interruption"
        )
    if command_type is not CommandType.ADVANCE_TIME:
        raise ContractValidationError(
            "only advance_time may return an interruption"
        )
    if save is None:
        raise ContractValidationError(
            "interrupted result must contain a save"
        )

    kind = interruption["kind"]
    if kind == "choice_required":
        pending_choice = save.session.pending_choice
        if pending_choice is None:
            raise ContractValidationError(
                "choice interruption requires a saved pending choice"
            )
        if interruption["choice_id"] != pending_choice.get("choice_id"):
            raise ContractValidationError(
                "result interruption choice_id must match the saved choice"
            )
        if (
            interruption["remaining_months"]
            != save.session.remaining_skip_months
        ):
            raise ContractValidationError(
                "result interruption remaining_months must match the save"
            )
        return

    if save.session.pending_choice is not None:
        raise ContractValidationError(
            "continuation interruption cannot contain a pending choice"
        )
    continuity_state = interruption["continuity_state"]
    focused_actor_id = save.session.focused_actor_id
    if continuity_state.get("actor_id") != focused_actor_id:
        raise ContractValidationError(
            "continuation interruption actor_id must match the save focus"
        )
    focused_actor = save.world.get("actors", {}).get(focused_actor_id)
    if (
        not isinstance(focused_actor, dict)
        or focused_actor.get("structural_status") != "dead"
    ):
        raise ContractValidationError(
            "continuation interruption requires a dead saved focus"
        )
    canonical_state = _canonical_continuity_state(
        save,
        focused_actor_id,
    )
    if not _strict_json_equal(continuity_state, canonical_state):
        raise ContractValidationError(
            "continuation interruption must match the canonical saved state"
        )


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Structured result returned by the headless engine dispatcher."""

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
                _validate_interruption(self.interruption),
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
        _assert_interruption_matches_result(
            self.interruption,
            command_type=self.command_type,
            ok=self.ok,
            save=self.save,
        )

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
        validated_interruption = (
            _validate_interruption(self.interruption)
            if self.interruption is not None
            else None
        )
        _assert_interruption_matches_result(
            validated_interruption,
            command_type=self.command_type,
            ok=self.ok,
            save=self.save,
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
                validated_interruption
                if validated_interruption is not None
                else None
            ),
            "error": self.error.to_dict() if self.error is not None else None,
        }
