import random


def _event(
    event_id,
    text,
    *,
    life_stages,
    outcome=None,
    min_age_months=None,
    max_age_months=None,
    tags=None,
    family_context=False,
    family_roles=None,
):
    """Builds one normalized monthly event definition."""
    return {
        "event_id": event_id,
        "text": text,
        "life_stages": list(life_stages),
        "min_age_months": min_age_months,
        "max_age_months": max_age_months,
        "outcome": outcome if outcome is not None else {"stat_changes": {}},
        "tags": list(tags) if tags is not None else [],
        "family_context": family_context,
        "family_roles": list(family_roles) if family_roles is not None else [],
    }


# Human monthly event definitions. This pool is intentionally human-content-scoped.
HUMAN_MONTHLY_EVENTS = [
    # Infant-specific events (Age 0-2 = Months 0-35)
    _event("infant_gurgle", "You gurgle happily at a colorful toy.", life_stages=["Infant"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "infant"]),
    _event("infant_sleep_grow", "You spend the month sleeping and eating, growing stronger.", life_stages=["Infant"], max_age_months=12, outcome={"stat_changes": {"health": 1}}, tags=["positive", "infant"]),
    _event("infant_new_sound", "A new sound catches your attention, a small spark of intelligence.", life_stages=["Infant"], outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "infant"]),
    _event("infant_explore_blanket", "You explore the textures of a soft blanket.", life_stages=["Infant"], outcome={"stat_changes": {}}, tags=["neutral", "infant"]),
    _event("infant_smile", "You smile at a familiar face.", life_stages=["Infant"], min_age_months=6, outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "infant"]),
    _event("infant_sniffle", "A minor sniffle makes you a bit fussy.", life_stages=["Infant"], min_age_months=3, outcome={"stat_changes": {"health": -1}}, tags=["negative", "infant"]),
    _event("infant_grasp", "You grasp an object tightly with your tiny hand.", life_stages=["Infant"], min_age_months=1, outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "infant"]),
    _event("infant_hug", "You receive a warm hug.", life_stages=["Infant"], min_age_months=2, outcome={"stat_changes": {"happiness": 2}}, tags=["positive", "infant"]),
    _event("infant_feet_discovery", "You become briefly fascinated by your own feet.", life_stages=["Infant"], outcome={"stat_changes": {}}, tags=["goofy", "infant"]),
    _event("infant_spit_take", "You tried to eat something you definitely should not have eaten.", life_stages=["Infant"], min_age_months=4, outcome={"stat_changes": {"health": -1}}, tags=["goofy", "infant"]),
    _event("infant_roll_over", "You roll over with great effort and immediate pride.", life_stages=["Infant"], min_age_months=4, max_age_months=10, outcome={"stat_changes": {"health": 1}}, tags=["positive", "infant"]),
    _event("infant_shadow_game", "Light and shadows on the wall hold your full attention for a while.", life_stages=["Infant"], outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "infant"]),
    _event("infant_sibling_garden_play", "{family_name} played with you in the garden.", life_stages=["Infant"], min_age_months=3, outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "infant", "family"], family_context=True, family_roles=["sibling"]),
    _event("infant_bubble_laugh", "A strange noise sends you into unstoppable baby laughter.", life_stages=["Infant"], outcome={"stat_changes": {"happiness": 2}}, tags=["positive", "infant"]),

    # Child-specific events (Age 3-9 = Months 36-119)
    _event("child_imaginary_friend", "You made a new imaginary friend!", life_stages=["Child"], outcome={"stat_changes": {"happiness": 2}}, tags=["positive", "child"]),
    _event("child_draw_picture", "You drew a colorful picture.", life_stages=["Child"], outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "child"]),
    _event("child_play_outside", "You played outside and got a little dirty.", life_stages=["Child"], min_age_months=48, outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "child"]),
    _event("child_tie_shoes", "You learned to tie your shoes!", life_stages=["Child"], min_age_months=60, outcome={"stat_changes": {"intelligence": 2}}, tags=["positive", "child"]),
    _event("child_simple_chore", "You helped a parent with a simple chore.", life_stages=["Child"], min_age_months=40, outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "child"]),
    _event("child_read_book", "You read a new children's book.", life_stages=["Child"], min_age_months=48, outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "child"]),
    _event("child_scrape", "A minor scrape from playing, quickly forgotten.", life_stages=["Child"], min_age_months=36, outcome={"stat_changes": {"health": -1}}, tags=["negative", "child"]),
    _event("child_playdate", "You had a fun playdate with another child.", life_stages=["Child"], min_age_months=48, outcome={"stat_changes": {"happiness": 2}}, tags=["positive", "child"]),
    _event("child_puddle_jump", "You found a puddle too tempting to avoid.", life_stages=["Child"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "child"]),
    _event("child_cardboard_fort", "You turned ordinary clutter into an impressive fortress.", life_stages=["Child"], min_age_months=42, outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "child"]),
    _event("child_lost_treasure", "You misplaced something extremely important to you for nearly a whole day.", life_stages=["Child"], outcome={"stat_changes": {"happiness": -1}}, tags=["negative", "child"]),
    _event("child_bug_observation", "You spent a while studying a tiny bug with serious concentration.", life_stages=["Child"], outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "child"]),
    _event("child_bedtime_story", "{family_name} told you a bedtime story.", life_stages=["Child"], min_age_months=36, outcome={"stat_changes": {"happiness": 2}}, tags=["positive", "child", "family"], family_context=True, family_roles=["mother", "father"]),
    _event("child_sibling_race", "{family_name} challenged you to see who could run faster.", life_stages=["Child"], min_age_months=48, outcome={"stat_changes": {"health": 1}}, tags=["positive", "child", "family"], family_context=True, family_roles=["sibling"]),
    _event("child_wrong_snack", "You tried to eat something you definitely should not have eaten.", life_stages=["Child"], min_age_months=36, outcome={"stat_changes": {"health": -1}}, tags=["goofy", "child"]),
    _event("child_secret_word", "You invented a secret word that seemed brilliant at the time.", life_stages=["Child"], outcome={"stat_changes": {}}, tags=["goofy", "child"]),

    # Teenager-specific events (Age 10-17)
    _event("teen_join_club", "You join an after-school club and find it surprisingly rewarding.", life_stages=["Teenager"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "teenager"]),
    _event("teen_study_session", "You spend extra time studying and understand a difficult topic a little better.", life_stages=["Teenager"], outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "teenager"]),
    _event("teen_pickup_game", "You join a casual game with other teens and come home tired but upbeat.", life_stages=["Teenager"], min_age_months=132, outcome={"stat_changes": {"health": 1}}, tags=["positive", "teenager"]),
    _event("teen_bad_sleep", "A restless week leaves you a little run down by the end of the month.", life_stages=["Teenager"], min_age_months=120, outcome={"stat_changes": {"health": -1}}, tags=["negative", "teenager"]),
    _event("teen_new_style", "You tried a new look and felt unexpectedly confident about it.", life_stages=["Teenager"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "teenager"]),
    _event("teen_embarrassing_memory", "An old embarrassing moment returns to haunt you at the worst possible time.", life_stages=["Teenager"], outcome={"stat_changes": {"happiness": -1}}, tags=["negative", "teenager"]),
    _event("teen_long_thought", "You stayed up late thinking about who you want to become.", life_stages=["Teenager"], outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral", "teenager"]),
    _event("teen_silly_argument", "You had a silly argument with {family_name}.", life_stages=["Teenager"], outcome={"stat_changes": {"happiness": -1}}, tags=["family", "teenager"], family_context=True, family_roles=["sibling"]),
    _event("teen_quiet_bike_ride", "A quiet ride gave you space to clear your head.", life_stages=["Teenager"], outcome={"stat_changes": {"health": 1}}, tags=["positive", "teenager"]),
    _event("teen_overheard_advice", "You overheard adult advice that was either wise or completely useless.", life_stages=["Teenager"], outcome={"stat_changes": {}}, tags=["neutral", "teenager"]),
    _event("teen_room_rearrange", "You rearranged your space for no clear reason and somehow felt better after.", life_stages=["Teenager"], outcome={"stat_changes": {"happiness": 1}}, tags=["neutral", "teenager"]),
    _event("teen_social_stumble", "A small awkward moment lingers in your mind much longer than it should.", life_stages=["Teenager"], outcome={"stat_changes": {"happiness": -1}}, tags=["negative", "teenager"]),
    _event("teen_hold_breath_contest", "{family_name} challenged you to see who could hold their breath longer.", life_stages=["Teenager"], outcome={"stat_changes": {"health": 1}}, tags=["family", "teenager"], family_context=True, family_roles=["sibling"]),
    _event("teen_lost_argument_with_self", "You had an argument with yourself. You lost.", life_stages=["Teenager", "Young Adult"], outcome={"stat_changes": {}}, tags=["goofy"]),

    # Young-adult-specific events (Age 18-24)
    _event("young_adult_budget_meal", "You stretch your money with a simple homemade meal plan.", life_stages=["Young Adult"], outcome={"stat_changes": {"money": 1}}, tags=["neutral", "young_adult"]),
    _event("young_adult_library_visit", "You spend an afternoon at the library and leave with a fresh idea.", life_stages=["Young Adult"], outcome={"stat_changes": {"intelligence": 1}}, tags=["positive", "young_adult"]),
    _event("young_adult_long_walk", "You take a long walk to clear your head after a busy month.", life_stages=["Young Adult"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "young_adult"]),
    _event("young_adult_unexpected_fee", "An unexpected small fee forces you to watch your spending more closely.", life_stages=["Young Adult"], outcome={"stat_changes": {"money": -1}}, tags=["negative", "young_adult"]),
    _event("young_adult_missed_bus", "A badly timed delay throws off your whole day.", life_stages=["Young Adult", "Adult"], outcome={"stat_changes": {"happiness": -1}}, tags=["negative"]),
    _event("young_adult_clear_morning", "A clear morning makes the future feel a little more manageable.", life_stages=["Young Adult"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "young_adult"]),
    _event("young_adult_new_recipe", "You tried a new recipe and it turned out better than expected.", life_stages=["Young Adult", "Adult"], outcome={"stat_changes": {"health": 1}}, tags=["positive"]),
    _event("young_adult_bad_purchase", "You spent money on something that immediately felt unnecessary.", life_stages=["Young Adult"], outcome={"stat_changes": {"money": -1}}, tags=["negative", "young_adult"]),
    _event("young_adult_day_trip", "A small adventure breaks up the routine of the month.", life_stages=["Young Adult"], outcome={"stat_changes": {"happiness": 2}}, tags=["positive", "young_adult"]),
    _event("young_adult_called_family", "You called {family_name} just to chat.", life_stages=["Young Adult", "Adult"], outcome={"stat_changes": {"happiness": 1}}, tags=["family"], family_context=True, family_roles=["mother", "father", "sibling"]),
    _event("young_adult_laundry_delay", "You put something off until it became mildly ridiculous.", life_stages=["Young Adult", "Adult"], outcome={"stat_changes": {}}, tags=["goofy"]),
    _event("young_adult_park_bench_thought", "You sat quietly for a while and let your thoughts settle.", life_stages=["Young Adult", "Adult", "Elder"], outcome={"stat_changes": {"intelligence": 1}}, tags=["neutral"]),
    _event("young_adult_peaceful_afternoon", "You enjoyed a peaceful afternoon.", life_stages=["Young Adult", "Adult", "Elder"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive"]),
    _event("young_adult_tiny_victory", "A small personal victory carries you farther than expected.", life_stages=["Young Adult"], outcome={"stat_changes": {"happiness": 1, "intelligence": 1}}, tags=["positive", "young_adult"]),

    # Adult-specific events (Age 25-64)
    _event("adult_home_cooked_meal", "You make time for a decent home-cooked meal and feel better for it.", life_stages=["Adult"], outcome={"stat_changes": {"health": 1}}, tags=["positive", "adult"]),
    _event("adult_quiet_weekend", "You give yourself a quiet weekend and return to routine in better spirits.", life_stages=["Adult"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "adult"]),
    _event("adult_plan_ahead", "You plan ahead for upcoming expenses and keep a little more money on hand.", life_stages=["Adult"], outcome={"stat_changes": {"money": 1}}, tags=["neutral", "adult"]),
    _event("adult_minor_ache", "A minor ache slows you down for a few days, but it passes.", life_stages=["Adult"], min_age_months=300, outcome={"stat_changes": {"health": -1}}, tags=["negative", "adult"]),
    _event("adult_forgot_room", "You forgot why you walked into the room.", life_stages=["Adult", "Elder"], outcome={"stat_changes": {}}, tags=["goofy"]),
    _event("adult_window_weather", "You spent a moment just watching the weather move past.", life_stages=["Adult", "Elder"], outcome={"stat_changes": {}}, tags=["neutral"]),
    _event("adult_nice_conversation", "A brief conversation leaves you in a better mood than expected.", life_stages=["Adult"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "adult"]),
    _event("adult_misplaced_item", "You lost track of a necessary object and found it in an obvious place.", life_stages=["Adult"], outcome={"stat_changes": {"happiness": -1}}, tags=["negative", "adult"]),
    _event("adult_called_family", "You called {family_name} just to chat.", life_stages=["Adult"], outcome={"stat_changes": {"happiness": 1}}, tags=["family", "adult"], family_context=True, family_roles=["mother", "father", "sibling"]),
    _event("adult_self_argument", "You had an argument with yourself. You lost.", life_stages=["Adult", "Elder"], outcome={"stat_changes": {}}, tags=["goofy"]),
    _event("adult_fixed_small_problem", "You solved a small problem that had been annoying you for too long.", life_stages=["Adult"], outcome={"stat_changes": {"intelligence": 1}}, tags=["positive", "adult"]),
    _event("adult_evening_stretch", "You gave your body a little care and felt the difference.", life_stages=["Adult", "Elder"], outcome={"stat_changes": {"health": 1}}, tags=["positive"]),
    _event("adult_unnecessary_worry", "You worried about something that never actually happened.", life_stages=["Adult"], outcome={"stat_changes": {"happiness": -1}}, tags=["negative", "adult"]),
    _event("adult_shared_meal_memory", "A familiar smell brings back a memory you had forgotten.", life_stages=["Adult", "Elder"], outcome={"stat_changes": {}}, tags=["neutral"]),

    # Elder-specific events (Age 65+)
    _event("elder_garden_walk", "You enjoy a gentle walk and appreciate the slower pace of the day.", life_stages=["Elder"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "elder"]),
    _event("elder_share_story", "You share an old story and feel pleasantly sharp while telling it.", life_stages=["Elder"], outcome={"stat_changes": {"intelligence": 1}}, tags=["positive", "elder"]),
    _event("elder_rest_day", "You take an extra rest day and let yourself move a little more gently.", life_stages=["Elder"], outcome={"stat_changes": {}}, tags=["neutral", "elder"]),
    _event("elder_stiff_morning", "A stiff morning reminds you to take things slowly this month.", life_stages=["Elder"], outcome={"stat_changes": {"health": -1}}, tags=["negative", "elder"]),
    _event("elder_old_joke", "An old joke still makes you laugh.", life_stages=["Elder"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "elder"]),
    _event("elder_shared_stories", "You shared old stories with {family_name}.", life_stages=["Elder"], outcome={"stat_changes": {"happiness": 1}}, tags=["family", "elder"], family_context=True, family_roles=["mother", "father", "sibling"]),
    _event("elder_slow_morning", "You take your time starting the day and refuse to feel bad about it.", life_stages=["Elder"], outcome={"stat_changes": {}}, tags=["neutral", "elder"]),
    _event("elder_forgot_name", "A name sat just out of reach until much later.", life_stages=["Elder"], outcome={"stat_changes": {"intelligence": -1}}, tags=["negative", "elder"]),
    _event("elder_birdwatch", "You spent time quietly watching birds and felt content.", life_stages=["Elder"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "elder"]),
    _event("elder_found_keepsake", "You found an old keepsake and lingered with the memory a while.", life_stages=["Elder"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "elder"]),
    _event("elder_weather_commentary", "You gave the weather a very thorough review.", life_stages=["Elder"], outcome={"stat_changes": {}}, tags=["goofy", "elder"]),
    _event("elder_small_wisdom", "You had a quiet moment of clarity about what matters.", life_stages=["Elder"], outcome={"stat_changes": {"intelligence": 1}}, tags=["positive", "elder"]),
    _event("elder_comfort_food", "You made something simple and familiar and enjoyed every bite.", life_stages=["Elder"], outcome={"stat_changes": {"health": 1}}, tags=["positive", "elder"]),
    _event("elder_peaceful_evening", "The evening passes gently, and that feels like enough.", life_stages=["Elder"], outcome={"stat_changes": {"happiness": 1}}, tags=["positive", "elder"]),
]


def _normalize_family_role(role):
    """Maps display labels and plural buckets to one family-role key."""
    normalized_role = str(role or "").strip().lower()
    role_map = {
        "mother": "mother",
        "father": "father",
        "brother": "sibling",
        "sister": "sibling",
        "sibling": "sibling",
        "son": "child",
        "daughter": "child",
        "child": "child",
        "parent": "parent",
    }
    return role_map.get(normalized_role, normalized_role)


def _get_matching_family_members(family_context, required_roles):
    """Returns family members that satisfy one or more requested roles."""
    if not family_context:
        return []

    normalized_required_roles = {_normalize_family_role(role) for role in required_roles}
    if not normalized_required_roles:
        return []

    matching_members = []
    for members in family_context.values():
        for member in members:
            member_role_key = member.get("role_key")
            if member_role_key is None:
                member_role_key = _normalize_family_role(member.get("role"))
            if member_role_key in normalized_required_roles:
                matching_members.append(member)
    return matching_members


def _get_human_eligible_events(lifecycle_state: dict, family_context=None) -> list[dict]:
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

        if event.get("family_context"):
            matching_family = _get_matching_family_members(
                family_context,
                event.get("family_roles") or [],
            )
            if not matching_family:
                continue

        eligible_events.append(event)

    return eligible_events


def _render_event_text(chosen_event, family_context):
    """Renders one event text, resolving family placeholders when required."""
    event_text = chosen_event["text"]
    if not chosen_event.get("family_context"):
        return event_text

    matching_family = _get_matching_family_members(
        family_context,
        chosen_event.get("family_roles") or [],
    )
    if not matching_family:
        return event_text

    family_member = random.choice(matching_family)
    return event_text.format(
        family_name=family_member["name"],
        family_role=family_member["role"],
    )


def get_human_monthly_event_from_lifecycle(
    lifecycle_state: dict,
    current_year: int,
    current_month: int,
    family_context=None,
) -> dict | None:
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

    eligible_events = _get_human_eligible_events(lifecycle_state, family_context=family_context)
    if not eligible_events:
        return None

    chosen_event = random.choice(eligible_events)

    return {
        "event_id": chosen_event["event_id"],
        "text": _render_event_text(chosen_event, family_context),
        "outcome": {
            "stat_changes": dict(chosen_event.get("outcome", {}).get("stat_changes", {}))
        },
        "tags": chosen_event.get("tags", []),
        "year": current_year,
        "month": current_month,
    }


def get_monthly_event(human_obj, current_year: int, current_month: int, family_context=None) -> dict | None:
    """
    Compatibility wrapper for the current human monthly event contract.
    The current event content remains human-scoped and derives event eligibility from lifecycle state
    instead of coupling selection logic to the concrete Human class import.
    """
    lifecycle_state = human_obj.get_lifecycle_state(current_year, current_month)
    return get_human_monthly_event_from_lifecycle(
        lifecycle_state,
        current_year,
        current_month,
        family_context=family_context,
    )
