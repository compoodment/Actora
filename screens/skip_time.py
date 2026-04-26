"""Skip-time screen controller and renderer."""

import curses

from ui import center_text, draw_text_block, get_content_bounds


class SkipTimeScreen:
    """Owns skip-time input handling and rendering."""

    def __init__(self, presets, back_keys, main_idle_message):
        self.presets = presets
        self.back_keys = back_keys
        self.main_idle_message = main_idle_message

    def handle_key(self, app, key):
        if key == 27:
            app.options_popup_active = True
            app.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            return
        if key == curses.KEY_BACKSPACE or key in (127, 8):
            if app.skip_custom_value:
                app.skip_custom_value = app.skip_custom_value[:-1]
            else:
                app.screen_name = "main"
                app.last_message = self.main_idle_message
            return
        if key in self.back_keys:
            app.screen_name = "main"
            app.last_message = self.main_idle_message
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            app.skip_selection = max(0, app.skip_selection - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            app.skip_selection = min(len(self.presets) - 1, app.skip_selection + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            app.confirm_skip_selection()
        elif ord("0") <= key <= ord("9"):
            if len(app.skip_custom_value) < 4:
                app.skip_custom_value += chr(key)

    def render(self, app, stdscr, height, width):
        custom_months = app.get_custom_skip_months()
        selected_months = app.get_selected_skip_months()
        content_left, content_width = get_content_bounds(width, max_width=76)
        lines = [
            center_text("TIME JUMP", content_width),
            "",
            app.last_message,
            "",
            "Presets",
        ]
        highlight_index = 5 + app.skip_selection
        for preset_months in self.presets:
            label = "month" if preset_months == 1 else "months"
            lines.append(f"{preset_months:>2} {label}")
        lines.extend(
            [
                "",
                "Custom Months",
                (
                    f"Typed value: {app.skip_custom_value} months"
                    if app.skip_custom_value
                    else "Typed value: none"
                ),
                (
                    f"Enter will advance {custom_months} months from the custom value."
                    if custom_months is not None
                    else f"Enter will advance {selected_months} months from the selected preset."
                ),
            ]
        )
        draw_text_block(
            stdscr,
            app.HEADER_ROWS,
            content_left,
            content_width,
            height - app.HEADER_ROWS - app.FOOTER_ROWS,
            lines,
            highlight_index=highlight_index,
        )
