"""Focused regressions for the safe source-fix checkpoint."""

from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from browser_state_controller import BrowserStateController
from continuation_controller import ContinuationController
from event_log_controller import EventLogController
from mechanics import HUMAN_TRAIT_COUNT, HUMAN_TRAIT_POOL
from views.browser import build_record_summary_lines, filter_player_facing_records
from world import World


def create_human(
    world: World,
    actor_id: str,
    first_name: str,
    *,
    sex: str = "Male",
    birth_year: int = 1,
    randomize_stats: bool = False,
):
    return world.create_human_actor(
        actor_id=actor_id,
        species="Human",
        first_name=first_name,
        last_name="Test",
        sex=sex,
        gender=sex,
        birth_year=birth_year,
        birth_month=1,
        randomize_stats=randomize_stats,
    )


class GeneratedTraitContractTests(unittest.TestCase):
    def test_generated_parents_newborns_and_meeting_npcs_use_canonical_four_traits(
        self,
    ) -> None:
        previous_random_state = random.getstate()
        try:
            random.seed(20260718)
            world = World(start_year=30, start_month=1)
            mother = create_human(
                world,
                "mother",
                "Morgan",
                sex="Female",
                birth_year=3,
                randomize_stats=True,
            )
            father = create_human(
                world,
                "father",
                "Frank",
                birth_year=1,
                randomize_stats=True,
            )
            player = create_human(
                world,
                "player",
                "Pat",
                birth_year=10,
            )
            world.set_focused_actor("player")

            _, newborn = world._create_family_child_birth(
                "mother",
                "father",
                birth_year=world.current_year,
                birth_month=world.current_month,
                birth_source="test",
            )
            _, meeting_npc = world.generate_meeting_npc(
                "player",
                culture_group="American",
            )
        finally:
            random.setstate(previous_random_state)

        canonical_traits = set(HUMAN_TRAIT_POOL)
        self.assertEqual(HUMAN_TRAIT_COUNT, 4)
        self.assertEqual(len(canonical_traits), 12)
        for generated_human in (mother, father, newborn, meeting_npc):
            with self.subTest(name=generated_human.get_full_name()):
                self.assertEqual(len(generated_human.traits), HUMAN_TRAIT_COUNT)
                self.assertEqual(
                    len(set(generated_human.traits)),
                    HUMAN_TRAIT_COUNT,
                )
                self.assertLessEqual(set(generated_human.traits), canonical_traits)


class EventCooldownTests(unittest.TestCase):
    def test_monthly_event_cooldown_survives_separate_advancement_calls(
        self,
    ) -> None:
        world = World(start_year=3, start_month=1)
        player = create_human(world, "player", "Player", birth_year=1)
        player.traits = [
            "Curious",
            "Social",
            "Impulsive",
            "Empathetic",
        ]
        world.set_focused_actor("player")
        observed_recent_ids: list[list[str]] = []

        def choose_event(
            _lifecycle,
            year,
            month,
            *,
            recent_event_ids,
            **_kwargs,
        ):
            observed_recent_ids.append(list(recent_event_ids))
            if "repeatable_event" in recent_event_ids:
                return None
            return {
                "event_id": "repeatable_event",
                "text": "A test event happened.",
                "outcome": {"stat_changes": {}},
                "tags": ["test"],
                "year": year,
                "month": month,
            }

        with patch(
            "world.get_human_monthly_event_from_lifecycle",
            side_effect=choose_event,
        ):
            first = world.simulate_advance_turn("player", 1)
            second = world.simulate_advance_turn("player", 1)

        self.assertEqual(len(first["events"]), 1)
        self.assertEqual(second["events"], [])
        self.assertEqual(observed_recent_ids, [[], ["repeatable_event"]])
        self.assertEqual(
            world.recent_event_ids_by_actor,
            {"player": ["repeatable_event"]},
        )

    def test_family_event_ids_do_not_displace_monthly_event_cooldown(
        self,
    ) -> None:
        world = World(start_year=3, start_month=1)
        player = create_human(world, "player", "Player", birth_year=1)
        player.traits = [
            "Curious",
            "Social",
            "Impulsive",
            "Empathetic",
        ]
        world.set_focused_actor("player")
        world.recent_event_ids_by_actor["player"] = [
            "one",
            "two",
            "three",
        ]
        family_result = {
            "surfaced_events": [
                {
                    "event_id": "family_sibling_birth",
                    "text": "A sibling was born.",
                    "outcome": {"stat_changes": {}},
                    "tags": ["family"],
                    "year": 3,
                    "month": 2,
                }
            ]
        }

        with (
            patch.object(
                world,
                "resolve_monthly_family_events",
                return_value=family_result,
            ),
            patch(
                "world.get_human_monthly_event_from_lifecycle",
                return_value=None,
            ),
        ):
            world.simulate_advance_turn("player", 1)

        self.assertEqual(
            world.recent_event_ids_by_actor["player"],
            ["one", "two", "three"],
        )


class RelationshipFacetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.world = World(start_year=40, start_month=1)
        create_human(self.world, "player", "Player", birth_year=10)
        self.world.set_focused_actor("player")

    def add_social_person(
        self,
        actor_id: str,
        first_name: str,
        closeness: int,
        *,
        status: str = "active",
    ) -> None:
        create_human(self.world, actor_id, first_name, birth_year=10)
        self.world.create_social_link_pair(
            "player",
            actor_id,
            closeness=closeness,
            status=status,
        )

    def test_friends_filter_excludes_acquaintances_and_former_ties_render_as_past(
        self,
    ) -> None:
        self.add_social_person("acquaintance", "Acquaintance", 15)
        self.add_social_person("friend", "Friend", 45)
        self.add_social_person("close_friend", "Close", 75)
        self.add_social_person("former", "Former", 48, status="former")

        friend_entries = self.world.get_relationship_entries_for(
            "player",
            filter_mode="friends",
        )
        self.assertEqual(
            {entry["actor_id"] for entry in friend_entries},
            {"friend", "close_friend"},
        )

        former_entries = self.world.get_relationship_entries_for(
            "player",
            filter_mode="former",
        )
        self.assertEqual(len(former_entries), 1)
        self.assertEqual(former_entries[0]["relationship_label"], "Past")
        self.assertEqual(former_entries[0]["social_status"], "former")

    def test_filtered_social_detail_keeps_social_facet_and_family_context(
        self,
    ) -> None:
        create_human(self.world, "father", "Aaron", birth_year=-20)
        self.world.add_link_pair(
            source_id="player",
            target_id="father",
            forward_type="family",
            forward_role="father",
            reverse_type="family",
            reverse_role="child",
        )
        self.world.create_social_link_pair(
            "player",
            "father",
            closeness=65,
            status="active",
        )

        browser_state = self.world.get_relationship_browser_data_for(
            "player",
            filter_mode="friends",
        )
        self.assertEqual(len(browser_state["entries"]), 1)
        summary = browser_state["selected_detail"]["summary"]
        self.assertEqual(summary["link_type"], "social")
        self.assertEqual(summary["relationship_label"], "Friend")
        self.assertEqual(summary["closeness"], 65)
        self.assertEqual(summary["family_relationship_label"], "Father")

        class BrowserApp:
            def __init__(self, world: World):
                self.world = world
                self.rel_filter_index = 0
                self.rel_browser_search_text = ""
                self.lineage_selection = 0
                self.selected_lineage_actor_id = "father"

            def get_focused_actor_id(self):
                return self.world.get_focused_actor_id()

        controller = BrowserStateController(
            lineage_record_limit=5,
            lineage_filter_labels={},
            rel_filter_options=["friends"],
        )
        controller_state = controller.get_relationship_browser_state(
            BrowserApp(self.world)
        )
        controller_summary = controller_state["selected_detail"]["summary"]
        self.assertEqual(controller_summary["link_type"], "social")
        self.assertEqual(controller_summary["family_relationship_label"], "Father")


