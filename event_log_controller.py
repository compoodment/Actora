"""Shell event-log accumulation controller."""

from views.browser import HIDDEN_PLAYER_RECORD_TYPES
from views.history import build_event_log_entry


class EventLogController:
    """Owns normalized event-log append and turn merge behavior."""

    def append_entry(self, app, kind, text, *, year=None, month=None, record_type=None):
        """Appends one event-log entry with normalized structure."""
        app.event_log.append(
            build_event_log_entry(
                kind,
                text,
                year=year,
                month=month,
                record_type=record_type,
            )
        )

    def append_turn(self, app, turn_result, months_to_advance, new_records, *, suppress_skip_marker=False):
        """Extends the event log from one completed advance."""
        actual_months_advanced = turn_result["months_advanced"]
        if actual_months_advanced <= 0:
            return

        if months_to_advance > 1 and not suppress_skip_marker:
            label = "Month" if actual_months_advanced == 1 else "Months"
            self.append_entry(
                app,
                "skip_marker",
                f"{actual_months_advanced} {label} Skipped",
            )

        visible_record_types = {"birth", "death"}
        merged_entries = []
        event_identity_keys = set()

        for sequence, structured_event in enumerate(turn_result["events"]):
            event_year = structured_event.get("year")
            event_month = structured_event.get("month")
            event_text = structured_event.get("text", "")
            event_key = (event_year, event_month, event_text)
            event_identity_keys.add(event_key)
            merged_entries.append(
                {
                    "sort_key": (
                        event_year if event_year is not None else -1,
                        event_month if event_month is not None else -1,
                        sequence,
                        0,
                    ),
                    "kind": "event",
                    "text": event_text,
                    "year": event_year,
                    "month": event_month,
                    "record_type": None,
                }
            )

        structural_sequence = len(merged_entries)
        for record in new_records:
            if record.get("record_type") in HIDDEN_PLAYER_RECORD_TYPES:
                continue
            if record.get("record_type") not in visible_record_types:
                continue
            if app.get_focused_actor_id() not in (record.get("actor_ids") or []):
                continue

            record_key = (
                record.get("year"),
                record.get("month"),
                record.get("text"),
            )
            if record_key in event_identity_keys:
                continue

            merged_entries.append(
                {
                    "sort_key": (
                        record.get("year") if record.get("year") is not None else -1,
                        record.get("month") if record.get("month") is not None else -1,
                        structural_sequence,
                        1,
                    ),
                    "kind": "event",
                    "text": record.get("text", ""),
                    "year": record.get("year"),
                    "month": record.get("month"),
                    "record_type": record.get("record_type"),
                }
            )
            structural_sequence += 1

        merged_entries.sort(key=lambda entry: entry["sort_key"])
        for entry in merged_entries:
            entry_year = entry.get("year")
            if entry_year is not None and entry_year > app.last_logged_year:
                for year in range(app.last_logged_year + 1, entry_year + 1):
                    self.append_entry(
                        app,
                        "year_header",
                        f"Year {year}",
                        year=year,
                    )
                app.last_logged_year = entry_year

            self.append_entry(
                app,
                entry["kind"],
                entry["text"],
                year=entry.get("year"),
                month=entry.get("month"),
                record_type=entry.get("record_type"),
            )
