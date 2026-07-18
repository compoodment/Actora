"""Headless orchestration for stable-ID pending-choice resolution."""

from __future__ import annotations

from collections.abc import Mapping

from mechanics import GENDER_IDENTITY_OPTIONS, SEXUALITY_OPTION_LABELS

from .action_queue import queue_action
from .advancement import advance_time
from .errors import CommandRejectedError
from .history import append_event_log_entry
from .ids import IdSource
from .json_types import JSONObject, JSONValue, clone_json
from .randomness import RandomSource
from .session import GameSession

_ACTION_CHOICE_TYPES = {
    "select_exercise_subtype": "personal",
    "select_read_subtype": "personal",
    "select_rest_subtype": "personal",
    "select_hang_out_target": "spend_time",
}
_LIFE_CHOICE_IDS = {
    "gender_identity",
    "sexuality",
    "meeting_npc",
}
_ALLOWED_GENDER_VALUES = set(GENDER_IDENTITY_OPTIONS)
_ALLOWED_SEXUALITY_VALUES = {
    value for _label, value in SEXUALITY_OPTION_LABELS
}


def _reject(reason: str, message: str, **details: JSONValue) -> None:
    raise CommandRejectedError(
        "choice_not_available",
        message,
        {"reason": reason, **details},
    )


def _focused_actor(world: object, session: GameSession) -> object:
    get_actor = getattr(world, "get_actor", None)
    actor = (
        get_actor(session.focused_actor_id)
        if callable(get_actor)
        else None
    )
    if actor is None or not callable(getattr(actor, "is_alive", None)):
        raise CommandRejectedError(
            "focused_actor_missing",
            "This life could not be found.",
            {"actor_id": session.focused_actor_id},
        )
    if not actor.is_alive():
        raise CommandRejectedError(
            "focused_actor_dead",
            "This life has ended. Continue as another person.",
            {"actor_id": session.focused_actor_id},
        )
    return actor


def _selected_value(
    pending_choice: Mapping[str, object],
    option_id: str | None,
) -> tuple[str | None, JSONValue]:
    options = pending_choice.get("options")
    if not isinstance(options, list):
        raise RuntimeError("validated pending choice has no option array")

    if option_id is None:
        if pending_choice.get("skippable") is not True:
            _reject(
                "selection_required",
                "Choose one of the available options.",
            )
        default_value = clone_json(
            pending_choice.get("default_value"),
            path="choice.default_value",
        )
        effective_option_id = next(
            (
                option.get("option_id")
                for option in options
                if isinstance(option, Mapping)
                and option.get("value") == default_value
            ),
            None,
        )
        return (
            effective_option_id
            if isinstance(effective_option_id, str)
            else None,
            default_value,
        )

    selected_option = next(
        (
            option
            for option in options
            if isinstance(option, Mapping)
            and option.get("option_id") == option_id
        ),
        None,
    )
    if selected_option is None:
        _reject(
            "option_not_available",
            "That option is no longer available.",
            option_id=option_id,
        )
    return (
        option_id,
        clone_json(
            selected_option.get("value"),
            path="choice.option.value",
        ),
    )


def _append_choice_event(
    session: GameSession,
    event: JSONObject,
) -> None:
    year = event["year"]
    month = event["month"]
    if not isinstance(year, int) or not isinstance(month, int):
        raise RuntimeError("choice event date must be integral")
    if year > session.last_logged_year:
        append_event_log_entry(
            session.event_log,
            "year_header",
            f"Year {year}",
            year=year,
        )
        session.last_logged_year = year
    append_event_log_entry(
        session.event_log,
        "event",
        str(event["text"]),
        year=year,
        month=month,
    )


def _choice_event(
    world: object,
    *,
    event_id: str,
    text: str,
    tags: list[str],
) -> JSONObject:
    return {
        "text": text,
        "year": getattr(world, "current_year"),
        "month": getattr(world, "current_month"),
        "event_id": event_id,
        "tags": tags,
    }


