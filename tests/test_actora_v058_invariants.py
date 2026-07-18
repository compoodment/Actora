"""Adversarial save/result invariants introduced with engine v0.58."""

from __future__ import annotations

import unittest
from copy import deepcopy

from actora_core import (
    CommandError,
    CommandResult,
    CommandType,
    InvariantError,
    SaveEnvelope,
    assert_valid_save_envelope,
)
from tests.test_actora_choice_continuation import (
    _continuation_save,
    _offer_gender,
    _offer_meeting,
    _rest_picker_save,
)
from tests.test_actora_core import build_test_world
from tests.test_actora_dispatcher import build_dispatch_save


class ExecutableSaveInvariantTests(unittest.TestCase):
    def assert_invalid(self, save_data, code: str) -> None:
        with self.assertRaisesRegex(InvariantError, code):
            assert_valid_save_envelope(SaveEnvelope.from_dict(save_data))

    def test_forged_life_choices_and_resume_counts_are_rejected(self) -> None:
        gender = _offer_gender(months=3).save.to_dict()

        forged_option = deepcopy(gender)
        forged_option["session"]["pending_choice"]["options"][-1] = {
            "option_id": "value:Hacker",
            "label": "Hacker",
            "value": "Hacker",
        }
        self.assert_invalid(
            forged_option,
            "noncanonical_life_choice_options",
        )

        forged_gate = deepcopy(gender)
        forged_gate["session"]["gender_choice_offered"] = False
        self.assert_invalid(
            forged_gate,
            "noncanonical_gender_choice_state",
        )

        oversized_resume = deepcopy(gender)
        oversized_resume["session"]["remaining_skip_months"] = 121
        self.assert_invalid(
            oversized_resume,
            "skip_resume_exceeds_command_limit",
        )

        action_resume = _rest_picker_save().to_dict()
        action_resume["session"]["remaining_skip_months"] = 1
        self.assert_invalid(
            action_resume,
            "invalid_choice_skip_resume",
        )

        meeting = _offer_meeting().save.to_dict()
        meeting["session"]["meeting_event_last_total_months"] -= 1
        self.assert_invalid(
            meeting,
            "noncanonical_meeting_choice_state",
        )

    def test_dead_focus_and_future_actor_ids_are_rejected(self) -> None:
        dead = _continuation_save(adult=False).to_dict()
        dead_with_action = deepcopy(dead)
        dead_with_action["session"]["active_actions"] = [
            {
                "action_id": "trace_action_00000001",
                "action_type": "spend_time",
                "target_actor_id": "friend",
                "label": "Spend time with Charles Babbage",
                "time_cost": 4,
            }
        ]
        self.assert_invalid(dead_with_action, "dead_focus_has_actions")

        future_actor = build_dispatch_save().to_dict()
        future_actor["world"]["actors"]["trace_npc_00000001"] = deepcopy(
            future_actor["world"]["actors"]["friend"]
        )
        self.assert_invalid(future_actor, "unissued_actor_id")

    def test_cross_role_id_sequence_reuse_is_rejected(self) -> None:
        reused = build_dispatch_save(next_id=2).to_dict()
        reused["world"]["actors"]["trace_npc_00000001"] = deepcopy(
            reused["world"]["actors"]["friend"]
        )
        reused["session"]["active_actions"] = [
            {
                "action_id": "trace_action_00000001",
                "action_type": "personal",
                "subtype_id": "music",
                "label": "Listen to Music",
                "time_cost": 2,
                "stat_changes": {"happiness": 3, "stress": -2},
                "event_text": (
                    "You put on some music and let yourself unwind."
                ),
            }
        ]
        self.assert_invalid(reused, "reused_issued_id_value")

    def test_impossible_prompt_age_and_lifecycle_are_rejected(
        self,
    ) -> None:
        too_young = _offer_gender().save.to_dict()
        too_young["session"]["gender_choice_age"] = 15
        self.assert_invalid(
            too_young,
            "noncanonical_gender_choice_state",
        )

        invalid_threshold = _offer_gender().save.to_dict()
        invalid_threshold["session"]["gender_choice_age"] = 11
        self.assert_invalid(
            invalid_threshold,
            "invalid_gender_choice_age",
        )

        meeting = _offer_meeting().save.to_dict()
        meeting["world"]["actors"]["player"]["birth_year"] = 3
        meeting["world"]["actors"]["player"]["birth_month"] = 8
        self.assert_invalid(
            meeting,
            "noncanonical_meeting_choice_state",
        )

    def test_identity_flags_suppression_and_cooldown_require_real_state(
        self,
    ) -> None:
        premature_gender = build_dispatch_save().to_dict()
        premature_gender["session"]["gender_choice_offered"] = True
        self.assert_invalid(
            premature_gender,
            "premature_gender_choice_state",
        )

        premature_sexuality = build_dispatch_save().to_dict()
        premature_sexuality["session"]["sexuality_choice_offered"] = True
        self.assert_invalid(
            premature_sexuality,
            "premature_sexuality_choice_state",
        )

        invalid_suppression = build_dispatch_save().to_dict()
        invalid_suppression["session"][
            "identity_popup_suppressed_for_resumed_adult"
        ] = True
        self.assert_invalid(
            invalid_suppression,
            "invalid_identity_suppression_state",
        )

        future_cooldown = build_dispatch_save().to_dict()
        future_cooldown["session"]["meeting_event_last_total_months"] = 44
        self.assert_invalid(
            future_cooldown,
            "future_meeting_cooldown",
        )

    def test_action_picker_default_must_remain_null(self) -> None:
        action_picker = _rest_picker_save().to_dict()
        action_picker["session"]["pending_choice"]["default_value"] = "music"
        self.assert_invalid(
            action_picker,
            "noncanonical_action_choice_state",
        )

    def test_completed_handoff_cannot_refocus_the_prior_dead_life(self) -> None:
        save = _continuation_save(adult=False)
        world_state = deepcopy(save.world)
        world = build_test_world()
        world.mark_actor_dead("player", reason="test continuation")
        world.handoff_focus_to_continuation("player", "friend")
        handoff_data = save.to_dict()
        handoff_data["world"] = deepcopy(world_state)
        handoff_data["world"]["records"] = deepcopy(world.records)
        handoff_data["world"]["focused_actor_id"] = "player"
        handoff_data["session"]["focused_actor_id"] = "player"
        self.assert_invalid(
            handoff_data,
            "completed_continuation_still_focused",
        )

    def test_world_rejects_duplicate_actor_insertion(self) -> None:
        world = build_test_world()
        with self.assertRaisesRegex(ValueError, "already exists"):
            world.add_actor("player", world.actors["friend"])


