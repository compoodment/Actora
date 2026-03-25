import random

# Human monthly event definitions. This pool is intentionally human-content-scoped.
HUMAN_MONTHLY_EVENTS = [
    # Infant-specific events (Age 0-2 = Months 0-35)
    {"event_id": "infant_gurgle", "text": "You gurgle happily at a colorful toy.", "stat": "happiness", "change": 1, "life_stages": ["Infant"], "tags": ["positive", "infant"]},
    {"event_id": "infant_sleep_grow", "text": "You spend the month sleeping and eating, growing stronger.", "stat": "health", "change": 1, "life_stages": ["Infant"], "max_age_months": 12, "tags": ["positive", "infant"]},
    {"event_id": "infant_new_sound", "text": "A new sound catches your attention, a small spark of intelligence.", "stat": "intelligence", "change": 1, "life_stages": ["Infant"], "tags": ["neutral", "infant"]},
    {"event_id": "infant_explore_blanket", "text": "You explore the textures of a soft blanket.", "stat": None, "change": 0, "life_stages": ["Infant"], "tags": ["neutral", "infant"]},
    {"event_id": "infant_smile", "text": "You smile at a familiar face.", "stat": "happiness", "change": 1, "life_stages": ["Infant"], "min_age_months": 6, "tags": ["positive", "infant"]},
    {"event_id": "infant_sniffle", "text": "A minor sniffle makes you a bit fussy.", "stat": "health", "change": -1, "life_stages": ["Infant"], "min_age_months": 3, "tags": ["negative", "infant"]},
    {"event_id": "infant_grasp", "text": "You grasp an object tightly with your tiny hand.", "stat": "intelligence", "change": 1, "life_stages": ["Infant"], "min_age_months": 1, "tags": ["neutral", "infant"]},
    {"event_id": "infant_hug", "text": "You receive a warm hug.", "stat": "happiness", "change": 2, "life_stages": ["Infant"], "min_age_months": 2, "tags": ["positive", "infant"]},

    # Child-specific events (Age 3-9 = Months 36-119)
    {"event_id": "child_imaginary_friend", "text": "You made a new imaginary friend!", "stat": "happiness", "change": 2, "life_stages": ["Child"], "tags": ["positive", "child"]},
    {"event_id": "child_draw_picture", "text": "You drew a colorful picture.", "stat": "intelligence", "change": 1, "life_stages": ["Child"], "tags": ["neutral", "child"]},
    {"event_id": "child_play_outside", "text": "You played outside and got a little dirty.", "stat": "happiness", "change": 1, "life_stages": ["Child"], "min_age_months": 48, "tags": ["positive", "child"]},
    {"event_id": "child_tie_shoes", "text": "You learned to tie your shoes!", "stat": "intelligence", "change": 2, "life_stages": ["Child"], "min_age_months": 60, "tags": ["positive", "child"]},
    {"event_id": "child_simple_chore", "text": "You helped a parent with a simple chore.", "stat": "happiness", "change": 1, "life_stages": ["Child"], "min_age_months": 40, "tags": ["positive", "child"]},
    {"event_id": "child_read_book", "text": "You read a new children's book.", "stat": "intelligence", "change": 1, "life_stages": ["Child"], "min_age_months": 48, "tags": ["neutral", "child"]},
    {"event_id": "child_scrape", "text": "A minor scrape from playing, quickly forgotten.", "stat": "health", "change": -1, "life_stages": ["Child"], "min_age_months": 36, "tags": ["negative", "child"]},
    {"event_id": "child_playdate", "text": "You had a fun playdate with another child.", "stat": "happiness", "change": 2, "life_stages": ["Child"], "min_age_months": 48, "tags": ["positive", "child"]},

    # Teenager-specific events (Age 10-17)
    {"event_id": "teen_join_club", "text": "You join an after-school club and find it surprisingly rewarding.", "stat": "happiness", "change": 1, "life_stages": ["Teenager"], "tags": ["positive", "teenager"]},
    {"event_id": "teen_study_session", "text": "You spend extra time studying and understand a difficult topic a little better.", "stat": "intelligence", "change": 1, "life_stages": ["Teenager"], "tags": ["neutral", "teenager"]},
    {"event_id": "teen_pickup_game", "text": "You join a casual game with other teens and come home tired but upbeat.", "stat": "health", "change": 1, "life_stages": ["Teenager"], "min_age_months": 132, "tags": ["positive", "teenager"]},
    {"event_id": "teen_bad_sleep", "text": "A restless week leaves you a little run down by the end of the month.", "stat": "health", "change": -1, "life_stages": ["Teenager"], "min_age_months": 120, "tags": ["negative", "teenager"]},

    # Young-adult-specific events (Age 18-24)
    {"event_id": "young_adult_budget_meal", "text": "You stretch your money with a simple homemade meal plan.", "stat": "money", "change": 1, "life_stages": ["Young Adult"], "tags": ["neutral", "young_adult"]},
    {"event_id": "young_adult_library_visit", "text": "You spend an afternoon at the library and leave with a fresh idea.", "stat": "intelligence", "change": 1, "life_stages": ["Young Adult"], "tags": ["positive", "young_adult"]},
    {"event_id": "young_adult_long_walk", "text": "You take a long walk to clear your head after a busy month.", "stat": "happiness", "change": 1, "life_stages": ["Young Adult"], "tags": ["positive", "young_adult"]},
    {"event_id": "young_adult_unexpected_fee", "text": "An unexpected small fee forces you to watch your spending more closely.", "stat": "money", "change": -1, "life_stages": ["Young Adult"], "tags": ["negative", "young_adult"]},

    # Adult-specific events (Age 25-64)
    {"event_id": "adult_home_cooked_meal", "text": "You make time for a decent home-cooked meal and feel better for it.", "stat": "health", "change": 1, "life_stages": ["Adult"], "tags": ["positive", "adult"]},
    {"event_id": "adult_quiet_weekend", "text": "You give yourself a quiet weekend and return to routine in better spirits.", "stat": "happiness", "change": 1, "life_stages": ["Adult"], "tags": ["positive", "adult"]},
    {"event_id": "adult_plan_ahead", "text": "You plan ahead for upcoming expenses and keep a little more money on hand.", "stat": "money", "change": 1, "life_stages": ["Adult"], "tags": ["neutral", "adult"]},
    {"event_id": "adult_minor_ache", "text": "A minor ache slows you down for a few days, but it passes.", "stat": "health", "change": -1, "life_stages": ["Adult"], "min_age_months": 300, "tags": ["negative", "adult"]},

    # Elder-specific events (Age 65+)
    {"event_id": "elder_garden_walk", "text": "You enjoy a gentle walk and appreciate the slower pace of the day.", "stat": "happiness", "change": 1, "life_stages": ["Elder"], "tags": ["positive", "elder"]},
    {"event_id": "elder_share_story", "text": "You share an old story and feel pleasantly sharp while telling it.", "stat": "intelligence", "change": 1, "life_stages": ["Elder"], "tags": ["positive", "elder"]},
    {"event_id": "elder_rest_day", "text": "You take an extra rest day and let yourself move a little more gently.", "stat": None, "change": 0, "life_stages": ["Elder"], "tags": ["neutral", "elder"]},
    {"event_id": "elder_stiff_morning", "text": "A stiff morning reminds you to take things slowly this month.", "stat": "health", "change": -1, "life_stages": ["Elder"], "tags": ["negative", "elder"]},
]


