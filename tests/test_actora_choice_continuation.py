"""Dispatcher coverage for choice resolution and death continuation."""

from __future__ import annotations

import random
import unittest
from copy import deepcopy

from mechanics import REST_SUBTYPES

from actora_core import (
    CommandType,
    DeterministicIdSource,
    GameSession,
    SaveEnvelope,
    SeededRandomSource,
    dispatch_command,
    dispatch_serialized_command,
    dumps_command_result,
    dumps_game_command,
    loads_command_result,
)
from actora_core.json_types import MAX_SAFE_INTEGER
from actora_core.serialization import (
    build_save_envelope,
    dumps_save_envelope,
)
from tests.test_actora_core import build_test_world
from tests.test_actora_dispatcher import command


def _dispatch_choice(save, choice_id: str, option_id: str | None):
    return dispatch_command(
        save,
        command(
            f"resolve-{choice_id}",
            CommandType.RESOLVE_CHOICE,
            {"choice_id": choice_id, "option_id": option_id},
            save.revision,
        ),
    )


def _offer_gender(*, current_gender: str = "Female", months: int = 1):
    world = build_test_world()
    world.actors["player"].gender = current_gender
    world.actors["player"].birth_year = -11
    world.actors["player"].birth_month = 8
    save = build_save_envelope(
        world,
        GameSession(
            focused_actor_id="player",
            last_logged_year=3,
            gender_choice_age=12,
            sexuality_choice_age=14,
        ),
        SeededRandomSource("gender-choice"),
        DeterministicIdSource("trace"),
        engine_version="headless-test",
    )
    return dispatch_command(
        save,
        command(
            "offer-gender",
            CommandType.ADVANCE_TIME,
            {"months": months},
            0,
        ),
    )


def _offer_sexuality():
    world = build_test_world()
    world.actors["player"].birth_year = -11
    world.actors["player"].birth_month = 8
    save = build_save_envelope(
        world,
        GameSession(
            focused_actor_id="player",
            last_logged_year=3,
            gender_choice_offered=True,
            gender_choice_age=12,
            sexuality_choice_age=14,
        ),
        SeededRandomSource("sexuality-choice"),
        DeterministicIdSource("trace"),
        engine_version="headless-test",
    )
    return dispatch_command(
        save,
        command(
            "offer-sexuality",
            CommandType.ADVANCE_TIME,
            {"months": 1},
            0,
        ),
    )


def _offer_meeting(*, next_id: int = 1):
    world = build_test_world()
    world.actors["player"].birth_year = -3
    save = build_save_envelope(
        world,
        GameSession(
            focused_actor_id="player",
            last_logged_year=3,
        ),
        SeededRandomSource(3),
        DeterministicIdSource("trace", next_value=next_id),
        engine_version="headless-test",
    )
    return dispatch_command(
        save,
        command(
            "offer-meeting",
            CommandType.ADVANCE_TIME,
            {"months": 1},
            0,
        ),
    )


def _picker_save(
    choice_id: str,
    options: list[dict[str, object]],
    *,
    selected_option_id: str,
):
    return build_save_envelope(
        build_test_world(),
        GameSession(
            focused_actor_id="player",
            last_logged_year=3,
            pending_choice={
                "choice_id": choice_id,
                "title": "Choose an action",
                "text": "Pick one option.",
                "question": "",
                "options": options,
                "selected_option_id": selected_option_id,
                "skippable": True,
                "default_value": None,
            },
        ),
        SeededRandomSource("picker-choice"),
        DeterministicIdSource("trace"),
        engine_version="headless-test",
    )


def _rest_picker_save():
    options = [
        {
            "option_id": f"subtype:{subtype['id']}",
            "label": f"{subtype['label']}  {subtype['time_cost']}h",
            "value": subtype["id"],
        }
        for subtype in REST_SUBTYPES
    ]
    return _picker_save(
        "select_rest_subtype",
        options,
        selected_option_id="subtype:nap",
    )


def _hang_out_picker_save():
    return _picker_save(
        "select_hang_out_target",
        [
            {
                "option_id": "actor:friend",
                "label": "Charles Babbage · Friend",
                "value": "friend",
            }
        ],
        selected_option_id="actor:friend",
    )


