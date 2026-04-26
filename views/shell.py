"""Shell chrome and lifecycle interrupt view helpers."""


def build_death_lines(continuity_state):
    """Builds the dead-focus interrupt copy for the TUI shell."""
    lines = [
        "You are dead.",
        continuity_state["focus_actor_name"],
    ]

    death_year = continuity_state["focus_actor_death_year"]
    death_month = continuity_state["focus_actor_death_month"]
    death_reason = continuity_state["focus_actor_death_reason"]

    death_context_parts = []
    if death_year is not None and death_month is not None:
        death_context_parts.append(f"Year {death_year}, Month {death_month}")
    if death_reason:
        death_context_parts.append(death_reason)

    if death_context_parts:
        lines.append(" | ".join(death_context_parts))
    lines.append("The universe continues.")
    return lines


def format_sim_date(year, month):
    """Formats one compact simulation date string."""
    return f"Year {year}, Month {month}"


def build_screen_chrome(screen_name, world, focused_actor_name):
    """Builds shell-owned title/subtitle text for the current screen."""
    title_map = {
        "main": "Life View",
        "profile": "Profile",
        "lineage": "Lineage Browser",
        "relationship_browser": "Relationships",
        "history": "History",
        "browser": "Browser",
        "actions": "Actions",
        "skip_time": "Skip Time",
        "death_ack": "Death",
        "continuation": "Continuation",
        "continuation_detail": "Continuation",
    }
    subtitle_map = {
        "main": focused_actor_name,
        "profile": focused_actor_name,
        "lineage": focused_actor_name,
        "relationship_browser": focused_actor_name,
        "history": focused_actor_name,
        "browser": focused_actor_name,
        "actions": focused_actor_name,
        "skip_time": "Choose a larger time jump or enter custom months",
        "death_ack": focused_actor_name,
        "continuation": focused_actor_name,
        "continuation_detail": focused_actor_name,
    }
    date_text = format_sim_date(world.current_year, world.current_month)
    return {
        "title": title_map.get(screen_name, "Actora"),
        "subtitle": subtitle_map.get(screen_name, focused_actor_name),
        "date_text": date_text,
    }
