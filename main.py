import curses
import random
import time
from uuid import uuid4


from events import get_meeting_event_for_player
from identity import prepare_parent_identity_context, generate_parent_identity_from_context
from mechanics import (
    EXERCISE_SUBTYPES,
    EXERCISE_TIME_COST,
    HANG_OUT_TIME_COST,
    READ_SUBTYPES,
    READ_TIME_COST,
    REST_SUBTYPES,
    REST_TIME_COST,
    SKIP_MONTH_PRESETS,
    get_monthly_free_hours,
)
from views.browser import (
    HIDDEN_PLAYER_RECORD_TYPES,
    build_lineage_row,
    build_record_summary_lines,
    filter_player_facing_records,
    get_social_tier_label,
)
from views.history import (
    build_event_log_entry,
    build_live_feed_lines,
    expand_render_lines,
    format_history_entry,
)
from views.shell import build_death_lines, build_screen_chrome
from screens.browser import BrowserScreen
from screens.history import HistoryScreen
from screens.lineage import LineageScreen
from screens.profile import ProfileScreen
from screens.relationships import RelationshipBrowserScreen
from views.profile import build_person_card_lines
from ui import (
    center_text,
    draw_box,
    draw_panel_text,
    draw_text_block,
    draw_truncated_block,
    draw_vertical_divider,
    get_content_bounds,
    get_scroll_window,
    split_centered_columns,
    truncate_for_width,
    wrap_text_line,
)
from wizard import (
    CREATION_STAT_LABELS,
    CREATION_STAT_ORDER,
    CreationWizard,
    build_randomized_starting_stats,
    format_stat_change_summary,
    normalize_creation_stats,
)
from world import (
    DEFAULT_CITY_ID,
    DEFAULT_COUNTRY_ID,
    WORLD_GEOGRAPHY,
    WORLD_GEOGRAPHY_BY_COUNTRY_ID,
    World,
)

LINEAGE_RECORD_LIMIT = 6
INSPECT_RECORD_LIMIT = 5
LINEAGE_FILTER_LABELS = {
    "all": "All",
    "living": "Living",
    "dead": "Dead",
}
REL_FILTER_OPTIONS = ["all", "family", "friends", "former", "living", "dead"]
REL_FILTER_LABELS = {
    "all": "All",
    "family": "Family",
    "friends": "Friends",
    "former": "Past",
    "living": "Living",
    "dead": "Dead",
}
PROFILE_CATEGORIES = [
    "identity", "appearance", "stats", "attributes", "traits",
    "mood", "needs", "skills", "location", "relationships",
]
MAIN_LEFT_SECTION_KEYS = ("identity", "location", "statistics", "relationships")
BACK_KEYS = {
    curses.KEY_BACKSPACE, 127, 8,
}
MAIN_IDLE_MESSAGE = "Living your life."
ADVANCE_THROTTLE_SECONDS = 0.2
MEETING_EVENT_COOLDOWN_MONTHS = 18
GENDER_IDENTITY_OPTIONS = ["Male", "Female", "Non-binary", "Agender", "Genderfluid", "Other"]
SEXUALITY_OPTION_LABELS = [
    ("Opposite gender (Heterosexual)", "Heterosexual"),
    ("Same gender (Homosexual)", "Homosexual"),
    ("Both genders (Bisexual)", "Bisexual"),
    ("No one in particular (Asexual)", "Asexual"),
    ("People regardless of gender (Pansexual)", "Pansexual"),
    ("It is hard to define (Queer)", "Queer"),
]


def generate_startup_actor_id(role):
    """Builds one narrow startup actor id without hardcoded singleton values."""
    return f"startup_{role}_{uuid4().hex[:8]}"


def build_snapshot_sections(snapshot_data):
    """Builds shell-owned snapshot sections from structured actor snapshot data."""
    identity = snapshot_data["identity"]
    time_state = snapshot_data["time"]
    location = snapshot_data["location"]
    statistics = snapshot_data["statistics"]
    relationships = snapshot_data["relationships"]

    section_pairs = [
        (
            "identity",
            "Identity",
            [
                f"Name: {identity['full_name']}",
                f"Species: {identity['species']}",
                f"Sex: {identity['sex']}",
                f"Gender: {identity['gender']}",
                f"Age: {identity['age']}",
                f"Life Stage: {identity['life_stage']}",
            ],
        ),
        (
            "time",
            "Time",
            [
                f"Sim Date: Year {time_state['year']}, Month {time_state['month']}",
            ],
        ),
        (
            "location",
            "Location",
            [
                f"Planet: {location['world_body_name']}",
                f"City: {location['current_place_name']}",
                f"Country: {location['jurisdiction_place_name']}",
            ],
        ),
        (
            "statistics",
            "Statistics",
            [
                f"Health: {statistics['health']}",
                f"Happiness: {statistics['happiness']}",
                f"Intelligence: {statistics['intelligence']}",
                f"Money: ${statistics['money']}",
            ],
        ),
        (
            "relationships",
            "Relationships",
            [f"  {entry['name']} · {entry['label']}" for entry in relationships] or ["  No living family."],
        ),
    ]
    return [
        {"key": key, "title": title, "lines": lines}
        for key, title, lines in section_pairs
    ]