class ContinuationRecordTests(unittest.TestCase):
    def build_dead_focus_world(self) -> World:
        world = World(start_year=80, start_month=4)
        create_human(world, "original", "Original", birth_year=1)
        create_human(
            world,
            "successor",
            "Successor",
            sex="Female",
            birth_year=50,
        )
        world.add_link_pair(
            source_id="original",
            target_id="successor",
            forward_type="family",
            forward_role="child",
            reverse_type="family",
            reverse_role="father",
        )
        world.set_focused_actor("original")
        world.mark_actor_dead("original", reason="Test")
        return world

    def test_successful_handoff_writes_one_structural_continuation_record(
        self,
    ) -> None:
        world = self.build_dead_focus_world()
        before_count = len(world.records)

        world.set_focused_actor("successor")
        with self.assertRaisesRegex(ValueError, "does not match current world focus"):
            world.handoff_focus_to_continuation("original", "successor")
        self.assertEqual(len(world.records), before_count)
        world.set_focused_actor("original")

        world.handoff_focus_to_continuation("original", "successor")

        new_records = world.records[before_count:]
        self.assertEqual(len(new_records), 1)
        continuation_record = new_records[0]
        self.assertEqual(continuation_record["record_type"], "continuation")
        self.assertEqual(
            continuation_record["actor_ids"],
            ["original", "successor"],
        )
        self.assertEqual(
            continuation_record["tags"],
            ["continuation", "structural_transition"],
        )
        self.assertEqual(
            continuation_record["metadata"],
            {
                "from_actor_id": "original",
                "successor_actor_id": "successor",
                "entry_method": "World.handoff_focus_to_continuation",
            },
        )
        with self.assertRaisesRegex(ValueError, "already handed off"):
            world.handoff_focus_to_continuation("original", "successor")
        world.set_focused_actor("original")
        with self.assertRaisesRegex(ValueError, "already handed off"):
            world.handoff_focus_to_continuation("original", "successor")
        self.assertEqual(world.records[before_count:], [continuation_record])

    def test_continuation_record_is_hidden_from_recent_record_surfaces(
        self,
    ) -> None:
        world = self.build_dead_focus_world()
        world.add_record(
            record_type="event",
            scope="actor",
            text="A visible record.",
            year=world.current_year,
            month=world.current_month,
            actor_ids=["successor"],
        )
        world.handoff_focus_to_continuation("original", "successor")
        successor_records = world.get_actor_records("successor")

        self.assertEqual(
            [record["text"] for record in filter_player_facing_records(successor_records)],
            ["A visible record."],
        )
        self.assertEqual(
            build_record_summary_lines(successor_records),
            [f"[{world.current_year:04d}-{world.current_month:02d}] A visible record."],
        )

    def test_continuation_keeps_year_headers_unique_and_record_out_of_history(
        self,
    ) -> None:
        world = self.build_dead_focus_world()

        class ContinuationApp:
            def __init__(self, current_world: World):
                self.world = current_world
                self.player_id = "original"
                self.continuation_selection = 0
                self.selected_continuation_actor_id = None
                self.last_logged_year = current_world.current_year
                self.event_log = [
                    {
                        "kind": "year_header",
                        "text": f"Year {current_world.current_year}",
                        "year": current_world.current_year,
                        "month": None,
                        "record_type": None,
                    }
                ]
                self.pending_choice = None
                self.remaining_skip_months = 0
                self.identity_popup_suppressed_for_resumed_adult = False
                self.gender_choice_offered = False
                self.sexuality_choice_offered = False
                self.gender_choice_age = 12
                self.sexuality_choice_age = 14
                self.meeting_event_last_total_months = 0
                self.screen_name = "continuation"
                self.quit_confirmation_active = False
                self.last_message = ""
                self.running = True

            def get_focused_actor_id(self):
                return self.world.get_focused_actor_id() or self.player_id

            def get_focused_actor(self):
                return self.world.get_actor(self.get_focused_actor_id())

        app = ContinuationApp(world)
        record_count_before = len(world.records)
        ContinuationController().choose_continuation(app)
        new_records = world.records[record_count_before:]

        self.assertEqual(app.last_logged_year, world.current_year)
        self.assertEqual(
            [record["record_type"] for record in new_records],
            ["continuation"],
        )

        EventLogController().append_turn(
            app,
            {
                "months_advanced": 1,
                "events": [
                    {
                        "text": "The new life continued.",
                        "year": world.current_year,
                        "month": world.current_month,
                    }
                ],
            },
            months_to_advance=1,
            new_records=new_records,
        )

        year_headers = [
            entry["year"]
            for entry in app.event_log
            if entry["kind"] == "year_header"
        ]
        self.assertEqual(year_headers, [world.current_year])
        self.assertNotIn(
            new_records[0]["text"],
            [entry["text"] for entry in app.event_log],
        )


if __name__ == "__main__":
    unittest.main()
