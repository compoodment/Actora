"""Tests for the first curses-free headless-core checkpoint."""

from __future__ import annotations

import json
import random as legacy_random
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

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
    RandomState,
    SaveEnvelope,
    SeededRandomSource,
)
from actora_core.serialization import (
    build_save_envelope,
    dumps_save_envelope,
    loads_save_envelope,
    restore_save_envelope,
    serialize_world,
)
from actora_core.validation import (
    assert_valid_save_envelope,
    assert_valid_world_state,
    collect_save_invariant_violations,
    collect_world_invariant_violations,
)
from world import World
from human import Human

REPO_ROOT = Path(__file__).resolve().parents[1]


def build_test_world() -> World:
    world = World(start_year=3, start_month=7)
    world.add_place("earth", "Earth", "world_body")
    world.add_place("test_country", "Test Country", "country", "earth")
    world.add_place("test_city", "Test City", "city", "test_country")
    world.create_human_actor(
        actor_id="player",
        species="Human",
        first_name="Ada",
        last_name="Lovelace",
        sex="Female",
        gender="Female",
        birth_year=1,
        birth_month=1,
        current_place_id="test_city",
        residence_place_id="test_city",
        jurisdiction_place_id="test_country",
    )
    world.create_human_actor(
        actor_id="friend",
        species="Human",
        first_name="Charles",
        last_name="Babbage",
        sex="Male",
        gender="Male",
        birth_year=-1,
        birth_month=4,
        current_place_id="test_city",
        residence_place_id="test_city",
        jurisdiction_place_id="test_country",
    )
    world.create_social_link_pair(
        "player",
        "friend",
        closeness=45,
        status="active",
        closeness_history_months=2,
    )
    world.actors["player"].traits = [
        "Curious",
        "Social",
        "Impulsive",
        "Empathetic",
    ]
    world.actors["friend"].traits = [
        "Chill",
        "Social",
        "Disciplined",
        "Ambitious",
    ]
    world.set_focused_actor("player")
    world._used_npc_last_names.add("Babbage")
    return world


class ImportBoundaryTests(unittest.TestCase):
    def test_package_import_does_not_load_curses(self) -> None:
        script = (
            "import sys; import actora_core; "
            "assert 'curses' not in sys.modules, sorted("
            "name for name in sys.modules if name.startswith('curses')); "
            "print('curses-free')"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), "curses-free")


