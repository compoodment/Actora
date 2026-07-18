"""Headless orchestration for authoritative month-by-month advancement."""

from __future__ import annotations

from events import get_meeting_event_for_player
from mechanics import (
    GENDER_IDENTITY_OPTIONS,
    MEETING_EVENT_COOLDOWN_MONTHS,
    SEXUALITY_OPTION_LABELS,
)

from .errors import CommandRejectedError
from .history import append_event_log_entry, append_turn_event_log
from .ids import IdSource
from .json_types import MAX_SAFE_INTEGER, JSONObject, clone_json_object
from .randomness import RandomSource
from .session import GameSession


def _value_options(
    labeled_values: tuple[tuple[str, str], ...],
) -> list[JSONObject]:
    return [
        {
            "option_id": f"value:{value}",
            "label": label,
            "value": value,
        }
        for label, value in labeled_values
    ]


def _maybe_offer_identity_choice(
    world: object,
    session: GameSession,
) -> bool:
    get_actor = getattr(world, "get_actor", None)
    actor = (
        get_actor(session.focused_actor_id)
        if callable(get_actor)
        else None
    )
    if (
        actor is None
        or not callable(getattr(actor, "is_alive", None))
        or not actor.is_alive()
    ):
        return False

    lifecycle = actor.get_lifecycle_state(
        getattr(world, "current_year"),
        getattr(world, "current_month"),
    )
    age_years = lifecycle["age_years"]
    current_gender = actor.gender or "Other"

    if session.identity_popup_suppressed_for_resumed_adult:
        return False

    if (
        age_years >= session.gender_choice_age
        and not session.gender_choice_offered
    ):
        gender_values = list(GENDER_IDENTITY_OPTIONS)
        if current_gender not in gender_values:
            gender_values.append(current_gender)
        labeled_values = tuple(
            (value, value) for value in gender_values
        )
        session.pending_choice = {
            "choice_id": "gender_identity",
            "title": "A moment of self-reflection",
            "text": (
                "As you grow, you find yourself thinking more about who "
                "you are."
            ),
            "question": "Your gender identity feels like:",
            "options": _value_options(labeled_values),
            "selected_option_id": f"value:{current_gender}",
            "skippable": True,
            "default_value": current_gender,
        }
        session.gender_choice_offered = True
        return True

    if (
        age_years >= session.sexuality_choice_age
        and not session.sexuality_choice_offered
    ):
        options = _value_options(SEXUALITY_OPTION_LABELS)
        session.pending_choice = {
            "choice_id": "sexuality",
            "title": "A new kind of awareness",
            "text": (
                "You have started noticing things about yourself you had "
                "not thought about before."
            ),
            "question": "You feel attracted to:",
            "options": options,
            "selected_option_id": options[0]["option_id"],
            "skippable": True,
            "default_value": None,
        }
        session.sexuality_choice_offered = True
        return True

    return False


def _maybe_offer_meeting_choice(
    world: object,
    session: GameSession,
    random_source: RandomSource,
) -> bool:
    get_actor = getattr(world, "get_actor", None)
    actor = (
        get_actor(session.focused_actor_id)
        if callable(get_actor)
        else None
    )
    if (
        actor is None
        or not callable(getattr(actor, "is_alive", None))
        or not actor.is_alive()
    ):
        return False

    current_year = getattr(world, "current_year")
    current_month = getattr(world, "current_month")
    current_total_months = current_year * 12 + current_month
    if (
        current_total_months - session.meeting_event_last_total_months
        < MEETING_EVENT_COOLDOWN_MONTHS
    ):
        return False

    lifecycle = actor.get_lifecycle_state(current_year, current_month)
    meeting_event = get_meeting_event_for_player(
        lifecycle,
        random_source=random_source,
    )
    if meeting_event is None:
        return False

    session.meeting_event_last_total_months = current_total_months
    labeled_values = (
        ("Introduce yourself", "introduce"),
        ("Keep to yourself", "keep_to_self"),
    )
    options = _value_options(labeled_values)
    session.pending_choice = {
        "choice_id": "meeting_npc",
        "title": "Someone new",
        "text": meeting_event["text"],
        "question": "Do you want to introduce yourself?",
        "options": options,
        "selected_option_id": options[0]["option_id"],
        "skippable": False,
    }
    return True


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


