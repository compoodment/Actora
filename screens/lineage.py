"""Lineage screen controller and renderer."""

import curses
import time

from ui import (
    center_text,
    draw_text_block,
    draw_truncated_block,
    draw_vertical_divider,
    get_content_bounds,
    split_centered_columns,
)
from views.browser import build_lineage_row, build_record_summary_lines
from views.profile import build_person_card_lines


class LineageScreen:
    """Owns lineage-browser input handling and rendering."""

    def __init__(self, filter_labels, back_keys, advance_throttle_seconds, main_idle_message):
        self.filter_labels = filter_labels
        self.back_keys = back_keys
        self.advance_throttle_seconds = advance_throttle_seconds
        self.main_idle_message = main_idle_message

    def handle_key(self, app, key):
        if app.lineage_search_active:
            if key == 27:
                app.lineage_search_active = False
                app.last_message = "Returned to lineage."
                return
            if key in (curses.KEY_ENTER, 10, 13):
                app.lineage_search_active = False
                app.lineage_selection = 0
                app.selected_lineage_actor_id = None
                if app.lineage_search_text:
                    app.last_message = f"Lineage search: {app.lineage_search_text}."
                else:
                    app.last_message = "Lineage search cleared."
                return
            if key == curses.KEY_BACKSPACE or key in (127, 8):
                if app.lineage_search_text:
                    app.lineage_search_text = app.lineage_search_text[:-1]
                    app.lineage_selection = 0
                    app.selected_lineage_actor_id = None
                return
            if 32 <= key <= 126 and len(app.lineage_search_text) < 24:
                app.lineage_search_text += chr(key)
                app.lineage_selection = 0
                app.selected_lineage_actor_id = None
                return

        lineage_entries = app.get_lineage_entries()
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - app.last_advance_time < self.advance_throttle_seconds:
                return
            app.last_advance_time = now
            app.advance_one_month()
            return
        if key in (ord("e"), ord("E")):
            app.open_skip_time()
            return
        if key in self.back_keys:
            app.screen_name = "main"
            app.lineage_search_active = False
            app.last_message = self.main_idle_message
            return
        if key in (ord("a"), ord("A")):
            app.set_lineage_filter_mode("all")
            return
        if key in (ord("l"), ord("L")):
            app.set_lineage_filter_mode("living")
            return
        if key in (ord("d"), ord("D")):
            app.set_lineage_filter_mode("dead")
            return
        if key == ord("/"):
            app.lineage_search_active = True
            app.last_message = "Type to search lineage names. Enter confirms. Esc cancels search."
            return
        if not lineage_entries:
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            app.lineage_selection = max(0, app.lineage_selection - 1)
            app.selected_lineage_actor_id = lineage_entries[app.lineage_selection]["actor_id"]
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            app.lineage_selection = min(len(lineage_entries) - 1, app.lineage_selection + 1)
            app.selected_lineage_actor_id = lineage_entries[app.lineage_selection]["actor_id"]
        elif key in (curses.KEY_ENTER, 10, 13):
            app.last_message = f"Inspecting {lineage_entries[app.lineage_selection]['full_name']}."

    def render(self, app, stdscr, height, width):
        browser_state = app.get_lineage_browser_state()
        lineage_entries = browser_state["entries"]
        selected_detail = browser_state["selected_detail"]

        top = app.HEADER_ROWS + app.BROWSER_CHROME_ROWS
        body_height = height - app.HEADER_ROWS - app.BROWSER_CHROME_ROWS - app.FOOTER_ROWS
        content_left, content_width = get_content_bounds(width, max_width=112)
        left_width, right_left, right_width = split_centered_columns(content_left, content_width)
        filter_label = self.filter_labels[browser_state["filter_mode"]]
        left_lines = [
            f"Archive • {filter_label} • {browser_state['result_count']} result(s)",
            app.get_lineage_search_status(),
            "",
        ]
        highlight_index = None
        if not lineage_entries:
            left_lines.append("No lineage entries match the current filter/search.")
        else:
            for index, entry in enumerate(lineage_entries):
                if index == app.lineage_selection:
                    highlight_index = len(left_lines)
                left_lines.append(build_lineage_row(entry))

        draw_truncated_block(
            stdscr,
            top,
            content_left,
            left_width,
            body_height,
            left_lines,
            highlight_index=highlight_index,
        )

        divider_x = right_left - 2
        draw_vertical_divider(stdscr, top, divider_x, body_height)

        if selected_detail is None:
            right_lines = [
                center_text("SELECTED PERSON", right_width),
                "",
                "No lineage detail available.",
                "",
                "Try another filter or search.",
            ]
        else:
            summary = selected_detail["summary"]
            records = selected_detail["records"]
            right_lines = []
            right_lines.append(center_text("SELECTED PERSON", right_width))
            right_lines.append("")
            right_lines.extend(build_person_card_lines(summary))
            right_lines.extend(
                [
                    "",
                    "Identity",
                    f"Species: {summary['species']}",
                    f"Sex: {summary['sex']}",
                    f"Gender: {summary['gender']}",
                    f"Condition: Health {summary['health']}   Happiness {summary['happiness']}   Intelligence {summary['intelligence']}",
                    f"Resources: ${summary['money']}",
                    "",
                    "Recent Records",
                ]
            )
            right_lines.extend(build_record_summary_lines(records))

        draw_text_block(stdscr, top, right_left, right_width, body_height, right_lines)