class DeterministicSourceTests(unittest.TestCase):
    def test_pcg32_public_trace_is_versioned_and_stable(self) -> None:
        source = SeededRandomSource(42)
        self.assertEqual(
            source.snapshot().to_dict(),
            {
                "algorithm": "pcg32-v1",
                "state": "185706b82c2e03f8",
                "increment": "000000000000006d",
            },
        )
        self.assertEqual(
            [source.randint(0, 999999) for _ in range(6)],
            [787127, 521225, 865072, 193171, 292939, 876654],
        )

        source = SeededRandomSource(42)
        self.assertEqual(
            [source.random() for _ in range(4)],
            [
                0.6303102186438938,
                0.7270080560068604,
                0.7486033647998483,
                0.7491247468042271,
            ],
        )

        source = SeededRandomSource(42)
        values = list(range(8))
        source.shuffle(values)
        self.assertEqual(values, [5, 6, 2, 4, 3, 0, 1, 7])

        source = SeededRandomSource(42)
        self.assertEqual(
            source.sample(list("abcdefgh"), 4),
            ["h", "c", "b", "g"],
        )

    def test_random_state_roundtrip_resumes_exactly(self) -> None:
        source = SeededRandomSource("actora")
        source.randint(1, 100)
        source.choice(["one", "two", "three"])
        serialized_state = json.loads(json.dumps(source.snapshot().to_dict()))
        restored = SeededRandomSource.from_state(
            RandomState.from_dict(serialized_state)
        )
        self.assertEqual(
            [source.randint(-1000, 1000) for _ in range(20)],
            [restored.randint(-1000, 1000) for _ in range(20)],
        )

    def test_id_state_roundtrip_resumes_exactly(self) -> None:
        source = DeterministicIdSource("test")
        self.assertEqual(source.next_id("actor"), "test_actor_00000001")
        serialized_state = json.loads(json.dumps(source.snapshot().to_dict()))
        restored = DeterministicIdSource.from_state(
            IdState.from_dict(serialized_state)
        )
        self.assertEqual(source.next_id("record"), "test_record_00000002")
        self.assertEqual(restored.next_id("record"), "test_record_00000002")
        with self.assertRaises(ContractValidationError):
            source.next_id("Bad Role")

    def test_session_defaults_use_injected_randomness(self) -> None:
        first = GameSession.new("player", SeededRandomSource(99))
        second = GameSession.new("player", SeededRandomSource(99))
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertGreaterEqual(first.gender_choice_age, 12)
        self.assertLessEqual(first.gender_choice_age, 15)
        self.assertGreaterEqual(first.sexuality_choice_age, 14)
        self.assertLessEqual(first.sexuality_choice_age, 17)

    def test_session_capture_and_apply_preserve_runtime_semantics(self) -> None:
        world = build_test_world()

        class Runtime(SimpleNamespace):
            def get_focused_actor_id(self):
                return self.world.get_focused_actor_id() or self.player_id

        source = Runtime(
            world=world,
            player_id="player",
            active_actions=[
                {
                    "action_id": "capture_action_00000001",
                    "action_type": "personal",
                    "subtype_id": "nap",
                    "label": "Take a Nap",
                    "time_cost": 2,
                    "stat_changes": {"happiness": 2, "stress": -3},
                    "event_text": "You took a proper nap.",
                }
            ],
            pending_choice={
                "choice_id": "gender_identity",
                "title": "Identity",
                "text": "Reflect.",
                "question": "You are:",
                "options": ["Female", "Non-binary"],
                "selected_index": 0,
                "skippable": True,
            },
            remaining_skip_months=11,
            event_log=[{"kind": "year_header", "text": "Year 3", "year": 3}],
            last_logged_year=3,
            gender_choice_offered=True,
            sexuality_choice_offered=False,
            identity_popup_suppressed_for_resumed_adult=False,
            gender_choice_age=13,
            sexuality_choice_age=16,
            meeting_event_last_total_months=22,
            hang_out_actor_ids=["friend"],
            personal_subtype_options=[{"id": "nap", "time_cost": 2}],
            screen_name="browser",
        )
        captured = GameSession.capture_runtime(source)
        self.assertEqual(
            captured.pending_choice["selected_option_id"],
            "value:Female",
        )
        self.assertEqual(
            captured.pending_choice["options"][0],
            {
                "option_id": "value:Female",
                "label": "Female",
                "value": "Female",
            },
        )
        self.assertNotIn("selected_index", captured.pending_choice)
        self.assertNotIn("hang_out_actor_ids", captured.to_dict())
        self.assertNotIn("personal_subtype_options", captured.to_dict())
        target = Runtime(
            world=world,
            player_id="friend",
            active_actions=[],
            pending_choice=None,
            screen_name="profile",
        )
        captured.apply_to_runtime(target)
        self.assertEqual(
            GameSession.capture_runtime(target).to_dict(),
            captured.to_dict(),
        )
        self.assertEqual(target.screen_name, "profile")

        source.active_actions[0]["label"] = "Mutated"
        self.assertEqual(captured.active_actions[0]["label"], "Take a Nap")

        legacy_source = Runtime(
            world=world,
            player_id="player",
            active_actions=[
                {
                    "action_type": "personal",
                    "subtype_id": "nap",
                    "label": "Take a Nap",
                    "time_cost": 2,
                    "stat_changes": {"happiness": 2, "stress": -3},
                    "event_text": "You took a proper nap.",
                }
            ],
            pending_choice=None,
        )
        with self.assertRaisesRegex(
            ContractValidationError,
            "engine-issued action_id",
        ):
            GameSession.capture_runtime(legacy_source)


