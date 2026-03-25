import random

MOTHER_FIRST_NAME_POOL = [
    "Aisha", "Anja", "Chiyo", "Elena", "Fatima", "Gabriela", "Hana", "Indira",
    "Jian", "Kailani", "Leila", "Mina", "Nia", "Renata", "Sofia", "Yara"
]

FATHER_FIRST_NAME_POOL = [
    "Arjun", "Bashir", "Carlos", "Daiki", "Ethan", "Felix", "Gao", "Haruki",
    "Javier", "Kwame", "Liam", "Musa", "Nikhil", "Omar", "Pablo", "Ravi"
]

FALLBACK_LAST_NAME_POOL = [
    "Abdullah", "Chen", "Díaz", "Eriksson", "Fernandez", "Gupta", "Hoffmann",
    "Ibrahim", "Kim", "Kovač", "Lee", "Müller", "Nakamura", "O'Sullivan",
    "Pereira", "Rossi", "Schmidt", "Silva", "Singh", "Smirnov", "Tan",
    "Wang", "Williams", "Zafar"
]


def resolve_family_last_name(player_last_name):
    if player_last_name:
        return player_last_name

    return random.choice(FALLBACK_LAST_NAME_POOL)


def prepare_parent_identity_context(
    role,
    player_last_name=None,
    family_last_name=None,
    species="Human",
    world=None,
    place_id=None,
    culture_key=None,
    era_key=None,
):
    """Builds the current structured identity-generation seam for startup parent generation.

    The returned context intentionally accepts future-facing fields, but the current
    implementation still resolves names through placeholder global pools.
    """
    resolved_family_last_name = family_last_name
    if resolved_family_last_name is None:
        resolved_family_last_name = resolve_family_last_name(player_last_name)

    return {
        "role": role,
        "species": species,
        "family_last_name": resolved_family_last_name,
        "player_last_name": player_last_name,
        "world": world,
        "place_id": place_id,
        "culture_key": culture_key,
        "era_key": era_key,
        "generation_mode": "placeholder_global_pools",
    }


def generate_parent_identity_from_context(identity_context):
    """Generates a parent identity from a structured context seam.

    Current behavior remains intentionally narrow and human-only: role selection and
    placeholder/global name pools are the only active generation inputs today.
    """
    role = identity_context.get("role")
    family_last_name = identity_context.get("family_last_name")

    if family_last_name is None:
        family_last_name = resolve_family_last_name(identity_context.get("player_last_name"))

    if role == "mother":
        return {
            "first_name": random.choice(MOTHER_FIRST_NAME_POOL),
            "last_name": family_last_name,
            "sex": "Female",
            "gender": "Female",
        }

    if role == "father":
        return {
            "first_name": random.choice(FATHER_FIRST_NAME_POOL),
            "last_name": family_last_name,
            "sex": "Male",
            "gender": "Male",
        }

    raise ValueError("role must be 'mother' or 'father'")


def generate_parent_identity(role, family_last_name, generation_context=None):
    context = prepare_parent_identity_context(
        role=role,
        family_last_name=family_last_name,
        player_last_name=(generation_context or {}).get("player_last_name") if generation_context else None,
        species=(generation_context or {}).get("species", "Human") if generation_context else "Human",
        world=(generation_context or {}).get("world") if generation_context else None,
        place_id=(generation_context or {}).get("place_id") if generation_context else None,
        culture_key=(generation_context or {}).get("culture_key") if generation_context else None,
        era_key=(generation_context or {}).get("era_key") if generation_context else None,
    )
    return generate_parent_identity_from_context(context)