def _continuation_save(
    *,
    adult: bool,
    seed: str = "continuation-choice",
    include_candidate: bool = True,
):
    world = build_test_world()
    world.actors["player"].birth_year = -30
    if adult:
        world.actors["friend"].birth_year = -30
    if not include_candidate:
        world.links = []
    world.mark_actor_dead("player", reason="test continuation")
    session = GameSession(
        focused_actor_id="player",
        event_log=[
            {
                "kind": "event",
                "text": "Before continuation.",
                "year": 3,
                "month": 7,
            }
        ],
        last_logged_year=1,
        gender_choice_offered=True,
        sexuality_choice_offered=True,
        identity_popup_suppressed_for_resumed_adult=True,
        gender_choice_age=12,
        sexuality_choice_age=14,
        meeting_event_last_total_months=43,
    )
    return build_save_envelope(
        world,
        session,
        SeededRandomSource(seed),
        DeterministicIdSource("trace", next_value=8),
        engine_version="headless-test",
        revision=4,
    )


class IdentityChoiceTests(unittest.TestCase):
    def test_empty_gender_offers_other_and_resolves_without_crashing(
        self,
    ) -> None:
        offered = _offer_gender(current_gender="")

        self.assertTrue(offered.ok)
        self.assertEqual(
            offered.interruption,
            {
                "kind": "choice_required",
                "choice_id": "gender_identity",
                "remaining_months": 0,
            },
        )
        self.assertEqual(
            offered.save.session.pending_choice["default_value"],
            "Other",
        )
        resolved = _dispatch_choice(
            offered.save,
            "gender_identity",
            None,
        )
        self.assertTrue(resolved.ok)
        self.assertEqual(
            resolved.save.world["actors"]["player"]["gender"],
            "Other",
        )

    def test_gender_changed_default_and_custom_paths(self) -> None:
        changed_offer = _offer_gender()
        self.assertTrue(changed_offer.ok)
        changed_rng = changed_offer.save.rng
        changed_ids = changed_offer.save.ids
        changed = _dispatch_choice(
            changed_offer.save,
            "gender_identity",
            "value:Non-binary",
        )
        self.assertTrue(changed.ok)
        self.assertEqual(
            changed.save.world["actors"]["player"]["gender"],
            "Non-binary",
        )
        self.assertEqual(changed.save.rng, changed_rng)
        self.assertEqual(changed.save.ids, changed_ids)
        self.assertIsNone(changed.save.session.pending_choice)
        self.assertEqual(
            changed.events,
            (
                {
                    "text": "You now identify as Non-binary.",
                    "year": 3,
                    "month": 8,
                    "event_id": "gender_identity",
                    "tags": ["identity", "choice"],
                },
            ),
        )

        default_offer = _offer_gender()
        default = _dispatch_choice(
            default_offer.save,
            "gender_identity",
            None,
        )
        self.assertTrue(default.ok)
        self.assertEqual(
            default.save.world["actors"]["player"]["gender"],
            "Female",
        )
        self.assertEqual(
            default.effects[0],
            {
                "kind": "choice_resolved",
                "choice_id": "gender_identity",
                "option_id": "value:Female",
            },
        )
        self.assertEqual(
            default.events[0]["text"],
            "You reflected on your identity.",
        )

        custom_offer = _offer_gender(current_gender="Demigirl")
        custom_choice = custom_offer.save.session.pending_choice
        self.assertEqual(custom_choice["default_value"], "Demigirl")
        self.assertEqual(
            custom_choice["options"][-1],
            {
                "option_id": "value:Demigirl",
                "label": "Demigirl",
                "value": "Demigirl",
            },
        )
        custom = _dispatch_choice(
            custom_offer.save,
            "gender_identity",
            "value:Demigirl",
        )
        self.assertTrue(custom.ok)
        self.assertEqual(
            custom.save.world["actors"]["player"]["gender"],
            "Demigirl",
        )
        self.assertEqual(
            custom.effects[0]["option_id"],
            "value:Demigirl",
        )

    def test_sexuality_selected_and_null_default_paths(self) -> None:
        selected_offer = _offer_sexuality()
        selected = _dispatch_choice(
            selected_offer.save,
            "sexuality",
            "value:Bisexual",
        )
        self.assertTrue(selected.ok)
        self.assertEqual(
            selected.save.world["actors"]["player"]["sexuality"],
            "Bisexual",
        )
        self.assertEqual(selected.events[0]["text"], "You identify as Bisexual.")
        self.assertEqual(
            selected.effects[0]["option_id"],
            "value:Bisexual",
        )

        null_offer = _offer_sexuality()
        null_result = _dispatch_choice(
            null_offer.save,
            "sexuality",
            None,
        )
        self.assertTrue(null_result.ok)
        self.assertIsNone(
            null_result.save.world["actors"]["player"]["sexuality"]
        )
        self.assertEqual(
            null_result.effects[0]["option_id"],
            None,
        )
        self.assertEqual(
            null_result.events[0]["text"],
            "You are still figuring things out.",
        )

    def test_sexuality_null_retains_existing_value_with_truthful_copy(
        self,
    ) -> None:
        offered_data = _offer_sexuality().save.to_dict()
        offered_data["world"]["actors"]["player"]["sexuality"] = "Bisexual"
        offered = SaveEnvelope.from_dict(offered_data)

        retained = _dispatch_choice(
            offered,
            "sexuality",
            None,
        )

        self.assertTrue(retained.ok)
        self.assertEqual(
            retained.save.world["actors"]["player"]["sexuality"],
            "Bisexual",
        )
        self.assertEqual(
            retained.effects[0],
            {
                "kind": "choice_resolved",
                "choice_id": "sexuality",
                "option_id": None,
            },
        )
        self.assertEqual(
            retained.events[0]["text"],
            "You still identify as Bisexual.",
        )


