import curses
import random
from uuid import uuid4


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
    filter_player_facing_records,
    get_social_tier_label,
)
from views.history import (
    expand_render_lines,
    format_history_entry,
)
from screens.actions import ActionsScreen
from screens.browser import BrowserScreen
from screens.death import DeathContinuationScreen
from screens.history import HistoryScreen
from screens.lineage import LineageScreen
from screens.main import MainScreen, build_snapshot_sections
from screens.profile import ProfileScreen
from screens.relationships import RelationshipBrowserScreen
from screens.skip_time import SkipTimeScreen
from app_router import AppRouter
from browser_state_controller import BrowserStateController
from choice_controller import ChoiceController
from continuation_controller import ContinuationController
from event_log_controller import EventLogController
from life_event_controller import LifeEventController
from shell_controller import ShellController
from shell_renderer import ShellRenderer
from time_controller import TimeController
from views.profile import build_person_card_lines
from ui import (
    draw_text_block,
    draw_truncated_block,
    get_content_bounds,
    get_scroll_window,
    split_centered_columns,
)
from wizard import (
    CREATION_STAT_LABELS,
    CREATION_STAT_ORDER,
    CreationWizard,
    build_randomized_starting_stats,
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
        self.app_router = AppRouter()
        self.browser_state_controller = BrowserStateController(
            LINEAGE_RECORD_LIMIT,
            LINEAGE_FILTER_LABELS,
            REL_FILTER_OPTIONS,
        )
        self.shell_renderer = ShellRenderer()
        self.shell_controller = ShellController(BACK_KEYS)
        self.choice_controller = ChoiceController(
            BACK_KEYS,
            SEXUALITY_OPTION_LABELS,
        )
        self.continuation_controller = ContinuationController()
        self.event_log_controller = EventLogController()
        self.life_event_controller = LifeEventController(
            MEETING_EVENT_COOLDOWN_MONTHS,
            GENDER_IDENTITY_OPTIONS,
            SEXUALITY_OPTION_LABELS,
        )
        self.time_controller = TimeController()
        self.lineage_selection = 0
        self.continuation_selection = 0
        self.death_screen = DeathContinuationScreen(BACK_KEYS)
        self.skip_selection = 0
        self.skip_custom_value = ""
        self.skip_time_screen = SkipTimeScreen(
            SKIP_MONTH_PRESETS,
            BACK_KEYS,
            MAIN_IDLE_MESSAGE,
        )
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
        self.main_screen = MainScreen(
            MAIN_LEFT_SECTION_KEYS,
            ADVANCE_THROTTLE_SECONDS,
            MAIN_IDLE_MESSAGE,
        )
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
        self.actions_screen = ActionsScreen(
            BACK_KEYS,
            ADVANCE_THROTTLE_SECONDS,
            MAIN_IDLE_MESSAGE,
        )

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
        return self.browser_state_controller.get_lineage_browser_state(self)

    def get_lineage_entries(self):
        return self.browser_state_controller.get_lineage_entries(self)

    def get_lineage_detail(self):
        return self.browser_state_controller.get_lineage_detail(self)

    def set_lineage_filter_mode(self, filter_mode):
        self.browser_state_controller.set_lineage_filter_mode(self, filter_mode)

    def clear_lineage_search(self):
        self.browser_state_controller.clear_lineage_search(self)

    def get_lineage_search_status(self):
        return self.browser_state_controller.get_lineage_search_status(self)

    def get_rel_browser_search_status(self):
        return self.browser_state_controller.get_rel_browser_search_status(self)

    def get_relationship_browser_state(self):
        return self.browser_state_controller.get_relationship_browser_state(self)

    def get_continuity_state(self):
        return self.continuation_controller.get_continuity_state(self)

    def append_event_log_entry(self, kind, text, *, year=None, month=None, record_type=None):
        self.event_log_controller.append_entry(
            self,
            kind,
            text,
            year=year,
            month=month,
            record_type=record_type,
        )

    def append_event_log_turn(self, turn_result, months_to_advance, new_records, *, suppress_skip_marker=False):
        self.event_log_controller.append_turn(
            self,
            turn_result,
            months_to_advance,
            new_records,
            suppress_skip_marker=suppress_skip_marker,
        )

    def maybe_offer_identity_choice(self):
        return self.life_event_controller.maybe_offer_identity_choice(self)

    def maybe_offer_meeting_event(self):
        return self.life_event_controller.maybe_offer_meeting_event(self)

    def resolve_choice(self, choice_id, selected_value):
        self.choice_controller.resolve_choice(self, choice_id, selected_value)

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
        self.time_controller.advance_time(self, months_to_advance, is_resume=is_resume)

    def advance_one_month(self):
        self.time_controller.advance_one_month(self)

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
        self.shell_controller.open_menu_selection(self)

    def _open_options_selection(self):
        self.shell_controller.open_options_selection(self)

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
        active_links = [
            l
            for l in social_links
            if l.get("metadata", {}).get("status") == "active"
            and (self.world.get_actor(l.get("target_id")) is not None)
            and self.world.get_actor(l.get("target_id")).is_alive()
        ]
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
        self.continuation_controller.acknowledge_death(self)

    def get_selected_continuation_candidate(self):
        return self.continuation_controller.get_selected_continuation_candidate(self)

    def open_continuation_detail(self):
        self.continuation_controller.open_continuation_detail(self)

    def choose_continuation(self):
        self.continuation_controller.choose_continuation(self)

    def get_actions_categories(self):
        """Returns the categories and their available actions for the current actor."""
        focused_actor_id = self.get_focused_actor_id()
        social_links = self.world.get_links(source_id=focused_actor_id, link_type="social")
        active_social = [
            lnk
            for lnk in social_links
            if lnk.get("metadata", {}).get("status") == "active"
            and (self.world.get_actor(lnk.get("target_id")) is not None)
            and self.world.get_actor(lnk.get("target_id")).is_alive()
        ]
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

    def handle_key(self, key):
        self.app_router.handle_key(self, key)

    def render_footer(self, stdscr, height, width):
        self.shell_renderer.render_footer(self, stdscr, height, width)

    def render_pending_choice(self, stdscr, height, width):
        self.shell_renderer.render_pending_choice(self, stdscr, height, width)

    def render_menu_popup(self, stdscr, height, width):
        self.shell_renderer.render_menu_popup(self, stdscr, height, width)

    def render_options_popup(self, stdscr, height, width):
        self.shell_renderer.render_options_popup(self, stdscr, height, width)

    def render_quit_confirmation(self, stdscr, height, width):
        self.shell_renderer.render_quit_confirmation(self, stdscr, height, width)

    def _get_logo_layout(self, width):
        return self.shell_renderer.get_logo_layout(width)

    def render_header(self, stdscr, width):
        self.shell_renderer.render_header(self, stdscr, width)

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

    def render(self, stdscr):
        self.app_router.render(self, stdscr)

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
