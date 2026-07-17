"""Read-only invariant checks for serialized world and save state."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from mechanics import (
    EXERCISE_SUBTYPES,
    HANG_OUT_TIME_COST,
    READ_SUBTYPES,
    REST_SUBTYPES,
    TRAIT_DEFINITIONS,
)

from .contracts import SaveEnvelope
from .errors import InvariantError, InvariantViolation
from .json_types import MAX_SAFE_INTEGER, MIN_SAFE_INTEGER

_HUMAN_STAT_KEYS = {
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
_SIGNED_STAT_KEYS = {"memory", "stress"}
_ACTOR_PLACE_FIELDS = (
    "current_place_id",
    "residence_place_id",
    "jurisdiction_place_id",
    "temporary_occupancy_place_id",
)
_APPEARANCE_FIELDS = {"eye_color", "hair_color", "skin_tone"}
_WORLD_FIELDS = {
    "current_year",
    "current_month",
    "actors",
    "links",
    "places",
    "records",
    "focused_actor_id",
    "recent_event_ids_by_actor",
    "used_npc_last_names",
}
_HUMAN_FIELDS = {
    "actor_type",
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
}
_LINK_FIELDS = {"source_id", "target_id", "type", "role", "metadata"}
_SOCIAL_METADATA_FIELDS = {
    "closeness",
    "status",
    "closeness_history_months",
    "ended_reason",
    "ended_year",
    "ended_month",
    "met_year",
    "met_month",
    "met_place_id",
}
_PERSONAL_ACTION_FIELDS = {
    "action_id",
    "action_type",
    "subtype_id",
    "label",
    "time_cost",
    "stat_changes",
    "event_text",
}
_SPEND_TIME_ACTION_FIELDS = {
    "action_id",
    "action_type",
    "target_actor_id",
    "label",
    "time_cost",
}
_PERSONAL_ACTIONS = {
    action["id"]: action
    for action in (*EXERCISE_SUBTYPES, *READ_SUBTYPES, *REST_SUBTYPES)
}
_PERSONAL_CHOICE_ACTION_IDS = {
    "select_exercise_subtype": {
        action["id"] for action in EXERCISE_SUBTYPES
    },
    "select_read_subtype": {
        action["id"] for action in READ_SUBTYPES
    },
    "select_rest_subtype": {
        action["id"] for action in REST_SUBTYPES
    },
}
_PENDING_CHOICE_FIELDS = {
    "choice_id",
    "title",
    "text",
    "question",
    "options",
    "selected_option_id",
    "skippable",
    "default_value",
}
_CHOICE_OPTION_FIELDS = {"option_id", "label", "value"}
_NON_TARGET_CHOICE_IDS = {
    "gender_identity",
    "sexuality",
    "meeting_npc",
}


def _is_int(value: object) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER
    )


def _is_finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    if isinstance(value, int):
        return _is_int(value)
    return math.isfinite(value) and MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER


def _unknown_fields(
    value: Mapping[object, object],
    allowed_fields: set[str],
) -> list[str]:
    return sorted(
        str(field)
        for field in value
        if not isinstance(field, str) or field not in allowed_fields
    )


def _social_role_for_closeness(closeness: int | float) -> str:
    if closeness >= 70:
        return "close_friend"
    if closeness >= 30:
        return "friend"
    return "acquaintance"


def _social_tier_label(closeness: int | float) -> str:
    return _social_role_for_closeness(closeness).replace("_", " ").title()


def _actor_is_alive(actor_data: object) -> bool:
    return (
        isinstance(actor_data, Mapping)
        and actor_data.get("structural_status") == "active"
    )


def _actor_full_name(actor_data: object) -> str | None:
    if not isinstance(actor_data, Mapping):
        return None
    first_name = actor_data.get("first_name")
    last_name = actor_data.get("last_name")
    if not isinstance(first_name, str) or not isinstance(last_name, str):
        return None
    return f"{first_name} {last_name}".strip()


def _parse_issued_id(
    identifier: object,
    *,
    namespace: str,
    role: str,
) -> int | None:
    """Returns the canonical sequential value for one engine-issued ID."""
    if not isinstance(identifier, str):
        return None
    prefix = f"{namespace}_{role}_"
    if not identifier.startswith(prefix):
        return None
    suffix = identifier[len(prefix):]
    if (
        not 8 <= len(suffix) <= 16
        or not suffix.isascii()
        or not suffix.isdigit()
    ):
        return None
    value = int(suffix)
    if value < 1 or identifier != f"{prefix}{value:08d}":
        return None
    return value


def _monthly_free_hours(actor_data: object) -> float | None:
    if not isinstance(actor_data, Mapping):
        return None
    traits = actor_data.get("traits")
    if not isinstance(traits, list):
        return None
    sleep_modifier = 0.0
    for trait in traits:
        if not isinstance(trait, str):
            return None
        sleep_modifier += TRAIT_DEFINITIONS.get(trait, {}).get(
            "sleep_modifier",
            0.0,
        )
    return 720 - ((8.0 + sleep_modifier) * 30) - 120


def _add(
    violations: list[InvariantViolation],
    code: str,
    path: str,
    message: str,
) -> None:
    violations.append(InvariantViolation(code=code, path=path, message=message))


def collect_world_invariant_violations(
    world_state: object,
) -> tuple[InvariantViolation, ...]:
    """Collects structural violations without mutating or constructing a World."""
    violations: list[InvariantViolation] = []
    if not isinstance(world_state, Mapping):
        return (
            InvariantViolation(
                code="world_not_object",
                path="world",
                message="world state must be an object",
            ),
        )

    current_year = world_state.get("current_year")
    current_month = world_state.get("current_month")
    unknown_world_fields = _unknown_fields(world_state, _WORLD_FIELDS)
    if unknown_world_fields:
        _add(
            violations,
            "unknown_world_fields",
            "world",
            "unknown " + ", ".join(str(field) for field in unknown_world_fields),
        )
    if not _is_int(current_year):
        _add(violations, "invalid_year", "world.current_year", "must be an integer")
    if not _is_int(current_month) or not 1 <= current_month <= 12:
        _add(
            violations,
            "invalid_month",
            "world.current_month",
            "must be an integer from 1 through 12",
        )

    actors = world_state.get("actors")
    places = world_state.get("places")
    links = world_state.get("links")
    records = world_state.get("records")
    if not isinstance(actors, Mapping):
        _add(violations, "actors_not_object", "world.actors", "must be an object")
        actors = {}
    if not isinstance(places, Mapping):
        _add(violations, "places_not_object", "world.places", "must be an object")
        places = {}
    if not isinstance(links, list):
        _add(violations, "links_not_array", "world.links", "must be an array")
        links = []
    if not isinstance(records, list):
        _add(violations, "records_not_array", "world.records", "must be an array")
        records = []

    actor_ids = set(actors)
    place_ids = set(places)
    for actor_id, actor_data in actors.items():
        path = f"world.actors.{actor_id}"
        if not isinstance(actor_id, str) or not actor_id:
            _add(violations, "invalid_actor_id", path, "actor ID must be a non-empty string")
        if not isinstance(actor_data, Mapping):
            _add(violations, "actor_not_object", path, "actor must be an object")
            continue
        unknown_actor_fields = _unknown_fields(actor_data, _HUMAN_FIELDS)
        if unknown_actor_fields:
            _add(
                violations,
                "unknown_actor_fields",
                path,
                "unknown "
                + ", ".join(str(field) for field in unknown_actor_fields),
            )
        if actor_data.get("actor_type") != "human":
            _add(
                violations,
                "unsupported_actor_type",
                f"{path}.actor_type",
                "only human actors are serializable in schema 1",
            )
        for identity_field in ("species", "first_name", "last_name", "sex", "gender"):
            if not isinstance(actor_data.get(identity_field), str):
                _add(
                    violations,
                    "invalid_actor_identity",
                    f"{path}.{identity_field}",
                    "must be a string",
                )
        if actor_data.get("sexuality") is not None and not isinstance(
            actor_data.get("sexuality"),
            str,
        ):
            _add(
                violations,
                "invalid_actor_identity",
                f"{path}.sexuality",
                "must be a string or null",
            )
        if not _is_int(actor_data.get("birth_year")):
            _add(
                violations,
                "invalid_birth_year",
                f"{path}.birth_year",
                "must be an integer",
            )
        birth_month = actor_data.get("birth_month")
        if not _is_int(birth_month) or not 1 <= birth_month <= 12:
            _add(
                violations,
                "invalid_birth_month",
                f"{path}.birth_month",
                "must be an integer from 1 through 12",
            )

        stats = actor_data.get("stats")
        if not isinstance(stats, Mapping):
            _add(violations, "stats_not_object", f"{path}.stats", "must be an object")
        else:
            missing_stats = sorted(_HUMAN_STAT_KEYS - set(stats))
            extra_stats = sorted(set(stats) - _HUMAN_STAT_KEYS)
            if missing_stats:
                _add(
                    violations,
                    "missing_stats",
                    f"{path}.stats",
                    f"missing {', '.join(missing_stats)}",
                )
            if extra_stats:
                _add(
                    violations,
                    "unknown_stats",
                    f"{path}.stats",
                    f"unknown {', '.join(str(item) for item in extra_stats)}",
                )
            for stat_name, stat_value in stats.items():
                stat_path = f"{path}.stats.{stat_name}"
                if not _is_finite_number(stat_value):
                    _add(
                        violations,
                        "invalid_stat_value",
                        stat_path,
                        "must be a finite number",
                    )
                    continue
                minimum, maximum = (
                    (-50, 50) if stat_name in _SIGNED_STAT_KEYS else (0, 100)
                )
                if not minimum <= stat_value <= maximum:
                    _add(
                        violations,
                        "stat_out_of_range",
                        stat_path,
                        f"must be between {minimum} and {maximum}",
                    )
        if not _is_finite_number(actor_data.get("money")):
            _add(
                violations,
                "invalid_money",
                f"{path}.money",
                "must be a finite number",
            )
        appearance = actor_data.get("appearance")
        if not isinstance(appearance, Mapping):
            _add(
                violations,
                "appearance_not_object",
                f"{path}.appearance",
                "must be an object",
            )
        else:
            if set(appearance) != _APPEARANCE_FIELDS:
                _add(
                    violations,
                    "invalid_appearance_shape",
                    f"{path}.appearance",
                    "must contain exactly eye_color, hair_color, and skin_tone",
                )
            for field_name in _APPEARANCE_FIELDS:
                value = appearance.get(field_name)
                if not isinstance(value, str) or not value:
                    _add(
                        violations,
                        "invalid_appearance_value",
                        f"{path}.appearance.{field_name}",
                        "must be a non-empty string",
                    )
        traits = actor_data.get("traits")
        if not isinstance(traits, list) or any(not isinstance(item, str) for item in traits):
            _add(
                violations,
                "traits_not_string_array",
                f"{path}.traits",
                "must be an array of strings",
            )
        elif (
            len(traits) != 4
            or len(set(traits)) != 4
            or any(trait not in TRAIT_DEFINITIONS for trait in traits)
        ):
            _add(
                violations,
                "invalid_human_traits",
                f"{path}.traits",
                "must contain exactly 4 unique canonical human traits",
            )

        for field_name in _ACTOR_PLACE_FIELDS:
            place_id = actor_data.get(field_name)
            if place_id is not None and (
                not isinstance(place_id, str) or place_id not in place_ids
            ):
                _add(
                    violations,
                    "dangling_actor_place",
                    f"{path}.{field_name}",
                    f"references unknown place '{place_id}'",
                )

        status = actor_data.get("structural_status")
        death_year = actor_data.get("death_year")
        death_month = actor_data.get("death_month")
        death_reason = actor_data.get("death_reason")
        if not isinstance(status, str) or status not in {"active", "dead"}:
            _add(
                violations,
                "invalid_structural_status",
                f"{path}.structural_status",
                "must be active or dead",
            )
        elif status == "active":
            if any(value is not None for value in (death_year, death_month, death_reason)):
                _add(
                    violations,
                    "active_actor_has_death_state",
                    path,
                    "active actor must not contain death state",
                )
        else:
            if not _is_int(death_year):
                _add(
                    violations,
                    "dead_actor_missing_year",
                    f"{path}.death_year",
                    "dead actor must contain an integer death year",
                )
            if not _is_int(death_month) or not 1 <= death_month <= 12:
                _add(
                    violations,
                    "dead_actor_missing_month",
                    f"{path}.death_month",
                    "dead actor must contain a death month from 1 through 12",
                )
            if not isinstance(death_reason, str) or not death_reason:
                _add(
                    violations,
                    "dead_actor_missing_reason",
                    f"{path}.death_reason",
                    "dead actor must contain a reason",
                )

    for place_id, place_data in places.items():
        path = f"world.places.{place_id}"
        if not isinstance(place_data, Mapping):
            _add(violations, "place_not_object", path, "place must be an object")
            continue
        if place_data.get("place_id") != place_id:
            _add(
                violations,
                "place_id_mismatch",
                f"{path}.place_id",
                "stored place ID must match its registry key",
            )
        for field_name in ("name", "kind"):
            if not isinstance(place_data.get(field_name), str) or not place_data.get(field_name):
                _add(
                    violations,
                    "invalid_place_field",
                    f"{path}.{field_name}",
                    "must be a non-empty string",
                )
        parent_id = place_data.get("parent_place_id")
        if parent_id is not None and (
            not isinstance(parent_id, str) or parent_id not in place_ids
        ):
            _add(
                violations,
                "dangling_place_parent",
                f"{path}.parent_place_id",
                f"references unknown place '{parent_id}'",
            )
        if not isinstance(place_data.get("metadata"), Mapping):
            _add(
                violations,
                "place_metadata_not_object",
                f"{path}.metadata",
                "must be an object",
            )

    for place_id in place_ids:
        visited: set[object] = set()
        cursor: object | None = place_id
        while isinstance(cursor, str) and cursor in places:
            if cursor in visited:
                _add(
                    violations,
                    "place_parent_cycle",
                    f"world.places.{place_id}.parent_place_id",
                    "place ancestry must not contain a cycle",
                )
                break
            visited.add(cursor)
            place_data = places[cursor]
            if not isinstance(place_data, Mapping):
                break
            cursor = place_data.get("parent_place_id")

    known_entity_ids = actor_ids | place_ids
    seen_links: set[tuple[object, object, object, object]] = set()
    for index, link in enumerate(links):
        path = f"world.links[{index}]"
        if not isinstance(link, Mapping):
            _add(violations, "link_not_object", path, "link must be an object")
            continue
        unknown_link_fields = _unknown_fields(link, _LINK_FIELDS)
        if unknown_link_fields:
            _add(
                violations,
                "unknown_link_fields",
                path,
                "unknown " + ", ".join(unknown_link_fields),
            )
        source_id = link.get("source_id")
        target_id = link.get("target_id")
        for endpoint_name, endpoint_id in (
            ("source_id", source_id),
            ("target_id", target_id),
        ):
            if not isinstance(endpoint_id, str) or endpoint_id not in known_entity_ids:
                _add(
                    violations,
                    "dangling_link_endpoint",
                    f"{path}.{endpoint_name}",
                    f"references unknown entity '{endpoint_id}'",
                )
        for field_name in ("type", "role"):
            if not isinstance(link.get(field_name), str) or not link.get(field_name):
                _add(
                    violations,
                    "invalid_link_field",
                    f"{path}.{field_name}",
                    "must be a non-empty string",
                )
        metadata = link.get("metadata")
        if not isinstance(metadata, Mapping):
            _add(
                violations,
                "link_metadata_not_object",
                f"{path}.metadata",
                "must be an object",
            )
        elif link.get("type") == "social":
            unknown_metadata_fields = _unknown_fields(
                metadata,
                _SOCIAL_METADATA_FIELDS,
            )
            if unknown_metadata_fields:
                _add(
                    violations,
                    "unknown_social_metadata_fields",
                    f"{path}.metadata",
                    "unknown " + ", ".join(unknown_metadata_fields),
                )
            closeness = metadata.get("closeness")
            if (
                not _is_finite_number(closeness)
                or not 0 <= closeness <= 100
            ):
                _add(
                    violations,
                    "invalid_social_closeness",
                    f"{path}.metadata.closeness",
                    "must be a finite number from 0 through 100",
                )
            history_months = metadata.get("closeness_history_months")
            if not _is_int(history_months) or history_months < 0:
                _add(
                    violations,
                    "invalid_social_history",
                    f"{path}.metadata.closeness_history_months",
                    "must be a non-negative integer",
                )
            status = metadata.get("status")
            if not isinstance(status, str) or status not in {"active", "former"}:
                _add(
                    violations,
                    "invalid_social_status",
                    f"{path}.metadata.status",
                    "must be active or former",
                )
            role = link.get("role")
            if _is_finite_number(closeness):
                expected_role = _social_role_for_closeness(closeness)
                if role != expected_role and not (
                    status == "former" and role == "former"
                ):
                    _add(
                        violations,
                        "social_role_mismatch",
                        f"{path}.role",
                        (
                            f"must be {expected_role} for closeness "
                            f"{closeness}, or former for an ended link"
                        ),
                    )
            for field_name in ("ended_year", "met_year"):
                value = metadata.get(field_name)
                if value is not None and not _is_int(value):
                    _add(
                        violations,
                        "invalid_social_year",
                        f"{path}.metadata.{field_name}",
                        "must be an integer or null",
                    )
            for field_name in ("ended_month", "met_month"):
                value = metadata.get(field_name)
                if value is not None and (
                    not _is_int(value) or not 1 <= value <= 12
                ):
                    _add(
                        violations,
                        "invalid_social_month",
                        f"{path}.metadata.{field_name}",
                        "must be an integer from 1 through 12 or null",
                    )
            for field_name in ("ended_reason",):
                value = metadata.get(field_name)
                if value is not None and (
                    not isinstance(value, str) or not value
                ):
                    _add(
                        violations,
                        "invalid_social_metadata",
                        f"{path}.metadata.{field_name}",
                        "must be a non-empty string or null",
                    )
            met_place_id = metadata.get("met_place_id")
            if met_place_id is not None and (
                not isinstance(met_place_id, str)
                or met_place_id not in place_ids
            ):
                _add(
                    violations,
                    "dangling_social_place",
                    f"{path}.metadata.met_place_id",
                    f"references unknown place '{met_place_id}'",
                )
        identity = (source_id, target_id, link.get("type"), link.get("role"))
        if all(isinstance(value, str) for value in identity):
            if identity in seen_links:
                _add(
                    violations,
                    "duplicate_link",
                    path,
                    "link identity duplicates an earlier link",
                )
            seen_links.add(identity)

    for index, record in enumerate(records):
        path = f"world.records[{index}]"
        if not isinstance(record, Mapping):
            _add(violations, "record_not_object", path, "record must be an object")
            continue
        for field_name in ("record_type", "scope", "text"):
            if not isinstance(record.get(field_name), str):
                _add(
                    violations,
                    "invalid_record_field",
                    f"{path}.{field_name}",
                    "must be a string",
                )
        if not _is_int(record.get("year")):
            _add(
                violations,
                "invalid_record_year",
                f"{path}.year",
                "must be an integer",
            )
        record_month = record.get("month")
        if not _is_int(record_month) or not 1 <= record_month <= 12:
            _add(
                violations,
                "invalid_record_month",
                f"{path}.month",
                "must be an integer from 1 through 12",
            )
        record_actor_ids = record.get("actor_ids")
        if not isinstance(record_actor_ids, list):
            _add(
                violations,
                "record_actor_ids_not_array",
                f"{path}.actor_ids",
                "must be an array",
            )
        else:
            for actor_index, actor_id in enumerate(record_actor_ids):
                if not isinstance(actor_id, str) or actor_id not in actor_ids:
                    _add(
                        violations,
                        "dangling_record_actor",
                        f"{path}.actor_ids[{actor_index}]",
                        f"references unknown actor '{actor_id}'",
                    )
        tags = record.get("tags")
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            _add(
                violations,
                "record_tags_not_string_array",
                f"{path}.tags",
                "must be an array of strings",
            )
        if not isinstance(record.get("metadata"), Mapping):
            _add(
                violations,
                "record_metadata_not_object",
                f"{path}.metadata",
                "must be an object",
            )

    focused_actor_id = world_state.get("focused_actor_id")
    if focused_actor_id is not None and (
        not isinstance(focused_actor_id, str) or focused_actor_id not in actor_ids
    ):
        _add(
            violations,
            "dangling_world_focus",
            "world.focused_actor_id",
            f"references unknown actor '{focused_actor_id}'",
        )
    recent_event_ids_by_actor = world_state.get("recent_event_ids_by_actor")
    if not isinstance(recent_event_ids_by_actor, Mapping):
        _add(
            violations,
            "recent_events_not_object",
            "world.recent_event_ids_by_actor",
            "must be an object",
        )
    else:
        for actor_id, event_ids in recent_event_ids_by_actor.items():
            path = f"world.recent_event_ids_by_actor.{actor_id}"
            if not isinstance(actor_id, str) or actor_id not in actor_ids:
                _add(
                    violations,
                    "dangling_recent_event_actor",
                    path,
                    f"references unknown actor '{actor_id}'",
                )
            if not isinstance(event_ids, list):
                _add(
                    violations,
                    "recent_event_ids_not_array",
                    path,
                    "must be an array",
                )
                continue
            if len(event_ids) > 3:
                _add(
                    violations,
                    "too_many_recent_event_ids",
                    path,
                    "must contain at most 3 event IDs",
                )
            if any(
                not isinstance(event_id, str) or not event_id
                for event_id in event_ids
            ):
                _add(
                    violations,
                    "invalid_recent_event_id",
                    path,
                    "must contain only non-empty strings",
                )
            elif len(set(event_ids)) != len(event_ids):
                _add(
                    violations,
                    "duplicate_recent_event_id",
                    path,
                    "must not contain duplicate event IDs",
                )
    used_last_names = world_state.get("used_npc_last_names")
    if (
        not isinstance(used_last_names, list)
        or any(not isinstance(name, str) for name in used_last_names)
        or (
            isinstance(used_last_names, list)
            and all(isinstance(name, str) for name in used_last_names)
            and len(set(used_last_names)) != len(used_last_names)
        )
    ):
        _add(
            violations,
            "invalid_used_last_names",
            "world.used_npc_last_names",
            "must be a unique array of strings",
        )

    return tuple(violations)


def collect_save_invariant_violations(
    envelope: SaveEnvelope,
) -> tuple[InvariantViolation, ...]:
    """Collects complete save violations, including cross-object references."""
    violations = list(collect_world_invariant_violations(envelope.world))
    world = envelope.world if isinstance(envelope.world, Mapping) else {}
    actors = world.get("actors")
    actor_ids = set(actors) if isinstance(actors, Mapping) else set()
    session = envelope.session

    if session.focused_actor_id not in actor_ids:
        _add(
            violations,
            "dangling_session_focus",
            "session.focused_actor_id",
            f"references unknown actor '{session.focused_actor_id}'",
        )
    world_focus = world.get("focused_actor_id")
    if world_focus != session.focused_actor_id:
        _add(
            violations,
            "focus_mismatch",
            "session.focused_actor_id",
            "session focus must match world focus",
        )
    current_year = world.get("current_year")
    if _is_int(current_year) and session.last_logged_year > current_year:
        _add(
            violations,
            "history_ahead_of_world",
            "session.last_logged_year",
            "must not be later than the world year",
        )
    if session.remaining_skip_months > 0 and session.pending_choice is None:
        _add(
            violations,
            "orphaned_skip_resume",
            "session.remaining_skip_months",
            "remaining skip time requires a pending choice",
        )

    links = world.get("links")
    active_social_targets: set[object] = set()
    social_link_by_target: dict[object, Mapping[object, object]] = {}
    if isinstance(links, list):
        for link in links:
            if (
                isinstance(link, Mapping)
                and link.get("source_id") == session.focused_actor_id
                and link.get("type") == "social"
                and isinstance(link.get("metadata"), Mapping)
                and link["metadata"].get("status") == "active"
            ):
                target_id = link.get("target_id")
                if isinstance(target_id, str) and target_id in actor_ids:
                    active_social_targets.add(target_id)
                    social_link_by_target[target_id] = link

    action_ids: set[str] = set()
    spend_time_targets: set[str] = set()
    queued_hours = 0.0
    for index, action in enumerate(session.active_actions):
        path = f"session.active_actions[{index}]"
        action_type = action.get("action_type")
        action_id = action.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            _add(
                violations,
                "invalid_action_id",
                f"{path}.action_id",
                "must be a non-empty string",
            )
        elif action_id in action_ids:
            _add(
                violations,
                "duplicate_action_id",
                f"{path}.action_id",
                "must be unique within the queue",
            )
        else:
            action_ids.add(action_id)
            issued_value = _parse_issued_id(
                action_id,
                namespace=envelope.ids.namespace,
                role="action",
            )
            if issued_value is None:
                _add(
                    violations,
                    "invalid_action_id_provenance",
                    f"{path}.action_id",
                    "must be a canonical action ID from this save namespace",
                )
            elif issued_value >= envelope.ids.next_value:
                _add(
                    violations,
                    "unissued_action_id",
                    f"{path}.action_id",
                    "must have been issued before ids.next_value",
                )

        if action_type == "personal":
            unknown_fields = _unknown_fields(action, _PERSONAL_ACTION_FIELDS)
            missing_fields = sorted(_PERSONAL_ACTION_FIELDS - set(action))
            if unknown_fields or missing_fields:
                _add(
                    violations,
                    "invalid_personal_action_shape",
                    path,
                    "must contain exactly the canonical personal-action fields",
                )
            subtype_id = action.get("subtype_id")
            canonical = (
                _PERSONAL_ACTIONS.get(subtype_id)
                if isinstance(subtype_id, str)
                else None
            )
            if canonical is None:
                _add(
                    violations,
                    "unknown_personal_subtype",
                    f"{path}.subtype_id",
                    f"unknown personal action subtype '{subtype_id}'",
                )
            else:
                for field_name in (
                    "label",
                    "time_cost",
                    "stat_changes",
                    "event_text",
                ):
                    if action.get(field_name) != canonical[field_name]:
                        _add(
                            violations,
                            "noncanonical_personal_action",
                            f"{path}.{field_name}",
                            "must match the engine-owned subtype definition",
                        )
        elif action_type == "spend_time":
            unknown_fields = _unknown_fields(action, _SPEND_TIME_ACTION_FIELDS)
            missing_fields = sorted(_SPEND_TIME_ACTION_FIELDS - set(action))
            if unknown_fields or missing_fields:
                _add(
                    violations,
                    "invalid_spend_time_action_shape",
                    path,
                    "must contain exactly the canonical spend-time fields",
                )
            target_actor_id = action.get("target_actor_id")
            if not isinstance(target_actor_id, str) or target_actor_id not in actor_ids:
                _add(
                    violations,
                    "dangling_action_target",
                    f"{path}.target_actor_id",
                    f"references unknown actor '{target_actor_id}'",
                )
            else:
                if not _actor_is_alive(actors.get(target_actor_id)):
                    _add(
                        violations,
                        "dead_action_target",
                        f"{path}.target_actor_id",
                        "spend-time target must be alive",
                    )
                if target_actor_id not in active_social_targets:
                    _add(
                        violations,
                        "inactive_action_target",
                        f"{path}.target_actor_id",
                        "spend-time target must have an active social link",
                    )
                if target_actor_id in spend_time_targets:
                    _add(
                        violations,
                        "duplicate_spend_time_target",
                        f"{path}.target_actor_id",
                        "only one spend-time action may target an actor",
                    )
                spend_time_targets.add(target_actor_id)
                target_name = _actor_full_name(actors.get(target_actor_id))
                if (
                    target_name is not None
                    and action.get("label") != f"Spend time with {target_name}"
                ):
                    _add(
                        violations,
                        "noncanonical_spend_time_label",
                        f"{path}.label",
                        "must be derived from the target actor",
                    )
            if action.get("time_cost") != HANG_OUT_TIME_COST:
                _add(
                    violations,
                    "noncanonical_spend_time_cost",
                    f"{path}.time_cost",
                    f"must be {HANG_OUT_TIME_COST}",
                )
        else:
            _add(
                violations,
                "invalid_action_type",
                f"{path}.action_type",
                "must be personal or spend_time",
            )

        time_cost = action.get("time_cost")
        if not _is_finite_number(time_cost) or time_cost < 0:
            _add(
                violations,
                "invalid_action_time_cost",
                f"{path}.time_cost",
                "must be a non-negative finite number",
            )
        else:
            queued_hours += time_cost

    focused_actor_data = (
        actors.get(session.focused_actor_id)
        if isinstance(actors, Mapping)
        else None
    )
    free_hours = _monthly_free_hours(focused_actor_data)
    if free_hours is not None and queued_hours > free_hours:
        _add(
            violations,
            "queued_time_exceeds_budget",
            "session.active_actions",
            f"queued actions use {queued_hours:g}h of {free_hours:g}h available",
        )

    pending_choice = session.pending_choice
    if pending_choice is not None:
        unknown_choice_fields = _unknown_fields(
            pending_choice,
            _PENDING_CHOICE_FIELDS,
        )
        required_choice_fields = _PENDING_CHOICE_FIELDS - {"default_value"}
        missing_choice_fields = sorted(
            required_choice_fields - set(pending_choice)
        )
        if unknown_choice_fields or missing_choice_fields:
            _add(
                violations,
                "invalid_choice_shape",
                "session.pending_choice",
                "must contain every required choice field and no unknown fields",
            )
        for field_name in ("title", "text", "question"):
            if not isinstance(pending_choice.get(field_name), str):
                _add(
                    violations,
                    "invalid_choice_text",
                    f"session.pending_choice.{field_name}",
                    "must be a string",
                )
        choice_id = pending_choice.get("choice_id")
        known_choice_ids = (
            _NON_TARGET_CHOICE_IDS
            | set(_PERSONAL_CHOICE_ACTION_IDS)
            | {"select_hang_out_target"}
        )
        if not isinstance(choice_id, str) or not choice_id:
            _add(
                violations,
                "invalid_choice_id",
                "session.pending_choice.choice_id",
                "must be a non-empty string",
            )
        elif choice_id not in known_choice_ids:
            _add(
                violations,
                "unsupported_choice_id",
                "session.pending_choice.choice_id",
                f"unknown choice '{choice_id}'",
            )

        options = pending_choice.get("options")
        normalized_options: list[Mapping[object, object]] = []
        option_ids: set[str] = set()
        if not isinstance(options, list) or not options:
            _add(
                violations,
                "invalid_choice_options",
                "session.pending_choice.options",
                "must be a non-empty array of option objects",
            )
        else:
            for index, option in enumerate(options):
                path = f"session.pending_choice.options[{index}]"
                if not isinstance(option, Mapping):
                    _add(
                        violations,
                        "choice_option_not_object",
                        path,
                        "must be an object",
                    )
                    continue
                normalized_options.append(option)
                if (
                    _unknown_fields(option, _CHOICE_OPTION_FIELDS)
                    or set(option) != _CHOICE_OPTION_FIELDS
                ):
                    _add(
                        violations,
                        "invalid_choice_option_shape",
                        path,
                        "must contain exactly option_id, label, and value",
                    )
                option_id = option.get("option_id")
                if not isinstance(option_id, str) or not option_id:
                    _add(
                        violations,
                        "invalid_choice_option_id",
                        f"{path}.option_id",
                        "must be a non-empty string",
                    )
                elif option_id in option_ids:
                    _add(
                        violations,
                        "duplicate_choice_option_id",
                        f"{path}.option_id",
                        "must be unique within the choice",
                    )
                else:
                    option_ids.add(option_id)
                if not isinstance(option.get("label"), str):
                    _add(
                        violations,
                        "invalid_choice_option_label",
                        f"{path}.label",
                        "must be a string",
                    )

        selected_option_id = pending_choice.get("selected_option_id")
        if (
            not isinstance(selected_option_id, str)
            or selected_option_id not in option_ids
        ):
            _add(
                violations,
                "invalid_choice_selection",
                "session.pending_choice.selected_option_id",
                "must identify one available stable option ID",
            )
        skippable = pending_choice.get("skippable")
        if not isinstance(skippable, bool):
            _add(
                violations,
                "invalid_choice_skippable",
                "session.pending_choice.skippable",
                "must be a boolean",
            )
        elif skippable and "default_value" not in pending_choice:
            _add(
                violations,
                "missing_choice_default",
                "session.pending_choice.default_value",
                "skippable choices must define a default value",
            )
        elif skippable:
            default_value = pending_choice.get("default_value")
            available_values = [
                option.get("value")
                for option in normalized_options
            ]
            if (
                default_value is not None
                and default_value not in available_values
            ):
                _add(
                    violations,
                    "invalid_choice_default",
                    "session.pending_choice.default_value",
                    "must be null or match one available option value",
                )
        elif "default_value" in pending_choice:
            _add(
                violations,
                "unexpected_choice_default",
                "session.pending_choice.default_value",
                "non-skippable choices must not define a default value",
            )

        option_values: set[str] = set()
        for index, option in enumerate(normalized_options):
            path = f"session.pending_choice.options[{index}]"
            value = option.get("value")
            option_id = option.get("option_id")
            label = option.get("label")
            if choice_id == "select_hang_out_target":
                if not isinstance(value, str) or value not in actor_ids:
                    _add(
                        violations,
                        "dangling_choice_target",
                        f"{path}.value",
                        f"references unknown actor '{value}'",
                    )
                    continue
                if value in option_values:
                    _add(
                        violations,
                        "duplicate_choice_target",
                        f"{path}.value",
                        "must not repeat an actor",
                    )
                option_values.add(value)
                if (
                    not _actor_is_alive(actors.get(value))
                    or value not in active_social_targets
                ):
                    _add(
                        violations,
                        "unavailable_choice_target",
                        f"{path}.value",
                        "must identify a living person with an active social link",
                    )
                if option_id != f"actor:{value}":
                    _add(
                        violations,
                        "unstable_choice_option_id",
                        f"{path}.option_id",
                        "hang-out option IDs must derive from the actor ID",
                    )
                actor_name = _actor_full_name(actors.get(value))
                link = social_link_by_target.get(value)
                metadata = (
                    link.get("metadata")
                    if isinstance(link, Mapping)
                    else None
                )
                closeness = (
                    metadata.get("closeness")
                    if isinstance(metadata, Mapping)
                    else None
                )
                if actor_name is not None and _is_finite_number(closeness):
                    expected_label = (
                        f"{actor_name} · {_social_tier_label(closeness)}"
                    )
                    if value in spend_time_targets:
                        expected_label += " (queued)"
                    if label != expected_label:
                        _add(
                            violations,
                            "choice_target_label_mismatch",
                            f"{path}.label",
                            "must describe the matching social target",
                        )
            elif (
                isinstance(choice_id, str)
                and choice_id in _PERSONAL_CHOICE_ACTION_IDS
            ):
                allowed_subtypes = _PERSONAL_CHOICE_ACTION_IDS[choice_id]
                canonical = (
                    _PERSONAL_ACTIONS.get(value)
                    if isinstance(value, str)
                    else None
                )
                if canonical is None or value not in allowed_subtypes:
                    _add(
                        violations,
                        "noncanonical_choice_subtype",
                        f"{path}.value",
                        "must identify a canonical subtype for this choice",
                    )
                    continue
                if value in option_values:
                    _add(
                        violations,
                        "duplicate_choice_subtype",
                        f"{path}.value",
                        "must not repeat a subtype",
                    )
                option_values.add(value)
                if option_id != f"subtype:{value}":
                    _add(
                        violations,
                        "unstable_choice_option_id",
                        f"{path}.option_id",
                        "personal-action option IDs must derive from the subtype",
                    )
                if label != f"{canonical['label']}  {canonical['time_cost']}h":
                    _add(
                        violations,
                        "choice_subtype_label_mismatch",
                        f"{path}.label",
                        "must describe the matching canonical subtype",
                    )
            elif isinstance(value, str):
                if option_id != f"value:{value}":
                    _add(
                        violations,
                        "unstable_choice_option_id",
                        f"{path}.option_id",
                        "choice option ID must derive from its stable value",
                    )
            else:
                _add(
                    violations,
                    "invalid_choice_option_value",
                    f"{path}.value",
                    "this choice requires a string value",
                )

    for index, entry in enumerate(session.event_log):
        path = f"session.event_log[{index}]"
        if not isinstance(entry.get("kind"), str) or not isinstance(entry.get("text"), str):
            _add(
                violations,
                "invalid_history_entry",
                path,
                "kind and text must be strings",
            )
        year = entry.get("year")
        month = entry.get("month")
        if year is not None and not _is_int(year):
            _add(
                violations,
                "invalid_history_year",
                f"{path}.year",
                "must be an integer or null",
            )
        if month is not None and (not _is_int(month) or not 1 <= month <= 12):
            _add(
                violations,
                "invalid_history_month",
                f"{path}.month",
                "must be an integer from 1 through 12 or null",
            )

    return tuple(violations)


def assert_valid_world_state(world_state: object) -> None:
    """Raises one grouped error when world state violates invariants."""
    violations = collect_world_invariant_violations(world_state)
    if violations:
        raise InvariantError(violations)


def assert_valid_save_envelope(envelope: SaveEnvelope) -> None:
    """Raises one grouped error when a save violates invariants."""
    violations = collect_save_invariant_violations(envelope)
    if violations:
        raise InvariantError(violations)