def _get_human_eligible_events(lifecycle_state: dict) -> list[dict]:
    """Filters the current human monthly event pool using derived lifecycle state."""
    age_in_months = lifecycle_state["age_months"]
    life_stage = lifecycle_state["life_stage"]

    eligible_events = []
    for event in HUMAN_MONTHLY_EVENTS:
        if event.get("life_stages") and life_stage not in event["life_stages"]:
            continue

        if event.get("min_age_months") is not None and age_in_months < event["min_age_months"]:
            continue
        if event.get("max_age_months") is not None and age_in_months > event["max_age_months"]:
            continue

        eligible_events.append(event)

    return eligible_events


def get_human_monthly_event_from_lifecycle(lifecycle_state: dict, current_year: int, current_month: int) -> dict | None:
    """
    Selects a monthly event from the current human-only content pool using derived lifecycle state.
    This helper does not imply species-general event support; it only makes the current boundary
    honest by separating human event selection from the concrete Human model object.
    """
    if lifecycle_state.get("life_stage_model") != "human_default":
        return None

    # 50% chance to generate an event this month
    if random.random() >= 0.5:
        return None

    eligible_events = _get_human_eligible_events(lifecycle_state)
    if not eligible_events:
        return None

    chosen_event = random.choice(eligible_events)

    stat_changes = {}
    if chosen_event["stat"]:
        stat_changes[chosen_event["stat"]] = chosen_event["change"]

    outcome = {
        "stat_changes": dict(stat_changes)
    }

    return {
        "event_id": chosen_event["event_id"],
        "text": chosen_event["text"],
        "outcome": outcome,
        "tags": chosen_event.get("tags", []),
        "year": current_year,
        "month": current_month,
    }


def get_monthly_event(human_obj, current_year: int, current_month: int) -> dict | None:
    """
    Compatibility wrapper for the current human monthly event contract.
    The current event content remains human-scoped and derives event eligibility from lifecycle state
    instead of coupling selection logic to the concrete Human class import.
    """
    lifecycle_state = human_obj.get_lifecycle_state(current_year, current_month)
    return get_human_monthly_event_from_lifecycle(lifecycle_state, current_year, current_month)
