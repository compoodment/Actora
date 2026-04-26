"""Lineage and relationship-browser view helpers."""

HIDDEN_PLAYER_RECORD_TYPES = {"family_bootstrap", "actor_entry"}


def build_lineage_row(entry):
    """Builds one compact lineage browser row."""
    return f"{entry['full_name']} · {entry['relationship_label']} · Age {entry['age']}"


def filter_player_facing_records(records):
    """Removes implementation-scaffolding records from player-facing surfaces."""
    return [
        record
        for record in records
        if record.get("record_type") not in HIDDEN_PLAYER_RECORD_TYPES
    ]


def build_record_summary_lines(records):
    """Builds compact record lines for inspectability surfaces."""
    filtered_records = filter_player_facing_records(records)
    if not filtered_records:
        return ["No records found."]
    return [
        f"[{record['year'] or 0:04d}-{record['month'] or 0:02d}] {record['text']}"
        for record in filtered_records
    ]


def get_social_tier_label(closeness):
    """Returns the display tier label for a social link closeness value."""
    if closeness >= 70:
        return "Close Friend"
    if closeness >= 30:
        return "Friend"
    return "Acquaintance"
