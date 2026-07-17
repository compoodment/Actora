"""Curses-free startup world construction and character-stat normalization."""

import random
from uuid import uuid4

from geography import (
    DEFAULT_CITY_ID,
    DEFAULT_COUNTRY_ID,
    WORLD_GEOGRAPHY,
    WORLD_GEOGRAPHY_BY_COUNTRY_ID,
)
from identity import (
    generate_parent_identity_from_context,
    prepare_parent_identity_context,
)
from world import World


CREATION_STAT_ORDER = [
    "health",
    "happiness",
    "intelligence",
    "strength",
    "charisma",
    "imagination",
    "wisdom",
    "discipline",
    "willpower",
    "looks",
    "fertility",
    "memory",
    "stress",
]


def normalize_creation_stats(stats, *, random_source=None):
    """Aligns creation and loaded stat blocks with the current stat model."""
    rng = random if random_source is None else random_source
    source_stats = dict(stats)
    normalized_stats = {}
    for stat_name in CREATION_STAT_ORDER:
        if stat_name == "imagination":
            if stat_name in source_stats:
                normalized_stats[stat_name] = source_stats[stat_name]
            else:
                normalized_stats[stat_name] = next(
                    (
                        stat_value
                        for legacy_name, stat_value in source_stats.items()
                        if legacy_name not in CREATION_STAT_ORDER
                    ),
                    50,
                )
            continue

        default_value = 10 if stat_name == "stress" else 50
        normalized_stats[stat_name] = source_stats.get(
            stat_name,
            default_value,
        )

    if "memory" not in source_stats:
        normalized_stats["memory"] = rng.randint(40, 70)
    if "stress" not in source_stats:
        normalized_stats["stress"] = rng.randint(5, 20)
    return normalized_stats


def generate_startup_actor_id(role, *, id_source=None):
    """Builds one startup actor ID through an optional injected source."""
    if id_source is not None:
        return id_source.next_id(f"startup_{role}")
    return f"startup_{role}_{uuid4().hex[:8]}"


def setup_initial_world_from_character(
    character_data,
    *,
    random_source=None,
    id_source=None,
) -> tuple[World, str]:
    """Initializes the startup world from one fully prepared character payload."""
    rng = random if random_source is None else random_source
    world = World(start_year=1, start_month=1)
    world.add_place(
        place_id="earth",
        name="Earth",
        kind="world_body",
        parent_place_id=None,
        metadata={},
    )
    for country in WORLD_GEOGRAPHY:
        world.add_place(
            place_id=country["country_id"],
            name=country["country_name"],
            kind="country",
            parent_place_id="earth",
            metadata=dict(country["metadata"]),
        )
        for city in country["cities"]:
            world.add_place(
                place_id=city["city_id"],
                name=city["city_name"],
                kind="city",
                parent_place_id=country["country_id"],
                metadata={},
            )

    startup_jurisdiction_place_id = (
        character_data.get("country_id") or DEFAULT_COUNTRY_ID
    )
    startup_place_id = character_data.get("city_id") or DEFAULT_CITY_ID
    startup_country = WORLD_GEOGRAPHY_BY_COUNTRY_ID.get(
        startup_jurisdiction_place_id
    )
    if startup_country is None:
        raise ValueError(
            f"Unknown startup country_id '{startup_jurisdiction_place_id}'"
        )
    if startup_place_id not in {
        city["city_id"] for city in startup_country["cities"]
    }:
        raise ValueError(
            "Unknown or mismatched startup city_id "
            f"'{startup_place_id}' for country_id "
            f"'{startup_jurisdiction_place_id}'"
        )

    mother_identity_context = prepare_parent_identity_context(
        role="mother",
        player_last_name=character_data["last_name"],
        place_id=startup_place_id,
        world=world,
        culture_group=startup_country["metadata"]["culture_group"],
        random_source=rng,
    )
    family_last_name = mother_identity_context["family_last_name"]
    father_identity_context = prepare_parent_identity_context(
        role="father",
        family_last_name=family_last_name,
        player_last_name=character_data["last_name"],
        place_id=startup_place_id,
        world=world,
        culture_group=startup_country["metadata"]["culture_group"],
        random_source=rng,
    )

    mother_identity = generate_parent_identity_from_context(
        mother_identity_context,
        random_source=rng,
    )
    father_identity = generate_parent_identity_from_context(
        father_identity_context,
        random_source=rng,
    )

    mother_id = generate_startup_actor_id("mother", id_source=id_source)
    father_id = generate_startup_actor_id("father", id_source=id_source)
    mother_age_years = rng.randint(22, 36)
    father_age_years = max(mother_age_years + rng.randint(1, 5), 24)
    world.create_human_actor(
        actor_id=mother_id,
        species="Human",
        first_name=mother_identity["first_name"],
        last_name=mother_identity["last_name"],
        sex=mother_identity["sex"],
        gender=mother_identity["gender"],
        birth_year=world.current_year - mother_age_years,
        birth_month=rng.randint(1, 12),
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=True,
        random_source=rng,
    )
    world.create_human_actor(
        actor_id=father_id,
        species="Human",
        first_name=father_identity["first_name"],
        last_name=father_identity["last_name"],
        sex=father_identity["sex"],
        gender=father_identity["gender"],
        birth_year=world.current_year - father_age_years,
        birth_month=rng.randint(1, 12),
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=True,
        random_source=rng,
    )
    world.add_link_pair(
        source_id=mother_id,
        target_id=father_id,
        forward_type="association",
        forward_role="coparent",
        reverse_type="association",
        reverse_role="coparent",
        forward_metadata={
            "bootstrap_source": "startup_coparent_association"
        },
        reverse_metadata={
            "bootstrap_source": "startup_coparent_association"
        },
    )

    world.bootstrap_older_siblings_for_newborn(
        mother_id=mother_id,
        father_id=father_id,
        player_birth_year=world.current_year,
        player_birth_month=1,
        random_source=rng,
        id_source=id_source,
    )

    player_id = generate_startup_actor_id("player", id_source=id_source)
    world.create_human_child_with_parents(
        child_id=player_id,
        first_name=character_data["first_name"],
        last_name=character_data["last_name"],
        sex=character_data["sex"],
        gender=character_data["gender"],
        mother_id=mother_id,
        father_id=father_id,
        birth_year=world.current_year,
        birth_month=1,
        place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=False,
        family_link_source="startup_family",
        birth_record_type="family_bootstrap",
        birth_record_text=(
            f"{character_data['first_name']} {character_data['last_name']}".strip()
            + " was bootstrapped with current startup family links."
        ),
        birth_record_tags=["family", "bootstrap"],
        birth_record_metadata={"is_startup_player": True},
        random_source=rng,
    )
    world.finalize_startup_human_actor(
        player_id,
        stats=normalize_creation_stats(
            character_data["stats"],
            random_source=rng,
        ),
        appearance=character_data["appearance"],
        traits=character_data["traits"],
        money=0,
        random_source=rng,
    )
    world.set_focused_actor(player_id)

    return world, player_id
