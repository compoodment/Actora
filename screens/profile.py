"""Profile screen controller and renderer."""

import curses
import time

from ui import draw_box, get_content_bounds, get_scroll_window, truncate_for_width
from views.profile import build_profile_popup_render_data, build_profile_summary_rows


class ProfileScreen:
    """Owns profile-screen input handling and rendering.

    ActoraTUI remains the application shell. This screen object deliberately receives
    the shell instance as `app` so this extraction can stay behavior-preserving while
    pulling profile-specific control flow out of the monolith.
    """

    def __init__(self, categories, back_keys, advance_throttle_seconds, main_idle_message):
        self.categories = categories
        self.back_keys = back_keys
        self.advance_throttle_seconds = advance_throttle_seconds
        self.main_idle_message = main_idle_message

    def handle_key(self, app, key):
        if app.profile_popup_open:
            if key in self.back_keys:
                app.profile_popup_open = False
                app.profile_popup_category = None
                app.profile_popup_scroll = 0
                return
            if key == 27:
                app.options_popup_active = True
                app.options_selection = 0
                return
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
            popup_data = build_profile_popup_render_data(
                app.profile_popup_category or self.categories[app.profile_selected_row],
                app.get_snapshot_data(),
                getattr(app, "_profile_content_width", 88),
                app.profile_body_height,
            )
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                app.profile_popup_scroll = max(0, app.profile_popup_scroll - 1)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                app.profile_popup_scroll = min(popup_data["max_scroll"], app.profile_popup_scroll + 1)
            return

        if key == 27:
            app.options_popup_active = True
            app.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - app.last_advance_time < self.advance_throttle_seconds:
                return
            app.last_advance_time = now
            app.advance_one_month()
        elif key in (ord("e"), ord("E")):
            app.open_skip_time()
        elif key in self.back_keys:
            app.screen_name = "main"
            app.last_message = self.main_idle_message
        elif key in (curses.KEY_UP, ord("w"), ord("W")):
            app.profile_selected_row = max(0, app.profile_selected_row - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            app.profile_selected_row = min(len(self.categories) - 1, app.profile_selected_row + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            app.profile_popup_open = True
            app.profile_popup_category = self.categories[app.profile_selected_row]
            app.profile_popup_scroll = 0

    def render(self, app, stdscr, height, width):
        top = app.HEADER_ROWS
        body_height = height - app.HEADER_ROWS - app.FOOTER_ROWS
        app._profile_body_height = body_height
        content_left, content_width = get_content_bounds(width, max_width=88)
        app._profile_content_width = content_width
        snapshot_data = app.get_snapshot_data()
        summary_rows = build_profile_summary_rows(snapshot_data)
        for index, (_category, label) in enumerate(summary_rows[:body_height]):
            attr = curses.A_REVERSE if index == app.profile_selected_row else curses.A_NORMAL
            stdscr.addnstr(
                top + index,
                content_left,
                truncate_for_width(label, content_width).ljust(content_width),
                content_width,
                attr,
            )

        if not app.profile_popup_open:
            return

        popup_data = build_profile_popup_render_data(
            app.profile_popup_category or self.categories[app.profile_selected_row],
            snapshot_data,
            content_width,
            body_height,
        )
        app.profile_popup_scroll = min(app.profile_popup_scroll, popup_data["max_scroll"])
        popup_width = popup_data["popup_width"]
        popup_height = popup_data["popup_height"]
        popup_left = max(content_left, content_left + (content_width - popup_width) // 2)
        popup_top = max(top + 1, top + (body_height - popup_height) // 2)
        title = popup_data["category"].replace("_", " ").title()

        draw_box(stdscr, popup_top, popup_left, popup_height, popup_width, title=title)

        visible_lines, _, _, _ = get_scroll_window(
            popup_data["rendered_lines"],
            popup_data["visible_content_height"],
            app.profile_popup_scroll,
        )
        for row_offset in range(popup_data["visible_content_height"]):
            row = popup_top + 1 + row_offset
            line = visible_lines[row_offset] if row_offset < len(visible_lines) else ""
            if row < top + body_height and popup_left + 1 < content_left + content_width:
                stdscr.addnstr(row, popup_left + 1, line.ljust(popup_width - 2), popup_width - 2)