class StrictResultShapeTests(unittest.TestCase):
    def test_unknown_effects_incomplete_events_and_failed_effects_reject(
        self,
    ) -> None:
        save = build_dispatch_save()
        with self.assertRaisesRegex(
            ValueError,
            "Unsupported result effect kind",
        ):
            CommandResult(
                command_id="bad-effect",
                command_type=CommandType.QUEUE_ACTION,
                ok=True,
                revision=save.revision,
                save=save,
                effects=({"kind": "anything_goes"},),
            )
        with self.assertRaisesRegex(ValueError, "must contain event_id"):
            CommandResult(
                command_id="bad-event",
                command_type=CommandType.QUEUE_ACTION,
                ok=True,
                revision=save.revision,
                save=save,
                events=({"text": "Incomplete."},),
            )
        with self.assertRaisesRegex(
            ValueError,
            "failed result must not contain events or effects",
        ):
            CommandResult(
                command_id="bad-failure",
                command_type=CommandType.QUEUE_ACTION,
                ok=False,
                revision=save.revision,
                save=save,
                effects=(
                    {
                        "kind": "action_queued",
                        "action_id": "trace_action_00000001",
                    },
                ),
                error=CommandError(
                    code="rejected",
                    message="No.",
                ),
            )


if __name__ == "__main__":
    unittest.main()