def advance_time(
    world: object,
    session: GameSession,
    random_source: RandomSource,
    id_source: IdSource,
    months_to_advance: int,
    *,
    suppress_skip_marker: bool = False,
) -> dict[str, object]:
    """Advances through the same ordered native systems without shell state."""
    if session.pending_choice is not None:
        raise CommandRejectedError(
            "choice_pending",
            "Resolve the pending choice before advancing time.",
            {"choice_id": session.pending_choice.get("choice_id")},
        )
    _focused_actor(world, session)
    current_year = getattr(world, "current_year")
    current_month = getattr(world, "current_month")
    target_total_months = (
        current_year * 12
        + current_month
        + months_to_advance
    )
    if target_total_months > MAX_SAFE_INTEGER:
        raise CommandRejectedError(
            "time_limit",
            "This timeline cannot advance any further.",
            {"reason": "timeline_limit"},
        )

    focused_actor_id = session.focused_actor_id
    queued_actions = list(session.active_actions)
    spend_time_actions = [
        action
        for action in queued_actions
        if action.get("action_type") == "spend_time"
    ]
    personal_actions = [
        action
        for action in queued_actions
        if action.get("action_type") == "personal"
    ]
    shared_actor_ids = {
        action["target_actor_id"]
        for action in spend_time_actions
        if isinstance(action.get("target_actor_id"), str)
    }

    aggregated_turn_result: dict[str, object] = {
        "months_advanced": 0,
        "events": [],
        "focused_actor_alive": True,
        "continuity_state": None,
    }
    new_records: list[dict[str, object]] = []
    resolved_action_ids: list[str] = []
    first_month = True

    for _ in range(months_to_advance):
        records = getattr(world, "records")
        prior_record_count = len(records)
        month_result = world.simulate_advance_turn(
            focused_actor_id,
            1,
            random_source=random_source,
            id_source=id_source,
        )
        new_records_this_month = records[prior_record_count:]
        new_records.extend(new_records_this_month)

        month_count = month_result["months_advanced"]
        aggregated_turn_result["months_advanced"] += month_count
        aggregated_events = aggregated_turn_result["events"]
        aggregated_events.extend(month_result["events"])
        aggregated_turn_result["focused_actor_alive"] = month_result[
            "focused_actor_alive"
        ]
        aggregated_turn_result["continuity_state"] = month_result[
            "continuity_state"
        ]

        if first_month:
            if month_result.get("focused_actor_alive", True):
                for action in spend_time_actions:
                    event = world.spend_time_with_actor(
                        focused_actor_id,
                        action["target_actor_id"],
                    )
                    if event is not None:
                        aggregated_events.append(event)
                        action_id = action.get("action_id")
                        if isinstance(action_id, str):
                            resolved_action_ids.append(action_id)

                for action in personal_actions:
                    event = world.resolve_personal_action(
                        focused_actor_id,
                        action,
                    )
                    if event is not None:
                        aggregated_events.append(event)
                        action_id = action.get("action_id")
                        if isinstance(action_id, str):
                            resolved_action_ids.append(action_id)
            session.active_actions = []

        for record in new_records_this_month:
            if record.get("record_type") != "death":
                continue
            actor_ids = record.get("actor_ids", [])
            if not isinstance(actor_ids, list):
                continue
            for dead_actor_id in actor_ids:
                if dead_actor_id == focused_actor_id:
                    continue
                event = world.resolve_social_death_impact(
                    focused_actor_id,
                    dead_actor_id,
                )
                if event is not None:
                    aggregated_events.append(event)

        if month_result.get("focused_actor_alive", True):
            month_shared = shared_actor_ids if first_month else set()
            drift_events = world.apply_social_link_decay(
                focused_actor_id,
                month_shared,
            )
            for drift in drift_events:
                append_event_log_entry(
                    session.event_log,
                    "event",
                    drift["text"],
                    year=drift["year"],
                    month=drift["month"],
                )

        first_month = False
        if month_count <= 0 or not month_result["focused_actor_alive"]:
            break

        offered_choice = _maybe_offer_identity_choice(world, session)
        if not offered_choice:
            offered_choice = _maybe_offer_meeting_choice(
                world,
                session,
                random_source,
            )
        if offered_choice:
            remaining = (
                months_to_advance
                - aggregated_turn_result["months_advanced"]
            )
            session.remaining_skip_months = max(0, remaining)
            break

    session.last_logged_year = append_turn_event_log(
        session.event_log,
        session.last_logged_year,
        focused_actor_id,
        aggregated_turn_result,
        months_to_advance,
        new_records,
        suppress_skip_marker=suppress_skip_marker,
    )

    months_advanced = aggregated_turn_result["months_advanced"]
    effects: list[JSONObject] = [
        {
            "kind": "time_advanced",
            "months_requested": months_to_advance,
            "months_advanced": months_advanced,
        }
    ]
    effects.extend(
        {
            "kind": "action_resolved",
            "action_id": action_id,
        }
        for action_id in resolved_action_ids
    )

    interruption: JSONObject | None = None
    if not aggregated_turn_result["focused_actor_alive"]:
        session.remaining_skip_months = 0
        continuity_state = aggregated_turn_result["continuity_state"]
        interruption = {
            "kind": "continuation_required",
            "continuity_state": clone_json_object(
                continuity_state,
                path="advance.continuity_state",
            ),
        }
    elif session.pending_choice is not None:
        interruption = {
            "kind": "choice_required",
            "choice_id": session.pending_choice["choice_id"],
            "remaining_months": session.remaining_skip_months,
        }
    else:
        session.remaining_skip_months = 0

    return {
        "months_advanced": months_advanced,
        "events": aggregated_turn_result["events"],
        "effects": effects,
        "interruption": interruption,
    }
