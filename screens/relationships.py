"""Relationship browser screen controller and renderer."""

import curses
import time

from ui import center_text, draw_text_block, draw_truncated_block, draw_vertical_divider, get_content_bounds
from views.browser import build_lineage_row, build_record_summary_lines
from views.profile import build_person_card_lines


class RelationshipBrowserScreen:
    """Owns relationship-browser input handling and rendering."""

    def __init__(self, filter_options, filter_labels, back_keys, advance_throttle_seconds, main_idle_message):
        self.filter_options = filter_options
        self.filter_labels = filter_labels
        self.back_keys = back_keys
        self.advance_throttle_seconds = advance_throttle_seconds
        self.main_idle_message = main_idle_message

    def handle_key(self, app, key, *, back_to="main"):
        if app.rel_browser_search_active:
            if key == 27:
                app.rel_browser_search_active = False
                app.rel_browser_search_text = ""
                app.lineage_selection = 0
                app.selected_lineage_actor_id = None
                app.last_message = "Search canceled."
                return
            if key in (curses.KEY_ENTER, 10, 13):
                app.rel_browser_search_active = False
                app.lineage_selection = 0
                app.selected_lineage_actor_id = None
                if app.rel_browser_search_text:
                    app.last_message = f"Search: {app.rel_browser_search_text}."
                else:
                    app.last_message = "Search cleared."
                return
            if key == curses.KEY_BACKSPACE or key in (127, 8):
                if app.rel_browser_search_text:
                    app.rel_browser_search_text = app.rel_browser_search_text[:-1]
                    app.lineage_selection = 0
                    app.selected_lineage_actor_id = None
                return
            if 32 <= key <= 126 and len(app.rel_browser_search_text) < 24:
                app.rel_browser_search_text += chr(key)
                app.lineage_selection = 0
                app.selected_lineage_actor_id = None
                return

        browser_state = app.get_relationship_browser_state()
        entries = browser_state["entries"]

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

        if key == ord("/"):
            app.rel_browser_search_active = True
            app.last_message = "Type to search names. Enter confirms. Esc cancels."
            return
        if app.rel_browser_focus == "filters":
            if key in self.back_keys:
                app.screen_name = back_to
                app.last_message = self.main_idle_message
                return
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                app.rel_filter_index = max(0, app.rel_filter_index - 1)
                app.lineage_selection = 0
                app.selected_lineage_actor_id = None
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                app.rel_filter_index = min(len(self.filter_options) - 1, app.rel_filter_index + 1)
                app.lineage_selection = 0
                app.selected_lineage_actor_id = None
            elif key in (9, curses.KEY_RIGHT, ord("d"), ord("D")):
                app.rel_browser_focus = "actors"
                app.last_message = "Browsing people."
        else:
            if key in (curses.KEY_LEFT, ord("a"), ord("A")) or key in self.back_keys:
                app.rel_browser_focus = "filters"
                app.last_message = "Browsing relationships."
                return
            if not entries:
                return
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                app.lineage_selection = max(0, app.lineage_selection - 1)
                app.selected_lineage_actor_id = entries[app.lineage_selection]["actor_id"]
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                app.lineage_selection = min(len(entries) - 1, app.lineage_selection + 1)
                app.selected_lineage_actor_id = entries[app.lineage_selection]["actor_id"]
            elif key in (curses.KEY_ENTER, 10, 13):
                if entries:
                    app.last_message = f"Inspecting {entries[app.lineage_selection]['full_name']}."

    def render(self, app, stdscr, height, width):
        browser_state = app.get_relationship_browser_state()
        entries = browser_state["entries"]
        selected_detail = browser_state["selected_detail"]

        top = app.HEADER_ROWS + app.BROWSER_CHROME_ROWS
        body_height = height - app.HEADER_ROWS - app.BROWSER_CHROME_ROWS - app.FOOTER_ROWS
        content_left, content_width = get_content_bounds(width, max_width=120)

        filter_col_width = 12
        gap = 2
        remaining_width = content_width - filter_col_width - gap
        actor_col_width = remaining_width * 5 // 10
        detail_left = content_left + filter_col_width + gap + actor_col_width + gap
        detail_width = max(20, content_width - filter_col_width - gap - actor_col_width - gap)
        actor_left = content_left + filter_col_width + gap

        filter_lines = []
        filter_highlight = None
        for idx, fkey in enumerate(self.filter_options):
            if idx == app.rel_filter_index:
                filter_highlight = len(filter_lines)
            marker = ">" if app.rel_browser_focus == "filters" and idx == app.rel_filter_index else " "
            filter_lines.append(f"{marker} {self.filter_labels[fkey]}")

        draw_truncated_block(
            stdscr, top, content_left, filter_col_width, body_height, filter_lines,
            highlight_index=filter_highlight,
        )

        divider1_x = content_left + filter_col_width + 1
        draw_vertical_divider(stdscr, top, divider1_x, body_height)

        actor_lines = []
        actor_highlight = None
        search_status = app.get_rel_browser_search_status()
        if search_status:
            actor_lines.append(search_status)
            actor_lines.append("")
        if not entries:
            actor_lines.append("No entries.")
        else:
            search_offset = len(actor_lines)
            for index, entry in enumerate(entries):
                if index == app.lineage_selection and app.rel_browser_focus == "actors":
                    actor_highlight = search_offset + index
                actor_lines.append(build_lineage_row(entry))

        draw_truncated_block(
            stdscr, top, actor_left, actor_col_width, body_height, actor_lines,
            highlight_index=actor_highlight,
        )

        divider2_x = detail_left - 1
        draw_vertical_divider(stdscr, top, divider2_x, body_height)

        if selected_detail is None:
            right_lines = [
                center_text("SELECTED PERSON", detail_width),
                "",
                "No detail available.",
            ]
        else:
            summary = selected_detail["summary"]
            records = selected_detail["records"]
            right_lines = []
            right_lines.append(center_text("SELECTED PERSON", detail_width))
            right_lines.append("")
            right_lines.extend(build_person_card_lines(summary))
            link_type = summary.get("link_type", "family")
            if link_type == "social":
                closeness = summary.get("closeness", 0)
                social_status = summary.get("social_status", "active")
                right_lines.extend([
                    "",
                    f"Social: {summary['relationship_label']}",
                    f"Closeness: {closeness}   Status: {'past' if social_status == 'former' else social_status}",
                ])
            else:
                right_lines.extend([
                    "",
                    "Identity",
                    f"Species: {summary['species']}",
                    f"Sex: {summary['sex']}",
                    f"Condition: Health {summary['health']}   Happiness {summary['happiness']}",
                ])
            right_lines.extend(["", "Recent Records"])
            right_lines.extend(build_record_summary_lines(records))

        draw_text_block(stdscr, top, detail_left, detail_width, body_height, right_lines)
