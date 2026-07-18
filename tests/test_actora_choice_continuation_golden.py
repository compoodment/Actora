"""Golden command traces for choice resolution and continuation."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from actora_core import (
    CommandType,
    DeterministicIdSource,
    GameSession,
    SeededRandomSource,
    dispatch_command,
)
from actora_core.serialization import (
    build_save_envelope,
    dumps_save_envelope,
    loads_save_envelope,
)
from tests.test_actora_core import build_test_world
from tests.test_actora_dispatcher import (
    build_dispatch_save,
    command,
)

GOLDEN_PATH = (
    Path(__file__).resolve().parent
    / "golden"
    / "dispatcher_choice_continuation_v1.json"
)


def _snapshot(result) -> dict[str, object]:
    save = result.save
    actor = (
        save.world["actors"].get(save.session.focused_actor_id)
        if save is not None
        else None
    )
    return {
        "command_id": result.command_id,
        "command_type": result.command_type.value,
        "ok": result.ok,
        "revision": result.revision,
        "error_code": result.error.code if result.error else None,
        "events": list(result.events),
        "effects": list(result.effects),
        "interruption": result.interruption,
        "save_sha256": (
            hashlib.sha256(
                dumps_save_envelope(save).encode("utf-8")
            ).hexdigest()
            if save is not None
            else None
        ),
        "date": (
            {
                "year": save.world["current_year"],
                "month": save.world["current_month"],
            }
            if save is not None
            else None
        ),
        "focused_actor_id": (
            save.session.focused_actor_id if save is not None else None
        ),
        "focused_identity": (
            {
                "gender": actor["gender"],
                "sexuality": actor["sexuality"],
            }
            if isinstance(actor, dict)
            else None
        ),
        "pending_choice_id": (
            save.session.pending_choice.get("choice_id")
            if save is not None
            and save.session.pending_choice is not None
            else None
        ),
        "remaining_skip_months": (
            save.session.remaining_skip_months
            if save is not None
            else None
        ),
        "actor_ids": (
            sorted(save.world["actors"]) if save is not None else []
        ),
        "rng": save.rng.to_dict() if save is not None else None,
        "ids": save.ids.to_dict() if save is not None else None,
    }


class ChoiceContinuationGoldenTraceTests(unittest.TestCase):
    def test_dispatcher_choice_continuation_v1_trace(self) -> None:
        identity_world = build_test_world()
        identity_world.actors["player"].birth_year = -11
        identity_world.actors["player"].birth_month = 8
        identity_save = build_dispatch_save(
            world=identity_world,
            session=GameSession(
                focused_actor_id="player",
                last_logged_year=3,
                gender_choice_age=12,
                sexuality_choice_age=14,
            )
        )
        identity_advance = dispatch_command(
            identity_save,
            command(
                "trace-identity-advance",
                CommandType.ADVANCE_TIME,
                {"months": 3},
                0,
            ),
        )
        gender_resolve = dispatch_command(
            loads_save_envelope(
                dumps_save_envelope(identity_advance.save)
            ),
            command(
                "trace-gender-resolve",
                CommandType.RESOLVE_CHOICE,
                {
                    "choice_id": "gender_identity",
                    "option_id": "value:Non-binary",
                },
                1,
            ),
        )
        sexuality_resolve = dispatch_command(
            gender_resolve.save,
            command(
                "trace-sexuality-resolve",
                CommandType.RESOLVE_CHOICE,
                {
                    "choice_id": "sexuality",
                    "option_id": "value:Bisexual",
                },
                2,
            ),
        )

        meeting_world = build_test_world()
        meeting_world.actors["player"].birth_year = -3
        meeting_save = build_save_envelope(
            meeting_world,
            GameSession(
                focused_actor_id="player",
                last_logged_year=3,
            ),
            SeededRandomSource(3),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        meeting_advance = dispatch_command(
            meeting_save,
            command(
                "trace-meeting-advance",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        meeting_resolve = dispatch_command(
            meeting_advance.save,
            command(
                "trace-meeting-resolve",
                CommandType.RESOLVE_CHOICE,
                {
                    "choice_id": "meeting_npc",
                    "option_id": "value:introduce",
                },
                1,
            ),
        )

        death_world = build_test_world()
        death_world.actors["player"].birth_year = -120
        death_save = build_save_envelope(
            death_world,
            GameSession(
                focused_actor_id="player",
                last_logged_year=3,
            ),
            SeededRandomSource(11),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        death_advance = dispatch_command(
            death_save,
            command(
                "trace-death-advance",
                CommandType.ADVANCE_TIME,
                {"months": 5},
                0,
            ),
        )
        continuation = dispatch_command(
            loads_save_envelope(
                dumps_save_envelope(death_advance.save)
            ),
            command(
                "trace-continue",
                CommandType.CONTINUE_AS,
                {"actor_id": "friend"},
                1,
            ),
        )

        observed = {
            "contract": "dispatcher-choice-continuation-v1",
            "steps": [
                _snapshot(identity_advance),
                _snapshot(gender_resolve),
                _snapshot(sexuality_resolve),
                _snapshot(meeting_advance),
                _snapshot(meeting_resolve),
                _snapshot(death_advance),
                _snapshot(continuation),
            ],
        }
        with GOLDEN_PATH.open("r", encoding="utf-8") as golden_file:
            expected = json.load(golden_file)
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
