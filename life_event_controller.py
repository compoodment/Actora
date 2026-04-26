"""Life-event choice offer controller."""

from events import get_meeting_event_for_player


class LifeEventController:
    """Owns pending-choice offers triggered by life progression."""

    def __init__(self, meeting_event_cooldown_months, gender_identity_options, sexuality_option_labels):
        self.meeting_event_cooldown_months = meeting_event_cooldown_months
        self.gender_identity_options = gender_identity_options
        self.sexuality_option_labels = sexuality_option_labels

    def maybe_offer_identity_choice(self, app):
        actor = app.get_focused_actor()
        if actor is None or not actor.is_alive():
            return False

        lifecycle = actor.get_lifecycle_state(app.world.current_year, app.world.current_month)
        age_years = lifecycle["age_years"]
        current_gender = actor.gender or "Other"

        if app.identity_popup_suppressed_for_resumed_adult:
            return False

        if age_years >= app.gender_choice_age and not app.gender_choice_offered:
            selected_index = (
                self.gender_identity_options.index(current_gender)
                if current_gender in self.gender_identity_options
                else 0
            )
            app.pending_choice = {
                "title": "A moment of self-reflection",
                "text": "As you grow, you find yourself thinking more about who you are.",
                "question": "Your gender identity feels like:",
                "options": list(self.gender_identity_options),
                "selected_index": selected_index,
                "skippable": True,
                "choice_id": "gender_identity",
                "default_value": current_gender,
            }
            app.gender_choice_offered = True
            app.last_message = "A personal choice needs your attention."
            return True

        if age_years >= app.sexuality_choice_age and not app.sexuality_choice_offered:
            app.pending_choice = {
                "title": "A new kind of awareness",
                "text": "You have started noticing things about yourself you had not thought about before.",
                "question": "You feel attracted to:",
                "options": [label for label, _ in self.sexuality_option_labels],
                "selected_index": 0,
                "skippable": True,
                "choice_id": "sexuality",
                "default_value": None,
            }
            app.sexuality_choice_offered = True
            app.last_message = "A personal choice needs your attention."
            return True

        return False

    def maybe_offer_meeting_event(self, app):
        """Fires a meeting-event popup choice when conditions and cooldown allow."""
        actor = app.get_focused_actor()
        if actor is None or not actor.is_alive():
            return False

        lifecycle = actor.get_lifecycle_state(app.world.current_year, app.world.current_month)
        current_total_months = app.world.current_year * 12 + app.world.current_month
        if current_total_months - app.meeting_event_last_total_months < self.meeting_event_cooldown_months:
            return False

        meeting_event = get_meeting_event_for_player(lifecycle)
        if meeting_event is None:
            return False

        app.meeting_event_last_total_months = current_total_months
        app.pending_choice = {
            "title": "Someone new",
            "text": meeting_event["text"],
            "question": "Do you want to introduce yourself?",
            "options": ["Introduce yourself", "Keep to yourself"],
            "selected_index": 0,
            "skippable": False,
            "choice_id": "meeting_npc",
        }
        app.last_message = "You notice someone nearby."
        return True
