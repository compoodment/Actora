"""History screen controller and renderer."""

import curses
import time

from ui import draw_text_block, get_content_bounds, get_scroll_window, truncate_for_width
from views.history import expand_render_lines


class HistoryScreen:
    """Owns history-screen input handling and rendering."""

    def __init__(self, back_keys, advance_throttle_seconds, main_idle_message):
        self.back_keys = back_keys
        self.advance_throttle_seconds = advance_throttle_seconds
        self.main_idle_message = main_idle_message

    def handle_key(self, app, key):
        if app.history_search_active:
            if key == 27:
                app.history_search_active = False
                app.history_search_value = ""
                app.last_message = "Year jump canceled."
                return
            if key in (curses.KEY_ENTER, 10, 13):
                typed_year = int(app.history_search_value) if app.history_search_value else 1
                app.jump_history_to_year(typed_year)
                app.history_search_active = False
                app.history_search_value = ""
                return
            if key == curses.KEY_BACKSPACE or key in (127, 8):
                app.history_search_value = app.history_search_value[:-1]
                return
            if ord("0") <= key <= ord("9") and len(app.history_search_value) < 9:
                app.history_search_value += chr(key)
                return
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
            app.history_search_active = False
            app.history_search_value = ""
            app.last_message = self.main_idle_message
        elif key == ord("/"):
            app.history_search_active = True
            app.history_search_value = ""
            app.history_scroll = 0
            app.last_message = "Type a year number. Enter jumps. Esc cancels."
        elif key in (curses.KEY_UP, ord("w"), ord("W")):
            app.history_scroll = max(0, app.history_scroll - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            app.history_scroll += 1

    def render(self, app, stdscr, height, width):
        top = app.HEADER_ROWS + app.BROWSER_CHROME_ROWS
        body_height = height - app.HEADER_ROWS - app.BROWSER_CHROME_ROWS - app.FOOTER_ROWS
        app._history_body_height = body_height
        content_left, content_width = get_content_bounds(width, max_width=104)
        app._history_content_width = content_width
        history_lines = expand_render_lines(app.get_history_lines(content_width), content_width)
        search_status = app.get_history_search_status()
        if search_status:
            history_lines = [search_status, ""] + history_lines
        content_body_height = body_height
        if len(history_lines) > body_height:
            content_body_height = max(1, body_height - 1)
        visible_lines, app.history_scroll, _, total_lines = get_scroll_window(
            history_lines,
            content_body_height,
            app.history_scroll,
        )
        draw_text_block(stdscr, top, content_left, content_width, content_body_height, visible_lines)

        if total_lines > content_body_height:
            scroll_label = (
                f"History: {app.history_scroll + 1}-"
                f"{app.history_scroll + len(visible_lines)} / {total_lines}"
            )
            stdscr.addnstr(
                min(height - 3, top + content_body_height),
                content_left,
                truncate_for_width(scroll_label, content_width),
                content_width,
                curses.A_DIM,
            )