class ActoraTUI:
    """Small actor-first curses shell layered on top of the existing world seams."""

    # Canonical shell geometry — change these when header/footer layout changes.
    HEADER_ROWS = 7   # rows 0–(HEADER_ROWS-1) are occupied by the header
    FOOTER_ROWS = 2   # rows (height-FOOTER_ROWS)..(height-1) are occupied by the footer
    # Browser adds 2 chrome rows (tab bar + separator) above its sub-screen body.
    BROWSER_CHROME_ROWS = 2

    def __init__(self, world, player_id):
        self.world = world
        self.player_id = player_id
        self.screen_name = "main"
        self.running = True
        self.lineage_selection = 0
        self.continuation_selection = 0
        self.skip_selection = 0
        self.skip_custom_value = ""
        self.selected_lineage_actor_id = None
        self.lineage_filter_mode = "all"
        self.lineage_search_text = ""
        self.lineage_search_active = False
        self.lineage_screen = LineageScreen(
            LINEAGE_FILTER_LABELS,
            BACK_KEYS,
            ADVANCE_THROTTLE_SECONDS,
            MAIN_IDLE_MESSAGE,
        )
        self.main_left_scroll = 0
        self.profile_scroll = 0
        self.profile_selected_row = 0
        self.profile_popup_open = False
        self.profile_popup_category = None
        self.profile_popup_scroll = 0
        self._profile_content_width = 88
        self.profile_screen = ProfileScreen(
            PROFILE_CATEGORIES,
            BACK_KEYS,
            ADVANCE_THROTTLE_SECONDS,
            MAIN_IDLE_MESSAGE,
        )
        self.history_scroll = 0
        self.history_search_active = False
        self.history_search_value = ""
        self.history_screen = HistoryScreen(
            BACK_KEYS,
            ADVANCE_THROTTLE_SECONDS,
            MAIN_IDLE_MESSAGE,
        )
        self.selected_continuation_actor_id = None
        self.last_message = MAIN_IDLE_MESSAGE
        self.event_log = []
        self.last_logged_year = 0
        self.last_advance_time = 0.0
        self.pending_choice = None
        self.remaining_skip_months = 0
        self.quit_confirmation_active = False
        self.quit_from_options = False
        self.menu_popup_active = False
        self.menu_selection = 0  # 0=Browser, 1=Actions, 2=Profile
        self.options_popup_active = False
        self.options_selection = 0
        self.gender_choice_offered = False
        self.sexuality_choice_offered = False
        self.identity_popup_suppressed_for_resumed_adult = False
        self.gender_choice_age = random.randint(12, 15)
        self.sexuality_choice_age = random.randint(14, 17)
        self.meeting_event_last_total_months = 0
        self.rel_browser_focus = "filters"
        self.rel_filter_index = 0
        self.rel_browser_search_active = False
        self.rel_browser_search_text = ""
        self.relationship_browser_screen = RelationshipBrowserScreen(
            REL_FILTER_OPTIONS,
            REL_FILTER_LABELS,
            BACK_KEYS,
            ADVANCE_THROTTLE_SECONDS,
            MAIN_IDLE_MESSAGE,
        )
        self.browser_tab = "relationships"
        self.browser_screen = BrowserScreen()
        self.active_actions = []
        self.hang_out_actor_ids = []
        self.personal_subtype_options = []
        self.actions_focus = "categories"
        self.actions_category_index = 0
        self.actions_action_index = 0

    def get_focused_actor_id(self):
        return self.world.get_focused_actor_id() or self.player_id

    def get_focused_actor(self):
        return self.world.get_actor(self.get_focused_actor_id())

    def get_snapshot_data(self):
        focused_actor_id = self.get_focused_actor_id()
        focused_actor = self.world.get_actor(focused_actor_id)
        if focused_actor is None:
            return {}
        return focused_actor.get_snapshot_data(
            self.world.current_year,
            self.world.current_month,
            self.world,
            focused_actor_id,
        )

    def sync_focus_state(self):
        """Applies shell-level dead-focus flow selection before rendering."""
        focused_actor = self.get_focused_actor()
        if focused_actor is None or focused_actor.is_alive():
            if self.screen_name in {"death_ack", "continuation", "continuation_detail"}:
                self.screen_name = "main"
            return

        if self.screen_name not in {"death_ack", "continuation", "continuation_detail"}:
            self.screen_name = "death_ack"

    def get_lineage_browser_state(self):
        browser_state = self.world.get_lineage_browser_data_for(
            self.get_focused_actor_id(),
            filter_mode=self.lineage_filter_mode,
            search_text=self.lineage_search_text,
            recent_record_limit=LINEAGE_RECORD_LIMIT,
        )

        entries = browser_state["entries"]
        if not entries:
            self.lineage_selection = 0
            self.selected_lineage_actor_id = None
            browser_state["selected_detail"] = None
            return browser_state

        if self.selected_lineage_actor_id is not None:
            matching_index = next(
                (
                    index
                    for index, entry in enumerate(entries)
                    if entry["actor_id"] == self.selected_lineage_actor_id
                ),
                None,
            )
            if matching_index is not None:
                self.lineage_selection = matching_index
            else:
                self.lineage_selection = 0
                self.selected_lineage_actor_id = entries[0]["actor_id"]
        else:
            self.lineage_selection = max(0, min(self.lineage_selection, len(entries) - 1))
            self.selected_lineage_actor_id = entries[self.lineage_selection]["actor_id"]

        browser_state["selected_detail"] = self.world.get_lineage_detail_for(
            self.get_focused_actor_id(),
            self.selected_lineage_actor_id,
            recent_record_limit=LINEAGE_RECORD_LIMIT,
        )
        return browser_state

    def get_lineage_entries(self):
        return self.get_lineage_browser_state()["entries"]

    def get_lineage_detail(self):
        return self.get_lineage_browser_state()["selected_detail"]

    def set_lineage_filter_mode(self, filter_mode):
        self.lineage_filter_mode = filter_mode
        self.lineage_selection = 0
        self.selected_lineage_actor_id = None
        self.last_message = f"Lineage filter: {LINEAGE_FILTER_LABELS[filter_mode]}."

    def clear_lineage_search(self):
        if self.lineage_search_text:
            self.lineage_search_text = ""
            self.lineage_selection = 0
            self.selected_lineage_actor_id = None
            self.last_message = "Lineage search cleared."

    def get_lineage_search_status(self):
        if self.lineage_search_active:
            return f"Search: {self.lineage_search_text}_"
        if self.lineage_search_text:
            return f"Search: {self.lineage_search_text}"
        return "Search: off"

    def get_rel_browser_search_status(self):
        """Returns the search status line for the relationship browser, or None."""
        if self.rel_browser_search_active:
            return f"Search: {self.rel_browser_search_text}_"
        if self.rel_browser_search_text:
            return f"Search: {self.rel_browser_search_text}"
        return None

    def get_relationship_browser_state(self):
        focused_actor_id = self.get_focused_actor_id()
        filter_mode = REL_FILTER_OPTIONS[self.rel_filter_index]
        browser_state = self.world.get_relationship_browser_data_for(
            focused_actor_id,
            filter_mode=filter_mode,
            search_text=self.rel_browser_search_text,
            recent_record_limit=LINEAGE_RECORD_LIMIT,
        )
        entries = browser_state["entries"]
        if not entries:
            self.lineage_selection = 0
            self.selected_lineage_actor_id = None
            browser_state["selected_detail"] = None
            return browser_state

        if self.selected_lineage_actor_id is not None:
            matching_index = next(
                (
                    index
                    for index, entry in enumerate(entries)
                    if entry["actor_id"] == self.selected_lineage_actor_id
                ),
                None,
            )
            if matching_index is not None:
                self.lineage_selection = matching_index
            else:
                self.lineage_selection = 0
                self.selected_lineage_actor_id = entries[0]["actor_id"]
        else:
            self.lineage_selection = max(0, min(self.lineage_selection, len(entries) - 1))
            self.selected_lineage_actor_id = entries[self.lineage_selection]["actor_id"]

        browser_state["selected_detail"] = self.world.get_relationship_detail_for(
            focused_actor_id,
            self.selected_lineage_actor_id,
            recent_record_limit=LINEAGE_RECORD_LIMIT,
        )
        return browser_state

    def get_continuity_state(self):
        return self.world.build_continuity_state_for(self.get_focused_actor_id())

    def append_event_log_entry(self, kind, text, *, year=None, month=None, record_type=None):
        """Appends one event-log entry with normalized structure."""
        self.event_log.append(
            build_event_log_entry(
                kind,
                text,
                year=year,
                month=month,
                record_type=record_type,
            )
        )

    def append_event_log_turn(self, turn_result, months_to_advance, new_records, *, suppress_skip_marker=False):
        """Extends the event log from one completed advance."""
        actual_months_advanced = turn_result["months_advanced"]
        if actual_months_advanced <= 0:
            return

        if months_to_advance > 1 and not suppress_skip_marker:
            label = "Month" if months_to_advance == 1 else "Months"
            self.append_event_log_entry(
                "skip_marker",
                f"{months_to_advance} {label} Skipped",
            )

        visible_record_types = {"birth", "death"}
        merged_entries = []
        event_identity_keys = set()

        for sequence, structured_event in enumerate(turn_result["events"]):
            event_year = structured_event.get("year")
            event_month = structured_event.get("month")
            event_text = structured_event.get("text", "")
            event_key = (event_year, event_month, event_text)
            event_identity_keys.add(event_key)
            merged_entries.append(
                {
                    "sort_key": (
                        event_year if event_year is not None else -1,
                        event_month if event_month is not None else -1,
                        sequence,
                        0,
                    ),
                    "kind": "event",
                    "text": event_text,
                    "year": event_year,
                    "month": event_month,
                    "record_type": None,
                }
            )

        structural_sequence = len(merged_entries)
        for record in new_records:
            if record.get("record_type") in HIDDEN_PLAYER_RECORD_TYPES:
                continue
            if record.get("record_type") not in visible_record_types:
                continue
            if self.get_focused_actor_id() not in (record.get("actor_ids") or []):
                continue

            record_key = (
                record.get("year"),
                record.get("month"),
                record.get("text"),
            )
            if record_key in event_identity_keys:
                continue

            merged_entries.append(
                {
                    "sort_key": (
                        record.get("year") if record.get("year") is not None else -1,
                        record.get("month") if record.get("month") is not None else -1,
                        structural_sequence,
                        1,
                    ),
                    "kind": "event",
                    "text": record.get("text", ""),
                    "year": record.get("year"),
                    "month": record.get("month"),
                    "record_type": record.get("record_type"),
                }
            )
            structural_sequence += 1

        merged_entries.sort(key=lambda entry: entry["sort_key"])
        for entry in merged_entries:
            entry_year = entry.get("year")
            if entry_year is not None and entry_year > self.last_logged_year:
                for year in range(self.last_logged_year + 1, entry_year + 1):
                    self.append_event_log_entry(
                        "year_header",
                        f"Year {year}",
                        year=year,
                    )
                self.last_logged_year = entry_year

            self.append_event_log_entry(
                entry["kind"],
                entry["text"],
                year=entry.get("year"),
                month=entry.get("month"),
                record_type=entry.get("record_type"),
            )

    def maybe_offer_identity_choice(self):
        actor = self.get_focused_actor()
        if actor is None or not actor.is_alive():
            return False

        lifecycle = actor.get_lifecycle_state(self.world.current_year, self.world.current_month)
        age_years = lifecycle["age_years"]
        current_gender = actor.gender or "Other"

        if self.identity_popup_suppressed_for_resumed_adult:
            return False

        if age_years >= self.gender_choice_age and not self.gender_choice_offered:
            selected_index = (
                GENDER_IDENTITY_OPTIONS.index(current_gender)
                if current_gender in GENDER_IDENTITY_OPTIONS
                else 0
            )
            self.pending_choice = {
                "title": "A moment of self-reflection",
                "text": "As you grow, you find yourself thinking more about who you are.",
                "question": "Your gender identity feels like:",
                "options": list(GENDER_IDENTITY_OPTIONS),
                "selected_index": selected_index,
                "skippable": True,
                "choice_id": "gender_identity",
                "default_value": current_gender,
            }
            self.gender_choice_offered = True
            self.last_message = "A personal choice needs your attention."
            return True

        if age_years >= self.sexuality_choice_age and not self.sexuality_choice_offered:
            self.pending_choice = {
                "title": "A new kind of awareness",
                "text": "You have started noticing things about yourself you had not thought about before.",
                "question": "You feel attracted to:",
                "options": [label for label, _ in SEXUALITY_OPTION_LABELS],
                "selected_index": 0,
                "skippable": True,
                "choice_id": "sexuality",
                "default_value": None,
            }
            self.sexuality_choice_offered = True
            self.last_message = "A personal choice needs your attention."
            return True

        return False

    def maybe_offer_meeting_event(self):
        """Fires a meeting-event popup choice when conditions and cooldown allow."""
        actor = self.get_focused_actor()
        if actor is None or not actor.is_alive():
            return False

        lifecycle = actor.get_lifecycle_state(self.world.current_year, self.world.current_month)
        current_total_months = self.world.current_year * 12 + self.world.current_month
        if current_total_months - self.meeting_event_last_total_months < MEETING_EVENT_COOLDOWN_MONTHS:
            return False

        meeting_event = get_meeting_event_for_player(lifecycle)
        if meeting_event is None:
            return False

        self.meeting_event_last_total_months = current_total_months
        self.pending_choice = {
            "title": "Someone new",
            "text": meeting_event["text"],
            "question": "Do you want to introduce yourself?",
            "options": ["Introduce yourself", "Keep to yourself"],
            "selected_index": 0,
            "skippable": False,
            "choice_id": "meeting_npc",
        }
        self.last_message = "You notice someone nearby."
        return True

    def resolve_choice(self, choice_id, selected_value):
        actor = self.get_focused_actor()
        if actor is None:
            self.pending_choice = None
            return

        if choice_id == "gender_identity":
            old_gender = actor.gender
            actor.gender = selected_value
            if selected_value != old_gender:
                self.append_event_log_entry(
                    "event",
                    f"You now identify as {selected_value}.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
            else:
                self.append_event_log_entry(
                    "event",
                    "You reflected on your identity.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
        elif choice_id == "sexuality":
            if selected_value is not None:
                actor.sexuality = selected_value
                self.append_event_log_entry(
                    "event",
                    f"You identify as {selected_value}.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
            else:
                self.append_event_log_entry(
                    "event",
                    "You are still figuring things out.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
        elif choice_id == "meeting_npc":
            if selected_value == "Introduce yourself":
                focused_actor_id = self.get_focused_actor_id()
                npc_actor_id, npc = self.world.generate_meeting_npc(focused_actor_id)
                self.world.create_social_link_pair(
                    focused_actor_id,
                    npc_actor_id,
                    closeness=15,
                    status="active",
                    closeness_history_months=0,
                )
                self.append_event_log_entry(
                    "event",
                    f"You introduced yourself to {npc.get_full_name()}.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
                self.last_message = f"You met {npc.get_full_name()}."
            else:
                self.append_event_log_entry(
                    "event",
                    "You decided to keep to yourself.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
                self.last_message = "You kept to yourself."

        elif choice_id == "select_hang_out_target":
            if selected_value is not None:
                options_list = (self.pending_choice or {}).get("options", [])
                try:
                    selected_idx = options_list.index(selected_value)
                    target_actor_id = self.hang_out_actor_ids[selected_idx]
                except (ValueError, IndexError):
                    self.pending_choice = None
                    return
                already_queued = any(
                    a["action_type"] == "spend_time" and a["target_actor_id"] == target_actor_id
                    for a in self.active_actions
                )
                if not already_queued:
                    focused_actor = self.world.get_focused_actor()
                    free_hours = get_monthly_free_hours(focused_actor)
                    used_hours = sum(a.get("time_cost", 0) for a in self.active_actions)
                    action_cost = HANG_OUT_TIME_COST
                    if used_hours + action_cost > free_hours:
                        self.last_message = "Not enough free time. (" + str(int(free_hours - used_hours)) + "h left)"
                        self.pending_choice = None
                        return
                    target_actor = self.world.get_actor(target_actor_id)
                    target_name = target_actor.get_full_name() if target_actor else "Someone"
                    self.active_actions.append({
                        "action_type": "spend_time",
                        "target_actor_id": target_actor_id,
                        "label": f"Spend time with {target_name}",
                        "time_cost": HANG_OUT_TIME_COST,
                    })
                    self.last_message = f"Queued: Spend time with {target_name}."
                else:
                    self.last_message = "Already queued to hang out with them."
            else:
                self.last_message = "Cancelled."
            self.pending_choice = None
            return
        elif choice_id in ("select_exercise_subtype", "select_read_subtype", "select_rest_subtype"):
            if selected_value is not None:
                options_list = (self.pending_choice or {}).get("options", [])
                try:
                    selected_idx = options_list.index(selected_value)
                    subtype = self.personal_subtype_options[selected_idx]
                except (ValueError, IndexError):
                    self.pending_choice = None
                    self.personal_subtype_options = []
                    return
                focused_actor = self.world.get_focused_actor()
                free_hours = get_monthly_free_hours(focused_actor)
                used_hours = sum(a.get("time_cost", 0) for a in self.active_actions)
                if used_hours + subtype["time_cost"] > free_hours:
                    self.last_message = "Not enough free time. (" + str(int(free_hours - used_hours)) + "h left)"
                    self.pending_choice = None
                    self.personal_subtype_options = []
                    return
                self.active_actions.append({
                    "action_type": "personal",
                    "subtype_id": subtype["id"],
                    "label": subtype["label"],
                    "time_cost": subtype["time_cost"],
                    "stat_changes": subtype["stat_changes"],
                })
                self.last_message = f"Queued: {subtype['label']}."
            else:
                self.last_message = "Cancelled."
            self.pending_choice = None
            self.personal_subtype_options = []
            return

        self.pending_choice = None
        remaining = self.remaining_skip_months
        self.remaining_skip_months = 0
        if remaining > 0:
            self.advance_time(remaining, is_resume=True)

    def open_history(self):
        self.screen_name = "history"
        self.history_scroll = 10**9
        self.history_search_active = False
        self.history_search_value = ""
        self.last_message = "Browsing event history."

    def open_profile(self):
        self.screen_name = "profile"
        self.profile_selected_row = 0
        self.profile_popup_open = False
        self.profile_popup_category = None
        self.profile_popup_scroll = 0
        self.last_message = "Viewing full profile."

    def get_history_lines(self, width):
        """Builds the logical full-screen history line list."""
        if not self.event_log:
            return ["No events yet."]
        lines = []
        for entry in self.event_log:
            if entry["kind"] == "year_header":
                if lines:
                    lines.append("")
                lines.append(format_history_entry(entry, width))
                lines.append("")
            else:
                lines.append(format_history_entry(entry, width))
        return lines

    def get_history_search_status(self):
        if not self.history_search_active:
            return None
        typed_year = self.history_search_value or ""
        return f"Jump to year: {typed_year}_"

    def jump_history_to_year(self, typed_year):
        clamped_year = max(1, min(typed_year, self.world.current_year))
        year_header_index = None
        fallback_index = None
        for index, entry in enumerate(self.event_log):
            if entry["kind"] != "year_header":
                continue
            fallback_index = index
            if entry["year"] >= clamped_year:
                year_header_index = index
                break

        if year_header_index is None:
            year_header_index = fallback_index
        if year_header_index is None:
            self.history_scroll = 0
            self.last_message = "No history entries are available yet."
            return

        history_width = getattr(self, "_history_content_width", 80)
        self.history_scroll = len(
            expand_render_lines(self.get_history_lines(history_width)[:year_header_index], history_width)
        )
        target_year = self.event_log[year_header_index]["year"]
        self.last_message = f"Jumped to Year {target_year}."

    def scroll_history_to_bottom(self):
        """Pins history view to the latest available entry."""
        self.history_scroll = 10**9

    @property
    def history_body_height(self):
        return getattr(self, "_history_body_height", 0)

    def advance_time(self, months_to_advance, *, is_resume=False):
        """Advances time using the existing world-owned simulation seam."""
        aggregated_turn_result = {
            "months_advanced": 0,
            "events": [],
            "focused_actor_alive": True,
            "continuity_state": None,
        }
        new_records = []
        focused_actor_id = self.get_focused_actor_id()

        spend_time_actions = [a for a in self.active_actions if a["action_type"] == "spend_time"]
        personal_actions_queued = [a for a in self.active_actions if a["action_type"] == "personal"]
        shared_actor_ids = {a["target_actor_id"] for a in spend_time_actions}

        first_month = True
        for _ in range(months_to_advance):
            prior_record_count = len(self.world.records)
            month_turn_result = self.world.simulate_advance_turn(self.player_id, 1)
            new_records_this_month = self.world.records[prior_record_count:]
            new_records.extend(new_records_this_month)
            aggregated_turn_result["months_advanced"] += month_turn_result["months_advanced"]
            aggregated_turn_result["events"].extend(month_turn_result["events"])
            aggregated_turn_result["focused_actor_alive"] = month_turn_result["focused_actor_alive"]
            aggregated_turn_result["continuity_state"] = month_turn_result["continuity_state"]

            if first_month:
                if month_turn_result.get("focused_actor_alive", True):
                    for action in spend_time_actions:
                        event = self.world.spend_time_with_actor(
                            focused_actor_id,
                            action["target_actor_id"],
                        )
                        if event is not None:
                            aggregated_turn_result["events"].append(event)

                    for action in personal_actions_queued:
                        event = self.world.resolve_personal_action(focused_actor_id, action)
                        if event is not None:
                            aggregated_turn_result["events"].append(event)

                self.active_actions = [
                    a for a in self.active_actions if a["action_type"] not in ("spend_time", "personal")
                ]

            for record in new_records_this_month:
                if record.get("record_type") != "death":
                    continue
                for dead_actor_id in record.get("actor_ids", []):
                    if dead_actor_id == focused_actor_id:
                        continue
                    event = self.world.resolve_social_death_impact(focused_actor_id, dead_actor_id)
                    if event is not None:
                        aggregated_turn_result["events"].append(event)

            if month_turn_result.get("focused_actor_alive", True):
                month_shared = shared_actor_ids if first_month else set()
                drift_events = self.world.apply_social_link_decay(focused_actor_id, month_shared)
                for drift in drift_events:
                    self.append_event_log_entry(
                        "event",
                        drift["text"],
                        year=drift["year"],
                        month=drift["month"],
                    )

            first_month = False

            if month_turn_result["months_advanced"] <= 0 or not month_turn_result["focused_actor_alive"]:
                break
            if self.maybe_offer_identity_choice():
                remaining = months_to_advance - aggregated_turn_result["months_advanced"]
                if remaining > 0:
                    self.remaining_skip_months = remaining
                break
            if self.maybe_offer_meeting_event():
                remaining = months_to_advance - aggregated_turn_result["months_advanced"]
                if remaining > 0:
                    self.remaining_skip_months = remaining
                break

        self.append_event_log_turn(aggregated_turn_result, months_to_advance, new_records, suppress_skip_marker=is_resume)
        actual_months_advanced = aggregated_turn_result["months_advanced"]
        if actual_months_advanced == 1:
            self.last_message = "Advanced 1 month."
        elif actual_months_advanced != months_to_advance:
            if self.pending_choice is not None:
                self.last_message = "A personal choice needs your attention."
            else:
                self.last_message = f"Advanced {actual_months_advanced} of {months_to_advance} months before death."
        else:
            self.last_message = f"Advanced {actual_months_advanced} months."
        if aggregated_turn_result["continuity_state"] is not None and not aggregated_turn_result["focused_actor_alive"]:
            self.screen_name = "death_ack"

    def advance_one_month(self):
        self.advance_time(1)

    def open_skip_time(self):
        self.skip_selection = 0
        self.skip_custom_value = ""
        self.screen_name = "skip_time"
        self.last_message = "Choose how far ahead to jump."

    def get_selected_skip_months(self):
        return SKIP_MONTH_PRESETS[self.skip_selection]

    def get_custom_skip_months(self):
        if not self.skip_custom_value:
            return None
        custom_months = int(self.skip_custom_value)
        if custom_months <= 0:
            return None
        return custom_months

    def confirm_skip_selection(self):
        custom = self.get_custom_skip_months()
        if self.skip_custom_value and custom is None:
            # Custom value present but invalid (e.g. "0") — reject, don't silently fall back
            self.last_message = "Enter a number greater than 0."
            return
        months_to_advance = custom or self.get_selected_skip_months()
        self.screen_name = "main"
        self.advance_time(months_to_advance)

    def open_lineage(self):
        self.lineage_selection = 0
        self.selected_lineage_actor_id = None
        self.lineage_search_active = False
        self.screen_name = "lineage"
        self.last_message = "Browsing lineage archive."

    def open_relationship_browser(self):
        self.lineage_selection = 0
        self.selected_lineage_actor_id = None
        self.rel_browser_focus = "filters"
        self.rel_filter_index = 0
        self.rel_browser_search_active = False
        self.rel_browser_search_text = ""
        self.screen_name = "relationship_browser"
        self.last_message = "Browsing relationships."

    def _open_menu_selection(self):
        """Opens the screen selected in the menu popup."""
        self.menu_popup_active = False
        if self.menu_selection == 0:
            self.open_browser("relationships")
        elif self.menu_selection == 1:
            self.open_actions()
        elif self.menu_selection == 2:
            self.open_profile()

    def _open_options_selection(self):
        if self.options_selection == 0:
            self.options_popup_active = False
            self.quit_confirmation_active = True
            self.quit_from_options = True
        # Items 1 and 2 (Help, Settings) are not yet implemented — do nothing

    def open_browser(self, tab="relationships"):
        """Opens the unified Browser screen on the specified tab."""
        self.browser_tab = tab
        if tab == "relationships":
            self.lineage_selection = 0
            self.selected_lineage_actor_id = None
            self.rel_browser_focus = "filters"
            self.rel_filter_index = 0
            self.rel_browser_search_active = False
            self.rel_browser_search_text = ""
            self.last_message = "Browsing relationships."
        else:
            self.history_scroll = 10**9
            self.history_search_active = False
            self.history_search_value = ""
            self.last_message = "Browsing event history."
        self.screen_name = "browser"

    def open_actions(self):
        """Opens the Actions screen."""
        self.screen_name = "actions"
        self.actions_focus = "categories"
        self.actions_category_index = 0
        self.actions_action_index = 0
        self.last_message = "Actions."

    def open_hang_out_select(self):
        """Opens the hang out overlay to select a friend to spend time with."""
        focused_actor_id = self.get_focused_actor_id()
        social_links = self.world.get_links(source_id=focused_actor_id, link_type="social")
        active_links = [l for l in social_links if l.get("metadata", {}).get("status") == "active"]
        if not active_links:
            self.last_message = "No active social connections are available for Hang Out yet."
            return

        options = []
        self.hang_out_actor_ids = []
        for link in active_links:
            target_id = link.get("target_id")
            target_actor = self.world.get_actor(target_id)
            if target_actor is None:
                continue
            meta = link.get("metadata", {})
            closeness = meta.get("closeness", 0)
            tier = get_social_tier_label(closeness)
            already_queued = any(
                a["action_type"] == "spend_time" and a["target_actor_id"] == target_id
                for a in self.active_actions
            )
            label = f"{target_actor.get_full_name()} · {tier}"
            if already_queued:
                label += " (queued)"
            options.append(label)
            self.hang_out_actor_ids.append(target_id)

        if not options:
            self.last_message = "No active social connections are available for Hang Out yet."
            return

        self.pending_choice = {
            "title": "Hang Out",
            "text": "Choose someone to spend time with.",
            "question": "",
            "options": options,
            "selected_index": 0,
            "skippable": True,
            "choice_id": "select_hang_out_target",
            "default_value": None,
        }
        self.last_message = "Select someone to hang out with."

    def scroll_main_left(self, delta):
        snapshot_sections = build_snapshot_sections(self.get_snapshot_data())
        left_sections = [
            section
            for section in snapshot_sections
            if section["key"] in MAIN_LEFT_SECTION_KEYS
        ]
        scrollable_lines = [self.last_message, ""]
        scrollable_lines.extend(self.build_main_left_lines(left_sections, include_time=False))
        visible_height = self.main_body_height
        if visible_height <= 0:
            visible_height = 1
        _, next_offset, _, _ = get_scroll_window(scrollable_lines, visible_height, self.main_left_scroll + delta)
        if next_offset != self.main_left_scroll:
            self.main_left_scroll = next_offset

    @property
    def main_body_height(self):
        return getattr(self, "_main_body_height", 0)

    @property
    def profile_body_height(self):
        return getattr(self, "_profile_body_height", 0)

    def build_main_left_lines(self, snapshot_sections, *, include_time):
        focused_actor_id = self.get_focused_actor_id()
        social_links = self.world.get_links(source_id=focused_actor_id, link_type="social")
        active_social_links = [
            lnk for lnk in social_links if lnk.get("metadata", {}).get("status") == "active"
        ]
        lines = []
        for section in snapshot_sections:
            if not include_time and section["key"] == "time":
                continue
            lines.append(section["title"])
            lines.extend(section["lines"])
            if section["key"] == "relationships" and active_social_links:
                for lnk in active_social_links:
                    target_id = lnk.get("target_id")
                    target_actor = self.world.get_actor(target_id)
                    if target_actor is None:
                        continue
                    meta = lnk.get("metadata", {})
                    closeness = meta.get("closeness", 0)
                    tier = get_social_tier_label(closeness)
                    lines.append(f"  {target_actor.get_full_name()} · {tier}")
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        return lines

    def acknowledge_death(self):
        continuity_state = self.get_continuity_state()
        self.continuation_selection = 0
        self.selected_continuation_actor_id = None
        self.screen_name = "continuation"
        if continuity_state["had_continuity_candidates"]:
            self.last_message = "Choose who to continue as."
        else:
            self.last_message = "No one is available to continue."

    def get_selected_continuation_candidate(self):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        if not candidates:
            return None

        self.continuation_selection = max(
            0,
            min(self.continuation_selection, len(candidates) - 1),
        )
        return candidates[self.continuation_selection]

    def open_continuation_detail(self):
        selected_candidate = self.get_selected_continuation_candidate()
        if selected_candidate is None:
            return
        self.selected_continuation_actor_id = selected_candidate["actor_id"]
        self.screen_name = "continuation_detail"
        self.last_message = f"Inspecting {selected_candidate['full_name']}."

    def choose_continuation(self):
        selected_candidate = self.get_selected_continuation_candidate()
        if selected_candidate is None:
            self.running = False
            return

        successor_actor_id = selected_candidate["actor_id"]
        handoff_result = self.world.handoff_focus_to_continuation(
            self.get_focused_actor_id(),
            successor_actor_id,
        )
        self.player_id = successor_actor_id
        self.last_logged_year = 0
        self.event_log.append(
            {
                "kind": "life_separator",
                "text": f"New Life: {handoff_result['new_focused_actor_name']}",
            }
        )
        self.pending_choice = None
        self.remaining_skip_months = 0
        continued_actor = self.get_focused_actor()
        continued_lifecycle = (
            continued_actor.get_lifecycle_state(self.world.current_year, self.world.current_month)
            if continued_actor is not None
            else None
        )
        self.identity_popup_suppressed_for_resumed_adult = False
        if continued_actor is not None and continued_lifecycle is not None and continued_lifecycle["age_years"] >= 18:
            continued_actor.auto_resolve_identity()
            self.gender_choice_offered = True
            self.sexuality_choice_offered = True
            self.identity_popup_suppressed_for_resumed_adult = True
        else:
            self.gender_choice_offered = False
            self.gender_choice_offered = False
        self.sexuality_choice_offered = False
        self.gender_choice_age = random.randint(12, 15)
        self.sexuality_choice_age = random.randint(14, 17)
        self.meeting_event_last_total_months = 0
        self.selected_continuation_actor_id = None
        self.screen_name = "main"
        self.quit_confirmation_active = False
        self.last_message = f"Your story continues as {handoff_result['new_focused_actor_name']}."

    def handle_pending_choice_key(self, key):
        # Q and E are blocked while a popup is active — cannot advance or skip during a choice
        if key in (ord("q"), ord("Q"), ord("e"), ord("E")):
            return

        if self.pending_choice is None:
            return

        options = self.pending_choice["options"]
        selected_index = self.pending_choice["selected_index"]
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.pending_choice["selected_index"] = max(0, selected_index - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.pending_choice["selected_index"] = min(len(options) - 1, selected_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            selected_option = options[self.pending_choice["selected_index"]]
            if self.pending_choice["choice_id"] == "sexuality":
                selected_value = dict(SEXUALITY_OPTION_LABELS)[selected_option]
            else:
                selected_value = selected_option
            self.resolve_choice(self.pending_choice["choice_id"], selected_value)
        elif self.pending_choice.get("skippable") and key in BACK_KEYS:
            self.resolve_choice(
                self.pending_choice["choice_id"],
                self.pending_choice.get("default_value"),
            )

    def handle_main_key(self, key):
        # Q = advance month
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - self.last_advance_time < ADVANCE_THROTTLE_SECONDS:
                return
            self.last_advance_time = now
            self.advance_one_month()
        # E = skip time
        elif key in (ord("e"), ord("E")):
            self.open_skip_time()
        # [1] = Menu popup
        elif key == ord("1"):
            self.menu_popup_active = not self.menu_popup_active
            self.menu_selection = 0
        # Esc = Options popup
        elif key == 27:
            self.options_popup_active = not self.options_popup_active
            if self.options_popup_active:
                self.options_selection = 0
            else:
                self.last_message = MAIN_IDLE_MESSAGE
        # WASD = movement aliases
        elif key in (ord("w"), ord("W"), curses.KEY_UP):
            self.scroll_main_left(-1)
        elif key in (ord("s"), ord("S"), curses.KEY_DOWN):
            self.scroll_main_left(1)

    def handle_history_key(self, key):
        self.history_screen.handle_key(self, key)

    def handle_profile_key(self, key):
        self.profile_screen.handle_key(self, key)

    def handle_lineage_key(self, key):
        self.lineage_screen.handle_key(self, key)

    def handle_relationship_browser_key(self, key, *, back_to="main"):
        self.relationship_browser_screen.handle_key(self, key, back_to=back_to)

    def handle_browser_key(self, key):
        self.browser_screen.handle_key(self, key)

    def get_actions_categories(self):
        """Returns the categories and their available actions for the current actor."""
        focused_actor_id = self.get_focused_actor_id()
        social_links = self.world.get_links(source_id=focused_actor_id, link_type="social")
        active_social = [lnk for lnk in social_links if lnk.get("metadata", {}).get("status") == "active"]
        social_actions = []
        if active_social:
            social_actions.append({"id": "hang_out", "label": "Hang Out", "links": active_social, "time_cost": HANG_OUT_TIME_COST})
        personal_actions = [
            {"id": "exercise", "label": "Exercise", "subtypes": EXERCISE_SUBTYPES, "time_cost": EXERCISE_TIME_COST},
            {"id": "read", "label": "Read", "subtypes": READ_SUBTYPES, "time_cost": READ_TIME_COST},
            {"id": "rest", "label": "Rest", "subtypes": REST_SUBTYPES, "time_cost": REST_TIME_COST},
        ]
        return [
            {"id": "social", "label": "Social", "actions": social_actions},
            {"id": "personal", "label": "Personal", "actions": personal_actions},
        ]

    def handle_actions_key(self, key):
        """Handles keys for the Actions screen."""
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - self.last_advance_time < ADVANCE_THROTTLE_SECONDS:
                return
            self.last_advance_time = now
            self.advance_one_month()
        elif key in (ord("e"), ord("E")):
            self.open_skip_time()
        elif key in BACK_KEYS:
            if self.actions_focus == "actions":
                self.actions_focus = "categories"
                self.actions_action_index = 0
            else:
                self.screen_name = "main"
                self.last_message = MAIN_IDLE_MESSAGE
        elif key in (curses.KEY_UP, ord("w"), ord("W")):
            if self.actions_focus == "categories":
                categories = self.get_actions_categories()
                self.actions_category_index = max(0, self.actions_category_index - 1)
                self.actions_action_index = 0
            else:
                categories = self.get_actions_categories()
                cat = categories[self.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                self.actions_action_index = max(0, self.actions_action_index - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            if self.actions_focus == "categories":
                categories = self.get_actions_categories()
                self.actions_category_index = min(len(categories) - 1, self.actions_category_index + 1)
                self.actions_action_index = 0
            else:
                categories = self.get_actions_categories()
                cat = categories[self.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                self.actions_action_index = min(max(0, len(actions) - 1), self.actions_action_index + 1)
        elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
            if self.actions_focus == "categories":
                categories = self.get_actions_categories()
                cat = categories[self.actions_category_index] if categories else None
                if cat and cat["actions"]:
                    self.actions_focus = "actions"
                    self.actions_action_index = 0
        elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
            if self.actions_focus == "actions":
                self.actions_focus = "categories"
                self.actions_action_index = 0
        elif key in (curses.KEY_ENTER, 10, 13):
            if self.actions_focus == "actions":
                categories = self.get_actions_categories()
                cat = categories[self.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                if actions and self.actions_action_index < len(actions):
                    action = actions[self.actions_action_index]
                    if action["id"] == "hang_out":
                        self.open_hang_out_select()
                    elif action["id"] in ("exercise", "read", "rest"):
                        subtypes = action["subtypes"]
                        self.personal_subtype_options = subtypes
                        self.pending_choice = {
                            "title": "Choose type",
                            "text": "",
                            "question": "",
                            "options": [f"{s['label']}  {s['time_cost']}h" for s in subtypes],
                            "selected_index": 0,
                            "skippable": True,
                            "choice_id": f"select_{action['id']}_subtype",
                            "default_value": None,
                        }
                        self.last_message = f"Choose how you want to {action['label'].lower()}."


    def handle_death_ack_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            return  # Q blocked on death screen — use Esc for Options
        elif key in (curses.KEY_ENTER, 10, 13):
            self.acknowledge_death()

    def handle_skip_time_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        # Q blocked during skip time — user is actively doing a time action
        if key in (ord("q"), ord("Q")):
            return  # do nothing
        if key in BACK_KEYS:
            self.screen_name = "main"
            self.last_message = MAIN_IDLE_MESSAGE
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.skip_selection = max(0, self.skip_selection - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.skip_selection = min(len(SKIP_MONTH_PRESETS) - 1, self.skip_selection + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            self.confirm_skip_selection()
        elif key == curses.KEY_BACKSPACE or key in (127, 8):
            self.skip_custom_value = self.skip_custom_value[:-1]
        elif ord("0") <= key <= ord("9"):
            if len(self.skip_custom_value) < 4:
                self.skip_custom_value += chr(key)

    def handle_continuation_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        if key in (ord("q"), ord("Q")):
            return  # Q blocked on continuation screen — use Esc for Options
        if key in BACK_KEYS:
            self.screen_name = "death_ack"
            self.last_message = "Returned to death summary."
            return
        if not candidates:
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.continuation_selection = max(0, self.continuation_selection - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.continuation_selection = min(
                len(candidates) - 1,
                self.continuation_selection + 1,
            )
        elif key in (curses.KEY_ENTER, 10, 13):
            self.open_continuation_detail()

    def handle_continuation_detail_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            return  # Q blocked on continuation screen — use Esc for Options
        elif key in BACK_KEYS:
            self.screen_name = "continuation"
            self.last_message = "Returned to available lives."
        elif key in (curses.KEY_ENTER, 10, 13):
            self.choose_continuation()

    def handle_key(self, key):
        self.sync_focus_state()
        if self.quit_confirmation_active:
            if key in BACK_KEYS or key == 27:
                self.quit_confirmation_active = False
                if self.quit_from_options:
                    self.quit_from_options = False
                    self.options_popup_active = True
                return
            if key in (curses.KEY_ENTER, 10, 13):
                self.running = False
                return
            return
        if self.options_popup_active:
            OPTIONS_ITEMS = ["Quit Game", "Help / Controls", "Settings"]
            if key == 27:
                self.options_popup_active = False
            elif key in (curses.KEY_UP, ord("w"), ord("W")):
                self.options_selection = max(0, self.options_selection - 1)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.options_selection = min(len(OPTIONS_ITEMS) - 1, self.options_selection + 1)
            elif key in (curses.KEY_ENTER, 10, 13):
                self._open_options_selection()
            return
        if self.menu_popup_active:
            MENU_ITEMS = ["Browser", "Actions", "Profile"]
            if key in BACK_KEYS:
                self.menu_popup_active = False
            elif key in (curses.KEY_UP, ord("w"), ord("W")):
                self.menu_selection = max(0, self.menu_selection - 1)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.menu_selection = min(len(MENU_ITEMS) - 1, self.menu_selection + 1)
            elif key == ord("1"):
                self.menu_selection = 0
                self._open_menu_selection()
            elif key == ord("2"):
                self.menu_selection = 1
                self._open_menu_selection()
            elif key == ord("3"):
                self.menu_selection = 2
                self._open_menu_selection()
            elif key in (curses.KEY_ENTER, 10, 13):
                self._open_menu_selection()
            return
        if self.pending_choice is not None:
            self.handle_pending_choice_key(key)
            return
        if self.screen_name == "main":
            self.handle_main_key(key)
        elif self.screen_name == "profile":
            self.handle_profile_key(key)
        elif self.screen_name == "lineage":
            self.handle_lineage_key(key)
        elif self.screen_name == "relationship_browser":
            self.handle_relationship_browser_key(key)
        elif self.screen_name == "history":
            self.handle_history_key(key)
        elif self.screen_name == "browser":
            self.handle_browser_key(key)
        elif self.screen_name == "actions":
            self.handle_actions_key(key)
        elif self.screen_name == "skip_time":
            self.handle_skip_time_key(key)
        elif self.screen_name == "death_ack":
            self.handle_death_ack_key(key)
        elif self.screen_name == "continuation":
            self.handle_continuation_key(key)
        elif self.screen_name == "continuation_detail":
            self.handle_continuation_detail_key(key)

    def render_footer(self, stdscr, height, width):
        footer_hints = {
            "main": "[Q] Advance Month   [E] Skip Time  |  [1] Menu  |  [Esc] Options",
            "profile": "[↑↓] Move  [Enter] View  [Bsp] Back",
            "lineage": "[↑↓] Move   [A] All   [L] Living   [D] Dead   [/] Search   [Bsp] Back   [Q] Advance",
            "relationship_browser": "[↑↓] Filter/Move   [/] Search   [Tab/→] Switch   [Bsp/←] Back   [Q] Advance",
            "history": "[↑↓] Scroll   [/] Jump to Year   [Bsp] Back   [Q] Advance",
            "browser": "[Tab] Switch Tab   [↑↓] Move   [/] Search   [Bsp] Back   [Q] Advance   [Esc] Options",
            "browser_rel_search": "Type search   [Enter] Confirm   [Esc] Cancel   [Q] Advance",
            "actions": "[↑↓] Move   [←→] Focus   [Enter] Select   [Bsp] Back   [Q] Advance   [Esc] Options",
            "history_search": "Type year [0-9]   [Enter] Continue   [Esc] Cancel   [Q] Advance",
            "lineage_search": "Type search   [Enter] Continue   [Esc] Cancel   [Q] Advance",
            "skip_time": "[↑↓] Move   [0-9] Custom   [Bksp] Erase   [Enter] Continue   [Bsp] Back   [Esc] Options",
            "death_ack": "[Enter] Continue   [Esc] Options",
            "continuation_detail": "[Enter] Continue   [Bsp] Back   [Esc] Options",
        }
        if self.screen_name == "lineage" and self.lineage_search_active:
            footer_text = footer_hints["lineage_search"]
        elif self.screen_name == "history" and self.history_search_active:
            footer_text = footer_hints["history_search"]
        elif self.screen_name == "profile" and self.profile_popup_open:
            footer_text = "[↑↓] Scroll  [Bsp] Close"
        elif self.screen_name == "browser" and self.browser_tab == "relationships" and self.rel_browser_search_active:
            footer_text = footer_hints["browser_rel_search"]
        elif self.screen_name == "browser" and self.browser_tab == "history" and self.history_search_active:
            footer_text = footer_hints["history_search"]
        elif self.screen_name == "continuation":
            continuity_state = self.get_continuity_state()
            if continuity_state["continuity_candidates"]:
                footer_text = "[↑↓] Move   [Enter] Continue   [Bsp] Back   [Esc] Options"
            else:
                footer_text = "[Bsp] Back   [Esc] Options"
        else:
            footer_text = footer_hints.get(self.screen_name, "")
        content_left, content_width = get_content_bounds(width, max_width=108, min_margin=1)
        full_hline = "═" * max(0, width - 1)
        stdscr.addnstr(height - 2, 0, full_hline, width - 1, curses.A_BOLD)
        stdscr.addnstr(
            height - 1,
            content_left,
            center_text(footer_text, content_width),
            content_width,
            curses.A_NORMAL,
        )

    def build_choice_popup_lines(self, choice):
        lines = [choice["text"], "", choice["question"], ""]
        option_line_indexes = []
        for index, option in enumerate(choice["options"]):
            option_line_indexes.append(len(lines))
            lines.append(f"{option}")
        lines.extend(
            [
                "",
                (
                    "[↑↓] Move   [Enter] Select   [Bsp] Skip"
                    if choice.get("skippable")
                    else "[↑↓] Move   [Enter] Select"
                ),
            ]
        )
        return lines, option_line_indexes

    def render_pending_choice(self, stdscr, height, width):
        if self.pending_choice is None:
            return

        box_width = min(max(40, width // 2), 50)
        inner_width = max(1, box_width - 2)
        popup_lines, option_line_indexes = self.build_choice_popup_lines(self.pending_choice)
        rendered_line_count = sum(len(wrap_text_line(line, inner_width)) for line in popup_lines)
        box_height = min(height - 4, max(9, rendered_line_count + 2))
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)

        draw_box(stdscr, top, left, box_height, box_width, title=self.pending_choice["title"])
        highlighted_line = option_line_indexes[self.pending_choice["selected_index"]]
        draw_panel_text(
            stdscr,
            top,
            left,
            box_height,
            box_width,
            popup_lines,
            highlight_index=highlighted_line,
        )

    def render_menu_popup(self, stdscr, height, width):
        MENU_ITEMS = ["Browser", "Actions", "Profile"]
        box_width = 32
        box_height = len(MENU_ITEMS) + 6
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        draw_box(stdscr, top, left, box_height, box_width, title="Menu")
        for i, item in enumerate(MENU_ITEMS):
            label = f"  {i+1}. {item}"
            attr = curses.A_REVERSE if i == self.menu_selection else curses.A_NORMAL
            row = top + 2 + i
            if row < height and left + 1 < width:
                stdscr.addnstr(row, left + 1, label.ljust(box_width - 2), box_width - 2, attr)
        hint_row = top + 2 + len(MENU_ITEMS) + 1
        hint = " [↑↓]  [Enter] Select  [Bsp] Back"
        if hint_row < height and left + 1 < width:
            stdscr.addnstr(hint_row, left + 1, hint.ljust(box_width - 2), box_width - 2)

    def render_options_popup(self, stdscr, height, width):
        OPTION_ITEMS = ["Quit Game", "Help / Controls", "Settings"]
        box_width = 36
        box_height = len(OPTION_ITEMS) + 6
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        draw_box(stdscr, top, left, box_height, box_width, title="Options")
        for i, item in enumerate(OPTION_ITEMS):
            prefix = "  "
            attr = curses.A_REVERSE if i == self.options_selection else curses.A_NORMAL
            if i > 0:
                attr |= curses.A_DIM
            label = f"{prefix}{item}"
            row = top + 2 + i
            if row < height and left + 1 < width:
                stdscr.addnstr(row, left + 1, label.ljust(box_width - 2), box_width - 2, attr)
        hint_row = top + 2 + len(OPTION_ITEMS) + 1
        hint = " [↑↓]  [Enter] Select  [Esc] Close"
        if hint_row < height and left + 1 < width:
            stdscr.addnstr(hint_row, left + 1, hint.ljust(box_width - 2), box_width - 2)

    def render_quit_confirmation(self, stdscr, height, width):
        box_width = min(max(36, width // 2), 44)
        box_height = 7
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        lines = [
            "Are you sure you want to quit?",
            "",
            "[Enter] Quit   [Bsp] Back",
        ]
        draw_box(stdscr, top, left, box_height, box_width, title="Quit")
        draw_panel_text(stdscr, top, left, box_height, box_width, lines)

    _LOGO_LINES = [
        "╗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄╔",
        "║█░░▒▒▓█▄░▄█▓▒▒░░█║",
        "║█░▒▒▓█▀░▄░▀█▓▒▒░█║",
        "║█░▒▒▓█▒▒█▒▒█▓▒▒░█║",
        "║█░▒▒▓█▄▀▓▀▄█▓▒▒░█║",
        "║█░░▒▒▓█▓▄▓█▓▒▒░░█║",
        "╝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀╚",
    ]

    def _get_logo_layout(self, width):
        """Returns (logo_x, logo_w, logo_center) — the canonical horizontal anchor for all shell layers."""
        logo_w = max(len(l) for l in self._LOGO_LINES)
        logo_x = (max(1, width - 1) - logo_w) // 2
        logo_center = logo_x + logo_w // 2
        return logo_x, logo_w, logo_center

    def render_header(self, stdscr, width):
        focused_actor = self.get_focused_actor()
        focused_actor_name = focused_actor.get_full_name() if focused_actor is not None else "Unknown"
        chrome = build_screen_chrome(self.screen_name, self.world, focused_actor_name)
        full_hline = "═" * max(0, width - 1)
        divider = "║"

        LOGO = self._LOGO_LINES
        logo_x, logo_w, _logo_center = self._get_logo_layout(width)

        # Left panel content
        try:
            snapshot = self.get_snapshot_data()
            loc = snapshot.get("location", {})
            stats = snapshot.get("statistics", {})
            city = loc.get("current_place_name", "")
            country = loc.get("jurisdiction_place_name", "")
            loc_str = f"{city}, {country}" if city and country else city or country or ""
            health = stats.get("health", 0)
            money = stats.get("money", 0)
            money_str = f"${money:,.0f}" if isinstance(money, (int, float)) else str(money)
        except Exception:
            loc_str = health = money_str = ""

        left_lines = [
            chrome["date_text"],
            chrome["subtitle"],
            chrome["title"],
            "",
            "",
        ]
        right_lines = [
            loc_str,
            f"Health: {health}",
            money_str,
            "",
            "",
        ]

        # Logo is centered via _get_logo_layout — canonical anchor for all shell layers.
        panel_left_w = logo_x           # columns 0 to logo_x-1
        panel_right_w = width - 1 - logo_x - logo_w  # columns after logo to end

        # Row 0: top separator with logo top line
        top_row = "═" * logo_x + LOGO[0] + "═" * panel_right_w
        try:
            stdscr.addnstr(0, 0, top_row[:width - 1], width - 1, curses.A_BOLD)
        except curses.error:
            pass

        # Rows 1-5: logo body + left/right info panels
        for i in range(5):
            logo_line = LOGO[i + 1] if i + 1 < len(LOGO) - 1 else ""
            left_val = left_lines[i] if i < len(left_lines) else ""
            right_val = right_lines[i] if i < len(right_lines) else ""
            left_text = f"{left_val:>{panel_left_w - 1}} "  # right-aligned, 1 space before ║
            right_text = f" {right_val}"                    # 1 space after ║
            try:
                stdscr.addnstr(i + 1, 0, left_text[:panel_left_w], panel_left_w)
                stdscr.addnstr(i + 1, logo_x, logo_line, logo_w, curses.A_BOLD)
                stdscr.addnstr(i + 1, logo_x + logo_w, right_text[:panel_right_w], panel_right_w)
            except curses.error:
                pass

        # Row 6: bottom separator with logo bottom line
        bot_row = "═" * logo_x + LOGO[-1] + "═" * panel_right_w
        try:
            stdscr.addnstr(self.HEADER_ROWS - 1, 0, bot_row[:width - 1], width - 1, curses.A_BOLD)
        except curses.error:
            pass

    def render_main(self, stdscr, height, width):
        snapshot_data = self.get_snapshot_data()
        snapshot_sections = build_snapshot_sections(snapshot_data)
        top = self.HEADER_ROWS
        body_height = height - self.HEADER_ROWS - self.FOOTER_ROWS
        self._main_body_height = body_height
        content_left, content_width = get_content_bounds(width, max_width=112)
        _, _logo_w, logo_center = self._get_logo_layout(width)
        # Pin divider to logo center so body │ and header ║ share the same column.
        divider_x = logo_center
        left_width = divider_x - content_left - 1
        right_left = divider_x + 2
        right_width = content_left + content_width - right_left

        left_sections = [
            section
            for section in snapshot_sections
            if section["key"] in MAIN_LEFT_SECTION_KEYS
        ]
        left_lines = [self.last_message, ""]
        left_lines.extend(self.build_main_left_lines(left_sections, include_time=False))
        visible_left_lines, self.main_left_scroll, main_left_max_offset, total_left_lines = get_scroll_window(
            left_lines,
            body_height,
            self.main_left_scroll,
        )
        right_lines = expand_render_lines(build_live_feed_lines(self.event_log), right_width)
        visible_right_lines, _, _, _ = get_scroll_window(
            right_lines,
            body_height,
            max(0, len(right_lines) - body_height),
        )

        draw_text_block(stdscr, top, content_left, left_width, body_height, visible_left_lines)
        draw_vertical_divider(stdscr, top, divider_x, body_height)
        draw_text_block(stdscr, top, right_left, right_width, body_height, visible_right_lines)

        if main_left_max_offset > 0:
            scroll_label = f"More details: {self.main_left_scroll + 1}-{self.main_left_scroll + len(visible_left_lines)} / {total_left_lines}"
            stdscr.addnstr(
                min(height - 3, top + body_height - 1),
                content_left,
                truncate_for_width(scroll_label, left_width),
                left_width,
                curses.A_DIM,
            )

    def render_profile(self, stdscr, height, width):
        self.profile_screen.render(self, stdscr, height, width)

    def render_lineage(self, stdscr, height, width):
        self.lineage_screen.render(self, stdscr, height, width)

    def render_relationship_browser(self, stdscr, height, width):
        self.relationship_browser_screen.render(self, stdscr, height, width)

    def render_history(self, stdscr, height, width):
        self.history_screen.render(self, stdscr, height, width)

    def render_browser(self, stdscr, height, width):
        self.browser_screen.render(self, stdscr, height, width)

    def render_actions(self, stdscr, height, width):
        """Renders the Actions screen: Categories | Actions | Details."""
        top = self.HEADER_ROWS
        body_height = height - self.HEADER_ROWS - self.FOOTER_ROWS
        content_left, content_width = get_content_bounds(width, max_width=120)
        col_w = content_width // 3
        cat_left = content_left
        act_left = content_left + col_w + 1
        det_left = content_left + col_w * 2 + 2
        det_width = content_width - col_w * 2 - 2

        categories = self.get_actions_categories()
        cat_idx = self.actions_category_index
        act_idx = self.actions_action_index
        current_cat = categories[cat_idx] if categories else None
        actions = current_cat["actions"] if current_cat else []
        current_action = actions[act_idx] if actions and act_idx < len(actions) else None

        # Categories column
        for i, cat in enumerate(categories):
            label = f" {cat['label']}"
            attr = curses.A_REVERSE if (i == cat_idx and self.actions_focus == "categories") else curses.A_NORMAL
            if i == cat_idx and self.actions_focus != "categories":
                attr = curses.A_BOLD
            row = top + 1 + i
            if row < height:
                stdscr.addnstr(row, cat_left, label.ljust(col_w - 1), col_w - 1, attr)
        if not categories:
            stdscr.addnstr(top + 1, cat_left, " (none)", col_w - 1, curses.A_DIM)

        # Divider 1
        draw_vertical_divider(stdscr, top, act_left - 1, body_height)

        # Actions column — available actions + queued section
        avail_rows = max(1, body_height // 2 - 2)
        if not actions:
            stdscr.addnstr(top + 1, act_left, " (none yet)", col_w - 1, curses.A_DIM)
        else:
            for i, action in enumerate(actions):
                if i >= avail_rows:
                    break
                label = f" {action['label']}"
                attr = curses.A_REVERSE if (i == act_idx and self.actions_focus == "actions") else curses.A_NORMAL
                row = top + 1 + i
                if row < height:
                    stdscr.addnstr(row, act_left, label.ljust(col_w - 1), col_w - 1, attr)

        # Queued section divider + list
        queue_top = top + avail_rows + 2
        if queue_top < height - 2:
            try:
                stdscr.hline(queue_top - 1, act_left, getattr(curses, "ACS_HLINE", ord("-")), col_w - 1)
            except curses.error:
                pass
            stdscr.addnstr(queue_top, act_left, " Queued", col_w - 1, curses.A_BOLD)
            if self.active_actions:
                for i, queued in enumerate(self.active_actions):
                    row = queue_top + 1 + i
                    if row >= height - 1:
                        break
                    stdscr.addnstr(row, act_left, f"  {queued['label']}", col_w - 1)
            else:
                if queue_top + 1 < height - 1:
                    stdscr.addnstr(queue_top + 1, act_left, " (nothing queued)", col_w - 1, curses.A_DIM)

        # Divider 2
        draw_vertical_divider(stdscr, top, det_left - 1, body_height)

        # Details column
        focused_actor = self.world.get_focused_actor()
        free_hours = int(get_monthly_free_hours(focused_actor))
        queued_hours = int(sum(a.get("time_cost", 0) for a in self.active_actions))
        remaining_hours = free_hours - queued_hours
        if current_action:
            det_lines = [f" {current_action['label']}", ""]
            if current_action["id"] == "hang_out":
                links = current_action.get("links", [])
                if links:
                    det_lines.append(" Who you can hang out with:")
                    det_lines.append("")
                    for lnk in links:
                        target_id = lnk.get("target_id")
                        target_actor = self.world.get_actor(target_id)
                        if target_actor is None:
                            continue
                        meta = lnk.get("metadata", {})
                        closeness = meta.get("closeness", 0)
                        tier = get_social_tier_label(closeness)
                        det_lines.append(f"  {target_actor.get_full_name()} · {tier}")
                else:
                    det_lines.append(" No active social connections yet.")
            elif current_action["id"] in ("exercise", "read", "rest"):
                det_lines.append(" Ways to spend your time:")
                det_lines.append("")
                for subtype in current_action.get("subtypes", []):
                    effects_text = format_stat_change_summary(subtype.get("stat_changes", {}))
                    det_lines.append(f"  {subtype['label']} - {subtype['time_cost']}h - {effects_text}")
            next_y = draw_text_block(stdscr, top, det_left, det_width, body_height, det_lines)
            if next_y < top + body_height:
                next_y = draw_text_block(stdscr, next_y, det_left, det_width, body_height - (next_y - top), [""])
            budget_lines = [
                (" Time Budget", curses.A_BOLD),
                (f"  {free_hours}h free", curses.A_DIM),
                (f"  {queued_hours}h queued", curses.A_DIM),
                (f"  {remaining_hours}h left", curses.A_DIM),
            ]
            y = next_y
            for raw_line, attr in budget_lines:
                for wrapped_line in wrap_text_line(raw_line, det_width):
                    if y >= top + body_height:
                        break
                    stdscr.addnstr(y, det_left, wrapped_line, det_width, attr)
                    y += 1
        else:
            stdscr.addnstr(top + 1, det_left, " Select an action", det_width, curses.A_DIM)
            budget_lines = [
                (" Time Budget", curses.A_BOLD),
                (f"  {free_hours}h free", curses.A_DIM),
                (f"  {queued_hours}h queued", curses.A_DIM),
                (f"  {remaining_hours}h left", curses.A_DIM),
            ]
            y = top + 3
            for raw_line, attr in budget_lines:
                for wrapped_line in wrap_text_line(raw_line, det_width):
                    if y >= top + body_height:
                        break
                    stdscr.addnstr(y, det_left, wrapped_line, det_width, attr)
                    y += 1

        # Show last_message feedback at bottom of details column if present
        if self.last_message:
            msg_row = top + body_height - 1
            if msg_row >= top:
                stdscr.addnstr(msg_row, det_left,
                               truncate_for_width(self.last_message, det_width),
                               det_width, curses.A_DIM)

    def build_actor_inspect_detail(self, actor_id, *, relationship_label=None, recent_record_limit=INSPECT_RECORD_LIMIT):
        """Builds one shell-owned inspectability payload for an actor."""
        actor = self.world.get_actor(actor_id)
        if actor is None:
            return None

        lifecycle_year = self.world.current_year
        lifecycle_month = self.world.current_month
        if not actor.is_alive() and actor.death_year is not None and actor.death_month is not None:
            lifecycle_year = actor.death_year
            lifecycle_month = actor.death_month

        lifecycle = actor.get_lifecycle_state(lifecycle_year, lifecycle_month)
        actor_records = self.world.get_actor_records(actor_id)
        recent_records = list(reversed(filter_player_facing_records(actor_records)))[:recent_record_limit]
        return {
            "full_name": actor.get_full_name(),
            "relationship_label": relationship_label or "Connected",
            "age": lifecycle["age_years"],
            "life_stage": lifecycle["life_stage"],
            "current_place_name": self.world.get_place_name(actor.current_place_id) or "Unknown",
            "health": actor.stats["health"],
            "happiness": actor.stats["happiness"],
            "intelligence": actor.stats["intelligence"],
            "money": actor.money,
            "records": recent_records,
        }

    def render_skip_time(self, stdscr, height, width):
        custom_months = self.get_custom_skip_months()
        selected_months = self.get_selected_skip_months()
        content_left, content_width = get_content_bounds(width, max_width=76)
        lines = [
            center_text("TIME JUMP", content_width),
            "",
            self.last_message,
            "",
            "Presets",
        ]
        highlight_index = 5 + self.skip_selection
        for preset_months in SKIP_MONTH_PRESETS:
            label = "month" if preset_months == 1 else "months"
            lines.append(f"{preset_months:>2} {label}")
        lines.extend(
            [
                "",
                "Custom Months",
                (
                    f"Typed value: {self.skip_custom_value} months"
                    if self.skip_custom_value
                    else "Typed value: none"
                ),
                (
                    f"Enter will advance {custom_months} months from the custom value."
                    if custom_months is not None
                    else f"Enter will advance {selected_months} months from the selected preset."
                ),
            ]
        )
        draw_text_block(stdscr, self.HEADER_ROWS, content_left, content_width, height - self.HEADER_ROWS - self.FOOTER_ROWS, lines, highlight_index=highlight_index)

    def render_death_ack(self, stdscr, height, width):
        continuity_state = self.get_continuity_state()
        content_left, content_width = get_content_bounds(width, max_width=74)
        death_detail = self.build_actor_inspect_detail(
            self.get_focused_actor_id(),
            relationship_label="Self",
        )
        lines = [
            "",
            center_text("DEATH", content_width),
            "",
        ]
        lines.extend(build_death_lines(continuity_state))
        if death_detail is not None:
            lines.extend(
                [
                    "",
                    "Life Summary",
                    f"Age at death: {death_detail['age']}",
                    f"Place at death: {death_detail['current_place_name']}",
                    (
                        "At death: "
                        f"Health {death_detail['health']}   Happiness {death_detail['happiness']}   "
                        f"Intelligence {death_detail['intelligence']}   Money ${death_detail['money']}"
                    ),
                    "",
                    "Recent Records",
                ]
            )
            lines.extend(build_record_summary_lines(death_detail["records"]))
        lines.extend(
            [
                "",
                center_text("Press Enter to continue.", content_width),
            ]
        )
        draw_text_block(
            stdscr,
            5,
            content_left,
            content_width,
            height - 7,
            lines,
        )

    def render_continuation(self, stdscr, height, width):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        content_left, content_width = get_content_bounds(width, max_width=96)
        lines = [
            "",
        ]
        highlight_index = None

        if not candidates:
            lines.append("No living family members were found.")
        else:
            self.continuation_selection = max(
                0,
                min(self.continuation_selection, len(candidates) - 1),
            )
            for index, candidate in enumerate(candidates):
                line = (
                    f"{candidate['full_name']} · {candidate['relationship_label']} · "
                    f"Age {candidate['age']} · {candidate.get('current_place_name') or 'Unknown'}"
                )
                if index == self.continuation_selection:
                    highlight_index = len(lines)
                lines.append(line)

        draw_text_block(stdscr, self.HEADER_ROWS, content_left, content_width, height - self.HEADER_ROWS - self.FOOTER_ROWS, lines, highlight_index=highlight_index)

    def render_continuation_detail(self, stdscr, height, width):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        selected_candidate = next(
            (
                candidate
                for candidate in candidates
                if candidate["actor_id"] == self.selected_continuation_actor_id
            ),
            None,
        )
        if selected_candidate is None:
            self.screen_name = "continuation"
            self.last_message = "This person is no longer available."
            self.render_continuation(stdscr, height, width)
            return

        detail = self.build_actor_inspect_detail(
            selected_candidate["actor_id"],
            relationship_label=selected_candidate["relationship_label"],
        )
        if detail is None:
            content_left, content_width = get_content_bounds(width, max_width=86)
            render_lines(stdscr, ["Actor data unavailable."], 0, content_left, height, width)
            return
        content_left, content_width = get_content_bounds(width, max_width=86)
        lines = [
            center_text("CONTINUATION DETAIL", content_width),
            "",
            detail["full_name"],
            (
                f"{detail['relationship_label']}   Age {detail['age']}   "
                f"Location: {detail['current_place_name']}"
            ),
            (
                f"Health {detail['health']}   Happiness {detail['happiness']}   "
                f"Intelligence {detail['intelligence']}   Money ${detail['money']}"
            ),
            "",
            "Recent Records",
        ]
        lines.extend(build_record_summary_lines(detail["records"]))
        draw_text_block(stdscr, self.HEADER_ROWS, content_left, content_width, height - self.HEADER_ROWS - self.FOOTER_ROWS, lines)

    def render(self, stdscr):
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        if height < 16 or width < 50:
            stdscr.addnstr(0, 0, "Terminal too small for Actora TUI. Resize and try again.", width - 1)
            return

        self.render_header(stdscr, width)
        if self.screen_name == "main":
            self.render_main(stdscr, height, width)
        elif self.screen_name == "profile":
            self.render_profile(stdscr, height, width)
        elif self.screen_name == "lineage":
            self.render_lineage(stdscr, height, width)
        elif self.screen_name == "relationship_browser":
            self.render_relationship_browser(stdscr, height, width)
        elif self.screen_name == "history":
            self.render_history(stdscr, height, width)
        elif self.screen_name == "browser":
            self.render_browser(stdscr, height, width)
        elif self.screen_name == "actions":
            self.render_actions(stdscr, height, width)
        elif self.screen_name == "skip_time":
            self.render_skip_time(stdscr, height, width)
        elif self.screen_name == "death_ack":
            self.render_death_ack(stdscr, height, width)
        elif self.screen_name == "continuation":
            self.render_continuation(stdscr, height, width)
        elif self.screen_name == "continuation_detail":
            self.render_continuation_detail(stdscr, height, width)

        self.render_footer(stdscr, height, width)
        self.render_pending_choice(stdscr, height, width)
        if self.menu_popup_active:
            self.render_menu_popup(stdscr, height, width)
        if self.options_popup_active:
            self.render_options_popup(stdscr, height, width)
        stdscr.refresh()

    def run(self, stdscr):
        """Runs the narrow curses shell until the user quits or the run ends."""
        curses.set_escdelay(25)
        curses.curs_set(0)
        stdscr.keypad(True)

        while self.running:
            self.sync_focus_state()
            self.render(stdscr)
            if self.quit_confirmation_active:
                self.render_quit_confirmation(stdscr, *stdscr.getmaxyx())
                stdscr.refresh()
            key = stdscr.getch()
            self.handle_key(key)


def setup_initial_world_from_character(character_data):
    """Initializes the startup world from one fully prepared character payload."""
    world = World(start_year=1, start_month=1)
    world.add_place(
        place_id="earth",
        name="Earth",
        kind="world_body",
        parent_place_id=None,
        metadata={},
    )
    for country in WORLD_GEOGRAPHY:
        world.add_place(
            place_id=country["country_id"],
            name=country["country_name"],
            kind="country",
            parent_place_id="earth",
            metadata=dict(country["metadata"]),
        )
        for city in country["cities"]:
            world.add_place(
                place_id=city["city_id"],
                name=city["city_name"],
                kind="city",
                parent_place_id=country["country_id"],
                metadata={},
            )

    startup_jurisdiction_place_id = character_data.get("country_id") or DEFAULT_COUNTRY_ID
    startup_place_id = character_data.get("city_id") or DEFAULT_CITY_ID
    startup_country = WORLD_GEOGRAPHY_BY_COUNTRY_ID.get(startup_jurisdiction_place_id)
    if startup_country is None:
        raise ValueError(f"Unknown startup country_id '{startup_jurisdiction_place_id}'")
    if startup_place_id not in {city["city_id"] for city in startup_country["cities"]}:
        raise ValueError(
            f"Unknown or mismatched startup city_id '{startup_place_id}' for country_id '{startup_jurisdiction_place_id}'"
        )

    mother_identity_context = prepare_parent_identity_context(
        role="mother",
        player_last_name=character_data["last_name"],
        place_id=startup_place_id,
        world=world,
        culture_group=startup_country["metadata"]["culture_group"],
    )
    family_last_name = mother_identity_context["family_last_name"]
    father_identity_context = prepare_parent_identity_context(
        role="father",
        family_last_name=family_last_name,
        player_last_name=character_data["last_name"],
        place_id=startup_place_id,
        world=world,
        culture_group=startup_country["metadata"]["culture_group"],
    )

    mother_identity = generate_parent_identity_from_context(mother_identity_context)
    father_identity = generate_parent_identity_from_context(father_identity_context)

    mother_id = generate_startup_actor_id("mother")
    father_id = generate_startup_actor_id("father")
    mother_age_years = random.randint(22, 36)
    father_age_years = max(mother_age_years + random.randint(1, 5), 24)
    world.create_human_actor(
        actor_id=mother_id,
        species="Human",
        first_name=mother_identity["first_name"],
        last_name=mother_identity["last_name"],
        sex=mother_identity["sex"],
        gender=mother_identity["gender"],
        birth_year=world.current_year - mother_age_years,
        birth_month=random.randint(1, 12),
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=True,
    )
    world.create_human_actor(
        actor_id=father_id,
        species="Human",
        first_name=father_identity["first_name"],
        last_name=father_identity["last_name"],
        sex=father_identity["sex"],
        gender=father_identity["gender"],
        birth_year=world.current_year - father_age_years,
        birth_month=random.randint(1, 12),
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=True,
    )
    world.add_link_pair(
        source_id=mother_id,
        target_id=father_id,
        forward_type="association",
        forward_role="coparent",
        reverse_type="association",
        reverse_role="coparent",
        forward_metadata={"bootstrap_source": "startup_coparent_association"},
        reverse_metadata={"bootstrap_source": "startup_coparent_association"},
    )

    world.bootstrap_older_siblings_for_newborn(
        mother_id=mother_id,
        father_id=father_id,
        player_birth_year=world.current_year,
        player_birth_month=1,
    )

    player_id = generate_startup_actor_id("player")
    player = world.create_human_child_with_parents(
        child_id=player_id,
        first_name=character_data["first_name"],
        last_name=character_data["last_name"],
        sex=character_data["sex"],
        gender=character_data["gender"],
        mother_id=mother_id,
        father_id=father_id,
        birth_year=world.current_year,
        birth_month=1,
        place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=False,
        family_link_source="startup_family",
        birth_record_type="family_bootstrap",
        birth_record_text=(
            f"{character_data['first_name']} {character_data['last_name']}".strip()
            + " was bootstrapped with current startup family links."
        ),
        birth_record_tags=["family", "bootstrap"],
        birth_record_metadata={"is_startup_player": True},
    )
    player.stats = normalize_creation_stats(character_data["stats"])
    player.appearance = dict(character_data["appearance"])
    player.traits = list(character_data["traits"])
    player.money = 0
    world.set_focused_actor(player_id)

    return world, player_id


def setup_initial_world(player_first_name, player_last_name, player_sex, player_gender):
    """Compatibility wrapper that delegates to character-data startup flow."""
    default_character_data = {
        "first_name": player_first_name,
        "last_name": player_last_name,
        "sex": player_sex,
        "gender": player_gender,
        "country_id": DEFAULT_COUNTRY_ID,
        "city_id": DEFAULT_CITY_ID,
        "appearance": {
            "eye_color": "Brown",
            "hair_color": "Black",
            "skin_tone": "Medium",
        },
        "traits": [],
        "stats": build_randomized_starting_stats(),
    }
    return setup_initial_world_from_character(default_character_data)


def run_creation_wizard():
    """Runs the curses-based character creation wizard and returns character data or None."""
    def _run(stdscr):
        wizard = CreationWizard(stdscr, BACK_KEYS)
        return wizard.run()

    try:
        return curses.wrapper(_run)
    except KeyboardInterrupt:
        return None



def run_game_tui(world, player_id):
    """Runs the actor-first curses TUI for ordinary play after startup creation completes."""
    tui = ActoraTUI(world, player_id)
    try:
        curses.wrapper(tui.run)
    except KeyboardInterrupt:
        pass


def start_game():
    """Runs character creation and the ordinary-play TUI."""
    character_data = run_creation_wizard()
    if character_data is None:
        return

    world, player_id = setup_initial_world_from_character(character_data)
    run_game_tui(world, player_id)


if __name__ == "__main__":
    start_game()