class MeetingAndActionChoiceTests(unittest.TestCase):
    def test_meeting_introduce_is_replayable_and_uses_saved_sources(self) -> None:
        offered = _offer_meeting()
        self.assertTrue(offered.ok)
        before = dumps_save_envelope(offered.save)
        before_rng = offered.save.rng
        global_state = random.getstate()

        first = _dispatch_choice(
            offered.save,
            "meeting_npc",
            "value:introduce",
        )
        second = _dispatch_choice(
            offered.save,
            "meeting_npc",
            "value:introduce",
        )

        self.assertTrue(first.ok)
        self.assertEqual(
            dumps_save_envelope(first.save),
            dumps_save_envelope(second.save),
        )
        self.assertEqual(dumps_save_envelope(offered.save), before)
        self.assertEqual(random.getstate(), global_state)
        self.assertNotEqual(first.save.rng, before_rng)
        self.assertEqual(first.save.ids.next_value, 2)
        self.assertIn("trace_npc_00000001", first.save.world["actors"])
        self.assertEqual(
            first.effects[:2],
            (
                {
                    "kind": "choice_resolved",
                    "choice_id": "meeting_npc",
                    "option_id": "value:introduce",
                },
                {
                    "kind": "person_met",
                    "actor_id": "trace_npc_00000001",
                    "name": "Liam Silva",
                },
            ),
        )
        self.assertEqual(
            first.events,
            (
                {
                    "text": "You introduced yourself to Liam Silva.",
                    "year": 3,
                    "month": 8,
                    "event_id": "meeting_npc_introduce",
                    "tags": ["social", "choice"],
                },
            ),
        )
        self.assertEqual(
            first.save.rng.to_dict(),
            {
                "algorithm": "pcg32-v1",
                "state": "09c5a142df053ee2",
                "increment": "000000000000006d",
            },
        )
        social_links = [
            link
            for link in first.save.world["links"]
            if {
                link["source_id"],
                link["target_id"],
            }
            == {"player", "trace_npc_00000001"}
            and link["type"] == "social"
        ]
        self.assertEqual(len(social_links), 2)
        self.assertTrue(
            all(
                link["metadata"]["closeness"] == 15
                and link["metadata"]["status"] == "active"
                for link in social_links
            )
        )

    def test_meeting_keep_to_self_consumes_no_rng_or_id(self) -> None:
        offered = _offer_meeting()
        global_state = random.getstate()
        kept = _dispatch_choice(
            offered.save,
            "meeting_npc",
            "value:keep_to_self",
        )
        replay = _dispatch_choice(
            offered.save,
            "meeting_npc",
            "value:keep_to_self",
        )

        self.assertTrue(kept.ok)
        self.assertEqual(kept.save.rng, offered.save.rng)
        self.assertEqual(kept.save.ids, offered.save.ids)
        self.assertEqual(
            dumps_save_envelope(kept.save),
            dumps_save_envelope(replay.save),
        )
        self.assertEqual(random.getstate(), global_state)
        self.assertEqual(
            kept.events[0]["text"],
            "You decided to keep to yourself.",
        )
        self.assertEqual(
            len(kept.save.world["actors"]),
            len(offered.save.world["actors"]),
        )

    def test_personal_and_social_pickers_queue_canonical_actions(self) -> None:
        rest = _dispatch_choice(
            _rest_picker_save(),
            "select_rest_subtype",
            "subtype:music",
        )
        self.assertTrue(rest.ok)
        self.assertEqual(
            rest.effects,
            (
                {
                    "kind": "choice_resolved",
                    "choice_id": "select_rest_subtype",
                    "option_id": "subtype:music",
                },
                {
                    "kind": "action_queued",
                    "action_id": "trace_action_00000001",
                },
            ),
        )
        self.assertEqual(
            rest.save.session.active_actions,
            [
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
            ],
        )

        social = _dispatch_choice(
            _hang_out_picker_save(),
            "select_hang_out_target",
            "actor:friend",
        )
        self.assertTrue(social.ok)
        self.assertEqual(
            social.save.session.active_actions[0],
            {
                "action_id": "trace_action_00000001",
                "action_type": "spend_time",
                "target_actor_id": "friend",
                "label": "Spend time with Charles Babbage",
                "time_cost": 4,
            },
        )

    def test_picker_cancel_clears_choice_without_consuming_sources(self) -> None:
        save = _rest_picker_save()
        before_rng = save.rng
        before_ids = save.ids
        cancelled = _dispatch_choice(
            save,
            "select_rest_subtype",
            None,
        )

        self.assertTrue(cancelled.ok)
        self.assertEqual(cancelled.save.session.active_actions, [])
        self.assertIsNone(cancelled.save.session.pending_choice)
        self.assertEqual(cancelled.save.rng, before_rng)
        self.assertEqual(cancelled.save.ids, before_ids)
        self.assertEqual(
            cancelled.effects,
            (
                {
                    "kind": "choice_resolved",
                    "choice_id": "select_rest_subtype",
                    "option_id": None,
                },
            ),
        )

    def test_already_queued_hangout_closes_as_source_free_noop(self) -> None:
        save_data = _hang_out_picker_save().to_dict()
        save_data["ids"]["next_value"] = 2
        save_data["session"]["active_actions"] = [
            {
                "action_id": "trace_action_00000001",
                "action_type": "spend_time",
                "target_actor_id": "friend",
                "label": "Spend time with Charles Babbage",
                "time_cost": 4,
            }
        ]
        save_data["session"]["pending_choice"]["options"][0]["label"] = (
            "Charles Babbage · Friend (queued)"
        )
        save = SaveEnvelope.from_dict(save_data)
        before_rng = save.rng
        before_ids = save.ids
        before_actions = deepcopy(save.session.active_actions)

        resolved = _dispatch_choice(
            save,
            "select_hang_out_target",
            "actor:friend",
        )

        self.assertTrue(resolved.ok)
        self.assertIsNone(resolved.save.session.pending_choice)
        self.assertEqual(resolved.save.session.active_actions, before_actions)
        self.assertEqual(resolved.save.rng, before_rng)
        self.assertEqual(resolved.save.ids, before_ids)
        self.assertEqual(
            resolved.effects,
            (
                {
                    "kind": "choice_resolved",
                    "choice_id": "select_hang_out_target",
                    "option_id": "actor:friend",
                },
            ),
        )


