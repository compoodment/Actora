"""Profile and person-card view helpers."""

from views.history import expand_render_lines


def format_stat_pair(left_label, left_value, right_label, right_value):
    """Builds one compact two-column stat row for profile rendering."""
    return f"  {left_label}: {left_value:<3}      {right_label}: {right_value}"


def build_person_card_lines(summary):
    """Builds a reusable person-card line set for lineage and continuity views."""
    status_label = "Alive" if summary.get("is_alive") else "Dead"
    age_label = "Age" if summary.get("is_alive") else "Age at Death"
    lines = [
        summary.get("full_name", "Unknown"),
        f"Status: {status_label}   Relationship: {summary.get('relationship_label', 'Connected')}",
        f"{age_label}: {summary.get('age', '?')}   Life Stage: {summary.get('life_stage', 'Unknown')}",
        f"Location: {summary.get('current_place_name') or 'Unknown'}",
    ]

    family_branch_label = summary.get("family_branch_label")
    if family_branch_label:
        lines.append(f"Family Side: {family_branch_label}")

    birth_date = summary.get("birth_date")
    if birth_date:
        lines.append(f"Born: {birth_date}")

    death_date = summary.get("death_date")
    if death_date:
        lines.append(f"Died: {death_date}")

    death_reason = summary.get("death_reason")
    if death_reason:
        lines.append(f"Cause: {death_reason}")

    return lines


def build_profile_summary_rows(snapshot_data):
    identity = snapshot_data["identity"]
    location = snapshot_data["location"]
    appearance = snapshot_data["appearance"]
    statistics = snapshot_data["statistics"]
    traits = snapshot_data["traits"]
    relationships = snapshot_data["relationships"]
    family_labels = {"Mother", "Father", "Son", "Daughter", "Brother", "Sister", "Grandparent", "Grandchild", "Sibling", "Uncle", "Aunt", "Nephew", "Niece", "Spouse", "Partner"}
    family_count = sum(1 for entry in relationships if entry.get("label") in family_labels)
    friend_count = max(0, len(relationships) - family_count)
    trait_summary = ", ".join(traits) if traits else "None"
    return [
        ("identity", f"Identity  ·  {identity['full_name']}  ·  Age {identity['age']}  ·  {identity['gender']}"),
        ("appearance", f"Appearance  ·  {appearance['eye_color']} eyes  ·  {appearance['hair_color']} hair"),
        ("stats", f"Stats  ·  Health {statistics['health']}  ·  Happiness {statistics['happiness']}  ·  Intel {statistics['intelligence']}  ·  ${statistics['money']}"),
        ("attributes", f"Attributes  ·  Str {statistics['strength']}  Cha {statistics['charisma']}  Img {statistics['imagination']}  Mem {statistics['memory']}  Wis {statistics['wisdom']}  Dsc {statistics['discipline']}  Wil {statistics['willpower']}  Srs {statistics['stress']}  Lks {statistics['looks']}  Fer {statistics['fertility']}"),
        ("traits", f"Traits  ·  {trait_summary}"),
        ("mood", "Mood  ·  —"),
        ("needs", "Needs  ·  —"),
        ("skills", "Skills  ·  —"),
        ("location", f"Location  ·  {location['current_place_name']}, {location['jurisdiction_place_name']}"),
        ("relationships", f"Relationships  ·  {family_count} family  ·  {friend_count} friends"),
    ]


def build_profile_popup_lines(category, snapshot_data):
    identity = snapshot_data["identity"]
    location = snapshot_data["location"]
    appearance = snapshot_data["appearance"]
    statistics = snapshot_data["statistics"]
    traits = snapshot_data["traits"]

    if category == "identity":
        return [
            f"Name: {identity['full_name']}",
            f"Species: {identity['species']}",
            f"Sex: {identity['sex']}",
            f"Gender: {identity['gender']}",
            f"Sexuality: {identity.get('sexuality') or 'Not yet known'}",
            f"Age: {identity['age']}",
            f"Life Stage: {identity['life_stage']}",
        ]
    if category == "appearance":
        return [
            f"Eye Color: {appearance['eye_color']}",
            f"Hair Color: {appearance['hair_color']}",
            f"Skin Tone: {appearance['skin_tone']}",
        ]
    if category == "stats":
        return [
            "Primary Stats",
            f"Health: {statistics['health']}",
            f"Happiness: {statistics['happiness']}",
            f"Intelligence: {statistics['intelligence']}",
            f"Money: ${statistics['money']}",
        ]
    if category == "attributes":
        return [
            "Secondary Stats",
            f"Strength: {statistics['strength']}",
            f"Charisma: {statistics['charisma']}",
            f"Imagination: {statistics['imagination']}",
            f"Memory: {statistics['memory']} (-50 to +50)",
            f"Wisdom: {statistics['wisdom']}",
            f"Discipline: {statistics['discipline']}",
            f"Willpower: {statistics['willpower']}",
            f"Stress: {statistics['stress']} (-50 to +50)",
            f"Looks: {statistics['looks']}",
            f"Fertility: {statistics['fertility']}",
        ]
    if category == "traits":
        return traits or ["None"]
    if category in {"mood", "needs", "skills"}:
        return ["Coming soon."]
    if category == "location":
        return [
            f"Planet: {location['world_body_name']}",
            f"City: {location['current_place_name']}",
            f"Country: {location['jurisdiction_place_name']}",
        ]
    if category == "relationships":
        return ["Open the Relationships Browser to see your full list."]
    return []


def build_profile_popup_render_data(category, snapshot_data, content_width, body_height):
    content_lines = build_profile_popup_lines(category, snapshot_data)
    popup_width = max(24, min(70, content_width - 4))
    inner_width = max(1, popup_width - 2)
    rendered_lines = expand_render_lines(content_lines, inner_width)
    popup_height = max(4, min(len(rendered_lines) + 2, max(4, body_height - 4)))
    visible_content_height = max(1, popup_height - 2)
    max_scroll = max(0, len(rendered_lines) - visible_content_height)
    return {
        "category": category,
        "content_lines": content_lines,
        "rendered_lines": rendered_lines,
        "popup_width": popup_width,
        "popup_height": popup_height,
        "visible_content_height": visible_content_height,
        "max_scroll": max_scroll,
    }
