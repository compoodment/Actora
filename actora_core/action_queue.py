"""Deterministic, presentation-free action-queue mutations."""

from __future__ import annotations

from collections.abc import Mapping

from mechanics import (
    EXERCISE_SUBTYPES,
    HANG_OUT_TIME_COST,
    READ_SUBTYPES,
    REST_SUBTYPES,
    get_monthly_free_hours,
)

from .errors import CommandRejectedError
from .ids import IdSource
from .json_types import JSONObject, clone_json_object
from .session import GameSession

_PERSONAL_ACTIONS = {
    action["id"]: action
    for action in (*EXERCISE_SUBTYPES, *READ_SUBTYPES, *REST_SUBTYPES)
}


def _focused_actor(world: object, session: GameSession) -> object:
    get_actor = getattr(world, "get_actor", None)
    actor = (
        get_actor(session.focused_actor_id)
        if callable(get_actor)
        else None
    )
    if actor is None or not callable(getattr(actor, "is_alive", None)):
        raise CommandRejectedError(
            "action_not_available",
            "That action is unavailable.",
            {"actor_id": session.focused_actor_id},
        )
    if not actor.is_alive():
        raise CommandRejectedError(
            "focused_actor_dead",
            "This life has ended. Continue as another person to take actions.",
            {"actor_id": session.focused_actor_id},
        )
    return actor


def _used_hours(session: GameSession) -> float:
    return sum(
        action["time_cost"]
        for action in session.active_actions
        if isinstance(action.get("time_cost"), (int, float))
        and not isinstance(action.get("time_cost"), bool)
    )


def _ensure_time_available(
    actor: object,
    session: GameSession,
    action_cost: int,
) -> None:
    free_hours = get_monthly_free_hours(actor)
    used_hours = _used_hours(session)
    if used_hours + action_cost > free_hours:
        raise CommandRejectedError(
            "time_budget_exceeded",
            "There is not enough free time to queue that action.",
            {
                "available_hours": max(0, free_hours - used_hours),
                "required_hours": action_cost,
            },
        )


def _active_social_target(
    world: object,
    focused_actor_id: str,
    target_actor_id: str,
) -> object | None:
    get_actor = getattr(world, "get_actor", None)
    get_links = getattr(world, "get_links", None)
    if not callable(get_actor) or not callable(get_links):
        return None
    target = get_actor(target_actor_id)
    if (
        target is None
        or not callable(getattr(target, "is_alive", None))
        or not target.is_alive()
    ):
        return None
    links = get_links(
        source_id=focused_actor_id,
        target_id=target_actor_id,
        link_type="social",
    )
    if any(
        isinstance(link, Mapping)
        and isinstance(link.get("metadata"), Mapping)
        and link["metadata"].get("status") == "active"
        for link in links
    ):
        return target
    return None


def queue_action(
    world: object,
    session: GameSession,
    id_source: IdSource,
    intent: JSONObject,
) -> str:
    """Validates one intent, appends its canonical action, and returns its ID."""
    if session.pending_choice is not None:
        raise CommandRejectedError(
            "action_not_available",
            "Resolve the pending choice before queueing an action.",
            {"choice_id": session.pending_choice.get("choice_id")},
        )
    actor = _focused_actor(world, session)
    action_type = intent.get("action_type")

    if action_type == "personal":
        subtype_id = intent.get("subtype_id")
        canonical = (
            _PERSONAL_ACTIONS.get(subtype_id)
            if isinstance(subtype_id, str)
            else None
        )
        if canonical is None:
            raise CommandRejectedError(
                "action_not_available",
                "That personal action is not available.",
                {"subtype_id": subtype_id},
            )
        action_cost = canonical["time_cost"]
        _ensure_time_available(actor, session, action_cost)
        action_id = id_source.next_id("action")
        action = {
            "action_id": action_id,
            "action_type": "personal",
            "subtype_id": canonical["id"],
            "label": canonical["label"],
            "time_cost": action_cost,
            "stat_changes": canonical["stat_changes"],
            "event_text": canonical["event_text"],
        }
    elif action_type == "spend_time":
        target_actor_id = intent.get("target_actor_id")
        target = (
            _active_social_target(
                world,
                session.focused_actor_id,
                target_actor_id,
            )
            if isinstance(target_actor_id, str)
            else None
        )
        if target is None:
            raise CommandRejectedError(
                "action_not_available",
                "That person is not available to spend time with.",
                {"target_actor_id": target_actor_id},
            )
        if any(
            action.get("action_type") == "spend_time"
            and action.get("target_actor_id") == target_actor_id
            for action in session.active_actions
        ):
            raise CommandRejectedError(
                "action_already_queued",
                "Time with that person is already queued.",
                {"target_actor_id": target_actor_id},
            )
        _ensure_time_available(actor, session, HANG_OUT_TIME_COST)
        get_full_name = getattr(target, "get_full_name", None)
        if not callable(get_full_name):
            raise CommandRejectedError(
                "action_not_available",
                "That person is not available to spend time with.",
                {"target_actor_id": target_actor_id},
            )
        target_name = get_full_name()
        action_id = id_source.next_id("action")
        action = {
            "action_id": action_id,
            "action_type": "spend_time",
            "target_actor_id": target_actor_id,
            "label": f"Spend time with {target_name}",
            "time_cost": HANG_OUT_TIME_COST,
        }
    else:
        raise CommandRejectedError(
            "unsupported_action",
            "That action is unavailable.",
            {"action_type": action_type},
        )

    session.active_actions.append(
        clone_json_object(action, path="queued_action")
    )
    return action_id


def remove_action(
    session: GameSession,
    *,
    action_id: str,
) -> str:
    """Removes one action by its durable engine-issued ID."""
    remove_index: int | None = None
    for index, action in enumerate(session.active_actions):
        if action.get("action_id") == action_id:
            remove_index = index
            break

    if remove_index is None:
        raise CommandRejectedError(
            "action_not_found",
            "The queued action was not found.",
            {"action_id": action_id},
        )

    removed = session.active_actions.pop(remove_index)
    removed_action_id = removed.get("action_id")
    if not isinstance(removed_action_id, str) or not removed_action_id:
        # Save invariants should make this unreachable.
        raise RuntimeError("validated queued action is missing action_id")
    return removed_action_id
