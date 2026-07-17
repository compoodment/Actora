"""Dispatcher coverage for deterministic creation and time advancement."""

from __future__ import annotations

import hashlib
import json
import random
import unittest
from copy import deepcopy
from pathlib import Path

from actora_core import (
    CommandType,
    ContractValidationError,
    DeterministicIdSource,
    GameSession,
    SeededRandomSource,
    dispatch_command,
    dispatch_serialized_command,
    dumps_command_result,
    dumps_game_command,
    loads_command_result,
)
from actora_core.serialization import (
    build_save_envelope,
    dumps_save_envelope,
    loads_save_envelope,
)
from actora_core.history import append_turn_event_log
from actora_core.json_types import MAX_SAFE_INTEGER, MIN_SAFE_INTEGER
from tests.test_actora_core import build_test_world
from tests.test_actora_dispatcher import (
    build_creation_character,
    build_dispatch_save,
    command,
)

GOLDEN_PATH = (
    Path(__file__).resolve().parent
    / "golden"
    / "dispatcher_create_advance_v1.json"
)


def _create(
    *,
    command_id: str = "create-request",
    seed: str = "0123456789abcdef",
):
    return dispatch_command(
        None,
        command(
            command_id,
            CommandType.CREATE_GAME,
            {
                "character": build_creation_character(),
                "seed": seed,
            },
            0,
        ),
    )


def _save_snapshot(result) -> dict:
    save = result.save
    if save is None:
        return {
            "save_sha256": None,
            "rng": None,
            "ids": None,
            "date": None,
            "actor_ids": [],
            "focused_actor_id": None,
            "cooldown": {},
        }
    serialized_save = dumps_save_envelope(save)
    return {
        "save_sha256": hashlib.sha256(
            serialized_save.encode("utf-8")
        ).hexdigest(),
        "rng": save.rng.to_dict(),
        "ids": save.ids.to_dict(),
        "date": {
            "year": save.world["current_year"],
            "month": save.world["current_month"],
        },
        "actor_ids": sorted(save.world["actors"]),
        "focused_actor_id": save.session.focused_actor_id,
        "cooldown": save.world["recent_event_ids_by_actor"],
    }


def _result_snapshot(result) -> dict:
    return {
        "command_id": result.command_id,
        "command_type": result.command_type.value,
        "ok": result.ok,
        "revision": result.revision,
        "error_code": (
            result.error.code if result.error is not None else None
        ),
        "events": list(result.events),
        "effects": list(result.effects),
        "interruption": result.interruption,
        **_save_snapshot(result),
    }


def _build_family_birth_save(*, next_id: int = 1):
    world = build_test_world()
    traits = ["Curious", "Social", "Disciplined", "Resilient"]
    for actor_id, sex, birth_year in (
        ("mother", "Female", -24),
        ("father", "Male", -26),
    ):
        actor = world.create_human_actor(
            actor_id=actor_id,
            species="Human",
            first_name=actor_id.title(),
            last_name="Family",
            sex=sex,
            gender=sex,
            birth_year=birth_year,
            birth_month=1,
            current_place_id="test_city",
            residence_place_id="test_city",
            jurisdiction_place_id="test_country",
        )
        actor.traits = list(traits)
    world.add_link_pair(
        "mother",
        "father",
        "association",
        "coparent",
        "association",
        "coparent",
    )
    return build_save_envelope(
        world,
        GameSession(
            focused_actor_id="player",
            last_logged_year=3,
            gender_choice_offered=True,
            sexuality_choice_offered=True,
            meeting_event_last_total_months=9999,
        ),
        SeededRandomSource(91),
        DeterministicIdSource("trace", next_value=next_id),
        engine_version="headless-test",
    )


