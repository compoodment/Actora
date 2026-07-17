"""Contract and deterministic trace tests for the action-queue dispatcher."""

from __future__ import annotations

import hashlib
import json
import unittest
from copy import deepcopy
from pathlib import Path

from mechanics import EXERCISE_SUBTYPES

from actora_core import (
    CommandError,
    CommandResult,
    CommandType,
    ContractValidationError,
    DeterministicIdSource,
    GameCommand,
    GameSession,
    IdState,
    InvariantError,
    SaveEnvelope,
    SeededRandomSource,
    dispatch_command,
    dispatch_serialized_command,
    dumps_command_result,
    dumps_game_command,
    loads_command_result,
    loads_game_command,
)
from actora_core.json_types import MAX_SAFE_INTEGER
from actora_core.serialization import (
    build_save_envelope,
    dumps_save_envelope,
    loads_save_envelope,
    restore_save_envelope,
    serialize_world,
)
from actora_core.validation import assert_valid_save_envelope
from tests.test_actora_core import build_test_world

GOLDEN_PATH = (
    Path(__file__).resolve().parent
    / "golden"
    / "dispatcher_action_queue_v1.json"
)


def build_dispatch_save(
    *,
    revision: int = 0,
    engine_kind: str = "python-headless",
    session: GameSession | None = None,
    next_id: int = 1,
) -> SaveEnvelope:
    world = build_test_world()
    world.recent_event_ids_by_actor = {
        "player": ["met_friend", "quiet_month"],
    }
    return build_save_envelope(
        world,
        session or GameSession(focused_actor_id="player", last_logged_year=3),
        SeededRandomSource("dispatcher-trace"),
        DeterministicIdSource("trace", next_value=next_id),
        engine_version="headless-test-0.1",
        engine_kind=engine_kind,
        revision=revision,
        metadata={
            "origin": "dispatcher-test",
            "nested": {"preserved": True},
        },
    )


def command(
    command_id: str,
    command_type: CommandType,
    payload: dict,
    revision: int,
) -> GameCommand:
    return GameCommand.create(
        command_type,
        payload,
        command_id=command_id,
        expected_revision=revision,
    )


def build_creation_character() -> dict:
    return {
        "first_name": "Ada",
        "last_name": "Trace",
        "sex": "Female",
        "gender": "Female",
        "country_id": "us",
        "city_id": "us_new_york",
        "appearance": {
            "eye_color": "Brown",
            "hair_color": "Black",
            "skin_tone": "Medium",
        },
        "traits": [
            "Curious",
            "Disciplined",
            "Empathetic",
            "Resilient",
        ],
        "stats": {
            "health": 80,
            "happiness": 70,
            "intelligence": 75,
            "strength": 50,
            "charisma": 55,
            "imagination": 65,
            "memory": 0,
            "wisdom": 45,
            "stress": 0,
            "discipline": 70,
            "willpower": 60,
            "looks": 50,
            "fertility": 50,
        },
    }


