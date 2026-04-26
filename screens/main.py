"""Main life-view screen controller and renderer."""

import curses
import time

from ui import draw_text_block, draw_vertical_divider, get_content_bounds, get_scroll_window, truncate_for_width
from views.history import build_live_feed_lines, expand_render_lines


class MainScreen:
    """Owns the main dashboard input handling and rendering."""

    def __init__(self, left_section_keys, advance_throttle_seconds, main_idle_message):
        self.left_section_keys = left_section_keys
        self.advance_throttle_seconds = advance_throttle_seconds
        self.main_idle_message = main_idle_message

    def handle_key(self, app, key):
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - app.last_advance_time < self.advance_throttle_seconds:
                return
            app.last_advance_time = now
            app.advance_one_month()
        elif key in (ord("e"), ord("E")):
            app.open_skip_time()
        elif key == ord("1"):
            app.menu_popup_active = not app.menu_popup_active
            app.menu_selection = 0
        elif key == 27:
            app.options_popup_active = not app.options_popup_active
            if app.options_popup_active:
                app.options_selection = 0
            else:
                app.last_message = self.main_idle_message
        elif key in (ord("w"), ord("W"), curses.KEY_UP):
            app.scroll_main_left(-1)
        elif key in (ord("s"), ord("S"), curses.KEY_DOWN):
            app.scroll_main_left(1)

    def render(self, app, stdscr, height, width):
        snapshot_data = app.get_snapshot_data()
        snapshot_sections = build_snapshot_sections(snapshot_data)
        top = app.HEADER_ROWS
        body_height = height - app.HEADER_ROWS - app.FOOTER_ROWS
        app._main_body_height = body_height
        content_left, content_width = get_content_bounds(width, max_width=112)
        _, _logo_w, logo_center = app._get_logo_layout(width)
        divider_x = logo_center
        left_width = divider_x - content_left - 1
        right_left = divider_x + 2
        right_width = content_left + content_width - right_left

        left_sections = [
            section
            for section in snapshot_sections
            if section["key"] in self.left_section_keys
        ]
        left_lines = [app.last_message, ""]
        left_lines.extend(app.build_main_left_lines(left_sections, include_time=False))
        visible_left_lines, app.main_left_scroll, main_left_max_offset, total_left_lines = get_scroll_window(
            left_lines,
            body_height,
            app.main_left_scroll,
        )
        right_lines = expand_render_lines(build_live_feed_lines(app.event_log), right_width)
        visible_right_lines, _, _, _ = get_scroll_window(
            right_lines,
            body_height,
            max(0, len(right_lines) - body_height),
        )

        draw_text_block(stdscr, top, content_left, left_width, body_height, visible_left_lines)
        draw_vertical_divider(stdscr, top, divider_x, body_height)
        draw_text_block(stdscr, top, right_left, right_width, body_height, visible_right_lines)

        if main_left_max_offset > 0:
            scroll_label = f"More details: {app.main_left_scroll + 1}-{app.main_left_scroll + len(visible_left_lines)} / {total_left_lines}"
            stdscr.addnstr(
                min(height - 3, top + body_height - 1),
                content_left,
                truncate_for_width(scroll_label, left_width),
                left_width,
                curses.A_DIM,
            )


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