class CreateGameDispatcherTests(unittest.TestCase):
    def test_create_is_replayable_request_owned_and_global_random_free(
        self,
    ) -> None:
        global_state = random.getstate()
        first = _create(command_id="browser-request-a")
        second = _create(command_id="browser-request-b")

        self.assertTrue(first.ok)
        self.assertTrue(second.ok)
        self.assertEqual(
            dumps_save_envelope(first.save),
            dumps_save_envelope(second.save),
        )
        self.assertEqual(random.getstate(), global_state)
        self.assertEqual(first.revision, 1)
        self.assertEqual(first.save.ids.next_value, 4)
        self.assertEqual(
            first.effects,
            (
                {
                    "kind": "game_created",
                    "focused_actor_id": (
                        "actora_startup_player_00000003"
                    ),
                },
            ),
        )

        different_seed = _create(seed="0123456789abcdee")
        self.assertNotEqual(
            dumps_save_envelope(first.save),
            dumps_save_envelope(different_seed.save),
        )

    def test_create_serialized_boundary_and_existing_save_rejection(
        self,
    ) -> None:
        request = command(
            "serialized-create",
            CommandType.CREATE_GAME,
            {
                "character": build_creation_character(),
                "seed": "0123456789abcdef",
            },
            0,
        )
        serialized_result = dispatch_serialized_command(
            None,
            dumps_game_command(request),
        )
        result = loads_command_result(serialized_result)
        self.assertTrue(result.ok)
        self.assertEqual(result.revision, 1)

        before = dumps_save_envelope(result.save)
        duplicate = dispatch_command(
            result.save,
            command(
                "duplicate-create",
                CommandType.CREATE_GAME,
                {
                    "character": build_creation_character(),
                    "seed": "0123456789abcdef",
                },
                1,
            ),
        )
        self.assertFalse(duplicate.ok)
        self.assertEqual(duplicate.error.code, "game_already_exists")
        self.assertEqual(dumps_save_envelope(duplicate.save), before)

        missing_save = dispatch_command(
            None,
            command(
                "advance-without-save",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        self.assertFalse(missing_save.ok)
        self.assertEqual(missing_save.error.code, "save_required")
        self.assertIsNone(missing_save.save)

        global_state = random.getstate()
        revision_conflict = dispatch_command(
            None,
            command(
                "create-wrong-revision",
                CommandType.CREATE_GAME,
                {
                    "character": build_creation_character(),
                    "seed": "0123456789abcdef",
                },
                1,
            ),
        )
        self.assertFalse(revision_conflict.ok)
        self.assertEqual(
            revision_conflict.error.code,
            "revision_conflict",
        )
        self.assertIsNone(revision_conflict.save)
        self.assertEqual(random.getstate(), global_state)


class AdvanceTimeDispatcherTests(unittest.TestCase):
    def test_one_month_orders_monthly_social_then_personal_events(
        self,
    ) -> None:
        social = dispatch_command(
            build_dispatch_save(),
            command(
                "queue-social",
                CommandType.QUEUE_ACTION,
                {
                    "action": {
                        "action_type": "spend_time",
                        "target_actor_id": "friend",
                    }
                },
                0,
            ),
        )
        personal = dispatch_command(
            social.save,
            command(
                "queue-personal",
                CommandType.QUEUE_ACTION,
                {
                    "action": {
                        "action_type": "personal",
                        "subtype_id": "nap",
                    }
                },
                1,
            ),
        )
        advanced = dispatch_command(
            personal.save,
            command(
                "advance-actions",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                2,
            ),
        )

        self.assertTrue(advanced.ok)
        self.assertEqual(advanced.revision, 3)
        self.assertEqual(
            [event.get("event_id") for event in advanced.events],
            ["infant_explore_blanket", "spend_time", "nap"],
        )
        self.assertEqual(
            advanced.effects,
            (
                {
                    "kind": "time_advanced",
                    "months_requested": 1,
                    "months_advanced": 1,
                },
                {
                    "kind": "action_resolved",
                    "action_id": "trace_action_00000001",
                },
                {
                    "kind": "action_resolved",
                    "action_id": "trace_action_00000002",
                },
            ),
        )
        self.assertEqual(advanced.save.session.active_actions, [])
        self.assertEqual(advanced.save.ids.next_value, 3)

    def test_one_month_resolves_queued_action_once(self) -> None:
        base = build_dispatch_save()
        base.world["actors"]["player"]["stats"]["happiness"] = 50
        base.world["actors"]["player"]["stats"]["stress"] = 0
        queued = dispatch_command(
            base,
            command(
                "queue-nap",
                CommandType.QUEUE_ACTION,
                {
                    "action": {
                        "action_type": "personal",
                        "subtype_id": "nap",
                    }
                },
                0,
            ),
        )
        advanced = dispatch_command(
            queued.save,
            command(
                "advance-with-nap",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                1,
            ),
        )
        control = dispatch_command(
            base,
            command(
                "advance-control",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )

        self.assertTrue(advanced.ok)
        self.assertEqual(advanced.revision, 2)
        self.assertEqual(advanced.save.session.active_actions, [])
        self.assertIn(
            {
                "kind": "action_resolved",
                "action_id": "trace_action_00000001",
            },
            advanced.effects,
        )
        self.assertTrue(
            any(
                event.get("event_id") == "nap"
                for event in advanced.events
            )
        )
        advanced_stats = advanced.save.world["actors"]["player"]["stats"]
        control_stats = control.save.world["actors"]["player"]["stats"]
        self.assertEqual(
            advanced_stats["happiness"],
            control_stats["happiness"] + 2,
        )
        self.assertEqual(
            advanced_stats["stress"],
            control_stats["stress"] - 3,
        )

    def test_reload_replay_matches_exactly(self) -> None:
        created = _create()
        reloaded = loads_save_envelope(
            dumps_save_envelope(created.save)
        )
        first = dispatch_command(
            created.save,
            command(
                "advance-a",
                CommandType.ADVANCE_TIME,
                {"months": 3},
                1,
            ),
        )
        second = dispatch_command(
            reloaded,
            command(
                "advance-b",
                CommandType.ADVANCE_TIME,
                {"months": 3},
                1,
            ),
        )
        self.assertEqual(
            dumps_save_envelope(first.save),
            dumps_save_envelope(second.save),
        )
        self.assertEqual(first.events, second.events)
        self.assertEqual(first.effects, second.effects)
        self.assertEqual(first.interruption, second.interruption)

    def test_identity_choice_interrupts_and_blocks_until_resolved(
        self,
    ) -> None:
        save = build_dispatch_save(
            session=GameSession(
                focused_actor_id="player",
                last_logged_year=3,
                gender_choice_age=0,
                sexuality_choice_age=0,
            )
        )
        result = dispatch_command(
            save,
            command(
                "identity-interrupt",
                CommandType.ADVANCE_TIME,
                {"months": 3},
                0,
            ),
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.effects[0]["months_advanced"], 1)
        self.assertEqual(
            result.interruption,
            {
                "kind": "choice_required",
                "choice_id": "gender_identity",
                "remaining_months": 2,
            },
        )
        choice = result.save.session.pending_choice
        self.assertEqual(choice["choice_id"], "gender_identity")
        self.assertEqual(choice["default_value"], "Female")
        self.assertEqual(result.save.session.remaining_skip_months, 2)

        before = dumps_save_envelope(result.save)
        blocked = dispatch_command(
            result.save,
            command(
                "blocked-by-choice",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                1,
            ),
        )
        self.assertFalse(blocked.ok)
        self.assertEqual(blocked.error.code, "choice_pending")
        self.assertEqual(dumps_save_envelope(blocked.save), before)

    def test_identity_choice_precedes_meeting_without_consuming_it(
        self,
    ) -> None:
        world = build_test_world()
        world.actors["player"].birth_year = -3
        identity_save = build_save_envelope(
            world,
            GameSession(
                focused_actor_id="player",
                last_logged_year=3,
                gender_choice_age=0,
                sexuality_choice_age=0,
            ),
            SeededRandomSource(3),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        sexuality_save = build_save_envelope(
            world,
            GameSession(
                focused_actor_id="player",
                last_logged_year=3,
                gender_choice_offered=True,
                gender_choice_age=0,
                sexuality_choice_age=0,
            ),
            SeededRandomSource(3),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        meeting_save = build_save_envelope(
            world,
            GameSession(
                focused_actor_id="player",
                last_logged_year=3,
                gender_choice_offered=True,
                sexuality_choice_offered=True,
            ),
            SeededRandomSource(3),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )

        identity_result = dispatch_command(
            identity_save,
            command(
                "identity-first",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        meeting_result = dispatch_command(
            meeting_save,
            command(
                "meeting-control",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        sexuality_result = dispatch_command(
            sexuality_save,
            command(
                "sexuality-second",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )

        self.assertEqual(
            identity_result.save.session.pending_choice["choice_id"],
            "gender_identity",
        )
        self.assertEqual(
            identity_result.save.session.meeting_event_last_total_months,
            0,
        )
        self.assertEqual(
            sexuality_result.save.session.pending_choice["choice_id"],
            "sexuality",
        )
        self.assertEqual(
            sexuality_result.save.session.meeting_event_last_total_months,
            0,
        )
        self.assertEqual(
            meeting_result.save.session.pending_choice["choice_id"],
            "meeting_npc",
        )
        self.assertEqual(
            meeting_result.save.session.meeting_event_last_total_months,
            44,
        )
        self.assertEqual(
            identity_result.save.rng,
            sexuality_result.save.rng,
        )
        self.assertNotEqual(
            identity_result.save.rng,
            meeting_result.save.rng,
        )

    def test_custom_current_gender_remains_a_valid_headless_default(
        self,
    ) -> None:
        world = build_test_world()
        world.actors["player"].gender = "Demigirl"
        save = build_save_envelope(
            world,
            GameSession(
                focused_actor_id="player",
                last_logged_year=3,
                gender_choice_age=0,
            ),
            SeededRandomSource(7),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        result = dispatch_command(
            save,
            command(
                "custom-gender-choice",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )

        self.assertTrue(result.ok)
        choice = result.save.session.pending_choice
        values = [option["value"] for option in choice["options"]]
        option_ids = [
            option["option_id"] for option in choice["options"]
        ]
        self.assertEqual(choice["default_value"], "Demigirl")
        self.assertIn("Demigirl", values)
        self.assertIn(choice["selected_option_id"], option_ids)

    def test_meeting_choice_uses_semantic_ids_and_cooldown(self) -> None:
        world = build_test_world()
        world.actors["player"].birth_year = -3
        session = GameSession(
            focused_actor_id="player",
            last_logged_year=3,
            gender_choice_offered=True,
            sexuality_choice_offered=True,
        )
        save = build_save_envelope(
            world,
            session,
            SeededRandomSource(3),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        result = dispatch_command(
            save,
            command(
                "meeting-interrupt",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        self.assertTrue(result.ok)
        choice = result.save.session.pending_choice
        self.assertEqual(choice["choice_id"], "meeting_npc")
        self.assertEqual(
            [
                (option["option_id"], option["value"])
                for option in choice["options"]
            ],
            [
                ("value:introduce", "introduce"),
                ("value:keep_to_self", "keep_to_self"),
            ],
        )
        self.assertNotIn("default_value", choice)
        self.assertEqual(
            result.save.session.meeting_event_last_total_months,
            44,
        )

    def test_guaranteed_death_stops_early_and_requests_continuation(
        self,
    ) -> None:
        world = build_test_world()
        world.actors["player"].birth_year = -120
        save = build_save_envelope(
            world,
            GameSession(
                focused_actor_id="player",
                last_logged_year=3,
            ),
            SeededRandomSource(11),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        result = dispatch_command(
            save,
            command(
                "death-interrupt",
                CommandType.ADVANCE_TIME,
                {"months": 5},
                0,
            ),
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.effects[0]["months_advanced"], 1)
        self.assertEqual(
            result.interruption["kind"],
            "continuation_required",
        )
        self.assertTrue(
            result.interruption["continuity_state"]["is_dead"]
        )
        self.assertEqual(result.save.session.remaining_skip_months, 0)
        self.assertEqual(
            result.save.world["actors"]["player"]["structural_status"],
            "dead",
        )

    def test_dead_focus_and_revision_limit_are_atomic(self) -> None:
        world = build_test_world()
        player = world.actors["player"]
        player.structural_status = "dead"
        player.death_year = 3
        player.death_month = 7
        player.death_reason = "test"
        dead_save = build_save_envelope(
            world,
            GameSession(focused_actor_id="player", last_logged_year=3),
            SeededRandomSource(11),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        dead_before = dumps_save_envelope(dead_save)
        dead_result = dispatch_command(
            dead_save,
            command(
                "advance-dead-focus",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        self.assertFalse(dead_result.ok)
        self.assertEqual(dead_result.error.code, "focused_actor_dead")
        self.assertEqual(
            dumps_save_envelope(dead_result.save),
            dead_before,
        )
        self.assertEqual(dumps_save_envelope(dead_save), dead_before)

        limited_save = build_dispatch_save(
            revision=MAX_SAFE_INTEGER,
        )
        limited_before = dumps_save_envelope(limited_save)
        limited_result = dispatch_command(
            limited_save,
            command(
                "advance-revision-limit",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                MAX_SAFE_INTEGER,
            ),
        )
        self.assertFalse(limited_result.ok)
        self.assertEqual(limited_result.error.code, "revision_conflict")
        self.assertEqual(
            limited_result.error.details,
            {"reason": "revision_limit"},
        )
        self.assertEqual(
            dumps_save_envelope(limited_result.save),
            limited_before,
        )
        self.assertEqual(
            dumps_save_envelope(limited_save),
            limited_before,
        )

    def test_year_limit_is_atomic_and_large_history_gaps_are_bounded(
        self,
    ) -> None:
        world = build_test_world()
        world.current_year = MAX_SAFE_INTEGER
        world.current_month = 1
        save = build_save_envelope(
            world,
            GameSession(focused_actor_id="player", last_logged_year=3),
            SeededRandomSource(11),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        before = dumps_save_envelope(save)
        result = dispatch_command(
            save,
            command(
                "advance-year-limit",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.error.code, "time_limit")
        self.assertEqual(
            result.error.details,
            {"reason": "timeline_limit"},
        )
        self.assertEqual(dumps_save_envelope(result.save), before)
        self.assertEqual(dumps_save_envelope(save), before)

        event_log = []
        last_logged_year = append_turn_event_log(
            event_log,
            3,
            "player",
            {
                "months_advanced": 1,
                "events": [
                    {
                        "event_id": "far_future",
                        "text": "A distant event.",
                        "outcome": {"stat_changes": {}},
                        "tags": [],
                        "year": MAX_SAFE_INTEGER,
                        "month": 12,
                    }
                ],
            },
            1,
            [],
        )
        self.assertEqual(last_logged_year, MAX_SAFE_INTEGER)
        self.assertEqual(
            event_log,
            [
                {
                    "kind": "year_header",
                    "text": f"Year {MAX_SAFE_INTEGER}",
                    "year": MAX_SAFE_INTEGER,
                    "month": None,
                    "record_type": None,
                },
                {
                    "kind": "event",
                    "text": "A distant event.",
                    "year": MAX_SAFE_INTEGER,
                    "month": 12,
                    "record_type": None,
                },
            ],
        )

        social_world = build_test_world()
        for link in social_world.links:
            link["metadata"]["closeness_history_months"] = (
                MAX_SAFE_INTEGER
            )
        social_save = build_save_envelope(
            social_world,
            GameSession(focused_actor_id="player", last_logged_year=3),
            SeededRandomSource(1),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        social_before = dumps_save_envelope(social_save)
        social_result = dispatch_command(
            social_save,
            command(
                "advance-social-counter-limit",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        self.assertFalse(social_result.ok)
        self.assertEqual(social_result.error.code, "state_limit")
        self.assertEqual(
            social_result.error.details,
            {"reason": "numeric_limit"},
        )
        self.assertEqual(
            dumps_save_envelope(social_result.save),
            social_before,
        )
        self.assertEqual(dumps_save_envelope(social_save), social_before)

        for money_boundary, seed in (
            (MAX_SAFE_INTEGER, 9),
            (MIN_SAFE_INTEGER, 30),
        ):
            money_world = build_test_world()
            money_world.current_year = 30
            money_world.current_month = 1
            for actor in money_world.actors.values():
                actor.birth_year = 10
            money_world.actors["player"].money = money_boundary
            money_save = build_save_envelope(
                money_world,
                GameSession(
                    focused_actor_id="player",
                    last_logged_year=30,
                    gender_choice_offered=True,
                    sexuality_choice_offered=True,
                    meeting_event_last_total_months=10000,
                ),
                SeededRandomSource(seed),
                DeterministicIdSource("trace"),
                engine_version="headless-test",
            )
            money_before = dumps_save_envelope(money_save)
            money_result = dispatch_command(
                money_save,
                command(
                    f"advance-money-limit-{seed}",
                    CommandType.ADVANCE_TIME,
                    {"months": 1},
                    0,
                ),
            )
            with self.subTest(money_boundary=money_boundary):
                self.assertFalse(money_result.ok)
                self.assertEqual(
                    money_result.error.code,
                    "state_limit",
                )
                self.assertEqual(
                    money_result.error.details,
                    {"reason": "numeric_limit"},
                )
                self.assertEqual(
                    dumps_save_envelope(money_result.save),
                    money_before,
                )
                self.assertEqual(
                    dumps_save_envelope(money_save),
                    money_before,
                )

    def test_family_birth_consumes_id_and_exhaustion_is_atomic(
        self,
    ) -> None:
        birth_result = dispatch_command(
            _build_family_birth_save(),
            command(
                "advance-family-birth",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        self.assertTrue(birth_result.ok)
        self.assertEqual(birth_result.save.ids.next_value, 2)
        self.assertIn(
            "trace_family_child_00000001",
            birth_result.save.world["actors"],
        )

        exhausted_save = _build_family_birth_save(
            next_id=MAX_SAFE_INTEGER,
        )
        exhausted_before = dumps_save_envelope(exhausted_save)
        exhausted_result = dispatch_command(
            exhausted_save,
            command(
                "advance-family-birth-exhausted",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        self.assertFalse(exhausted_result.ok)
        self.assertEqual(
            exhausted_result.error.code,
            "identifier_limit",
        )
        self.assertEqual(
            dumps_save_envelope(exhausted_result.save),
            exhausted_before,
        )
        self.assertEqual(
            dumps_save_envelope(exhausted_save),
            exhausted_before,
        )


class InterruptionContractTests(unittest.TestCase):
    def _identity_result(self):
        return dispatch_command(
            build_dispatch_save(
                session=GameSession(
                    focused_actor_id="player",
                    last_logged_year=3,
                    gender_choice_age=0,
                    sexuality_choice_age=0,
                )
            ),
            command(
                "identity-contract",
                CommandType.ADVANCE_TIME,
                {"months": 3},
                0,
            ),
        )

    def _death_result(self):
        world = build_test_world()
        world.actors["player"].birth_year = -120
        save = build_save_envelope(
            world,
            GameSession(focused_actor_id="player", last_logged_year=3),
            SeededRandomSource(11),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        return dispatch_command(
            save,
            command(
                "death-contract",
                CommandType.ADVANCE_TIME,
                {"months": 2},
                0,
            ),
        )

    def test_valid_choice_and_continuation_interruptions_roundtrip(
        self,
    ) -> None:
        for result in (self._identity_result(), self._death_result()):
            with self.subTest(kind=result.interruption["kind"]):
                serialized = dumps_command_result(result)
                self.assertEqual(
                    loads_command_result(serialized).to_dict(),
                    result.to_dict(),
                )

        blank_name_world = build_test_world()
        blank_name_player = blank_name_world.actors["player"]
        blank_name_player.first_name = ""
        blank_name_player.last_name = ""
        blank_name_player.birth_year = -120
        blank_name_save = build_save_envelope(
            blank_name_world,
            GameSession(focused_actor_id="player", last_logged_year=3),
            SeededRandomSource(11),
            DeterministicIdSource("trace"),
            engine_version="headless-test",
        )
        blank_name_result = dispatch_command(
            blank_name_save,
            command(
                "blank-name-death",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        self.assertTrue(blank_name_result.ok)
        self.assertEqual(
            blank_name_result.interruption["continuity_state"][
                "focus_actor_name"
            ],
            "",
        )
        loads_command_result(dumps_command_result(blank_name_result))

    def test_malformed_and_state_mismatched_interruptions_are_rejected(
        self,
    ) -> None:
        identity_data = self._identity_result().to_dict()
        invalid_choice_interruptions = (
            {},
            {"kind": "unknown"},
            {
                "kind": "choice_required",
                "choice_id": "gender_identity",
                "remaining_months": 2,
                "extra": True,
            },
            {
                "kind": "choice_required",
                "choice_id": 7,
                "remaining_months": 2,
            },
            {
                "kind": "choice_required",
                "choice_id": "gender_identity",
                "remaining_months": -1,
            },
            {
                "kind": "choice_required",
                "choice_id": "sexuality",
                "remaining_months": 2,
            },
            {
                "kind": "choice_required",
                "choice_id": "gender_identity",
                "remaining_months": 1,
            },
        )
        for interruption in invalid_choice_interruptions:
            malformed = deepcopy(identity_data)
            malformed["interruption"] = interruption
            with self.subTest(interruption=interruption):
                with self.assertRaises(ContractValidationError):
                    loads_command_result(json.dumps(malformed))

        death_data = self._death_result().to_dict()
        invalid_continuations = (
            {
                "kind": "continuation_required",
                "continuity_state": [],
            },
            {
                "kind": "continuation_required",
                "continuity_state": {
                    **death_data["interruption"]["continuity_state"],
                    "extra": True,
                },
            },
            {
                "kind": "continuation_required",
                "continuity_state": {
                    **death_data["interruption"]["continuity_state"],
                    "actor_id": "friend",
                },
            },
            {
                "kind": "continuation_required",
                "continuity_state": {
                    **death_data["interruption"]["continuity_state"],
                    "focus_actor_name": "Forged Name",
                },
            },
            {
                "kind": "continuation_required",
                "continuity_state": {
                    **death_data["interruption"]["continuity_state"],
                    "continuity_candidates": [],
                    "continuity_candidate_ids": [],
                    "had_continuity_candidates": False,
                },
            },
            {
                "kind": "continuation_required",
                "continuity_state": {
                    **death_data["interruption"]["continuity_state"],
                    "continuity_candidates": [
                        {
                            **death_data["interruption"][
                                "continuity_state"
                            ]["continuity_candidates"][0],
                            "full_name": "Forged Candidate",
                        }
                    ],
                },
            },
        )
        for interruption in invalid_continuations:
            malformed = deepcopy(death_data)
            malformed["interruption"] = interruption
            with self.subTest(interruption=interruption):
                with self.assertRaises(ContractValidationError):
                    loads_command_result(json.dumps(malformed))

        missing_death_interruption = deepcopy(death_data)
        missing_death_interruption["interruption"] = None
        with self.assertRaises(ContractValidationError):
            loads_command_result(json.dumps(missing_death_interruption))

        failed = dispatch_command(
            None,
            command(
                "missing-save-contract",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        ).to_dict()
        failed["interruption"] = identity_data["interruption"]
        with self.assertRaises(ContractValidationError):
            loads_command_result(json.dumps(failed))

        non_advance = _create(command_id="create-contract").to_dict()
        non_advance["interruption"] = identity_data["interruption"]
        with self.assertRaises(ContractValidationError):
            loads_command_result(json.dumps(non_advance))

    def test_continuation_candidates_must_match_exact_saved_snapshot(
        self,
    ) -> None:
        death_data = self._death_result().to_dict()
        candidate = death_data["interruption"]["continuity_state"][
            "continuity_candidates"
        ][0]
        forged_values = {
            "actor_id": "forged-candidate",
            "full_name": "Forged Candidate",
            "link_type": "family",
            "link_role": "child",
            "relationship_label": "Child",
            "relationship_priority": 0,
            "family_branch_label": "Maternal",
            "structural_status": "dead",
            "is_alive": False,
            "age": candidate["age"] + 1,
            "life_stage": "Elder",
            "current_place_name": "Forged Place",
        }
        for field_name, forged_value in forged_values.items():
            malformed = deepcopy(death_data)
            forged_candidate = malformed["interruption"][
                "continuity_state"
            ]["continuity_candidates"][0]
            forged_candidate[field_name] = forged_value
            if field_name == "actor_id":
                malformed["interruption"]["continuity_state"][
                    "continuity_candidate_ids"
                ][0] = forged_value
            with self.subTest(field_name=field_name):
                with self.assertRaises(ContractValidationError):
                    loads_command_result(json.dumps(malformed))

        extra_field = deepcopy(death_data)
        extra_field["interruption"]["continuity_state"][
            "continuity_candidates"
        ][0]["extra"] = True
        with self.assertRaises(ContractValidationError):
            loads_command_result(json.dumps(extra_field))

        missing_field = deepcopy(death_data)
        del missing_field["interruption"]["continuity_state"][
            "continuity_candidates"
        ][0]["age"]
        with self.assertRaises(ContractValidationError):
            loads_command_result(json.dumps(missing_field))

        for field_name, forged_value in (
            ("is_alive", 1),
            ("age", float(candidate["age"])),
            (
                "relationship_priority",
                float(candidate["relationship_priority"]),
            ),
        ):
            wrong_type = deepcopy(death_data)
            wrong_type["interruption"]["continuity_state"][
                "continuity_candidates"
            ][0][field_name] = forged_value
            with self.subTest(wrong_type=field_name):
                with self.assertRaises(ContractValidationError):
                    loads_command_result(json.dumps(wrong_type))

    def test_continuation_candidate_order_must_match_saved_world(
        self,
    ) -> None:
        world = build_test_world()
        second_friend = world.create_human_actor(
            actor_id="second_friend",
            species="Human",
            first_name="Grace",
            last_name="Hopper",
            sex="Female",
            gender="Female",
            birth_year=0,
            birth_month=9,
            current_place_id="test_city",
            residence_place_id="test_city",
            jurisdiction_place_id="test_country",
        )
        second_friend.traits = [
            "Driven",
            "Curious",
            "Disciplined",
            "Resilient",
        ]
        world.create_social_link_pair(
            "player",
            "second_friend",
            closeness=45,
            status="active",
            closeness_history_months=2,
        )
        world.actors["player"].birth_year = -120
        result = dispatch_command(
            build_save_envelope(
                world,
                GameSession(
                    focused_actor_id="player",
                    last_logged_year=3,
                ),
                SeededRandomSource(11),
                DeterministicIdSource("trace"),
                engine_version="headless-test",
            ),
            command(
                "ordered-death-contract",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                0,
            ),
        )
        result_data = result.to_dict()
        continuity_state = result_data["interruption"][
            "continuity_state"
        ]
        self.assertEqual(len(continuity_state["continuity_candidates"]), 2)

        continuity_state["continuity_candidates"].reverse()
        continuity_state["continuity_candidate_ids"].reverse()
        with self.assertRaises(ContractValidationError):
            loads_command_result(json.dumps(result_data))

    def test_mutated_interruption_is_revalidated_before_serialization(
        self,
    ) -> None:
        result = self._identity_result()
        result.interruption["remaining_months"] = 1
        with self.assertRaises(ContractValidationError):
            dumps_command_result(result)


class CreateAdvanceGoldenTraceTests(unittest.TestCase):
    def test_dispatcher_create_advance_v1_trace(self) -> None:
        create_result = _create(command_id="trace-create-01")
        reloaded_save = loads_save_envelope(
            dumps_save_envelope(create_result.save)
        )
        advance_result = dispatch_command(
            reloaded_save,
            command(
                "trace-advance-02",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                1,
            ),
        )
        observed = {
            "contract": "dispatcher-create-advance-v1",
            "steps": [
                _result_snapshot(create_result),
                _result_snapshot(advance_result),
            ],
        }
        with GOLDEN_PATH.open("r", encoding="utf-8") as golden_file:
            expected = json.load(golden_file)
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
