"""Continuation handoff controller."""

import random


class ContinuationController:
    """Owns death acknowledgement and continuation handoff orchestration."""

    def get_continuity_state(self, app):
        return app.world.build_continuity_state_for(app.get_focused_actor_id())

    def acknowledge_death(self, app):
        continuity_state = self.get_continuity_state(app)
        app.continuation_selection = 0
        app.selected_continuation_actor_id = None
        app.screen_name = "continuation"
        if continuity_state["had_continuity_candidates"]:
            app.last_message = "Choose who to continue as."
        else:
            app.last_message = "No one is available to continue."

    def get_selected_continuation_candidate(self, app):
        continuity_state = self.get_continuity_state(app)
        candidates = continuity_state["continuity_candidates"]
        if not candidates:
            return None

        app.continuation_selection = max(
            0,
            min(app.continuation_selection, len(candidates) - 1),
        )
        return candidates[app.continuation_selection]

    def open_continuation_detail(self, app):
        selected_candidate = self.get_selected_continuation_candidate(app)
        if selected_candidate is None:
            return
        app.selected_continuation_actor_id = selected_candidate["actor_id"]
        app.screen_name = "continuation_detail"
        app.last_message = f"Inspecting {selected_candidate['full_name']}."

    def choose_continuation(self, app):
        selected_candidate = self.get_selected_continuation_candidate(app)
        if selected_candidate is None:
            app.running = False
            return

        successor_actor_id = selected_candidate["actor_id"]
        handoff_result = app.world.handoff_focus_to_continuation(
            app.get_focused_actor_id(),
            successor_actor_id,
        )
        app.player_id = successor_actor_id
        app.last_logged_year = 0
        app.event_log.append(
            {
                "kind": "life_separator",
                "text": f"New Life: {handoff_result['new_focused_actor_name']}",
            }
        )
        app.pending_choice = None
        app.remaining_skip_months = 0
        continued_actor = app.get_focused_actor()
        continued_lifecycle = (
            continued_actor.get_lifecycle_state(app.world.current_year, app.world.current_month)
            if continued_actor is not None
            else None
        )
        app.identity_popup_suppressed_for_resumed_adult = False
        if continued_actor is not None and continued_lifecycle is not None and continued_lifecycle["age_years"] >= 18:
            continued_actor.auto_resolve_identity()
            app.gender_choice_offered = True
            app.sexuality_choice_offered = True
            app.identity_popup_suppressed_for_resumed_adult = True
        else:
            app.gender_choice_offered = False
            app.gender_choice_offered = False
        app.sexuality_choice_offered = False
        app.gender_choice_age = random.randint(12, 15)
        app.sexuality_choice_age = random.randint(14, 17)
        app.meeting_event_last_total_months = 0
        app.selected_continuation_actor_id = None
        app.screen_name = "main"
        app.quit_confirmation_active = False
        app.last_message = f"Your story continues as {handoff_result['new_focused_actor_name']}."
