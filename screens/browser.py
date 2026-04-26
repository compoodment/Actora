"""Unified browser screen controller and renderer."""

import curses

from ui import center_text, get_content_bounds


class BrowserScreen:
    """Owns tab switching and wrapper chrome for browser sub-screens."""

    def handle_key(self, app, key):
        search_active = (
            (app.browser_tab == "relationships" and app.rel_browser_search_active)
            or (app.browser_tab == "history" and app.history_search_active)
        )
        if not search_active and key == 27:
            app.options_popup_active = True
            app.options_selection = 0
            return
        if not search_active and key == 9:
            if app.browser_tab == "relationships":
                app.browser_tab = "history"
                app.last_message = "Browsing event history."
            else:
                app.browser_tab = "relationships"
                app.last_message = "Browsing relationships."
            return
        if app.browser_tab == "relationships":
            app.handle_relationship_browser_key(key, back_to="main")
        elif app.browser_tab == "history":
            app.handle_history_key(key)

    def render(self, app, stdscr, height, width):
        content_left, content_width = get_content_bounds(width, max_width=120, min_margin=1)

        rel_label = "[ Relationships ]" if app.browser_tab == "relationships" else "  Relationships  "
        hist_label = "[ History ]" if app.browser_tab == "history" else "  History  "
        tab_bar = f"{rel_label}     │     {hist_label}"
        try:
            stdscr.addnstr(app.HEADER_ROWS, content_left, center_text(tab_bar, content_width), content_width)
            hline_char = getattr(curses, "ACS_HLINE", ord("-"))
            stdscr.hline(app.HEADER_ROWS + 1, content_left, hline_char, content_width)
        except curses.error:
            pass

        if app.browser_tab == "relationships":
            app.render_relationship_browser(stdscr, height, width)
        else:
            app.render_history(stdscr, height, width)