def _resolve_life_choice(
    world: object,
    session: GameSession,
    random_source: RandomSource,
    id_source: IdSource,
    *,
    choice_id: str,
    value: JSONValue,
) -> tuple[JSONObject, list[JSONObject]]:
    actor = _focused_actor(world, session)
    effects: list[JSONObject] = []

    if choice_id == "gender_identity":
        current_gender = getattr(actor, "gender", None)
        allowed_values = set(_ALLOWED_GENDER_VALUES)
        if isinstance(current_gender, str):
            allowed_values.add(current_gender)
        if not isinstance(value, str) or value not in allowed_values:
            _reject(
                "option_not_available",
                "That gender option is no longer available.",
            )
        result = world.resolve_human_identity_choice(
            session.focused_actor_id,
            choice_id,
            value,
        )
        text = (
            f"You now identify as {value}."
            if result["changed"]
            else "You reflected on your identity."
        )
        return (
            _choice_event(
                world,
                event_id="gender_identity",
                text=text,
                tags=["identity", "choice"],
            ),
            effects,
        )

    if choice_id == "sexuality":
        if value is not None and (
            not isinstance(value, str)
            or value not in _ALLOWED_SEXUALITY_VALUES
        ):
            _reject(
                "option_not_available",
                "That identity option is no longer available.",
            )
        previous_value = getattr(actor, "sexuality", None)
        world.resolve_human_identity_choice(
            session.focused_actor_id,
            choice_id,
            value,
        )
        if value is not None:
            text = f"You identify as {value}."
        elif previous_value is None:
            text = "You are still figuring things out."
        else:
            text = f"You still identify as {previous_value}."
        return (
            _choice_event(
                world,
                event_id="sexuality",
                text=text,
                tags=["identity", "choice"],
            ),
            effects,
        )

    if choice_id != "meeting_npc":
        _reject(
            "unsupported_choice",
            "That choice cannot be resolved by this engine.",
            choice_id=choice_id,
        )
    if value not in {"introduce", "keep_to_self"}:
        _reject(
            "option_not_available",
            "That meeting option is no longer available.",
        )

    if value == "introduce":
        npc_actor_id, npc = world.generate_meeting_npc(
            session.focused_actor_id,
            random_source=random_source,
            id_source=id_source,
        )
        world.create_social_link_pair(
            session.focused_actor_id,
            npc_actor_id,
            closeness=15,
            status="active",
            closeness_history_months=0,
        )
        npc_name = npc.get_full_name()
        effects.append(
            {
                "kind": "person_met",
                "actor_id": npc_actor_id,
                "name": npc_name,
            }
        )
        text = f"You introduced yourself to {npc_name}."
    else:
        text = "You decided to keep to yourself."
    return (
        _choice_event(
            world,
            event_id=f"meeting_npc_{value}",
            text=text,
            tags=["social", "choice"],
        ),
        effects,
    )


def _queue_selected_action(
    world: object,
    session: GameSession,
    id_source: IdSource,
    *,
    choice_id: str,
    value: JSONValue,
) -> str | None:
    if not isinstance(value, str):
        _reject(
            "option_not_available",
            "That action option is no longer available.",
        )
    action_type = _ACTION_CHOICE_TYPES[choice_id]
    if choice_id == "select_hang_out_target" and any(
        action.get("action_type") == "spend_time"
        and action.get("target_actor_id") == value
        for action in session.active_actions
    ):
        return None
    intent: JSONObject
    if action_type == "personal":
        intent = {
            "action_type": "personal",
            "subtype_id": value,
        }
    else:
        intent = {
            "action_type": "spend_time",
            "target_actor_id": value,
        }
    return queue_action(world, session, id_source, intent)


def resolve_choice(
    world: object,
    session: GameSession,
    random_source: RandomSource,
    id_source: IdSource,
    *,
    choice_id: str,
    option_id: str | None,
) -> dict[str, object]:
    """Resolves one saved stable-ID choice and any saved skip continuation."""
    pending_choice = session.pending_choice
    if pending_choice is None:
        _reject(
            "no_pending_choice",
            "There is no choice waiting for a response.",
        )
    saved_choice_id = pending_choice.get("choice_id")
    if saved_choice_id != choice_id:
        _reject(
            "choice_id_mismatch",
            "That choice is no longer waiting for a response.",
            expected_choice_id=(
                saved_choice_id
                if isinstance(saved_choice_id, str)
                else None
            ),
            requested_choice_id=choice_id,
        )
    if choice_id not in _LIFE_CHOICE_IDS | set(_ACTION_CHOICE_TYPES):
        _reject(
            "unsupported_choice",
            "That choice cannot be resolved by this engine.",
            choice_id=choice_id,
        )

    _focused_actor(world, session)
    effective_option_id, value = _selected_value(
        pending_choice,
        option_id,
    )
    remaining_months = session.remaining_skip_months
    session.pending_choice = None
    session.remaining_skip_months = 0

    effects: list[JSONObject] = [
        {
            "kind": "choice_resolved",
            "choice_id": choice_id,
            "option_id": effective_option_id,
        }
    ]
    events: list[JSONObject] = []

    if choice_id in _ACTION_CHOICE_TYPES:
        if value is not None:
            action_id = _queue_selected_action(
                world,
                session,
                id_source,
                choice_id=choice_id,
                value=value,
            )
            if action_id is not None:
                effects.append(
                    {"kind": "action_queued", "action_id": action_id}
                )
    else:
        event, life_effects = _resolve_life_choice(
            world,
            session,
            random_source,
            id_source,
            choice_id=choice_id,
            value=value,
        )
        events.append(event)
        effects.extend(life_effects)
        _append_choice_event(session, event)

    interruption: JSONObject | None = None
    if remaining_months > 0:
        resumed = advance_time(
            world,
            session,
            random_source,
            id_source,
            remaining_months,
            suppress_skip_marker=True,
        )
        resumed_events = resumed.get("events")
        resumed_effects = resumed.get("effects")
        if not isinstance(resumed_events, list) or not isinstance(
            resumed_effects,
            list,
        ):
            raise RuntimeError(
                "resumed advance_time returned an invalid result shape"
            )
        events.extend(resumed_events)
        effects.extend(resumed_effects)
        resumed_interruption = resumed.get("interruption")
        if resumed_interruption is not None:
            if not isinstance(resumed_interruption, dict):
                raise RuntimeError(
                    "resumed advance_time returned an invalid interruption"
                )
            interruption = resumed_interruption

    return {
        "events": events,
        "effects": effects,
        "interruption": interruption,
    }
