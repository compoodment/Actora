"""Shell event-log accumulation controller."""

from actora_core.history import (
    append_event_log_entry,
    append_turn_event_log,
)


class EventLogController:
    """Owns normalized event-log append and turn merge behavior."""

    def append_entry(self, app, kind, text, *, year=None, month=None, record_type=None):
        """Appends one event-log entry with normalized structure."""
        append_event_log_entry(
            app.event_log,
            kind,
            text,
            year=year,
            month=month,
            record_type=record_type,
        )

    def append_turn(self, app, turn_result, months_to_advance, new_records, *, suppress_skip_marker=False):
        """Extends the event log from one completed advance."""
        app.last_logged_year = append_turn_event_log(
            app.event_log,
            app.last_logged_year,
            app.get_focused_actor_id(),
            turn_result,
            months_to_advance,
            new_records,
            suppress_skip_marker=suppress_skip_marker,
        )
