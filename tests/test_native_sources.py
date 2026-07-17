import random
import re
import subprocess
import sys
import unittest

from actora_core import DeterministicIdSource, SeededRandomSource
from actora_core.serialization import serialize_world
from events import get_meeting_event_for_player
from game_setup import setup_initial_world_from_character
from world import World


def build_creation_character():
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


def build_deterministic_startup(seed="native-seed", namespace="native"):
    random_source = SeededRandomSource(seed)
    id_source = DeterministicIdSource(namespace)
    world, player_id = setup_initial_world_from_character(
        build_creation_character(),
        random_source=random_source,
        id_source=id_source,
    )
    return world, player_id, random_source, id_source


class NativeSourceInjectionTests(unittest.TestCase):
    def test_startup_and_advance_are_repeatable_and_global_rng_isolated(self):
        global_state = random.getstate()

        first = build_deterministic_startup()
        second = build_deterministic_startup()

        self.assertEqual(first[1], second[1])
        self.assertEqual(serialize_world(first[0]), serialize_world(second[0]))
        self.assertEqual(first[2].snapshot(), second[2].snapshot())
        self.assertEqual(first[3].snapshot(), second[3].snapshot())
        self.assertEqual(random.getstate(), global_state)

        first_result = first[0].simulate_advance_turn(
            first[1],
            24,
            random_source=first[2],
            id_source=first[3],
        )
        second_result = second[0].simulate_advance_turn(
            second[1],
            24,
            random_source=second[2],
            id_source=second[3],
        )

        self.assertEqual(first_result, second_result)
        self.assertEqual(serialize_world(first[0]), serialize_world(second[0]))
        self.assertEqual(first[2].snapshot(), second[2].snapshot())
        self.assertEqual(first[3].snapshot(), second[3].snapshot())
        self.assertEqual(random.getstate(), global_state)

    def test_complete_human_stats_do_not_consume_injected_randomness(self):
        random_source = SeededRandomSource("normalization")
        before = random_source.snapshot()
        world = World(start_year=1)

        world.create_human_actor(
            actor_id="complete_actor",
            species="Human",
            first_name="Complete",
            last_name="Stats",
            sex="Female",
            gender="Female",
            birth_year=1,
            birth_month=1,
            randomize_stats=False,
            random_source=random_source,
        )

        self.assertEqual(random_source.snapshot(), before)

    def test_meeting_event_selection_uses_only_the_explicit_source(self):
        lifecycle = {
            "life_stage_model": "human_default",
            "age_months": 144,
            "life_stage": "Child",
        }
        first_source = SeededRandomSource("meeting-event")
        second_source = SeededRandomSource("meeting-event")
        global_state = random.getstate()

        first_event = get_meeting_event_for_player(
            lifecycle,
            random_source=first_source,
        )
        second_event = get_meeting_event_for_player(
            lifecycle,
            random_source=second_source,
        )

        self.assertEqual(first_event, second_event)
        self.assertEqual(first_source.snapshot(), second_source.snapshot())
        self.assertEqual(random.getstate(), global_state)

    def test_generated_people_and_ids_share_the_explicit_sources(self):
        first = build_deterministic_startup()
        second = build_deterministic_startup()

        first_npc_id, _ = first[0].generate_meeting_npc(
            first[1],
            random_source=first[2],
            id_source=first[3],
        )
        second_npc_id, _ = second[0].generate_meeting_npc(
            second[1],
            random_source=second[2],
            id_source=second[3],
        )
        self.assertEqual(first_npc_id, second_npc_id)
        self.assertTrue(first_npc_id.startswith("native_npc_"))

        first_parent_ids = first[0].get_parent_ids_for(first[1])
        second_parent_ids = second[0].get_parent_ids_for(second[1])
        first_child_id, _ = first[0]._create_family_child_birth(
            first_parent_ids["mother_id"],
            first_parent_ids["father_id"],
            birth_year=first[0].current_year,
            birth_month=first[0].current_month,
            birth_source="test_family_birth",
            random_source=first[2],
            id_source=first[3],
        )
        second_child_id, _ = second[0]._create_family_child_birth(
            second_parent_ids["mother_id"],
            second_parent_ids["father_id"],
            birth_year=second[0].current_year,
            birth_month=second[0].current_month,
            birth_source="test_family_birth",
            random_source=second[2],
            id_source=second[3],
        )

        self.assertEqual(first_child_id, second_child_id)
        self.assertTrue(first_child_id.startswith("native_family_child_"))
        self.assertEqual(serialize_world(first[0]), serialize_world(second[0]))
        self.assertEqual(first[2].snapshot(), second[2].snapshot())
        self.assertEqual(first[3].snapshot(), second[3].snapshot())

    def test_omitted_sources_preserve_legacy_random_and_uuid_paths(self):
        global_state = random.getstate()
        try:
            random.seed(410)
            world, player_id = setup_initial_world_from_character(
                build_creation_character()
            )
            self.assertRegex(
                player_id,
                re.compile(r"^startup_player_[0-9a-f]{8}$"),
            )
            result = world.simulate_advance_turn(player_id, 1)
            self.assertEqual(result["months_advanced"], 1)
        finally:
            random.setstate(global_state)

    def test_curses_free_boundaries_do_not_load_shell_modules(self):
        script = (
            "import sys; "
            "import game_setup; "
            "import actora_core; "
            "assert 'curses' not in sys.modules; "
            "assert 'main' not in sys.modules; "
            "assert 'wizard' not in sys.modules"
        )
        subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            cwd=".",
        )


if __name__ == "__main__":
    unittest.main()