class SaveRoundtripTests(unittest.TestCase):
    def build_envelope(self, *, revision: int = 4):
        world = build_test_world()
        random_source = SeededRandomSource(2026)
        id_source = DeterministicIdSource("save")
        id_source.next_id("record")
        session = GameSession(
            focused_actor_id="player",
            active_actions=[
                {
                    "action_id": "save_action_00000001",
                    "action_type": "spend_time",
                    "target_actor_id": "friend",
                    "label": "Spend time with Charles Babbage",
                    "time_cost": 4,
                }
            ],
            pending_choice={
                "title": "Hang Out",
                "text": "Choose someone to spend time with.",
                "question": "",
                "options": [
                    {
                        "option_id": "actor:friend",
                        "label": "Charles Babbage · Friend (queued)",
                        "value": "friend",
                    }
                ],
                "selected_option_id": "actor:friend",
                "skippable": True,
                "choice_id": "select_hang_out_target",
                "default_value": None,
            },
            remaining_skip_months=0,
            event_log=[
                {
                    "kind": "event",
                    "text": "A test event.",
                    "year": 3,
                    "month": 7,
                    "record_type": None,
                }
            ],
            last_logged_year=3,
            gender_choice_age=13,
            sexuality_choice_age=16,
            meeting_event_last_total_months=18,
        )
        envelope = build_save_envelope(
            world,
            session,
            random_source,
            id_source,
            engine_version="test-engine",
            revision=revision,
            metadata={"source_revision": "test"},
        )
        return world, random_source, id_source, envelope

    def test_world_and_save_json_roundtrip(self) -> None:
        world, random_source, id_source, envelope = self.build_envelope()
        original_snapshot = envelope.to_dict()
        serialized = dumps_save_envelope(envelope)
        loaded = loads_save_envelope(serialized)
        self.assertEqual(loaded.to_dict(), original_snapshot)

        restored = restore_save_envelope(loaded)
        self.assertEqual(serialize_world(restored.world), envelope.world)
        self.assertEqual(restored.session.to_dict(), envelope.session.to_dict())
        self.assertEqual(
            [random_source.randint(0, 10_000) for _ in range(12)],
            [restored.random_source.randint(0, 10_000) for _ in range(12)],
        )
        self.assertEqual(
            id_source.next_id("actor"),
            restored.id_source.next_id("actor"),
        )

        world.current_year = 999
        world.actors["player"].first_name = "Mutated"
        self.assertEqual(envelope.world["current_year"], 3)
        self.assertEqual(
            envelope.world["actors"]["player"]["first_name"],
            "Ada",
        )

    def test_world_restore_does_not_run_human_constructor(self) -> None:
        _, _, _, envelope = self.build_envelope()
        with patch.object(
            Human,
            "__init__",
            side_effect=AssertionError("constructor must not run"),
        ):
            restored = restore_save_envelope(envelope)
        self.assertEqual(restored.world.get_focused_actor().get_full_name(), "Ada Lovelace")

    def test_restored_world_preserves_current_turn_behavior_with_same_legacy_seed(
        self,
    ) -> None:
        world, _, _, envelope = self.build_envelope()
        restored_world = restore_save_envelope(envelope).world
        previous_random_state = legacy_random.getstate()
        try:
            legacy_random.seed(771)
            original_result = world.simulate_advance_turn("player", 1)
            legacy_random.seed(771)
            restored_result = restored_world.simulate_advance_turn("player", 1)
        finally:
            legacy_random.setstate(previous_random_state)
        self.assertEqual(restored_result, original_result)
        self.assertEqual(serialize_world(restored_world), serialize_world(world))

    def test_strict_loader_rejects_duplicate_keys_and_nonfinite_numbers(self) -> None:
        with self.assertRaisesRegex(ContractValidationError, "duplicate key"):
            loads_save_envelope('{"format_version":1,"format_version":1}')
        with self.assertRaisesRegex(ContractValidationError, "invalid constant"):
            loads_save_envelope('{"value":NaN}')
        _, _, _, envelope = self.build_envelope()
        future_save = envelope.to_dict()
        future_save["schema_version"] = 2
        with self.assertRaisesRegex(ContractValidationError, "schema_version 2"):
            loads_save_envelope(json.dumps(future_save))
        unknown_session_state = envelope.to_dict()
        unknown_session_state["session"]["future_field"] = True
        with self.assertRaisesRegex(ContractValidationError, "unknown fields"):
            loads_save_envelope(json.dumps(unknown_session_state))

    def test_successful_command_result_roundtrip(self) -> None:
        _, _, _, envelope = self.build_envelope(revision=8)
        envelope.session.pending_choice = None
        result = CommandResult(
            command_id="save_command_00000003",
            command_type=CommandType.ADVANCE_TIME,
            ok=True,
            revision=8,
            save=envelope,
            events=(
                {
                    "event_id": "month_passed",
                    "text": "One month passed.",
                    "year": 3,
                    "month": 8,
                    "tags": ["time"],
                },
            ),
            effects=(
                {
                    "kind": "time_advanced",
                    "months_requested": 1,
                    "months_advanced": 1,
                },
            ),
        )
        self.assertEqual(
            CommandResult.from_dict(result.to_dict()).to_dict(),
            result.to_dict(),
        )
        failed = CommandResult(
            command_id="save_command_00000004",
            command_type=CommandType.ADVANCE_TIME,
            ok=False,
            revision=8,
            save=envelope,
            error=CommandError(
                code="revision_conflict",
                message="The save changed in another writer.",
            ),
        )
        self.assertFalse(CommandResult.from_dict(failed.to_dict()).ok)


