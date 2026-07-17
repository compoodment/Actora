"""Regression tests for legacy TUI choice adaptation."""

from __future__ import annotations

import json
import unittest
from types import SimpleNamespace

from actora_core import GameSession
from life_event_controller import LifeEventController
from mechanics import (
    GENDER_IDENTITY_OPTIONS,
    MEETING_EVENT_COOLDOWN_MONTHS,
    SEXUALITY_OPTION_LABELS,
)


class LegacyRuntime(SimpleNamespace):
    """Small TUI-shaped runtime used at the GameSession adapter boundary."""

    def get_focused_actor_id(self) -> str:
        return self.player_id


class LegacyChoiceAdapterTests(unittest.TestCase):
    def test_meeting_choice_semantics_survive_capture_apply_and_recapture(
        self,
    ) -> None:
        source = LegacyRuntime(
            player_id="player",
            active_actions=[],
            pending_choice={
                "choice_id": "meeting_npc",
                "title": "Someone new",
                "text": "You notice someone nearby.",
                "question": "Do you want to introduce yourself?",
                "options": [
                    "Introduce yourself",
                    "Keep to yourself",
                ],
                "selected_index": 1,
                "skippable": False,
            },
        )

        captured = GameSession.capture_runtime(source)
        self.assertEqual(
            captured.pending_choice["options"],
            [
                {
                    "option_id": "value:introduce",
                    "label": "Introduce yourself",
                    "value": "introduce",
                },
                {
                    "option_id": "value:keep_to_self",
                    "label": "Keep to yourself",
                    "value": "keep_to_self",
                },
            ],
        )
        self.assertEqual(
            captured.pending_choice["selected_option_id"],
            "value:keep_to_self",
        )

        serialized = json.loads(json.dumps(captured.to_dict()))
        restored = GameSession.from_dict(serialized)
        target = LegacyRuntime(
            player_id="other",
            active_actions=[],
            pending_choice=None,
        )
        restored.apply_to_runtime(target)

        self.assertEqual(target.player_id, "player")
        self.assertEqual(
            target.pending_choice["options"],
            ["Introduce yourself", "Keep to yourself"],
        )
        self.assertEqual(target.pending_choice["selected_index"], 1)
        self.assertEqual(
            GameSession.capture_runtime(target).to_dict(),
            restored.to_dict(),
        )


class CustomGenderChoiceTests(unittest.TestCase):
    def test_custom_current_gender_remains_an_available_selection_and_default(
        self,
    ) -> None:
        current_gender = "Demigirl"

        class Actor:
            gender = current_gender

            @staticmethod
            def is_alive() -> bool:
                return True

            @staticmethod
            def get_lifecycle_state(_year: int, _month: int) -> dict[str, int]:
                return {"age_years": 13}

        class Runtime(LegacyRuntime):
            def get_focused_actor(self) -> Actor:
                return self.actor

        app = Runtime(
            actor=Actor(),
            world=SimpleNamespace(current_year=13, current_month=1),
            player_id="player",
            active_actions=[],
            pending_choice=None,
            identity_popup_suppressed_for_resumed_adult=False,
            gender_choice_age=12,
            sexuality_choice_age=14,
            gender_choice_offered=False,
            sexuality_choice_offered=False,
            last_message="",
        )
        controller = LifeEventController(
            MEETING_EVENT_COOLDOWN_MONTHS,
            GENDER_IDENTITY_OPTIONS,
            SEXUALITY_OPTION_LABELS,
        )

        self.assertTrue(controller.maybe_offer_identity_choice(app))
        options = app.pending_choice["options"]
        selected_index = app.pending_choice["selected_index"]
        default_value = app.pending_choice["default_value"]
        self.assertEqual(options.count(current_gender), 1)
        self.assertEqual(options[selected_index], current_gender)
        self.assertIn(default_value, options)

        captured = GameSession.capture_runtime(app)
        structured_options = captured.pending_choice["options"]
        available_values = [option["value"] for option in structured_options]
        available_option_ids = [
            option["option_id"] for option in structured_options
        ]
        self.assertIn(captured.pending_choice["default_value"], available_values)
        self.assertIn(
            captured.pending_choice["selected_option_id"],
            available_option_ids,
        )
        self.assertEqual(
            captured.pending_choice["selected_option_id"],
            f"value:{current_gender}",
        )


if __name__ == "__main__":
    unittest.main()