class DispatcherMutationTests(unittest.TestCase):
    def test_personal_intent_queues_only_canonical_engine_effects(self) -> None:
        save = build_dispatch_save(revision=4)
        before = dumps_save_envelope(save)
        result = dispatch_command(
            save,
            command(
                "request-personal",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "nap"}},
                4,
            ),
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.revision, 5)
        self.assertEqual(result.events, ())
        self.assertEqual(
            result.effects,
            ({"kind": "action_queued", "action_id": "trace_action_00000001"},),
        )
        self.assertEqual(
            result.save.session.active_actions,
            [
                {
                    "action_id": "trace_action_00000001",
                    "action_type": "personal",
                    "subtype_id": "nap",
                    "label": "Take a Nap",
                    "time_cost": 2,
                    "stat_changes": {"happiness": 2, "stress": -3},
                    "event_text": "You took a proper nap.",
                }
            ],
        )
        self.assertEqual(result.save.ids.next_value, 2)
        self.assertEqual(dumps_save_envelope(save), before)

    def test_spend_time_duplicate_is_atomic_and_does_not_consume_id(self) -> None:
        save = build_dispatch_save()
        first = dispatch_command(
            save,
            command(
                "request-social-1",
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
        before_failure = dumps_save_envelope(first.save)
        duplicate = dispatch_command(
            first.save,
            command(
                "request-social-2",
                CommandType.QUEUE_ACTION,
                {
                    "action": {
                        "action_type": "spend_time",
                        "target_actor_id": "friend",
                    }
                },
                1,
            ),
        )
        self.assertFalse(duplicate.ok)
        self.assertEqual(duplicate.error.code, "action_already_queued")
        self.assertEqual(dumps_save_envelope(duplicate.save), before_failure)
        self.assertEqual(duplicate.save.ids.next_value, 2)

        unavailable = dispatch_command(
            first.save,
            command(
                "request-social-3",
                CommandType.QUEUE_ACTION,
                {
                    "action": {
                        "action_type": "spend_time",
                        "target_actor_id": "missing",
                    }
                },
                1,
            ),
        )
        self.assertEqual(unavailable.error.code, "action_not_available")
        self.assertEqual(dumps_save_envelope(unavailable.save), before_failure)

    def test_remove_uses_durable_id_only(self) -> None:
        queued = dispatch_command(
            build_dispatch_save(),
            command(
                "request-queue",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "run"}},
                0,
            ),
        )
        removed = dispatch_command(
            queued.save,
            command(
                "request-remove",
                CommandType.REMOVE_ACTION,
                {"action_id": "trace_action_00000001"},
                1,
            ),
        )
        self.assertTrue(removed.ok)
        self.assertEqual(removed.revision, 2)
        self.assertEqual(removed.save.session.active_actions, [])
        self.assertEqual(
            removed.effects,
            ({"kind": "action_removed", "action_id": "trace_action_00000001"},),
        )

        before_missing = dumps_save_envelope(removed.save)
        missing = dispatch_command(
            removed.save,
            command(
                "request-missing",
                CommandType.REMOVE_ACTION,
                {"action_id": "trace_action_99999999"},
                2,
            ),
        )
        self.assertEqual(missing.error.code, "action_not_found")
        self.assertEqual(dumps_save_envelope(missing.save), before_missing)

        with self.assertRaises(ContractValidationError):
            command(
                "request-index",
                CommandType.REMOVE_ACTION,
                {"action_index": 0},
                2,
            )

    def test_all_domain_failures_preserve_revision_rng_ids_and_save_bytes(self) -> None:
        save = build_dispatch_save(revision=9)
        before = dumps_save_envelope(save)
        snapshots = []
        commands = (
            command(
                "request-stale",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "nap"}},
                8,
            ),
            command(
                "request-unsupported-action",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "dance"}},
                9,
            ),
            command(
                "request-unimplemented",
                CommandType.RESOLVE_CHOICE,
                {
                    "choice_id": "gender_identity",
                    "option_id": "value:Female",
                },
                9,
            ),
        )
        expected_codes = (
            "revision_conflict",
            "unsupported_action",
            "command_not_implemented",
        )
        for request, expected_code in zip(commands, expected_codes):
            result = dispatch_command(save, request)
            self.assertFalse(result.ok)
            self.assertEqual(result.error.code, expected_code)
            self.assertEqual(result.revision, 9)
            snapshots.append(dumps_save_envelope(result.save))
        self.assertEqual(snapshots, [before, before, before])
        self.assertEqual(dumps_save_envelope(save), before)

    def test_dead_life_and_exhausted_time_return_player_safe_errors(self) -> None:
        dead_world = build_test_world()
        dead_world.recent_event_ids_by_actor = {}
        player = dead_world.actors["player"]
        player.structural_status = "dead"
        player.death_year = 3
        player.death_month = 7
        player.death_reason = "test"
        dead_save = build_save_envelope(
            dead_world,
            GameSession(focused_actor_id="player", last_logged_year=3),
            SeededRandomSource(1),
            DeterministicIdSource("trace"),
            engine_version="test",
        )
        dead_result = dispatch_command(
            dead_save,
            command(
                "request-after-life",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "nap"}},
                0,
            ),
        )
        self.assertEqual(dead_result.error.code, "focused_actor_dead")
        self.assertIn("life has ended", dead_result.error.message)
        self.assertNotIn("actor", dead_result.error.message.lower())
        self.assertNotIn("deceased", dead_result.error.message.lower())

        canonical = EXERCISE_SUBTYPES[1]
        full_queue = [
            {
                "action_id": f"trace_action_{index:08d}",
                "action_type": "personal",
                "subtype_id": canonical["id"],
                "label": canonical["label"],
                "time_cost": canonical["time_cost"],
                "stat_changes": canonical["stat_changes"],
                "event_text": canonical["event_text"],
            }
            for index in range(1, 61)
        ]
        budget_save = build_dispatch_save(
            session=GameSession(
                focused_actor_id="player",
                active_actions=full_queue,
                last_logged_year=3,
            ),
            next_id=61,
        )
        before = dumps_save_envelope(budget_save)
        budget_result = dispatch_command(
            budget_save,
            command(
                "request-over-budget",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "nap"}},
                0,
            ),
        )
        self.assertEqual(budget_result.error.code, "time_budget_exceeded")
        self.assertEqual(dumps_save_envelope(budget_result.save), before)

    def test_request_ids_never_consume_simulation_ids(self) -> None:
        save = build_dispatch_save()
        initial_ids = save.ids
        rejected = command(
            "browser-owned-request-id",
            CommandType.QUEUE_ACTION,
            {"action": {"action_type": "dance"}},
            0,
        )
        self.assertEqual(save.ids, initial_ids)
        result = dispatch_command(save, rejected)
        self.assertEqual(result.save.ids, initial_ids)

        accepted = dispatch_command(
            result.save,
            command(
                "another-browser-id",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "walk"}},
                0,
            ),
        )
        self.assertEqual(
            accepted.save.session.active_actions[0]["action_id"],
            "trace_action_00000001",
        )


