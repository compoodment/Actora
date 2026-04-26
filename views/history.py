"""History and event-log view helpers."""

from ui import build_centered_rule, wrap_text_line


def build_event_log_entry(kind, text, *, year=None, month=None, record_type=None):
    """Builds one normalized event-log entry for shell-owned history rendering."""
    return {
        "kind": kind,
        "text": text,
        "year": year,
        "month": month,
        "record_type": record_type,
    }


def get_event_log_marker(record_type):
    """Returns the optional visual marker prefix for structural record entries."""
    if record_type == "birth":
        return "★ "
    if record_type == "death":
        return "✦ "
    return ""


def build_history_separator(year, width):
    """Builds one centered year separator for the history browser."""
    return build_centered_rule(f"Year {year}", width, fill_char="─")


def format_history_entry(entry, width):
    """Formats one event-log entry for the full history screen."""
    if entry["kind"] == "year_header":
        return build_history_separator(entry["year"], width)
    if entry["kind"] == "life_separator":
        return build_centered_rule(entry["text"], width, fill_char="═")
    if entry["kind"] == "skip_marker":
        return entry["text"]
    if entry["kind"] == "event":
        year = entry["year"] if entry["year"] is not None else 0
        month = entry["month"] if entry["month"] is not None else 0
        marker = get_event_log_marker(entry.get("record_type"))
        return f"[{year:04d}-{month:02d}] {marker}{entry['text']}"
    return entry["text"]


def build_live_feed_lines(event_log):
    """Builds the logical line list for the non-scrollable live event feed."""
    if not event_log:
        return ["No events yet."]

    lines = []
    for entry in event_log:
        if entry["kind"] == "year_header":
            if lines:
                lines.append("")
            lines.append(entry["text"])
        elif entry["kind"] == "life_separator":
            lines.append("")
            lines.append(entry["text"])
        elif entry["kind"] == "event":
            marker = get_event_log_marker(entry.get("record_type"))
            if entry.get("record_type") in {"birth", "death"} and entry.get("year") is not None:
                lines.append(f"{marker}[Year {entry['year']}] {entry['text']}")
            else:
                lines.append(f"{marker}{entry['text']}")
        else:
            lines.append(entry["text"])
    return lines


def expand_render_lines(lines, width):
    """Expands logical lines into wrapped render lines for scrolling surfaces."""
    render_lines = []
    for line in lines:
        render_lines.extend(wrap_text_line(line, width))
    return render_lines
