"""Lineage and relationship browser state adapter."""


class BrowserStateController:
    """Owns shell selection/search state adaptation for browser screens."""

    def __init__(self, lineage_record_limit, lineage_filter_labels, rel_filter_options):
        self.lineage_record_limit = lineage_record_limit
        self.lineage_filter_labels = lineage_filter_labels
        self.rel_filter_options = rel_filter_options

    def get_lineage_browser_state(self, app):
        browser_state = app.world.get_lineage_browser_data_for(
            app.get_focused_actor_id(),
            filter_mode=app.lineage_filter_mode,
            search_text=app.lineage_search_text,
            recent_record_limit=self.lineage_record_limit,
        )

        entries = browser_state["entries"]
        if not entries:
            app.lineage_selection = 0
            app.selected_lineage_actor_id = None
            browser_state["selected_detail"] = None
            return browser_state

        if app.selected_lineage_actor_id is not None:
            matching_index = next(
                (
                    index
                    for index, entry in enumerate(entries)
                    if entry["actor_id"] == app.selected_lineage_actor_id
                ),
                None,
            )
            if matching_index is not None:
                app.lineage_selection = matching_index
            else:
                app.lineage_selection = 0
                app.selected_lineage_actor_id = entries[0]["actor_id"]
        else:
            app.lineage_selection = max(0, min(app.lineage_selection, len(entries) - 1))
            app.selected_lineage_actor_id = entries[app.lineage_selection]["actor_id"]

        browser_state["selected_detail"] = app.world.get_lineage_detail_for(
            app.get_focused_actor_id(),
            app.selected_lineage_actor_id,
            recent_record_limit=self.lineage_record_limit,
        )
        return browser_state

    def get_lineage_entries(self, app):
        return self.get_lineage_browser_state(app)["entries"]

    def get_lineage_detail(self, app):
        return self.get_lineage_browser_state(app)["selected_detail"]

    def set_lineage_filter_mode(self, app, filter_mode):
        app.lineage_filter_mode = filter_mode
        app.lineage_selection = 0
        app.selected_lineage_actor_id = None
        app.last_message = f"Lineage filter: {self.lineage_filter_labels[filter_mode]}."

    def clear_lineage_search(self, app):
        if app.lineage_search_text:
            app.lineage_search_text = ""
            app.lineage_selection = 0
            app.selected_lineage_actor_id = None
            app.last_message = "Lineage search cleared."

    def get_lineage_search_status(self, app):
        if app.lineage_search_active:
            return f"Search: {app.lineage_search_text}_"
        if app.lineage_search_text:
            return f"Search: {app.lineage_search_text}"
        return "Search: off"

    def get_rel_browser_search_status(self, app):
        """Returns the search status line for the relationship browser, or None."""
        if app.rel_browser_search_active:
            return f"Search: {app.rel_browser_search_text}_"
        if app.rel_browser_search_text:
            return f"Search: {app.rel_browser_search_text}"
        return None

    def get_relationship_browser_state(self, app):
        focused_actor_id = app.get_focused_actor_id()
        filter_mode = self.rel_filter_options[app.rel_filter_index]
        browser_state = app.world.get_relationship_browser_data_for(
            focused_actor_id,
            filter_mode=filter_mode,
            search_text=app.rel_browser_search_text,
            recent_record_limit=self.lineage_record_limit,
        )
        entries = browser_state["entries"]
        if not entries:
            app.lineage_selection = 0
            app.selected_lineage_actor_id = None
            browser_state["selected_detail"] = None
            return browser_state

        if app.selected_lineage_actor_id is not None:
            matching_index = next(
                (
                    index
                    for index, entry in enumerate(entries)
                    if entry["actor_id"] == app.selected_lineage_actor_id
                ),
                None,
            )
            if matching_index is not None:
                app.lineage_selection = matching_index
            else:
                app.lineage_selection = 0
                app.selected_lineage_actor_id = entries[0]["actor_id"]
        else:
            app.lineage_selection = max(0, min(app.lineage_selection, len(entries) - 1))
            app.selected_lineage_actor_id = entries[app.lineage_selection]["actor_id"]

        browser_state["selected_detail"] = app.world.get_relationship_detail_for(
            focused_actor_id,
            app.selected_lineage_actor_id,
            recent_record_limit=self.lineage_record_limit,
        )
        return browser_state