class ContractHardeningTests(unittest.TestCase):
    def test_intent_contract_rejects_client_authored_effects_and_extras(self) -> None:
        invalid_actions = (
            {
                "action_type": "personal",
                "subtype_id": "nap",
                "time_cost": 0,
            },
            {
                "action_type": "personal",
                "subtype_id": "nap",
                "stat_changes": {"health": 100},
            },
            {
                "action_type": "spend_time",
                "target_actor_id": "friend",
                "label": "Client label",
            },
            {"action_type": "dance", "time_cost": 0},
        )
        for index, action_intent in enumerate(invalid_actions):
            with self.subTest(action_intent=action_intent):
                with self.assertRaisesRegex(
                    ContractValidationError,
                    "unknown fields",
                ):
                    command(
                        f"request-invalid-{index}",
                        CommandType.QUEUE_ACTION,
                        {"action": action_intent},
                        0,
                    )

        top_level = command(
            "request-valid",
            CommandType.QUEUE_ACTION,
            {"action": {"action_type": "personal", "subtype_id": "nap"}},
            0,
        ).to_dict()
        top_level["future"] = True
        with self.assertRaisesRegex(ContractValidationError, "unknown fields"):
            GameCommand.from_dict(top_level)

    def test_create_seed_advance_limit_and_safe_integer_boundaries(self) -> None:
        create = command(
            "request-create",
            CommandType.CREATE_GAME,
            {
                "character": build_creation_character(),
                "seed": "0123456789abcdef",
            },
            0,
        )
        result = dispatch_command(None, create)
        self.assertTrue(result.ok)
        self.assertIsNone(result.error)
        self.assertEqual(result.revision, 1)
        self.assertEqual(result.save.engine_version, "0.57.0")
        self.assertEqual(
            result.save.session.focused_actor_id,
            "actora_startup_player_00000003",
        )
        self.assertEqual(result.save.ids.next_value, 4)
        self.assertEqual(
            sorted(result.save.world["actors"]),
            [
                "actora_startup_father_00000002",
                "actora_startup_mother_00000001",
                "actora_startup_player_00000003",
            ],
        )

        invalid_create_payloads = (
            {"character": build_creation_character()},
            {
                "character": build_creation_character(),
                "seed": "ABCDEF0123456789",
            },
            {
                "character": build_creation_character(),
                "seed": "short",
            },
        )
        for payload in invalid_create_payloads:
            with self.assertRaises(ContractValidationError):
                command(
                    "request-invalid-create",
                    CommandType.CREATE_GAME,
                    payload,
                    0,
                )

        malformed_characters = []
        for field_name in (
            "first_name",
            "appearance",
            "traits",
            "stats",
        ):
            malformed = build_creation_character()
            del malformed[field_name]
            malformed_characters.append(malformed)

        wrong_gender = build_creation_character()
        wrong_gender["gender"] = "Male"
        malformed_characters.append(wrong_gender)

        duplicate_traits = build_creation_character()
        duplicate_traits["traits"] = ["Curious"] * 4
        malformed_characters.append(duplicate_traits)

        extra_stat = build_creation_character()
        extra_stat["stats"]["client_power"] = 100
        malformed_characters.append(extra_stat)

        out_of_range_stat = build_creation_character()
        out_of_range_stat["stats"]["health"] = 101
        malformed_characters.append(out_of_range_stat)

        unknown_country = build_creation_character()
        unknown_country["country_id"] = "unknown"
        malformed_characters.append(unknown_country)

        mismatched_city = build_creation_character()
        mismatched_city["city_id"] = "germany_berlin"
        malformed_characters.append(mismatched_city)

        for index, character in enumerate(malformed_characters):
            with self.subTest(character_index=index):
                with self.assertRaises(ContractValidationError):
                    command(
                        f"request-invalid-character-{index}",
                        CommandType.CREATE_GAME,
                        {
                            "character": character,
                            "seed": "0123456789abcdef",
                        },
                        0,
                    )

        command(
            "request-max-revision",
            CommandType.ADVANCE_TIME,
            {"months": 120},
            MAX_SAFE_INTEGER,
        )
        with self.assertRaises(ContractValidationError):
            command(
                "request-too-many-months",
                CommandType.ADVANCE_TIME,
                {"months": 121},
                0,
            )
        with self.assertRaisesRegex(
            ContractValidationError,
            "JavaScript-safe",
        ):
            command(
                "request-unsafe-revision",
                CommandType.ADVANCE_TIME,
                {"months": 1},
                MAX_SAFE_INTEGER + 1,
            )
        with self.assertRaisesRegex(
            ContractValidationError,
            "JavaScript-safe",
        ):
            IdState(namespace="trace", next_value=MAX_SAFE_INTEGER + 1)

    def test_invalid_actions_choices_social_numbers_and_cooldowns_are_rejected(
        self,
    ) -> None:
        save = build_dispatch_save()

        bad_action = deepcopy(save.to_dict())
        bad_action["session"]["active_actions"] = [
            {
                "action_id": "bad_action",
                "action_type": "personal",
                "subtype_id": "nap",
                "label": "Take a Nap",
                "time_cost": 2,
                "stat_changes": {
                    "happiness": 2,
                    "stress": -3,
                    "not_a_stat": 5,
                },
                "event_text": "You took a proper nap.",
            }
        ]
        with self.assertRaisesRegex(InvariantError, "noncanonical_personal_action"):
            assert_valid_save_envelope(SaveEnvelope.from_dict(bad_action))

        bad_appearance = deepcopy(save.to_dict())
        bad_appearance["world"]["actors"]["player"]["appearance"] = {}
        with self.assertRaisesRegex(InvariantError, "invalid_appearance"):
            assert_valid_save_envelope(
                SaveEnvelope.from_dict(bad_appearance)
            )

        bad_traits = deepcopy(save.to_dict())
        bad_traits["world"]["actors"]["player"]["traits"] = [
            "Curious",
            "Curious",
            "Legacy",
            "Driven",
        ]
        with self.assertRaisesRegex(InvariantError, "invalid_human_traits"):
            assert_valid_save_envelope(SaveEnvelope.from_dict(bad_traits))

        invalid_status = deepcopy(save.to_dict())
        invalid_status["world"]["actors"]["player"]["structural_status"] = []
        with self.assertRaisesRegex(InvariantError, "invalid_structural_status"):
            assert_valid_save_envelope(SaveEnvelope.from_dict(invalid_status))

        incomplete_choice = deepcopy(save.to_dict())
        incomplete_choice["session"]["pending_choice"] = {
            "choice_id": "gender_identity",
            "options": ["Female"],
            "selected_index": 0,
            "skippable": True,
            "default_value": "Female",
        }
        with self.assertRaisesRegex(InvariantError, "invalid_choice_shape"):
            assert_valid_save_envelope(SaveEnvelope.from_dict(incomplete_choice))

        mismatched_choice = deepcopy(save.to_dict())
        mismatched_choice["session"]["pending_choice"] = {
            "choice_id": "select_hang_out_target",
            "title": "Hang Out",
            "text": "Choose.",
            "question": "",
            "options": [
                {
                    "option_id": "actor:friend",
                    "label": "The wrong person",
                    "value": "friend",
                }
            ],
            "selected_option_id": "actor:friend",
            "skippable": True,
            "default_value": None,
        }
        with self.assertRaisesRegex(
            InvariantError,
            "choice_target_label_mismatch",
        ):
            assert_valid_save_envelope(SaveEnvelope.from_dict(mismatched_choice))

        invalid_default = deepcopy(save.to_dict())
        invalid_default["session"]["pending_choice"] = {
            "choice_id": "gender_identity",
            "title": "Identity",
            "text": "Reflect.",
            "question": "You are:",
            "options": [
                {
                    "option_id": "value:Female",
                    "label": "Female",
                    "value": "Female",
                },
                {
                    "option_id": "value:Non-binary",
                    "label": "Non-binary",
                    "value": "Non-binary",
                },
            ],
            "selected_option_id": "value:Female",
            "skippable": True,
            "default_value": "Hacker",
        }
        with self.assertRaisesRegex(InvariantError, "invalid_choice_default"):
            assert_valid_save_envelope(
                SaveEnvelope.from_dict(invalid_default)
            )

        unhashable_choice_id = deepcopy(invalid_default)
        unhashable_choice_id["session"]["pending_choice"]["choice_id"] = []
        unhashable_choice_id["session"]["pending_choice"][
            "default_value"
        ] = "Female"
        with self.assertRaisesRegex(InvariantError, "invalid_choice_id"):
            assert_valid_save_envelope(
                SaveEnvelope.from_dict(unhashable_choice_id)
            )

        unissued_action = deepcopy(save.to_dict())
        unissued_action["session"]["active_actions"] = [
            {
                "action_id": "trace_action_00000001",
                "action_type": "personal",
                "subtype_id": "nap",
                "label": "Take a Nap",
                "time_cost": 2,
                "stat_changes": {"happiness": 2, "stress": -3},
                "event_text": "You took a proper nap.",
            }
        ]
        with self.assertRaisesRegex(InvariantError, "unissued_action_id"):
            assert_valid_save_envelope(
                SaveEnvelope.from_dict(unissued_action)
            )

        oversized_action_id = deepcopy(unissued_action)
        oversized_action_id["session"]["active_actions"][0][
            "action_id"
        ] = "trace_action_" + ("9" * 5000)
        with self.assertRaisesRegex(
            InvariantError,
            "invalid_action_id_provenance",
        ):
            assert_valid_save_envelope(
                SaveEnvelope.from_dict(oversized_action_id)
            )

        legacy_parallel_choice = deepcopy(save.to_dict())
        legacy_parallel_choice["session"]["hang_out_actor_ids"] = ["friend"]
        with self.assertRaisesRegex(
            ContractValidationError,
            "unknown fields",
        ):
            SaveEnvelope.from_dict(legacy_parallel_choice)

        bad_social = deepcopy(save.to_dict())
        bad_social["world"]["links"][0]["metadata"][
            "closeness_history_months"
        ] = "two"
        with self.assertRaisesRegex(InvariantError, "invalid_social_history"):
            assert_valid_save_envelope(SaveEnvelope.from_dict(bad_social))

        unhashable_social_target = deepcopy(save.to_dict())
        unhashable_social_target["world"]["links"][0]["target_id"] = []
        with self.assertRaisesRegex(InvariantError, "dangling_link_endpoint"):
            assert_valid_save_envelope(
                SaveEnvelope.from_dict(unhashable_social_target)
            )

        unhashable_social_status = deepcopy(save.to_dict())
        unhashable_social_status["world"]["links"][0]["metadata"]["status"] = {}
        with self.assertRaisesRegex(InvariantError, "invalid_social_status"):
            assert_valid_save_envelope(
                SaveEnvelope.from_dict(unhashable_social_status)
            )

        ended_social = deepcopy(save.to_dict())
        for link in ended_social["world"]["links"]:
            link["metadata"]["status"] = "former"
            link["metadata"]["closeness"] = 0
            link["role"] = "former"
        assert_valid_save_envelope(SaveEnvelope.from_dict(ended_social))

        bad_cooldown = deepcopy(save.to_dict())
        bad_cooldown["world"]["recent_event_ids_by_actor"]["missing"] = ["one"]
        with self.assertRaisesRegex(
            InvariantError,
            "dangling_recent_event_actor",
        ):
            assert_valid_save_envelope(SaveEnvelope.from_dict(bad_cooldown))

        duplicate_cooldown = deepcopy(save.to_dict())
        duplicate_cooldown["world"]["recent_event_ids_by_actor"]["player"] = [
            "same",
            "same",
        ]
        with self.assertRaisesRegex(
            InvariantError,
            "duplicate_recent_event_id",
        ):
            assert_valid_save_envelope(
                SaveEnvelope.from_dict(duplicate_cooldown)
            )

    def test_nested_result_save_is_validated_at_construction_and_serialization(
        self,
    ) -> None:
        save = build_dispatch_save(revision=2)
        save.world["actors"]["player"]["stats"]["health"] = 101
        with self.assertRaisesRegex(InvariantError, "stat_out_of_range"):
            CommandResult(
                command_id="request-invalid-result",
                command_type=CommandType.ADVANCE_TIME,
                ok=True,
                revision=2,
                save=save,
            )

        valid_save = build_dispatch_save(revision=2)
        result = CommandResult(
            command_id="request-mutable-result",
            command_type=CommandType.ADVANCE_TIME,
            ok=True,
            revision=2,
            save=valid_save,
        )
        valid_save.world["actors"]["player"]["stats"]["health"] = 101
        with self.assertRaisesRegex(InvariantError, "stat_out_of_range"):
            result.to_dict()

        malformed_world = build_dispatch_save(revision=2)
        malformed_world.world = []
        with self.assertRaisesRegex(InvariantError, "world_not_object"):
            malformed_world.to_dict()

    def test_wire_objects_reject_unknown_fields_and_strict_json(self) -> None:
        with self.assertRaisesRegex(ContractValidationError, "duplicate key"):
            loads_game_command(
                '{"command_id":"one","command_id":"two"}'
            )
        with self.assertRaisesRegex(ContractValidationError, "invalid constant"):
            loads_game_command('{"value":NaN}')
        with self.assertRaisesRegex(ContractValidationError, "JavaScript-safe"):
            loads_game_command(
                '{"contract_version":' + ("9" * 5000) + "}"
            )
        with self.assertRaisesRegex(ContractValidationError, "JavaScript-safe"):
            loads_save_envelope(
                '{"revision":' + ("9" * 5000) + "}"
            )
        with self.assertRaisesRegex(ContractValidationError, "duplicate key"):
            loads_command_result('{"ok":true,"ok":false}')
        with self.assertRaisesRegex(ContractValidationError, "unknown fields"):
            CommandError.from_dict(
                {"code": "x", "message": "x", "future": True}
            )

        failed = CommandResult(
            command_id="request-failed",
            command_type=CommandType.ADVANCE_TIME,
            ok=False,
            revision=0,
            save=None,
            error=CommandError(code="x", message="x"),
        ).to_dict()
        failed["future"] = True
        with self.assertRaisesRegex(ContractValidationError, "unknown fields"):
            CommandResult.from_dict(failed)

        save = build_dispatch_save()
        save.format_version = True
        with self.assertRaisesRegex(ContractValidationError, "must be an integer"):
            save.to_dict()
        save = build_dispatch_save()
        save.schema_version = 1.0
        with self.assertRaisesRegex(ContractValidationError, "must be an integer"):
            save.to_dict()

    def test_canonical_transport_roundtrip_and_serialized_dispatch(self) -> None:
        save = build_dispatch_save()
        request = command(
            "request-transport",
            CommandType.QUEUE_ACTION,
            {"action": {"action_type": "personal", "subtype_id": "music"}},
            0,
        )
        serialized_request = dumps_game_command(request)
        self.assertEqual(
            dumps_game_command(loads_game_command(serialized_request)),
            serialized_request,
        )
        serialized_result = dispatch_serialized_command(
            dumps_save_envelope(save),
            serialized_request,
        )
        result = loads_command_result(serialized_result)
        self.assertTrue(result.ok)
        self.assertEqual(
            dumps_command_result(result),
            serialized_result,
        )

    def test_restore_preserves_complete_provenance_and_world_cooldowns(self) -> None:
        save = build_dispatch_save(revision=12)
        restored = restore_save_envelope(save)
        self.assertEqual(restored.engine_version, save.engine_version)
        self.assertEqual(restored.engine_kind, save.engine_kind)
        self.assertEqual(restored.revision, save.revision)
        self.assertEqual(restored.format_version, save.format_version)
        self.assertEqual(restored.schema_version, save.schema_version)
        self.assertEqual(restored.metadata, save.metadata)
        self.assertIsNot(restored.metadata, save.metadata)
        self.assertEqual(serialize_world(restored.world), save.world)
        self.assertEqual(
            restored.world.recent_event_ids_by_actor,
            {"player": ["met_friend", "quiet_month"]},
        )

    def test_engine_kind_mismatch_is_structured_and_atomic(self) -> None:
        save = build_dispatch_save(engine_kind="legacy-terminal")
        before = dumps_save_envelope(save)
        result = dispatch_command(
            save,
            command(
                "request-wrong-engine",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "nap"}},
                0,
            ),
        )
        self.assertEqual(result.error.code, "engine_kind_mismatch")
        self.assertEqual(result.error.details["actual_engine_kind"], "legacy-terminal")
        self.assertEqual(dumps_save_envelope(result.save), before)


