"""Headless orchestration for death-continuation handoff."""

from __future__ import annotations

from .errors import CommandRejectedError
from .history import append_event_log_entry
from .json_types import JSONObject
from .randomness import RandomSource
from .session import (
    GENDER_CHOICE_AGE_RANGE,
    SEXUALITY_CHOICE_AGE_RANGE,
    GameSession,
)


def _reject(reason: str, message: str, **details: object) -> None:
    raise CommandRejectedError(
        "continuation_not_available",
        message,
        {"reason": reason, **details},
    )


def continue_as(
    world: object,
    session: GameSession,
    random_source: RandomSource,
    *,
    successor_actor_id: str,
) -> dict[str, object]:
    """Hands focus from the current dead life to one canonical successor."""
    if session.pending_choice is not None:
        _reject(
            "choice_pending",
            "Resolve the pending choice before continuing as someone else.",
        )
    if session.remaining_skip_months:
        _reject(
            "skip_resume_pending",
            "Resolve the interrupted time advance before continuing.",
        )

    from_actor_id = session.focused_actor_id
    get_actor = getattr(world, "get_actor", None)
    from_actor = (
        get_actor(from_actor_id)
        if callable(get_actor)
        else None
    )
    if from_actor is None or not callable(
        getattr(from_actor, "is_alive", None)
    ):
        _reject(
            "focus_missing",
            "This life could not be found.",
            actor_id=from_actor_id,
        )
    if from_actor.is_alive():
        _reject(
            "focus_alive",
            "Continuation is only available after this life ends.",
            actor_id=from_actor_id,
        )

    continuity_state = world.build_continuity_state_for(from_actor_id)
    candidate_ids = continuity_state.get("continuity_candidate_ids")
    if not isinstance(candidate_ids, list) or not candidate_ids:
        _reject(
            "no_candidates",
            "No one is currently available to continue as.",
        )
    if successor_actor_id not in candidate_ids:
        _reject(
            "candidate_unavailable",
            "That person is no longer available to continue as.",
            actor_id=successor_actor_id,
        )

    try:
        handoff = world.handoff_focus_to_continuation(
            from_actor_id,
            successor_actor_id,
        )
    except ValueError as exc:
        raise CommandRejectedError(
            "continuation_not_available",
            "That person is no longer available to continue as.",
            {
                "reason": "candidate_unavailable",
                "actor_id": successor_actor_id,
            },
        ) from exc

    session.focused_actor_id = successor_actor_id
    session.active_actions = []
    session.pending_choice = None
    session.remaining_skip_months = 0
    session.meeting_event_last_total_months = 0
    session.last_logged_year = getattr(world, "current_year")
    successor_name = handoff["new_focused_actor_name"]
    append_event_log_entry(
        session.event_log,
        "life_separator",
        f"New Life: {successor_name}",
    )

    successor = world.get_actor(successor_actor_id)
    if successor is None:
        raise RuntimeError("continuation successor disappeared after handoff")
    lifecycle = successor.get_lifecycle_state(
        getattr(world, "current_year"),
        getattr(world, "current_month"),
    )
    age_years = lifecycle.get("age_years")
    if not isinstance(age_years, int):
        raise RuntimeError("continuation successor has invalid lifecycle")

    if age_years >= 18:
        world.auto_resolve_human_identity(
            successor_actor_id,
            random_source=random_source,
        )
        session.gender_choice_offered = True
        session.sexuality_choice_offered = True
        session.identity_popup_suppressed_for_resumed_adult = True
    else:
        session.gender_choice_offered = False
        session.sexuality_choice_offered = False
        session.identity_popup_suppressed_for_resumed_adult = False

    session.gender_choice_age = random_source.randint(
        *GENDER_CHOICE_AGE_RANGE
    )
    session.sexuality_choice_age = random_source.randint(
        *SEXUALITY_CHOICE_AGE_RANGE
    )

    effects: list[JSONObject] = [
        {
            "kind": "continued_as",
            "previous_actor_id": from_actor_id,
            "focused_actor_id": successor_actor_id,
        }
    ]
    return {
        "events": [],
        "effects": effects,
        "interruption": None,
    }
