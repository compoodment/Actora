"""Pending-choice modal input controller."""

import curses


class ChoiceController:
    """Owns input handling for pending modal choices."""

    def __init__(self, back_keys, sexuality_option_labels):
        self.back_keys = back_keys
        self.sexuality_option_labels = sexuality_option_labels

    def handle_key(self, app, key):
        if key in (ord("q"), ord("Q"), ord("e"), ord("E")):
            return

        if app.pending_choice is None:
            return

        options = app.pending_choice["options"]
        selected_index = app.pending_choice["selected_index"]
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            app.pending_choice["selected_index"] = max(0, selected_index - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            app.pending_choice["selected_index"] = min(len(options) - 1, selected_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            selected_option = options[app.pending_choice["selected_index"]]
            if app.pending_choice["choice_id"] == "sexuality":
                selected_value = dict(self.sexuality_option_labels)[selected_option]
            else:
                selected_value = selected_option
            app.resolve_choice(app.pending_choice["choice_id"], selected_value)
        elif app.pending_choice.get("skippable") and key in self.back_keys:
            app.resolve_choice(
                app.pending_choice["choice_id"],
                app.pending_choice.get("default_value"),
            )
