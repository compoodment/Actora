"""Global shell modal/input controller."""

import curses


class ShellController:
    """Owns global menu/options/quit modal input handling."""

    MENU_ITEMS = ["Browser", "Actions", "Profile"]
    OPTIONS_ITEMS = ["Quit Game", "Help / Controls", "Settings"]

    def __init__(self, back_keys):
        self.back_keys = back_keys

    def open_menu_selection(self, app):
        app.menu_popup_active = False
        if app.menu_selection == 0:
            app.open_browser("relationships")
        elif app.menu_selection == 1:
            app.open_actions()
        elif app.menu_selection == 2:
            app.open_profile()

    def open_options_selection(self, app):
        if app.options_selection == 0:
            app.options_popup_active = False
            app.quit_confirmation_active = True
            app.quit_from_options = True

    def handle_modal_key(self, app, key):
        """Handles active global modals. Returns True when input was consumed."""
        if app.quit_confirmation_active:
            if key in self.back_keys or key == 27:
                app.quit_confirmation_active = False
                if app.quit_from_options:
                    app.quit_from_options = False
                    app.options_popup_active = True
                return True
            if key in (curses.KEY_ENTER, 10, 13):
                app.running = False
                return True
            return True

        if app.options_popup_active:
            if key == 27:
                app.options_popup_active = False
            elif key in (curses.KEY_UP, ord("w"), ord("W")):
                app.options_selection = max(0, app.options_selection - 1)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                app.options_selection = min(len(self.OPTIONS_ITEMS) - 1, app.options_selection + 1)
            elif key in (curses.KEY_ENTER, 10, 13):
                self.open_options_selection(app)
            return True

        if app.menu_popup_active:
            if key in self.back_keys:
                app.menu_popup_active = False
            elif key in (curses.KEY_UP, ord("w"), ord("W")):
                app.menu_selection = max(0, app.menu_selection - 1)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                app.menu_selection = min(len(self.MENU_ITEMS) - 1, app.menu_selection + 1)
            elif key == ord("1"):
                app.menu_selection = 0
                self.open_menu_selection(app)
            elif key == ord("2"):
                app.menu_selection = 1
                self.open_menu_selection(app)
            elif key == ord("3"):
                app.menu_selection = 2
                self.open_menu_selection(app)
            elif key in (curses.KEY_ENTER, 10, 13):
                self.open_menu_selection(app)
            return True

        return False
