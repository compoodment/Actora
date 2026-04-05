SKIP_MONTH_PRESETS = (1, 3, 6, 12, 24, 60)
HANG_OUT_TIME_COST = 4  # hours
EXERCISE_TIME_COST = 6  # hours (estimated ~1.5hr session, 4 sessions/month)
READ_TIME_COST = 8  # hours (estimated ~2hr/session, 4 sessions/month)
REST_TIME_COST = 4  # hours (a proper rest day equivalent)

EXERCISE_SUBTYPES = [
    {"id": "home_workout", "label": "Home Workout", "time_cost": 4, "stat_changes": {"strength": 2, "health": 1}, "event_text": "You worked out at home."},
    {"id": "gym_session", "label": "Gym Session", "time_cost": 6, "stat_changes": {"strength": 3, "health": 2}, "event_text": "You hit the gym."},
    {"id": "run", "label": "Go for a Run", "time_cost": 3, "stat_changes": {"health": 3, "strength": 1}, "event_text": "You went for a run."},
]
READ_SUBTYPES = [
    {"id": "read_fiction", "label": "Read Fiction", "time_cost": 6, "stat_changes": {"happiness": 2, "imagination": 2}, "event_text": "You got lost in a good novel."},
    {"id": "read_nonfic", "label": "Read Non-Fiction", "time_cost": 6, "stat_changes": {"intelligence": 2, "wisdom": 1}, "event_text": "You read something that made you think."},
    {"id": "read_history", "label": "Read History", "time_cost": 6, "stat_changes": {"wisdom": 3}, "event_text": "You read about the past."},
    {"id": "read_science", "label": "Read Science", "time_cost": 6, "stat_changes": {"intelligence": 3}, "event_text": "You read something scientific."},
]
REST_SUBTYPES = [
    {"id": "nap", "label": "Take a Nap", "time_cost": 2, "stat_changes": {"happiness": 2, "stress": -3}, "event_text": "You took a proper nap."},
    {"id": "music", "label": "Listen to Music", "time_cost": 2, "stat_changes": {"happiness": 3, "stress": -2}, "event_text": "You put on some music and let yourself unwind."},
    {"id": "walk", "label": "Take a Walk", "time_cost": 2, "stat_changes": {"happiness": 2, "health": 1}, "event_text": "You went for a walk and cleared your head."},
]

TRAIT_DEFINITIONS = {
    "Driven": {"sleep_modifier": -0.5},
    "Chill": {"sleep_modifier": +0.5},
    "Curious": {"sleep_modifier": 0.0},
    "Social": {"sleep_modifier": 0.0},
    "Disciplined": {"sleep_modifier": -0.5},
    "Impulsive": {"sleep_modifier": 0.0},
    "Empathetic": {"sleep_modifier": 0.0},
    "Resilient": {"sleep_modifier": 0.0},
    "Introverted": {"sleep_modifier": +0.5},
    "Extraverted": {"sleep_modifier": -0.5},
    "Restless": {"sleep_modifier": -1.0},
    "Ambitious": {"sleep_modifier": 0.0},
}


def get_monthly_free_hours(actor):
    """Returns the actor's monthly free hours based on sleep hours from traits."""
    sleep_modifier = 0.0
    for trait in getattr(actor, "traits", []):
        defn = TRAIT_DEFINITIONS.get(trait, {})
        sleep_modifier += defn.get("sleep_modifier", 0.0)
    sleep_hours = (8.0 + sleep_modifier) * 30
    maintenance_hours = 120
    return 720 - sleep_hours - maintenance_hours
