"""Global shell chrome, footer, and popup rendering."""

import curses

from ui import (
    center_text,
    draw_box,
    draw_panel_text,
    get_content_bounds,
    wrap_text_line,
)
from views.shell import build_screen_chrome


class ShellRenderer:
    """Owns global chrome and overlay rendering for the TUI shell."""

    LOGO_LINES = [
        "╗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄╔",
        "║█░░▒▒▓█▄░▄█▓▒▒░░█║",
        "║█░▒▒▓█▀░▄░▀█▓▒▒░█║",
        "║█░▒▒▓█▒▒█▒▒█▓▒▒░█║",
        "║█░▒▒▓█▄▀▓▀▄█▓▒▒░█║",
        "║█░░▒▒▓█▓▄▓█▓▒▒░░█║",
        "╝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀╚",
    ]

    MENU_ITEMS = ["Browser", "Actions", "Profile"]
    OPTION_ITEMS = ["Quit Game", "Help / Controls", "Settings"]

    def get_logo_layout(self, width):
        """Returns (logo_x, logo_w, logo_center), the canonical horizontal shell anchor."""
        logo_w = max(len(line) for line in self.LOGO_LINES)
        logo_x = (max(1, width - 1) - logo_w) // 2
        logo_center = logo_x + logo_w // 2
        return logo_x, logo_w, logo_center

    def render_footer(self, app, stdscr, height, width):
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
        if app.screen_name == "lineage" and app.lineage_search_active:
            footer_text = footer_hints["lineage_search"]
        elif app.screen_name == "history" and app.history_search_active:
            footer_text = footer_hints["history_search"]
        elif app.screen_name == "profile" and app.profile_popup_open:
            footer_text = "[↑↓] Scroll  [Bsp] Close"
        elif app.screen_name == "browser" and app.browser_tab == "relationships" and app.rel_browser_search_active:
            footer_text = footer_hints["browser_rel_search"]
        elif app.screen_name == "browser" and app.browser_tab == "history" and app.history_search_active:
            footer_text = footer_hints["history_search"]
        elif app.screen_name == "continuation":
            continuity_state = app.get_continuity_state()
            if continuity_state["continuity_candidates"]:
                footer_text = "[↑↓] Move   [Enter] Continue   [Bsp] Back   [Esc] Options"
            else:
                footer_text = "[Bsp] Back   [Esc] Options"
        else:
            footer_text = footer_hints.get(app.screen_name, "")
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

    def render_pending_choice(self, app, stdscr, height, width):
        if app.pending_choice is None:
            return

        box_width = min(max(40, width // 2), 50)
        inner_width = max(1, box_width - 2)
        popup_lines, option_line_indexes = self.build_choice_popup_lines(app.pending_choice)
        rendered_line_count = sum(len(wrap_text_line(line, inner_width)) for line in popup_lines)
        box_height = min(height - 4, max(9, rendered_line_count + 2))
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)

        draw_box(stdscr, top, left, box_height, box_width, title=app.pending_choice["title"])
        highlighted_line = option_line_indexes[app.pending_choice["selected_index"]]
        draw_panel_text(
            stdscr,
            top,
            left,
            box_height,
            box_width,
            popup_lines,
            highlight_index=highlighted_line,
        )

    def render_menu_popup(self, app, stdscr, height, width):
        box_width = 32
        box_height = len(self.MENU_ITEMS) + 6
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        draw_box(stdscr, top, left, box_height, box_width, title="Menu")
        for i, item in enumerate(self.MENU_ITEMS):
            label = f"  {i+1}. {item}"
            attr = curses.A_REVERSE if i == app.menu_selection else curses.A_NORMAL
            row = top + 2 + i
            if row < height and left + 1 < width:
                stdscr.addnstr(row, left + 1, label.ljust(box_width - 2), box_width - 2, attr)
        hint_row = top + 2 + len(self.MENU_ITEMS) + 1
        hint = " [↑↓]  [Enter] Select  [Bsp] Back"
        if hint_row < height and left + 1 < width:
            stdscr.addnstr(hint_row, left + 1, hint.ljust(box_width - 2), box_width - 2)

    def render_options_popup(self, app, stdscr, height, width):
        box_width = 36
        box_height = len(self.OPTION_ITEMS) + 6
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        draw_box(stdscr, top, left, box_height, box_width, title="Options")
        for i, item in enumerate(self.OPTION_ITEMS):
            prefix = "  "
            attr = curses.A_REVERSE if i == app.options_selection else curses.A_NORMAL
            if i > 0:
                attr |= curses.A_DIM
            label = f"{prefix}{item}"
            row = top + 2 + i
            if row < height and left + 1 < width:
                stdscr.addnstr(row, left + 1, label.ljust(box_width - 2), box_width - 2, attr)
        hint_row = top + 2 + len(self.OPTION_ITEMS) + 1
        hint = " [↑↓]  [Enter] Select  [Esc] Close"
        if hint_row < height and left + 1 < width:
            stdscr.addnstr(hint_row, left + 1, hint.ljust(box_width - 2), box_width - 2)

    def render_quit_confirmation(self, app, stdscr, height, width):
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

    def render_header(self, app, stdscr, width):
        focused_actor = app.get_focused_actor()
        focused_actor_name = focused_actor.get_full_name() if focused_actor is not None else "Unknown"
        chrome = build_screen_chrome(app.screen_name, app.world, focused_actor_name)

        logo_x, logo_w, _logo_center = self.get_logo_layout(width)

        try:
            snapshot = app.get_snapshot_data()
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

        panel_left_w = logo_x
        panel_right_w = width - 1 - logo_x - logo_w

        top_row = "═" * logo_x + self.LOGO_LINES[0] + "═" * panel_right_w
        try:
            stdscr.addnstr(0, 0, top_row[:width - 1], width - 1, curses.A_BOLD)
        except curses.error:
            pass

        for i in range(5):
            logo_line = self.LOGO_LINES[i + 1] if i + 1 < len(self.LOGO_LINES) - 1 else ""
            left_val = left_lines[i] if i < len(left_lines) else ""
            right_val = right_lines[i] if i < len(right_lines) else ""
            left_text = f"{left_val:>{panel_left_w - 1}} "
            right_text = f" {right_val}"
            try:
                stdscr.addnstr(i + 1, 0, left_text[:panel_left_w], panel_left_w)
                stdscr.addnstr(i + 1, logo_x, logo_line, logo_w, curses.A_BOLD)
                stdscr.addnstr(i + 1, logo_x + logo_w, right_text[:panel_right_w], panel_right_w)
            except curses.error:
                pass

        bot_row = "═" * logo_x + self.LOGO_LINES[-1] + "═" * panel_right_w
        try:
            stdscr.addnstr(app.HEADER_ROWS - 1, 0, bot_row[:width - 1], width - 1, curses.A_BOLD)
        except curses.error:
            pass
