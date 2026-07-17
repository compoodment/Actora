"""Curses-free accumulation for Actora's saved event log."""

from __future__ import annotations

HIDDEN_PLAYER_RECORD_TYPES = {
    "family_bootstrap",
    "actor_entry",
    "continuation",
}


def build_event_log_entry(
    kind: str,
    text: str,
    *,
    year: int | None = None,
    month: int | None = None,
    record_type: str | None = None,
) -> dict[str, object]:
    """Builds one normalized entry shared by native and terminal history."""
    return {
        "kind": kind,
        "text": text,
        "year": year,
        "month": month,
        "record_type": record_type,
    }


def append_event_log_entry(
    event_log: list[dict[str, object]],
    kind: str,
    text: str,
    *,
    year: int | None = None,
    month: int | None = None,
    record_type: str | None = None,
) -> None:
    """Appends one normalized event-log entry."""
    event_log.append(
        build_event_log_entry(
            kind,
            text,
            year=year,
            month=month,
            record_type=record_type,
        )
    )


def append_turn_event_log(
    event_log: list[dict[str, object]],
    last_logged_year: int,
    focused_actor_id: str,
    turn_result: dict[str, object],
    months_to_advance: int,
    new_records: list[dict[str, object]],
    *,
    suppress_skip_marker: bool = False,
) -> int:
    """Merges one completed advance and returns the new year cursor."""
    actual_months_advanced = turn_result["months_advanced"]
    if not isinstance(actual_months_advanced, int) or actual_months_advanced <= 0:
        return last_logged_year

    if months_to_advance > 1 and not suppress_skip_marker:
        label = "Month" if actual_months_advanced == 1 else "Months"
        append_event_log_entry(
            event_log,
            "skip_marker",
            f"{actual_months_advanced} {label} Skipped",
        )

    visible_record_types = {"birth", "death"}
    merged_entries: list[dict[str, object]] = []
    event_identity_keys: set[tuple[object, object, object]] = set()
    structured_events = turn_result.get("events", [])
    if not isinstance(structured_events, list):
        structured_events = []

    for sequence, structured_event in enumerate(structured_events):
        if not isinstance(structured_event, dict):
            continue
        event_year = structured_event.get("year")
        event_month = structured_event.get("month")
        event_text = structured_event.get("text", "")
        event_identity_keys.add((event_year, event_month, event_text))
        merged_entries.append(
            {
                "sort_key": (
                    event_year if isinstance(event_year, int) else -1,
                    event_month if isinstance(event_month, int) else -1,
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
        if not isinstance(record, dict):
            continue
        record_type = record.get("record_type")
        if record_type in HIDDEN_PLAYER_RECORD_TYPES:
            continue
        if record_type not in visible_record_types:
            continue
        actor_ids = record.get("actor_ids")
        if not isinstance(actor_ids, list) or focused_actor_id not in actor_ids:
            continue

        record_key = (
            record.get("year"),
            record.get("month"),
            record.get("text"),
        )
        if record_key in event_identity_keys:
            continue

        record_year = record.get("year")
        record_month = record.get("month")
        merged_entries.append(
            {
                "sort_key": (
                    record_year if isinstance(record_year, int) else -1,
                    record_month if isinstance(record_month, int) else -1,
                    structural_sequence,
                    1,
                ),
                "kind": "event",
                "text": record.get("text", ""),
                "year": record_year,
                "month": record_month,
                "record_type": record_type,
            }
        )
        structural_sequence += 1

    merged_entries.sort(key=lambda entry: entry["sort_key"])
    for entry in merged_entries:
        entry_year = entry.get("year")
        if isinstance(entry_year, int) and entry_year > last_logged_year:
            # Empty years carry no history. Writing only the next represented
            # year also keeps schema-valid but widely separated dates bounded.
            append_event_log_entry(
                event_log,
                "year_header",
                f"Year {entry_year}",
                year=entry_year,
            )
            last_logged_year = entry_year

        append_event_log_entry(
            event_log,
            str(entry["kind"]),
            str(entry["text"]),
            year=entry.get("year") if isinstance(entry.get("year"), int) else None,
            month=(
                entry.get("month")
                if isinstance(entry.get("month"), int)
                else None
            ),
            record_type=(
                entry.get("record_type")
                if isinstance(entry.get("record_type"), str)
                else None
            ),
        )
    return last_logged_year
