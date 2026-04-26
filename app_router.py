"""Top-level TUI input/render routing."""


class AppRouter:
    """Owns screen dispatch for input and rendering."""

    def handle_key(self, app, key):
        app.sync_focus_state()
        if app.shell_controller.handle_modal_key(app, key):
            return
        if app.pending_choice is not None:
            app.choice_controller.handle_key(app, key)
            return
        if app.screen_name == "main":
            app.main_screen.handle_key(app, key)
        elif app.screen_name == "profile":
            app.profile_screen.handle_key(app, key)
        elif app.screen_name == "lineage":
            app.lineage_screen.handle_key(app, key)
        elif app.screen_name == "relationship_browser":
            app.relationship_browser_screen.handle_key(app, key)
        elif app.screen_name == "history":
            app.history_screen.handle_key(app, key)
        elif app.screen_name == "browser":
            app.browser_screen.handle_key(app, key)
        elif app.screen_name == "actions":
            app.actions_screen.handle_key(app, key)
        elif app.screen_name == "skip_time":
            app.skip_time_screen.handle_key(app, key)
        elif app.screen_name == "death_ack":
            app.death_screen.handle_death_ack_key(app, key)
        elif app.screen_name == "continuation":
            app.death_screen.handle_continuation_key(app, key)
        elif app.screen_name == "continuation_detail":
            app.death_screen.handle_continuation_detail_key(app, key)

    def render(self, app, stdscr):
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        if height < 16 or width < 50:
            stdscr.addnstr(0, 0, "Terminal too small for Actora TUI. Resize and try again.", width - 1)
            return

        app.render_header(stdscr, width)
        if app.screen_name == "main":
            app.main_screen.render(app, stdscr, height, width)
        elif app.screen_name == "profile":
            app.profile_screen.render(app, stdscr, height, width)
        elif app.screen_name == "lineage":
            app.lineage_screen.render(app, stdscr, height, width)
        elif app.screen_name == "relationship_browser":
            app.relationship_browser_screen.render(app, stdscr, height, width)
        elif app.screen_name == "history":
            app.history_screen.render(app, stdscr, height, width)
        elif app.screen_name == "browser":
            app.browser_screen.render(app, stdscr, height, width)
        elif app.screen_name == "actions":
            app.actions_screen.render(app, stdscr, height, width)
        elif app.screen_name == "skip_time":
            app.skip_time_screen.render(app, stdscr, height, width)
        elif app.screen_name == "death_ack":
            app.death_screen.render_death_ack(app, stdscr, height, width)
        elif app.screen_name == "continuation":
            app.death_screen.render_continuation(app, stdscr, height, width)
        elif app.screen_name == "continuation_detail":
            app.death_screen.render_continuation_detail(app, stdscr, height, width)

        app.render_footer(stdscr, height, width)
        app.render_pending_choice(stdscr, height, width)
        if app.menu_popup_active:
            app.render_menu_popup(stdscr, height, width)
        if app.options_popup_active:
            app.render_options_popup(stdscr, height, width)
        stdscr.refresh()