class CommandAndInvariantTests(unittest.TestCase):
    def test_command_contract_validates_payload_and_revision(self) -> None:
        command = GameCommand.create(
            CommandType.ADVANCE_TIME,
            {"months": 12},
            expected_revision=4,
            command_id="request-advance",
        )
        self.assertEqual(
            GameCommand.from_dict(command.to_dict()).to_dict(),
            command.to_dict(),
        )
        nullable_choice = GameCommand.create(
            CommandType.RESOLVE_CHOICE,
            {"choice_id": "sexuality", "option_id": None},
            expected_revision=4,
            command_id="request-choice",
        )
        self.assertIsNone(nullable_choice.payload["option_id"])
        with self.assertRaises(ContractValidationError):
            GameCommand.create(
                CommandType.RESOLVE_CHOICE,
                {
                    "choice_id": "sexuality",
                    "selected_value": "Bisexual",
                },
                expected_revision=4,
                command_id="request-client-authored-choice-value",
            )

        invalid_cases = (
            (CommandType.ADVANCE_TIME, {"months": 0}),
            (CommandType.RESOLVE_CHOICE, {"choice_id": "sexuality"}),
            (CommandType.REMOVE_ACTION, {}),
            (
                CommandType.REMOVE_ACTION,
                {"action_id": "one", "action_index": 0},
            ),
        )
        for command_type, payload in invalid_cases:
            with self.subTest(command_type=command_type, payload=payload):
                with self.assertRaises(ContractValidationError):
                    GameCommand.create(
                        command_type,
                        payload,
                        expected_revision=4,
                        command_id="request-invalid",
                    )

    def test_world_invariants_report_dangling_and_invalid_state(self) -> None:
        state = serialize_world(build_test_world())
        broken = deepcopy(state)
        broken["links"][0]["target_id"] = "missing"
        broken["actors"]["player"]["stats"]["health"] = 101
        broken["places"]["test_city"]["parent_place_id"] = "missing_place"
        violations = collect_world_invariant_violations(broken)
        codes = {violation.code for violation in violations}
        self.assertIn("dangling_link_endpoint", codes)
        self.assertIn("stat_out_of_range", codes)
        self.assertIn("dangling_place_parent", codes)
        with self.assertRaises(InvariantError):
            assert_valid_world_state(broken)

    def test_world_invariants_do_not_crash_on_json_shaped_bad_ids(self) -> None:
        state = serialize_world(build_test_world())
        state["places"]["test_city"]["parent_place_id"] = []
        state["actors"]["player"]["current_place_id"] = []
        state["links"][0]["target_id"] = {}
        state["records"][0]["actor_ids"] = [{}]
        violations = collect_world_invariant_violations(state)
        codes = {violation.code for violation in violations}
        self.assertIn("dangling_place_parent", codes)
        self.assertIn("dangling_actor_place", codes)
        self.assertIn("dangling_link_endpoint", codes)
        self.assertIn("dangling_record_actor", codes)

    def test_save_invariants_report_focus_and_queue_errors(self) -> None:
        world = build_test_world()
        session = GameSession(
            focused_actor_id="friend",
            active_actions=[
                {
                    "action_type": "spend_time",
                    "target_actor_id": "missing",
                    "label": "Missing",
                    "time_cost": -1,
                }
            ],
        )
        envelope = SaveEnvelope(
            engine_version="test",
            world=serialize_world(world),
            session=session,
            rng=SeededRandomSource(1).snapshot(),
            ids=DeterministicIdSource("test").snapshot(),
        )
        violations = collect_save_invariant_violations(envelope)
        codes = {violation.code for violation in violations}
        self.assertIn("focus_mismatch", codes)
        self.assertIn("dangling_action_target", codes)
        self.assertIn("invalid_action_time_cost", codes)
        with self.assertRaises(InvariantError):
            assert_valid_save_envelope(envelope)


if __name__ == "__main__":
    unittest.main()
