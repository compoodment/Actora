import curses
import random
import textwrap
from uuid import uuid4

from banners import ACTORA_TITLE_BANNER, QUIT_BANNER
from identity import prepare_parent_identity_context, generate_parent_identity_from_context
from world import World

EVENT_DETAIL_THRESHOLD = 8
EVENT_RECENT_DISPLAY_LIMIT = 5
INPUT_INTERRUPTED_MESSAGE = "Input interrupted. Exiting Actora."
BACK_KEYS = {
    27,
    curses.KEY_BACKSPACE,
    127,
    8,
}


def generate_startup_actor_id(role):
    """Builds one narrow startup actor id without hardcoded singleton values."""
    return f"startup_{role}_{uuid4().hex[:8]}"


def safe_input(prompt):
    """Reads one input value and exits cleanly on interruption/EOF."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print(f"\n{INPUT_INTERRUPTED_MESSAGE}")
        raise SystemExit(0)


def build_snapshot_sections(snapshot_data):
    """Builds shell-owned snapshot sections from structured actor snapshot data."""
    identity = snapshot_data["identity"]
    time_state = snapshot_data["time"]
    location = snapshot_data["location"]
    statistics = snapshot_data["statistics"]
    relationships = snapshot_data["relationships"]

    return [
        (
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
            "Time",
            [
                f"Sim Date: Year {time_state['year']}, Month {time_state['month']}",
            ],
        ),
        (
            "Location",
            [
                f"World Body: {location['world_body_name']}",
                f"Current Place: {location['current_place_name']}",
                f"Jurisdiction: {location['jurisdiction_place_name']}",
            ],
        ),
        (
            "Statistics",
            [
                f"Health: {statistics['health']}",
                f"Happiness: {statistics['happiness']}",
                f"Intelligence: {statistics['intelligence']}",
                f"Money: ${statistics['money']}",
            ],
        ),
        (
            "Relationships",
            [
                f"Mother: {relationships['mother_name']}",
                f"Father: {relationships['father_name']}",
            ],
        ),
    ]


def build_event_lines(turn_result):
    """Builds shell-owned event summary lines for the current turn result."""
    if not turn_result["had_any_events"]:
        return [
            "Recent Activity",
            "No notable events occurred during this period.",
        ]

    total_events = len(turn_result["events"])
    if total_events <= EVENT_DETAIL_THRESHOLD:
        lines = ["Recent Activity"]
        for structured_event in turn_result["events"]:
            lines.append(
                f"[Year {structured_event['year']}, Month {structured_event['month']}] "
                f"{structured_event['text']}"
            )
        return lines

    recent_events = turn_result["events"][-EVENT_RECENT_DISPLAY_LIMIT:]
    omitted_count = total_events - len(recent_events)
    lines = [
        "Recent Activity",
        f"{total_events} notable events occurred.",
        f"Showing the most recent {len(recent_events)}:",
    ]
    for structured_event in recent_events:
        lines.append(
            f"[Year {structured_event['year']}, Month {structured_event['month']}] "
            f"{structured_event['text']}"
        )
    if omitted_count > 0:
        lines.append(f"... {omitted_count} older events omitted.")
    return lines


def build_death_lines(continuity_state):
    """Builds the dead-focus interrupt copy for the TUI shell."""
    lines = [
        "Death",
        "You are dead.",
        continuity_state["focus_actor_name"],
    ]

    death_year = continuity_state["focus_actor_death_year"]
    death_month = continuity_state["focus_actor_death_month"]
    death_reason = continuity_state["focus_actor_death_reason"]

    death_context_parts = []
    if death_year is not None and death_month is not None:
        death_context_parts.append(f"Year {death_year}, Month {death_month}")
    if death_reason:
        death_context_parts.append(death_reason)

    if death_context_parts:
        lines.append(" | ".join(death_context_parts))
    lines.append("The universe continues.")
    return lines


def wrap_text_line(text, width):
    """Wraps one line of text to the available width while preserving blank lines."""
    if width <= 1:
        return [text[:1]]
    if text == "":
        return [""]
    return textwrap.wrap(text, width=width) or [""]


def draw_text_block(stdscr, start_y, start_x, width, height, lines, *, highlight_index=None):
    """Draws a wrapped block of text inside the provided bounds."""
    y = start_y
    for index, raw_line in enumerate(lines):
        wrapped_lines = wrap_text_line(raw_line, width)
        attr = curses.A_REVERSE if highlight_index == index else curses.A_NORMAL
        for wrapped_line in wrapped_lines:
            if y >= start_y + height:
                return y
            stdscr.addnstr(y, start_x, wrapped_line, width, attr)
            y += 1
    return y


class ActoraTUI:
    """Small actor-first curses shell layered on top of the existing world seams."""

    def __init__(self, world, player_id):
        self.world = world
        self.player_id = player_id
        self.screen_name = "main"
        self.running = True
        self.lineage_selection = 0
        self.continuation_selection = 0
        self.selected_lineage_actor_id = None
        self.last_message = "A/Enter advances one month."
        self.last_event_lines = [
            "Recent Activity",
            "No time has passed yet.",
        ]

    def get_focused_actor_id(self):
        return self.world.get_focused_actor_id() or self.player_id

    def get_focused_actor(self):
        return self.world.get_actor(self.get_focused_actor_id())

    def get_snapshot_data(self):
        focused_actor_id = self.get_focused_actor_id()
        focused_actor = self.world.get_actor(focused_actor_id)
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
            if self.screen_name in {"death_ack", "continuation"}:
                self.screen_name = "main"
            return

        if self.screen_name not in {"death_ack", "continuation"}:
            self.screen_name = "death_ack"

    def get_lineage_entries(self):
        return self.world.get_lineage_entries_for(self.get_focused_actor_id())

    def get_lineage_detail(self):
        if self.selected_lineage_actor_id is None:
            return None
        return self.world.get_lineage_detail_for(
            self.get_focused_actor_id(),
            self.selected_lineage_actor_id,
        )

    def get_continuity_state(self):
        return self.world.build_continuity_state_for(self.get_focused_actor_id())

    def advance_one_month(self):
        """Advances time using the existing world-owned simulation seam."""
        turn_result = self.world.simulate_advance_turn(self.player_id, 1)
        self.last_event_lines = build_event_lines(turn_result)
        self.last_message = "Advanced 1 month."
        if turn_result["continuity_state"] is not None and not turn_result["focused_actor_alive"]:
            self.screen_name = "death_ack"

    def open_lineage(self):
        self.lineage_selection = 0
        self.selected_lineage_actor_id = None
        self.screen_name = "lineage"
        self.last_message = "Browsing lineage."

    def open_lineage_detail(self):
        lineage_entries = self.get_lineage_entries()
        if not lineage_entries:
            self.last_message = "No family-linked lineage entries were found."
            return
        self.lineage_selection = max(0, min(self.lineage_selection, len(lineage_entries) - 1))
        self.selected_lineage_actor_id = lineage_entries[self.lineage_selection]["actor_id"]
        self.screen_name = "lineage_detail"

    def acknowledge_death(self):
        continuity_state = self.get_continuity_state()
        self.continuation_selection = 0
        self.screen_name = "continuation"
        if continuity_state["had_continuity_candidates"]:
            self.last_message = "Choose a continuation target."
        else:
            self.last_message = "No valid continuation target exists."

    def choose_continuation(self):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        if not candidates:
            self.running = False
            return

        self.continuation_selection = max(
            0,
            min(self.continuation_selection, len(candidates) - 1),
        )
        successor_actor_id = candidates[self.continuation_selection]["actor_id"]
        handoff_result = self.world.handoff_focus_to_continuation(
            self.get_focused_actor_id(),
            successor_actor_id,
        )
        self.screen_name = "main"
        self.last_message = (
            f"Focus moved from {handoff_result['previous_actor_name']} "
            f"to {handoff_result['new_focused_actor_name']}."
        )
        self.last_event_lines = [
            "Recent Activity",
            self.last_message,
        ]

    def handle_main_key(self, key):
        if key in (ord("q"), ord("Q")):
            self.running = False
        elif key in (curses.KEY_ENTER, 10, 13, ord("a"), ord("A")):
            self.advance_one_month()
        elif key in (ord("l"), ord("L")):
            self.open_lineage()

    def handle_lineage_key(self, key):
        lineage_entries = self.get_lineage_entries()
        if key in BACK_KEYS or key in (ord("q"), ord("Q")):
            self.screen_name = "main"
            self.last_message = "Returned to actor view."
            return
        if not lineage_entries:
            return
        if key == curses.KEY_UP:
            self.lineage_selection = max(0, self.lineage_selection - 1)
        elif key == curses.KEY_DOWN:
            self.lineage_selection = min(len(lineage_entries) - 1, self.lineage_selection + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            self.open_lineage_detail()

    def handle_lineage_detail_key(self, key):
        if key in BACK_KEYS or key in (ord("q"), ord("Q")):
            self.screen_name = "lineage"
            self.last_message = "Returned to lineage list."

    def handle_death_ack_key(self, key):
        if key in (ord("q"), ord("Q")):
            self.running = False
        elif key in (curses.KEY_ENTER, 10, 13):
            self.acknowledge_death()

    def handle_continuation_key(self, key):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        if key in (ord("q"), ord("Q")):
            self.running = False
            return
        if not candidates:
            return
        if key == curses.KEY_UP:
            self.continuation_selection = max(0, self.continuation_selection - 1)
        elif key == curses.KEY_DOWN:
            self.continuation_selection = min(
                len(candidates) - 1,
                self.continuation_selection + 1,
            )
        elif key in (curses.KEY_ENTER, 10, 13):
            self.choose_continuation()

    def handle_key(self, key):
        self.sync_focus_state()
        if self.screen_name == "main":
            self.handle_main_key(key)
        elif self.screen_name == "lineage":
            self.handle_lineage_key(key)
        elif self.screen_name == "lineage_detail":
            self.handle_lineage_detail_key(key)
        elif self.screen_name == "death_ack":
            self.handle_death_ack_key(key)
        elif self.screen_name == "continuation":
            self.handle_continuation_key(key)

    def render_footer(self, stdscr, height, width):
        footer_hints = {
            "main": "A/Enter advance   L lineage   Q quit",
            "lineage": "Up/Down move   Enter inspect   Esc/Backspace/Q back",
            "lineage_detail": "Esc/Backspace/Q back",
            "death_ack": "Enter acknowledge   Q quit",
            "continuation": "Up/Down move   Enter continue   Q quit",
        }
        footer_text = footer_hints.get(self.screen_name, "")
        stdscr.hline(height - 2, 0, curses.ACS_HLINE, width)
        stdscr.addnstr(height - 1, 0, footer_text.ljust(width), width, curses.A_REVERSE)

    def render_main(self, stdscr, height, width):
        snapshot_data = self.get_snapshot_data()
        snapshot_sections = build_snapshot_sections(snapshot_data)
        identity_name = snapshot_data["identity"]["full_name"]

        lines = [f"Actora | {identity_name}", self.last_message, ""]
        for section_title, section_lines in snapshot_sections:
            lines.append(section_title)
            lines.extend(f"  {line}" for line in section_lines)
            lines.append("")
        lines.extend(self.last_event_lines)
        draw_text_block(stdscr, 0, 0, width, height - 2, lines)

    def render_lineage(self, stdscr, height, width):
        lineage_entries = self.get_lineage_entries()
        lines = ["Lineage", self.last_message, ""]
        highlight_index = None

        if not lineage_entries:
            lines.append("No family-linked lineage entries were found.")
        else:
            self.lineage_selection = max(0, min(self.lineage_selection, len(lineage_entries) - 1))
            for entry in lineage_entries:
                if entry["is_alive"]:
                    line = (
                        f"{entry['full_name']} [{entry['relationship_label']}] "
                        f"- Age {entry['age']} - {entry['current_place_name']}"
                    )
                else:
                    line = (
                        f"{entry['full_name']} [{entry['relationship_label']}] "
                        f"- {entry['birth_date']} / {entry['death_date']} "
                        f"- {entry['death_reason']} - {entry['current_place_name']}"
                    )
                if len(lines) == 3 + self.lineage_selection:
                    highlight_index = len(lines)
                lines.append(line)

        draw_text_block(stdscr, 0, 0, width, height - 2, lines, highlight_index=highlight_index)

    def render_lineage_detail(self, stdscr, height, width):
        lineage_detail = self.get_lineage_detail()
        if lineage_detail is None:
            self.screen_name = "lineage"
            self.render_lineage(stdscr, height, width)
            return

        summary = lineage_detail["summary"]
        records = lineage_detail["records"]
        lines = [
            f"Lineage Detail | {summary['full_name']}",
            "",
            f"Relationship: {summary['relationship_label']}",
            f"Species: {summary['species']}",
            f"Sex: {summary['sex']}",
            f"Gender: {summary['gender']}",
            f"Status: {summary['structural_status'].title()}",
            (
                f"Age at Death: {summary['age']}"
                if summary["death_date"] is not None
                else f"Age: {summary['age']}"
            ),
            f"Life Stage: {summary['life_stage']}",
            f"Born: {summary['birth_date']}",
        ]
        if summary["death_date"] is not None:
            lines.append(f"Died: {summary['death_date']}")
            lines.append(f"Cause of Death: {summary['death_reason']}")
        lines.extend(
            [
                f"Place: {summary['current_place_name']}",
                "",
                "Core Statistics",
                f"  Health: {summary['health']}",
                f"  Happiness: {summary['happiness']}",
                f"  Intelligence: {summary['intelligence']}",
                f"  Money: ${summary['money']}",
                "",
                "Recent Records",
            ]
        )
        if not records:
            lines.append("  No records found.")
        else:
            for record in records:
                lines.append(
                    f"  [{record['year']:04d}-{record['month']:02d}] "
                    f"({record['record_type']}) {record['text']}"
                )
        draw_text_block(stdscr, 0, 0, width, height - 2, lines)

    def render_death_ack(self, stdscr, height, width):
        continuity_state = self.get_continuity_state()
        draw_text_block(
            stdscr,
            0,
            0,
            width,
            height - 2,
            build_death_lines(continuity_state),
        )

    def render_continuation(self, stdscr, height, width):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        lines = ["Continuation", self.last_message, ""]
        highlight_index = None

        if not candidates:
            lines.append("No living connected continuation candidates were found.")
            lines.append("Press Q to quit this run.")
        else:
            self.continuation_selection = max(
                0,
                min(self.continuation_selection, len(candidates) - 1),
            )
            for candidate in candidates:
                line = (
                    f"{candidate['full_name']} [{candidate['relationship_label']}] "
                    f"- Age {candidate['age']} ({candidate['life_stage']}) "
                    f"- {candidate['current_place_name'] or 'Unknown'}"
                )
                if len(lines) == 3 + self.continuation_selection:
                    highlight_index = len(lines)
                lines.append(line)

        draw_text_block(stdscr, 0, 0, width, height - 2, lines, highlight_index=highlight_index)

    def render(self, stdscr):
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        if height < 12 or width < 50:
            stdscr.addnstr(0, 0, "Terminal too small for Actora TUI. Resize and try again.", width - 1)
            return

        if self.screen_name == "main":
            self.render_main(stdscr, height, width)
        elif self.screen_name == "lineage":
            self.render_lineage(stdscr, height, width)
        elif self.screen_name == "lineage_detail":
            self.render_lineage_detail(stdscr, height, width)
        elif self.screen_name == "death_ack":
            self.render_death_ack(stdscr, height, width)
        elif self.screen_name == "continuation":
            self.render_continuation(stdscr, height, width)

        self.render_footer(stdscr, height, width)
        stdscr.refresh()

    def run(self, stdscr):
        """Runs the narrow curses shell until the user quits or the run ends."""
        curses.curs_set(0)
        stdscr.keypad(True)

        while self.running:
            self.sync_focus_state()
            self.render(stdscr)
            key = stdscr.getch()
            self.handle_key(key)


def create_character():
    """Handles the character creation flow and returns player details."""
    print("\n--- Character Creation ---")

    while True:
        player_first_name = safe_input("Enter your character's first name: ").strip()
        if player_first_name:
            break
        print("First name cannot be empty. Please enter a name.")

    player_last_name = safe_input("Enter your character's last name (optional): ").strip()

    sex_options = ["Male", "Female", "Intersex"]
    print("\nSelect biological sex:")
    for i, option in enumerate(sex_options, 1):
        print(f"  {i}) {option}")
    while True:
        try:
            choice = int(safe_input(f"Enter choice (1-{len(sex_options)}): ").strip())
            if 1 <= choice <= len(sex_options):
                player_sex = sex_options[choice - 1]
                break
            print("Invalid number. Please choose from the options.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    gender_options = ["Male", "Female", "Non-binary", "Agender", "Genderfluid", "Other"]
    print("\nSelect gender identity:")
    for i, option in enumerate(gender_options, 1):
        print(f"  {i}) {option}")
    while True:
        try:
            choice = int(safe_input(f"Enter choice (1-{len(gender_options)}): ").strip())
            if 1 <= choice <= len(gender_options):
                selected_gender = gender_options[choice - 1]
                if selected_gender == "Other":
                    while True:
                        custom_gender = safe_input("Enter your gender identity: ").strip()
                        if custom_gender:
                            player_gender = custom_gender
                            break
                        print("Gender identity cannot be empty. Please enter a value.")
                else:
                    player_gender = selected_gender
                break
            print("Invalid number. Please choose from the options.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print("--------------------------")
    return player_first_name, player_last_name, player_sex, player_gender


def setup_initial_world(player_first_name, player_last_name, player_sex, player_gender):
    """Initializes the world and sets up the player and parents."""
    world = World(start_year=1, start_month=1)
    world.add_place(
        place_id="earth",
        name="Earth",
        kind="world_body",
        parent_place_id=None,
        metadata={},
    )
    world.add_place(
        place_id="earth_country_01",
        name="Starter Country",
        kind="country",
        parent_place_id="earth",
        metadata={},
    )
    world.add_place(
        place_id="earth_city_01",
        name="Starter City",
        kind="city",
        parent_place_id="earth_country_01",
        metadata={},
    )

    startup_place_id = "earth_city_01"
    startup_jurisdiction_place_id = "earth_country_01"

    mother_identity_context = prepare_parent_identity_context(
        role="mother",
        player_last_name=player_last_name,
        place_id=startup_place_id,
        world=world,
    )
    family_last_name = mother_identity_context["family_last_name"]
    father_identity_context = prepare_parent_identity_context(
        role="father",
        family_last_name=family_last_name,
        player_last_name=player_last_name,
        place_id=startup_place_id,
        world=world,
    )

    mother_identity = generate_parent_identity_from_context(mother_identity_context)
    father_identity = generate_parent_identity_from_context(father_identity_context)

    mother_id = generate_startup_actor_id("mother")
    father_id = generate_startup_actor_id("father")
    world.create_human_actor(
        actor_id=mother_id,
        species="Human",
        first_name=mother_identity["first_name"],
        last_name=mother_identity["last_name"],
        sex=mother_identity["sex"],
        gender=mother_identity["gender"],
        birth_year=world.current_year - 25,
        birth_month=random.randint(1, 12),
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
    )
    world.create_human_actor(
        actor_id=father_id,
        species="Human",
        first_name=father_identity["first_name"],
        last_name=father_identity["last_name"],
        sex=father_identity["sex"],
        gender=father_identity["gender"],
        birth_year=world.current_year - 27,
        birth_month=random.randint(1, 12),
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
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

    player_id = generate_startup_actor_id("player")
    world.create_human_child_with_parents(
        child_id=player_id,
        first_name=player_first_name,
        last_name=player_last_name,
        sex=player_sex,
        gender=player_gender,
        mother_id=mother_id,
        father_id=father_id,
        birth_year=world.current_year,
        birth_month=1,
        place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=True,
    )
    world.set_focused_actor(player_id)

    return world, player_id


def run_game_tui(world, player_id):
    """Runs the actor-first curses shell for ordinary play."""
    tui = ActoraTUI(world, player_id)
    try:
        curses.wrapper(tui.run)
    except KeyboardInterrupt:
        pass
    print(QUIT_BANNER)


def start_game():
    print(ACTORA_TITLE_BANNER)

    player_first_name, player_last_name, player_sex, player_gender = create_character()
    world, player_id = setup_initial_world(
        player_first_name,
        player_last_name,
        player_sex,
        player_gender,
    )
    run_game_tui(world, player_id)


if __name__ == "__main__":
    start_game()