class GoldenTraceTests(unittest.TestCase):
    def test_dispatcher_action_queue_v1_trace(self) -> None:
        save = build_dispatch_save()
        steps = (
            command(
                "trace-request-01",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "nap"}},
                0,
            ),
            command(
                "trace-request-02",
                CommandType.QUEUE_ACTION,
                {
                    "action": {
                        "action_type": "spend_time",
                        "target_actor_id": "friend",
                    }
                },
                1,
            ),
            command(
                "trace-request-03",
                CommandType.QUEUE_ACTION,
                {
                    "action": {
                        "action_type": "spend_time",
                        "target_actor_id": "friend",
                    }
                },
                2,
            ),
            command(
                "trace-request-04",
                CommandType.REMOVE_ACTION,
                {"action_id": "trace_action_00000001"},
                2,
            ),
            command(
                "trace-request-05",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "run"}},
                2,
            ),
            command(
                "trace-request-06",
                CommandType.REMOVE_ACTION,
                {"action_id": "trace_action_99999999"},
                3,
            ),
            command(
                "trace-request-07",
                CommandType.RESOLVE_CHOICE,
                {
                    "choice_id": "gender_identity",
                    "option_id": "value:Female",
                },
                3,
            ),
            command(
                "trace-request-08",
                CommandType.QUEUE_ACTION,
                {"action": {"action_type": "personal", "subtype_id": "run"}},
                3,
            ),
        )

        observed_steps = []
        for index, request in enumerate(steps):
            if index == 7:
                save = loads_save_envelope(dumps_save_envelope(save))
            result = dispatch_command(save, request)
            if result.save is not None:
                save = result.save
                serialized_save = dumps_save_envelope(save)
                save_hash = hashlib.sha256(
                    serialized_save.encode("utf-8")
                ).hexdigest()
                actions = deepcopy(save.session.active_actions)
                next_id = save.ids.next_value
            else:
                save_hash = None
                actions = []
                next_id = None
            observed_steps.append(
                {
                    "command_id": request.command_id,
                    "command_type": request.command_type.value,
                    "ok": result.ok,
                    "revision": result.revision,
                    "error_code": (
                        result.error.code if result.error is not None else None
                    ),
                    "effects": list(result.effects),
                    "actions": actions,
                    "next_id": next_id,
                    "save_sha256": save_hash,
                }
            )

        observed = {
            "contract": "dispatcher-action-queue-v1",
            "steps": observed_steps,
        }
        with GOLDEN_PATH.open("r", encoding="utf-8") as golden_file:
            expected = json.load(golden_file)
        self.assertEqual(observed, expected)


if __name__ == "__main__":
    unittest.main()