class ChoiceAtomicityAndResumeTests(unittest.TestCase):
    def assert_atomic_failure(
        self,
        save,
        result,
        *,
        code: str,
        reason: str,
    ) -> None:
        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, code)
        self.assertEqual(result.error.details["reason"], reason)
        self.assertEqual(
            dumps_save_envelope(result.save),
            dumps_save_envelope(save),
        )

    def test_mismatch_and_no_pending_choice_are_atomic(self) -> None:
        offered = _offer_gender()
        mismatched = _dispatch_choice(
            offered.save,
            "sexuality",
            "value:Bisexual",
        )
        self.assert_atomic_failure(
            offered.save,
            mismatched,
            code="choice_not_available",
            reason="choice_id_mismatch",
        )

        no_choice_save = build_save_envelope(
            build_test_world(),
            GameSession(focused_actor_id="player", last_logged_year=3),
            SeededRandomSource(1),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        no_choice = _dispatch_choice(
            no_choice_save,
            "gender_identity",
            "value:Female",
        )
        self.assert_atomic_failure(
            no_choice_save,
            no_choice,
            code="choice_not_available",
            reason="no_pending_choice",
        )

    def test_meeting_null_and_identifier_exhaustion_are_atomic(self) -> None:
        offered = _offer_meeting()
        null_meeting = _dispatch_choice(
            offered.save,
            "meeting_npc",
            None,
        )
        self.assert_atomic_failure(
            offered.save,
            null_meeting,
            code="choice_not_available",
            reason="selection_required",
        )

        exhausted_dict = deepcopy(offered.save.to_dict())
        exhausted_dict["ids"]["next_value"] = MAX_SAFE_INTEGER
        exhausted = SaveEnvelope.from_dict(exhausted_dict)
        before = dumps_save_envelope(exhausted)
        global_state = random.getstate()
        rejected = _dispatch_choice(
            exhausted,
            "meeting_npc",
            "value:introduce",
        )
        self.assertFalse(rejected.ok)
        self.assertEqual(rejected.error.code, "identifier_limit")
        self.assertEqual(dumps_save_envelope(rejected.save), before)
        self.assertEqual(dumps_save_envelope(exhausted), before)
        self.assertEqual(random.getstate(), global_state)

    def test_picker_invalid_option_and_identifier_exhaustion_are_atomic(
        self,
    ) -> None:
        picker = _rest_picker_save()
        unavailable = _dispatch_choice(
            picker,
            "select_rest_subtype",
            "subtype:missing",
        )
        self.assert_atomic_failure(
            picker,
            unavailable,
            code="choice_not_available",
            reason="option_not_available",
        )

        exhausted_data = _rest_picker_save().to_dict()
        exhausted_data["ids"]["next_value"] = MAX_SAFE_INTEGER
        exhausted = SaveEnvelope.from_dict(exhausted_data)
        before = dumps_save_envelope(exhausted)
        result = _dispatch_choice(
            exhausted,
            "select_rest_subtype",
            "subtype:music",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, "identifier_limit")
        self.assertEqual(dumps_save_envelope(result.save), before)
        self.assertEqual(dumps_save_envelope(exhausted), before)

    def test_resolution_resumes_skip_until_the_next_choice(self) -> None:
        offered = _offer_gender(months=3)
        self.assertEqual(offered.save.session.remaining_skip_months, 2)
        resolved = _dispatch_choice(
            offered.save,
            "gender_identity",
            "value:Non-binary",
        )

        self.assertTrue(resolved.ok)
        self.assertEqual(resolved.revision, offered.revision + 1)
        self.assertEqual(
            resolved.interruption,
            {
                "kind": "choice_required",
                "choice_id": "sexuality",
                "remaining_months": 1,
            },
        )
        self.assertEqual(
            resolved.save.session.pending_choice["choice_id"],
            "sexuality",
        )
        self.assertEqual(resolved.save.session.remaining_skip_months, 1)
        self.assertEqual(resolved.effects[1]["kind"], "time_advanced")
        self.assertEqual(resolved.effects[1]["months_requested"], 2)
        self.assertEqual(resolved.effects[1]["months_advanced"], 1)
        self.assertEqual(
            sum(
                entry.get("kind") == "skip_marker"
                for entry in resolved.save.session.event_log
            ),
            1,
        )

    def test_resolution_resumes_skip_until_death(self) -> None:
        world = build_test_world()
        world.actors["player"].birth_year = -120
        pending = _offer_gender().save.session.pending_choice
        save = build_save_envelope(
            world,
            GameSession(
                focused_actor_id="player",
                pending_choice=pending,
                remaining_skip_months=3,
                last_logged_year=3,
                gender_choice_offered=True,
            ),
            SeededRandomSource(11),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        resolved = _dispatch_choice(
            save,
            "gender_identity",
            "value:Female",
        )

        self.assertTrue(resolved.ok)
        self.assertEqual(
            resolved.interruption["kind"],
            "continuation_required",
        )
        self.assertEqual(
            resolved.save.world["actors"]["player"]["structural_status"],
            "dead",
        )
        self.assertEqual(resolved.save.session.remaining_skip_months, 0)
        self.assertIsNone(resolved.save.session.pending_choice)
        self.assertEqual(resolved.effects[1]["kind"], "time_advanced")
        self.assertEqual(resolved.effects[1]["months_advanced"], 1)


class ContinuationTests(unittest.TestCase):
    def _continue(self, save, actor_id: str = "friend"):
        return dispatch_command(
            save,
            command(
                "continue-life",
                CommandType.CONTINUE_AS,
                {"actor_id": actor_id},
                save.revision,
            ),
        )

    def assert_common_handoff(self, before, result) -> None:
        self.assertTrue(result.ok)
        self.assertEqual(result.revision, before.revision + 1)
        self.assertEqual(result.save.session.focused_actor_id, "friend")
        self.assertEqual(result.save.world["focused_actor_id"], "friend")
        self.assertEqual(result.save.session.active_actions, [])
        self.assertIsNone(result.save.session.pending_choice)
        self.assertEqual(result.save.session.remaining_skip_months, 0)
        self.assertEqual(
            result.save.session.meeting_event_last_total_months,
            0,
        )
        self.assertEqual(result.save.session.last_logged_year, 3)
        self.assertEqual(
            result.save.session.event_log[-1],
            {
                "kind": "life_separator",
                "text": "New Life: Charles Babbage",
                "year": None,
                "month": None,
                "record_type": None,
            },
        )
        self.assertEqual(
            result.effects,
            (
                {
                    "kind": "continued_as",
                    "previous_actor_id": "player",
                    "focused_actor_id": "friend",
                },
            ),
        )
        self.assertEqual(result.events, ())
        self.assertIsNone(result.interruption)
        self.assertEqual(result.save.ids, before.ids)
        continuation_records = [
            record
            for record in result.save.world["records"]
            if record["record_type"] == "continuation"
        ]
        self.assertEqual(len(continuation_records), 1)
        self.assertEqual(
            continuation_records[0],
            {
                "record_type": "continuation",
                "scope": "actor",
                "text": (
                    "The story continued as Charles Babbage "
                    "after Ada Lovelace died."
                ),
                "year": 3,
                "month": 7,
                "actor_ids": ["player", "friend"],
                "tags": ["continuation", "structural_transition"],
                "metadata": {
                    "from_actor_id": "player",
                    "successor_actor_id": "friend",
                    "entry_method": "World.handoff_focus_to_continuation",
                },
            },
        )

    def test_minor_handoff_resets_exact_state_and_only_draws_new_ages(
        self,
    ) -> None:
        seed = "minor-continuation"
        save = _continuation_save(adult=False, seed=seed)
        expected = SeededRandomSource(seed)
        expected_gender_age = expected.randint(12, 15)
        expected_sexuality_age = expected.randint(14, 17)
        global_state = random.getstate()
        result = self._continue(save)

        self.assert_common_handoff(save, result)
        self.assertEqual(random.getstate(), global_state)
        self.assertFalse(result.save.session.gender_choice_offered)
        self.assertFalse(result.save.session.sexuality_choice_offered)
        self.assertFalse(
            result.save.session.identity_popup_suppressed_for_resumed_adult
        )
        self.assertEqual(
            result.save.session.gender_choice_age,
            expected_gender_age,
        )
        self.assertEqual(
            result.save.session.sexuality_choice_age,
            expected_sexuality_age,
        )
        self.assertEqual(result.save.rng, expected.snapshot())
        self.assertIsNone(
            result.save.world["actors"]["friend"]["sexuality"]
        )

    def test_adult_handoff_auto_resolves_identity_and_is_replayable(
        self,
    ) -> None:
        save = _continuation_save(adult=True, seed="adult-continuation")
        before = dumps_save_envelope(save)
        global_state = random.getstate()
        first = self._continue(save)
        second = self._continue(save)

        self.assert_common_handoff(save, first)
        self.assertEqual(
            dumps_save_envelope(first.save),
            dumps_save_envelope(second.save),
        )
        self.assertEqual(dumps_save_envelope(save), before)
        self.assertEqual(random.getstate(), global_state)
        self.assertTrue(first.save.session.gender_choice_offered)
        self.assertTrue(first.save.session.sexuality_choice_offered)
        self.assertTrue(
            first.save.session.identity_popup_suppressed_for_resumed_adult
        )
        self.assertEqual(first.save.session.gender_choice_age, 13)
        self.assertEqual(first.save.session.sexuality_choice_age, 14)
        self.assertEqual(
            first.save.world["actors"]["friend"]["gender"],
            "Male",
        )
        self.assertEqual(
            first.save.world["actors"]["friend"]["sexuality"],
            "Queer",
        )
        self.assertEqual(
            first.save.rng.to_dict(),
            {
                "algorithm": "pcg32-v1",
                "state": "6a78433dbc17ad67",
                "increment": "000000000000006d",
            },
        )
        self.assertEqual(first.save.ids, save.ids)

    def test_invalid_candidate_no_candidates_and_alive_focus_are_atomic(
        self,
    ) -> None:
        dead = _continuation_save(adult=False)
        invalid = self._continue(dead, "missing")
        self.assertFalse(invalid.ok)
        self.assertEqual(invalid.error.code, "continuation_not_available")
        self.assertEqual(
            invalid.error.details["reason"],
            "candidate_unavailable",
        )
        self.assertEqual(
            dumps_save_envelope(invalid.save),
            dumps_save_envelope(dead),
        )

        no_candidates = _continuation_save(
            adult=False,
            include_candidate=False,
        )
        none_available = self._continue(no_candidates)
        self.assertFalse(none_available.ok)
        self.assertEqual(
            none_available.error.details["reason"],
            "no_candidates",
        )
        self.assertEqual(
            dumps_save_envelope(none_available.save),
            dumps_save_envelope(no_candidates),
        )

        alive = build_save_envelope(
            build_test_world(),
            GameSession(focused_actor_id="player", last_logged_year=3),
            SeededRandomSource(1),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        focus_alive = self._continue(alive)
        self.assertFalse(focus_alive.ok)
        self.assertEqual(
            focus_alive.error.details["reason"],
            "focus_alive",
        )
        self.assertEqual(
            dumps_save_envelope(focus_alive.save),
            dumps_save_envelope(alive),
        )


class SerializedChoiceContinuationTests(unittest.TestCase):
    def assert_serialized_matches_native(self, save, request) -> None:
        native = dispatch_command(save, request)
        serialized = dispatch_serialized_command(
            dumps_save_envelope(save),
            dumps_game_command(request),
        )
        loaded = loads_command_result(serialized)
        self.assertEqual(
            dumps_command_result(loaded),
            dumps_command_result(native),
        )

    def test_choice_and_continuation_cross_the_json_boundary_exactly(
        self,
    ) -> None:
        offered = _offer_gender()
        choice_request = command(
            "serialized-choice",
            CommandType.RESOLVE_CHOICE,
            {
                "choice_id": "gender_identity",
                "option_id": "value:Agender",
            },
            offered.save.revision,
        )
        self.assert_serialized_matches_native(
            offered.save,
            choice_request,
        )

        dead = _continuation_save(adult=True)
        continuation_request = command(
            "serialized-continuation",
            CommandType.CONTINUE_AS,
            {"actor_id": "friend"},
            dead.revision,
        )
        self.assert_serialized_matches_native(
            dead,
            continuation_request,
        )


if __name__ == "__main__":
    unittest.main()
