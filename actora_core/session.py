"""Serializable game-session state currently scattered across the TUI shell."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import ContractValidationError
from .json_types import (
    JSONValue,
    clone_json,
    clone_json_object,
    require_int,
    require_nonempty_string,
)
from .randomness import RandomSource


def _clone_object_list(value: object, *, path: str) -> list[dict[str, JSONValue]]:
    if not isinstance(value, list):
        raise ContractValidationError(f"{path} must be an array")
    return [
        clone_json_object(item, path=f"{path}[{index}]")
        for index, item in enumerate(value)
    ]


def _stable_option_id(
    choice_id: object,
    value: JSONValue,
    *,
    index: int,
) -> str:
    if choice_id == "select_hang_out_target" and isinstance(value, str):
        return f"actor:{value}"
    if (
        choice_id
        in {
            "select_exercise_subtype",
            "select_read_subtype",
            "select_rest_subtype",
        }
        and isinstance(value, str)
    ):
        return f"subtype:{value}"
    if isinstance(value, str):
        return f"value:{value}"
    return f"option:{index}"


def _capture_pending_choice(runtime: Any) -> dict[str, JSONValue] | None:
    raw_choice = getattr(runtime, "pending_choice", None)
    if raw_choice is None:
        return None
    choice = clone_json_object(raw_choice, path="runtime.pending_choice")
    raw_options = choice.get("options")
    if (
        isinstance(raw_options, list)
        and raw_options
        and all(isinstance(option, dict) for option in raw_options)
    ):
        return choice
    if (
        not isinstance(raw_options, list)
        or not raw_options
        or any(not isinstance(label, str) for label in raw_options)
    ):
        raise ContractValidationError(
            "runtime.pending_choice.options must be a non-empty string array"
        )

    choice_id = choice.get("choice_id")
    values: list[JSONValue]
    if choice_id == "select_hang_out_target":
        values = list(getattr(runtime, "hang_out_actor_ids", []))
    elif choice_id in {
        "select_exercise_subtype",
        "select_read_subtype",
        "select_rest_subtype",
    }:
        subtype_options = getattr(runtime, "personal_subtype_options", [])
        if not isinstance(subtype_options, list):
            raise ContractValidationError(
                "runtime.personal_subtype_options must be an array"
            )
        values = [
            subtype.get("id") if isinstance(subtype, dict) else None
            for subtype in subtype_options
        ]
    elif choice_id == "sexuality":
        choice_controller = getattr(runtime, "choice_controller", None)
        labels = getattr(choice_controller, "sexuality_option_labels", ())
        value_by_label = dict(labels) if isinstance(labels, (list, tuple)) else {}
        values = [value_by_label.get(label, label) for label in raw_options]
    else:
        values = list(raw_options)
    if len(values) != len(raw_options):
        raise ContractValidationError(
            "runtime choice values must match the displayed option count"
        )

    structured_options: list[dict[str, JSONValue]] = []
    for index, (label, value) in enumerate(zip(raw_options, values)):
        structured_options.append(
            {
                "option_id": _stable_option_id(
                    choice_id,
                    value,
                    index=index,
                ),
                "label": label,
                "value": clone_json(
                    value,
                    path=f"runtime.pending_choice.options[{index}].value",
                ),
            }
        )
    selected_index = require_int(
        choice.get("selected_index"),
        path="runtime.pending_choice.selected_index",
        minimum=0,
        maximum=len(structured_options) - 1,
    )
    structured_choice = {
        field_name: clone_json(
            choice.get(field_name),
            path=f"runtime.pending_choice.{field_name}",
        )
        for field_name in (
            "choice_id",
            "title",
            "text",
            "question",
            "skippable",
        )
    }
    structured_choice["options"] = structured_options
    structured_choice["selected_option_id"] = structured_options[
        selected_index
    ]["option_id"]
    if "default_value" in choice:
        structured_choice["default_value"] = clone_json(
            choice["default_value"],
            path="runtime.pending_choice.default_value",
        )
    return structured_choice


def _apply_pending_choice_to_runtime(
    runtime: Any,
    pending_choice: dict[str, JSONValue] | None,
) -> None:
    runtime.hang_out_actor_ids = []
    runtime.personal_subtype_options = []
    if pending_choice is None:
        runtime.pending_choice = None
        return

    choice = clone_json_object(
        pending_choice,
        path="session.pending_choice",
    )
    options = choice.get("options")
    if not isinstance(options, list) or any(
        not isinstance(option, dict) for option in options
    ):
        raise ContractValidationError(
            "session.pending_choice.options must be an object array"
        )
    selected_option_id = choice.get("selected_option_id")
    selected_index = next(
        (
            index
            for index, option in enumerate(options)
            if option.get("option_id") == selected_option_id
        ),
        None,
    )
    if selected_index is None:
        raise ContractValidationError(
            "session.pending_choice.selected_option_id is unavailable"
        )
    runtime.pending_choice = {
        field_name: clone_json(
            choice.get(field_name),
            path=f"session.pending_choice.{field_name}",
        )
        for field_name in (
            "choice_id",
            "title",
            "text",
            "question",
            "skippable",
        )
    }
    runtime.pending_choice["options"] = [
        option.get("label") for option in options
    ]
    runtime.pending_choice["selected_index"] = selected_index
    if "default_value" in choice:
        runtime.pending_choice["default_value"] = clone_json(
            choice["default_value"],
            path="session.pending_choice.default_value",
        )

    choice_id = choice.get("choice_id")
    if choice_id == "select_hang_out_target":
        runtime.hang_out_actor_ids = [
            option.get("value") for option in options
        ]
    elif choice_id in {
        "select_exercise_subtype",
        "select_read_subtype",
        "select_rest_subtype",
    }:
        from mechanics import EXERCISE_SUBTYPES, READ_SUBTYPES, REST_SUBTYPES

        subtype_by_id = {
            subtype["id"]: subtype
            for subtype in (
                *EXERCISE_SUBTYPES,
                *READ_SUBTYPES,
                *REST_SUBTYPES,
            )
        }
        runtime.personal_subtype_options = [
            clone_json_object(
                subtype_by_id.get(option.get("value")),
                path=f"session.pending_choice.options[{index}].subtype",
            )
            for index, option in enumerate(options)
        ]


@dataclass(slots=True)
class GameSession:
    """Headless state that must survive between commands.

    The fields mirror simulation-relevant state currently held by ``ActoraTUI``:
    action queues, pending/resumable choices, player-facing history bookkeeping,
    identity-choice gates, and meeting cooldown. Choice targets and values live
    inside complete, stable-ID option objects instead of positional side arrays.
    Screen names, popup visibility, scroll offsets, selected UI rows, footer
    messages, and quit state are intentionally presentation-only and excluded.
    """

    focused_actor_id: str
    active_actions: list[dict[str, JSONValue]] = field(default_factory=list)
    pending_choice: dict[str, JSONValue] | None = None
    remaining_skip_months: int = 0
    event_log: list[dict[str, JSONValue]] = field(default_factory=list)
    last_logged_year: int = 0
    gender_choice_offered: bool = False
    sexuality_choice_offered: bool = False
    identity_popup_suppressed_for_resumed_adult: bool = False
    gender_choice_age: int = 12
    sexuality_choice_age: int = 14
    meeting_event_last_total_months: int = 0

    def __post_init__(self) -> None:
        self.focused_actor_id = require_nonempty_string(
            self.focused_actor_id,
            path="session.focused_actor_id",
        )
        self.active_actions = _clone_object_list(
            self.active_actions,
            path="session.active_actions",
        )
        if self.pending_choice is not None:
            self.pending_choice = clone_json_object(
                self.pending_choice,
                path="session.pending_choice",
            )
        self.event_log = _clone_object_list(
            self.event_log,
            path="session.event_log",
        )
        self.remaining_skip_months = require_int(
            self.remaining_skip_months,
            path="session.remaining_skip_months",
            minimum=0,
        )
        self.last_logged_year = require_int(
            self.last_logged_year,
            path="session.last_logged_year",
            minimum=0,
        )
        self.gender_choice_age = require_int(
            self.gender_choice_age,
            path="session.gender_choice_age",
            minimum=0,
        )
        self.sexuality_choice_age = require_int(
            self.sexuality_choice_age,
            path="session.sexuality_choice_age",
            minimum=0,
        )
        self.meeting_event_last_total_months = require_int(
            self.meeting_event_last_total_months,
            path="session.meeting_event_last_total_months",
            minimum=0,
        )
        for field_name in (
            "gender_choice_offered",
            "sexuality_choice_offered",
            "identity_popup_suppressed_for_resumed_adult",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise ContractValidationError(f"session.{field_name} must be a boolean")

    @classmethod
    def new(cls, focused_actor_id: str, random_source: RandomSource) -> "GameSession":
        """Creates the current shell defaults through injected randomness."""
        return cls(
            focused_actor_id=focused_actor_id,
            gender_choice_age=random_source.randint(12, 15),
            sexuality_choice_age=random_source.randint(14, 17),
        )

    @classmethod
    def capture_runtime(cls, runtime: Any) -> "GameSession":
        """Captures TUI-shaped state once queued actions are engine-authored.

        The legacy terminal currently queues actions without durable IDs. Until
        it routes queue mutations through the dispatcher, a non-empty legacy
        queue is rejected instead of inventing IDs outside the saved ID source.
        """
        if hasattr(runtime, "get_focused_actor_id"):
            focused_actor_id = runtime.get_focused_actor_id()
        else:
            focused_actor_id = getattr(runtime, "player_id", None)
        active_actions = getattr(runtime, "active_actions", [])
        if not isinstance(active_actions, list):
            raise ContractValidationError(
                "runtime.active_actions must be an array"
            )
        for index, action in enumerate(active_actions):
            if (
                not isinstance(action, dict)
                or not isinstance(action.get("action_id"), str)
                or not action["action_id"]
            ):
                raise ContractValidationError(
                    "runtime.active_actions"
                    f"[{index}] must contain an engine-issued action_id"
                )
        return cls(
            focused_actor_id=focused_actor_id,
            active_actions=active_actions,
            pending_choice=_capture_pending_choice(runtime),
            remaining_skip_months=getattr(runtime, "remaining_skip_months", 0),
            event_log=getattr(runtime, "event_log", []),
            last_logged_year=getattr(runtime, "last_logged_year", 0),
            gender_choice_offered=getattr(runtime, "gender_choice_offered", False),
            sexuality_choice_offered=getattr(runtime, "sexuality_choice_offered", False),
            identity_popup_suppressed_for_resumed_adult=getattr(
                runtime,
                "identity_popup_suppressed_for_resumed_adult",
                False,
            ),
            gender_choice_age=getattr(runtime, "gender_choice_age", 12),
            sexuality_choice_age=getattr(runtime, "sexuality_choice_age", 14),
            meeting_event_last_total_months=getattr(
                runtime,
                "meeting_event_last_total_months",
                0,
            ),
        )

    def apply_to_runtime(self, runtime: Any) -> None:
        """Restores captured state onto the current TUI-compatible runtime."""
        world = getattr(runtime, "world", None)
        if world is not None and hasattr(world, "set_focused_actor"):
            world.set_focused_actor(self.focused_actor_id)
        runtime.player_id = self.focused_actor_id
        runtime.active_actions = clone_json(self.active_actions, path="session.active_actions")
        _apply_pending_choice_to_runtime(runtime, self.pending_choice)
        runtime.remaining_skip_months = self.remaining_skip_months
        runtime.event_log = clone_json(self.event_log, path="session.event_log")
        runtime.last_logged_year = self.last_logged_year
        runtime.gender_choice_offered = self.gender_choice_offered
        runtime.sexuality_choice_offered = self.sexuality_choice_offered
        runtime.identity_popup_suppressed_for_resumed_adult = (
            self.identity_popup_suppressed_for_resumed_adult
        )
        runtime.gender_choice_age = self.gender_choice_age
        runtime.sexuality_choice_age = self.sexuality_choice_age
        runtime.meeting_event_last_total_months = self.meeting_event_last_total_months

    @classmethod
    def from_dict(cls, data: object) -> "GameSession":
        if not isinstance(data, dict):
            raise ContractValidationError("session must be an object")
        allowed_fields = {
            "focused_actor_id",
            "active_actions",
            "pending_choice",
            "remaining_skip_months",
            "event_log",
            "last_logged_year",
            "gender_choice_offered",
            "sexuality_choice_offered",
            "identity_popup_suppressed_for_resumed_adult",
            "gender_choice_age",
            "sexuality_choice_age",
            "meeting_event_last_total_months",
        }
        unknown_fields = sorted(
            str(field)
            for field in data
            if not isinstance(field, str) or field not in allowed_fields
        )
        if unknown_fields:
            raise ContractValidationError(
                "session contains unknown fields: " + ", ".join(unknown_fields)
            )
        return cls(
            focused_actor_id=data.get("focused_actor_id"),
            active_actions=data.get("active_actions", []),
            pending_choice=data.get("pending_choice"),
            remaining_skip_months=data.get("remaining_skip_months", 0),
            event_log=data.get("event_log", []),
            last_logged_year=data.get("last_logged_year", 0),
            gender_choice_offered=data.get("gender_choice_offered", False),
            sexuality_choice_offered=data.get("sexuality_choice_offered", False),
            identity_popup_suppressed_for_resumed_adult=data.get(
                "identity_popup_suppressed_for_resumed_adult",
                False,
            ),
            gender_choice_age=data.get("gender_choice_age", 12),
            sexuality_choice_age=data.get("sexuality_choice_age", 14),
            meeting_event_last_total_months=data.get(
                "meeting_event_last_total_months",
                0,
            ),
        )

    def to_dict(self) -> dict[str, JSONValue]:
        focused_actor_id = require_nonempty_string(
            self.focused_actor_id,
            path="session.focused_actor_id",
        )
        active_actions = _clone_object_list(
            self.active_actions,
            path="session.active_actions",
        )
        pending_choice = (
            clone_json_object(
                self.pending_choice,
                path="session.pending_choice",
            )
            if self.pending_choice is not None
            else None
        )
        remaining_skip_months = require_int(
            self.remaining_skip_months,
            path="session.remaining_skip_months",
            minimum=0,
        )
        event_log = _clone_object_list(
            self.event_log,
            path="session.event_log",
        )
        last_logged_year = require_int(
            self.last_logged_year,
            path="session.last_logged_year",
            minimum=0,
        )
        gender_choice_age = require_int(
            self.gender_choice_age,
            path="session.gender_choice_age",
            minimum=0,
        )
        sexuality_choice_age = require_int(
            self.sexuality_choice_age,
            path="session.sexuality_choice_age",
            minimum=0,
        )
        meeting_event_last_total_months = require_int(
            self.meeting_event_last_total_months,
            path="session.meeting_event_last_total_months",
            minimum=0,
        )
        boolean_values: dict[str, bool] = {}
        for field_name in (
            "gender_choice_offered",
            "sexuality_choice_offered",
            "identity_popup_suppressed_for_resumed_adult",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, bool):
                raise ContractValidationError(
                    f"session.{field_name} must be a boolean"
                )
            boolean_values[field_name] = value
        return {
            "focused_actor_id": focused_actor_id,
            "active_actions": active_actions,
            "pending_choice": pending_choice,
            "remaining_skip_months": remaining_skip_months,
            "event_log": event_log,
            "last_logged_year": last_logged_year,
            "gender_choice_offered": boolean_values["gender_choice_offered"],
            "sexuality_choice_offered": boolean_values[
                "sexuality_choice_offered"
            ],
            "identity_popup_suppressed_for_resumed_adult": (
                boolean_values[
                    "identity_popup_suppressed_for_resumed_adult"
                ]
            ),
            "gender_choice_age": gender_choice_age,
            "sexuality_choice_age": sexuality_choice_age,
            "meeting_event_last_total_months": meeting_event_last_total_months,
        }
