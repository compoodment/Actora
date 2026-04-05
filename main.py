import curses
import random
import time
import textwrap
from uuid import uuid4


from events import get_meeting_event_for_player
from human import Human
from identity import prepare_parent_identity_context, generate_parent_identity_from_context
from world import World

LINEAGE_RECORD_LIMIT = 6
INSPECT_RECORD_LIMIT = 5
SKIP_MONTH_PRESETS = (1, 3, 6, 12, 24, 60)
INPUT_INTERRUPTED_MESSAGE = "Input interrupted. Exiting Actora."
LINEAGE_FILTER_LABELS = {
    "all": "All",
    "living": "Living",
    "dead": "Dead",
}
REL_FILTER_OPTIONS = ["all", "family", "friends", "former", "living", "dead"]
REL_FILTER_LABELS = {
    "all": "All",
    "family": "Family",
    "friends": "Friends",
    "former": "Past",
    "living": "Living",
    "dead": "Dead",
}
MAIN_LEFT_SECTION_KEYS = ("identity", "location", "statistics", "relationships")
HIDDEN_PLAYER_RECORD_TYPES = {"family_bootstrap", "actor_entry"}
BACK_KEYS = {
    curses.KEY_BACKSPACE, 127, 8,
}
MAIN_IDLE_MESSAGE = "Living your life."
ADVANCE_THROTTLE_SECONDS = 0.2
MEETING_EVENT_COOLDOWN_MONTHS = 18
CREATION_SEX_OPTIONS = ["Male", "Female", "Intersex"]
CREATION_EYE_COLOR_OPTIONS = ["Brown", "Blue", "Green", "Hazel", "Gray", "Amber", "Other"]
CREATION_HAIR_COLOR_OPTIONS = ["Black", "Brown", "Blonde", "Red", "Auburn", "Other"]
CREATION_SKIN_TONE_OPTIONS = ["Light", "Fair", "Medium", "Olive", "Tan", "Brown", "Dark", "Other"]
CREATION_TRAIT_POOL = ["Driven", "Chill", "Curious", "Social", "Disciplined", "Impulsive", "Empathetic", "Resilient", "Introverted", "Extraverted", "Restless", "Ambitious"]
HANG_OUT_TIME_COST = 4  # hours
EXERCISE_TIME_COST = 6  # hours (estimated ~1.5hr session, 4 sessions/month)
READ_TIME_COST = 8  # hours (estimated ~2hr/session, 4 sessions/month)
REST_TIME_COST = 4  # hours (a proper rest day equivalent)
EXERCISE_SUBTYPES = [
    {"id": "home_workout", "label": "Home Workout", "time_cost": 4, "stat_changes": {"strength": 2, "health": 1}},
    {"id": "gym_session", "label": "Gym Session", "time_cost": 6, "stat_changes": {"strength": 3, "health": 2}},
    {"id": "run", "label": "Go for a Run", "time_cost": 3, "stat_changes": {"health": 3, "strength": 1}},
]
READ_SUBTYPES = [
    {"id": "read_fiction", "label": "Read Fiction", "time_cost": 6, "stat_changes": {"happiness": 2, "imagination": 2}},
    {"id": "read_nonfic", "label": "Read Non-Fiction", "time_cost": 6, "stat_changes": {"intelligence": 2, "wisdom": 1}},
    {"id": "read_history", "label": "Read History", "time_cost": 6, "stat_changes": {"wisdom": 3}},
    {"id": "read_science", "label": "Read Science", "time_cost": 6, "stat_changes": {"intelligence": 3}},
]
REST_SUBTYPES = [
    {"id": "nap", "label": "Take a Nap", "time_cost": 2, "stat_changes": {"happiness": 2, "stress": -3}},
    {"id": "music", "label": "Listen to Music", "time_cost": 2, "stat_changes": {"happiness": 3, "stress": -2}},
    {"id": "walk", "label": "Take a Walk", "time_cost": 2, "stat_changes": {"happiness": 2, "health": 1}},
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


def format_stat_change_summary(stat_changes):
    parts = []
    for stat_name, amount in stat_changes.items():
        label = CREATION_STAT_LABELS.get(stat_name, stat_name.replace("_", " ").title())
        sign = "+" if amount > 0 else "-"
        parts.append(f"{sign}{label}")
    return " ".join(parts)

QUESTIONNAIRE_QUESTIONS = [
    {
        "style": "childhood",
        "text": "As a kid, what did you do when you had a free afternoon?",
        "options": [
            {"text": "I was already outside before anyone noticed I had left", "stat_changes": {"health": 4, "strength": 3}, "trait_suggest": "Restless"},
            {"text": "I found something to take apart, build, or figure out", "stat_changes": {"intelligence": 5, "imagination": 4}, "trait_suggest": "Curious"},
            {"text": "I would find one person and spend the whole afternoon with them", "stat_changes": {"charisma": 4, "happiness": 4}, "trait_suggest": "Social"},
            {"text": "I would end up somewhere quiet, reading or just thinking", "stat_changes": {"intelligence": 4, "wisdom": 4}, "trait_suggest": "Introverted"},
        ],
    },
    {
        "style": "situational",
        "text": "When you decide you want something...",
        "options": [
            {"text": "I go after it before I talk myself out of it", "stat_changes": {"imagination": 4, "happiness": 3}, "trait_suggest": "Impulsive"},
            {"text": "I adapt the plan to whatever is in the way and keep moving", "stat_changes": {"willpower": 5, "discipline": 3}, "trait_suggest": "Driven"},
            {"text": "I sit with it until I am sure it is actually worth pursuing", "stat_changes": {"discipline": 6, "intelligence": 3}, "trait_suggest": "Disciplined"},
            {"text": "I trust that if it is meant to happen, it will", "stat_changes": {"happiness": 5, "wisdom": 3}, "trait_suggest": "Chill"},
        ],
    },
    {
        "style": "situational",
        "text": "In a room full of people you do not know...",
        "options": [
            {"text": "I am already talking to someone", "stat_changes": {"charisma": 6, "happiness": 4}, "trait_suggest": "Extraverted"},
            {"text": "I find the one interesting person and stay there", "stat_changes": {"intelligence": 4, "charisma": 3}, "trait_suggest": "Curious"},
            {"text": "I watch for a while before deciding who is worth talking to", "stat_changes": {"wisdom": 5, "intelligence": 3}, "trait_suggest": "Introverted"},
            {"text": "I make sure everyone seems comfortable before I do", "stat_changes": {"charisma": 4, "happiness": 4}, "trait_suggest": "Empathetic"},
        ],
    },
    {
        "style": "spectrum",
        "text": "What does it mean to you to succeed at something?",
        "options": [
            {"text": "Getting there faster and better than anyone expected", "stat_changes": {"strength": 4, "discipline": 5}, "trait_suggest": "Driven"},
            {"text": "Leaving something behind that would not exist without you", "stat_changes": {"intelligence": 5, "wisdom": 4}, "trait_suggest": "Ambitious"},
            {"text": "Figuring it out in a way that was entirely your own", "stat_changes": {"imagination": 5, "wisdom": 3}, "trait_suggest": "Curious"},
            {"text": "Reaching a place where you actually want to be", "stat_changes": {"happiness": 5, "wisdom": 4}, "trait_suggest": "Chill"},
        ],
    },
    {
        "style": "childhood",
        "text": "The hardest thing about growing up was...",
        "options": [
            {"text": "Waiting. Everything moved too slowly", "stat_changes": {"willpower": 5, "stress": 4}, "trait_suggest": "Restless"},
            {"text": "Figuring out who I could actually trust", "stat_changes": {"wisdom": 5, "willpower": 4}, "trait_suggest": "Resilient"},
            {"text": "Not having enough time alone", "stat_changes": {"wisdom": 5, "intelligence": 3}, "trait_suggest": "Introverted"},
            {"text": "Watching people I cared about struggle", "stat_changes": {"wisdom": 4, "charisma": 4}, "trait_suggest": "Empathetic"},
        ],
    },
    {
        "style": "spectrum",
        "text": "When you want something...",
        "options": [
            {"text": "I go after it immediately", "stat_changes": {"willpower": 5, "strength": 4}, "trait_suggest": "Impulsive"},
            {"text": "I figure out the fastest path and start", "stat_changes": {"discipline": 5, "intelligence": 4}, "trait_suggest": "Driven"},
            {"text": "I make sure I actually want it before I move", "stat_changes": {"wisdom": 5, "discipline": 4}, "trait_suggest": "Disciplined"},
            {"text": "I let it come to me", "stat_changes": {"happiness": 5, "wisdom": 4}, "trait_suggest": "Chill"},
        ],
    },
    {
        "style": "situational",
        "text": "When you meet someone new, what are you actually paying attention to?",
        "options": [
            {"text": "The gap between what they say and how they carry themselves", "stat_changes": {"intelligence": 5, "wisdom": 4}, "trait_suggest": "Curious"},
            {"text": "Whether they are comfortable, or putting on something", "stat_changes": {"charisma": 5, "wisdom": 4}, "trait_suggest": "Empathetic"},
            {"text": "Whether this is someone who could matter to you", "stat_changes": {"charisma": 4, "intelligence": 4}, "trait_suggest": "Ambitious"},
            {"text": "Whether they seem like someone who would actually get you", "stat_changes": {"happiness": 5, "charisma": 4}, "trait_suggest": "Social"},
        ],
    },
    {
        "style": "spectrum",
        "text": "When do you feel most like yourself?",
        "options": [
            {"text": "When I am in motion, doing something", "stat_changes": {"health": 5, "strength": 4}, "trait_suggest": "Restless"},
            {"text": "When I am deep in something difficult", "stat_changes": {"intelligence": 4, "discipline": 5}, "trait_suggest": "Driven"},
            {"text": "When I am around people, any people", "stat_changes": {"happiness": 5, "charisma": 4}, "trait_suggest": "Extraverted"},
            {"text": "When I have space to think without interruption", "stat_changes": {"intelligence": 5, "wisdom": 4}, "trait_suggest": "Introverted"},
        ],
    },
    {
        "style": "childhood",
        "text": "Growing up, your relationship with rules was...",
        "options": [
            {"text": "I followed them. Structure made sense to me", "stat_changes": {"discipline": 6, "willpower": 4}, "trait_suggest": "Disciplined"},
            {"text": "I followed them when they made sense, ignored the rest", "stat_changes": {"willpower": 5, "imagination": 4}, "trait_suggest": "Impulsive"},
            {"text": "I looked for the edges, the exceptions", "stat_changes": {"intelligence": 5, "imagination": 4}, "trait_suggest": "Curious"},
            {"text": "I thought about why they existed before deciding", "stat_changes": {"wisdom": 5, "discipline": 3}, "trait_suggest": "Resilient"},
        ],
    },
    {
        "style": "spectrum",
        "text": "What makes you want to get better at something?",
        "options": [
            {"text": "Knowing I am not where I should be yet", "stat_changes": {"intelligence": 5, "discipline": 4}, "trait_suggest": "Ambitious"},
            {"text": "Wanting to understand it properly, not just well enough", "stat_changes": {"intelligence": 6, "wisdom": 4}, "trait_suggest": "Curious"},
            {"text": "Seeing someone I respect do it in a way I could not", "stat_changes": {"charisma": 4, "intelligence": 3}, "trait_suggest": "Social"},
            {"text": "Stumbling into it and finding I actually enjoy it", "stat_changes": {"imagination": 5, "happiness": 3}, "trait_suggest": "Chill"},
        ],
    },
    {
        "style": "situational",
        "text": "After a long day with people...",
        "options": [
            {"text": "I feel energised. I want more", "stat_changes": {"charisma": 5, "happiness": 4}, "trait_suggest": "Extraverted"},
            {"text": "I need quiet. Time alone resets me", "stat_changes": {"wisdom": 5, "intelligence": 4}, "trait_suggest": "Introverted"},
            {"text": "I feel okay but I need to process", "stat_changes": {"wisdom": 4, "charisma": 3}, "trait_suggest": "Empathetic"},
            {"text": "I did not really notice either way", "stat_changes": {"happiness": 5, "health": 4}, "trait_suggest": "Chill"},
        ],
    },
    {
        "style": "situational",
        "text": "When things fall apart...",
        "options": [
            {"text": "I start rebuilding before the dust settles", "stat_changes": {"willpower": 6, "discipline": 4}, "trait_suggest": "Driven"},
            {"text": "I feel it fully, then get back up", "stat_changes": {"willpower": 5, "happiness": 3}, "trait_suggest": "Resilient"},
            {"text": "I take it apart to understand what went wrong", "stat_changes": {"intelligence": 5, "wisdom": 4}, "trait_suggest": "Curious"},
            {"text": "I step back until I know what I am walking back into", "stat_changes": {"wisdom": 5, "discipline": 4}, "trait_suggest": "Disciplined"},
        ],
    },
    {
        "style": "gut_pick",
        "text": "Which one is more you?",
        "options": [
            {"text": "I say what I think, even if the timing is wrong", "stat_changes": {"charisma": 3, "willpower": 5}, "trait_suggest": "Impulsive"},
            {"text": "I say what I think after I have worked out how to say it", "stat_changes": {"intelligence": 5, "wisdom": 4}, "trait_suggest": "Disciplined"},
            {"text": "I say what the other person needs to hear", "stat_changes": {"charisma": 6, "wisdom": 4}, "trait_suggest": "Empathetic"},
            {"text": "I say what I think will move things forward", "stat_changes": {"charisma": 5, "intelligence": 4}, "trait_suggest": "Ambitious"},
        ],
    },
    {
        "style": "childhood",
        "text": "As a kid, you were the type who...",
        "options": [
            {"text": "Was already onto the next thing before others caught up", "stat_changes": {"health": 4, "imagination": 4}, "trait_suggest": "Restless"},
            {"text": "Kept working after everyone else had stopped", "stat_changes": {"discipline": 5, "intelligence": 4}, "trait_suggest": "Driven"},
            {"text": "Got back up every time, even when it hurt", "stat_changes": {"willpower": 6, "health": 4}, "trait_suggest": "Resilient"},
            {"text": "Always knew when someone nearby was not okay", "stat_changes": {"charisma": 4, "wisdom": 4}, "trait_suggest": "Empathetic"},
        ],
    },
    {
        "style": "situational",
        "text": "What makes you trust someone?",
        "options": [
            {"text": "Consistent behaviour over a long stretch", "stat_changes": {"wisdom": 5, "discipline": 4}, "trait_suggest": "Disciplined"},
            {"text": "Honesty, even when it is inconvenient", "stat_changes": {"willpower": 5, "wisdom": 4}, "trait_suggest": "Resilient"},
            {"text": "The feeling that they actually see you", "stat_changes": {"happiness": 5, "charisma": 4}, "trait_suggest": "Social"},
            {"text": "That they are curious about the same things you are", "stat_changes": {"intelligence": 5, "charisma": 3}, "trait_suggest": "Curious"},
        ],
    },
    {
        "style": "spectrum",
        "text": "What makes you want to get better at something?",
        "options": [
            {"text": "I want to be better at it than I was before", "stat_changes": {"intelligence": 5, "discipline": 4}, "trait_suggest": "Ambitious"},
            {"text": "I want to understand it properly, not just enough", "stat_changes": {"intelligence": 6, "wisdom": 4}, "trait_suggest": "Curious"},
            {"text": "Someone I respect does it", "stat_changes": {"charisma": 4, "intelligence": 3}, "trait_suggest": "Social"},
            {"text": "It came up and seemed interesting", "stat_changes": {"imagination": 5, "happiness": 3}, "trait_suggest": "Chill"},
        ],
    },
    {
        "style": "situational",
        "text": "When someone underestimates you...",
        "options": [
            {"text": "I use it", "stat_changes": {"willpower": 5, "charisma": 4}, "trait_suggest": "Ambitious"},
            {"text": "I prove them wrong quietly", "stat_changes": {"discipline": 5, "willpower": 4}, "trait_suggest": "Resilient"},
            {"text": "I do not really notice", "stat_changes": {"happiness": 5, "wisdom": 4}, "trait_suggest": "Chill"},
            {"text": "I wonder what gave them that impression", "stat_changes": {"intelligence": 5, "wisdom": 3}, "trait_suggest": "Curious"},
        ],
    },
    {
        "style": "spectrum",
        "text": "A good day is one where...",
        "options": [
            {"text": "Everything on the list got done", "stat_changes": {"discipline": 6, "happiness": 4}, "trait_suggest": "Disciplined"},
            {"text": "Something unexpected happened and you handled it", "stat_changes": {"happiness": 5, "willpower": 4}, "trait_suggest": "Impulsive"},
            {"text": "You moved something forward that actually mattered", "stat_changes": {"discipline": 5, "intelligence": 4}, "trait_suggest": "Driven"},
            {"text": "You did not feel like you owed anyone your time", "stat_changes": {"happiness": 6, "health": 4}, "trait_suggest": "Chill"},
        ],
    },
    {
        "style": "situational",
        "text": "When someone near you is struggling...",
        "options": [
            {"text": "You feel it before they say a word", "stat_changes": {"charisma": 5, "wisdom": 4}, "trait_suggest": "Empathetic"},
            {"text": "You quietly make things easier without making a thing of it", "stat_changes": {"charisma": 5, "happiness": 4}, "trait_suggest": "Social"},
            {"text": "You give them space until they are ready", "stat_changes": {"wisdom": 5, "intelligence": 3}, "trait_suggest": "Introverted"},
            {"text": "You ask what they need and then do it", "stat_changes": {"willpower": 4, "discipline": 4}, "trait_suggest": "Driven"},
        ],
    },
    {
        "style": "spectrum",
        "text": "Downtime feels like...",
        "options": [
            {"text": "A waste. I always find something to fill it", "stat_changes": {"health": 4, "discipline": 3}, "trait_suggest": "Restless"},
            {"text": "Something I have to earn", "stat_changes": {"discipline": 5, "stress": 4}, "trait_suggest": "Driven"},
            {"text": "Exactly what I needed", "stat_changes": {"happiness": 6, "health": 4}, "trait_suggest": "Chill"},
            {"text": "A chance to think without pressure", "stat_changes": {"wisdom": 5, "intelligence": 4}, "trait_suggest": "Introverted"},
        ],
    },
    {
        "style": "situational",
        "text": "What kind of problem actually satisfies you to solve?",
        "options": [
            {"text": "One that asked more of you than you expected", "stat_changes": {"willpower": 5, "intelligence": 4}, "trait_suggest": "Resilient"},
            {"text": "One no one had bothered to look at properly", "stat_changes": {"intelligence": 6, "imagination": 4}, "trait_suggest": "Curious"},
            {"text": "One where solving it changed how you see things", "stat_changes": {"intelligence": 5, "wisdom": 4}, "trait_suggest": "Ambitious"},
            {"text": "One where you figured it out with someone else alongside you", "stat_changes": {"charisma": 5, "intelligence": 3}, "trait_suggest": "Social"},
        ],
    },
    {
        "style": "gut_pick",
        "text": "Which fits better?",
        "options": [
            {"text": "I get energy from being around people", "stat_changes": {"charisma": 6, "happiness": 5}, "trait_suggest": "Extraverted"},
            {"text": "I lose energy being around people", "stat_changes": {"wisdom": 5, "intelligence": 5}, "trait_suggest": "Introverted"},
        ],
    },
    {
        "style": "gut_pick",
        "text": "Which fits better?",
        "options": [
            {"text": "I think things through before I act", "stat_changes": {"discipline": 6, "wisdom": 5}, "trait_suggest": "Disciplined"},
            {"text": "I act and figure it out as I go", "stat_changes": {"willpower": 5, "imagination": 5}, "trait_suggest": "Impulsive"},
        ],
    },
    {
        "style": "formative",
        "text": "The thing that shaped you most was...",
        "options": [
            {"text": "Someone who believed in you when you did not", "stat_changes": {"willpower": 6, "happiness": 4}, "trait_suggest": "Resilient"},
            {"text": "Something you had to figure out alone", "stat_changes": {"intelligence": 5, "wisdom": 5}, "trait_suggest": "Curious"},
            {"text": "A moment when you realised what you actually wanted", "stat_changes": {"intelligence": 4, "discipline": 4}, "trait_suggest": "Ambitious"},
            {"text": "Learning how to be around people properly", "stat_changes": {"charisma": 6, "happiness": 4}, "trait_suggest": "Extraverted"},
        ],
    },
]
CREATION_STAT_ORDER = [
    "health",
    "happiness",
    "intelligence",
    "strength",
    "charisma",
    "imagination",
    "memory",
    "wisdom",
    "stress",
    "discipline",
    "willpower",
    "looks",
    "fertility",
]
CREATION_STAT_LABELS = {
    "health": "Health",
    "happiness": "Happiness",
    "intelligence": "Intelligence",
    "strength": "Strength",
    "charisma": "Charisma",
    "imagination": "Imagination",
    "memory": "Memory",
    "wisdom": "Wisdom",
    "stress": "Stress",
    "discipline": "Discipline",
    "willpower": "Willpower",
    "looks": "Looks",
    "fertility": "Fertility",
}


def normalize_creation_stats(stats):
    """Aligns creation and loaded stat blocks with the current stat model."""
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
                        if legacy_name not in CREATION_STAT_LABELS
                    ),
                    50,
                )
            continue

        default_value = 10 if stat_name == "stress" else 50
        normalized_stats[stat_name] = source_stats.get(stat_name, default_value)

    if "memory" not in source_stats:
        normalized_stats["memory"] = random.randint(40, 70)
    if "stress" not in source_stats:
        normalized_stats["stress"] = random.randint(5, 20)
    return normalized_stats
GENDER_IDENTITY_OPTIONS = ["Male", "Female", "Non-binary", "Agender", "Genderfluid", "Other"]
SEXUALITY_OPTION_LABELS = [
    ("Opposite gender (Heterosexual)", "Heterosexual"),
    ("Same gender (Homosexual)", "Homosexual"),
    ("Both genders (Bisexual)", "Bisexual"),
    ("No one in particular (Asexual)", "Asexual"),
    ("People regardless of gender (Pansexual)", "Pansexual"),
    ("It is hard to define (Queer)", "Queer"),
]
WORLD_GEOGRAPHY = [
    {
        "country_id": "us",
        "country_name": "United States",
        "metadata": {"region": "North America", "culture_group": "American", "primary_language": "English"},
        "cities": [
            {"city_id": "us_new_york", "city_name": "New York"},
            {"city_id": "us_los_angeles", "city_name": "Los Angeles"},
            {"city_id": "us_chicago", "city_name": "Chicago"},
            {"city_id": "us_houston", "city_name": "Houston"},
            {"city_id": "us_phoenix", "city_name": "Phoenix"},
        ],
    },
    {
        "country_id": "brazil",
        "country_name": "Brazil",
        "metadata": {"region": "South America", "culture_group": "Brazilian", "primary_language": "Portuguese"},
        "cities": [
            {"city_id": "brazil_sao_paulo", "city_name": "São Paulo"},
            {"city_id": "brazil_rio_de_janeiro", "city_name": "Rio de Janeiro"},
            {"city_id": "brazil_brasilia", "city_name": "Brasília"},
            {"city_id": "brazil_salvador", "city_name": "Salvador"},
        ],
    },
    {
        "country_id": "uk",
        "country_name": "United Kingdom",
        "metadata": {"region": "Europe", "culture_group": "British", "primary_language": "English"},
        "cities": [
            {"city_id": "uk_london", "city_name": "London"},
            {"city_id": "uk_manchester", "city_name": "Manchester"},
            {"city_id": "uk_birmingham", "city_name": "Birmingham"},
        ],
    },
    {
        "country_id": "netherlands",
        "country_name": "Netherlands",
        "metadata": {"region": "Europe", "culture_group": "Dutch", "primary_language": "Dutch"},
        "cities": [
            {"city_id": "netherlands_amsterdam", "city_name": "Amsterdam"},
            {"city_id": "netherlands_rotterdam", "city_name": "Rotterdam"},
            {"city_id": "netherlands_amersfoort", "city_name": "Amersfoort"},
            {"city_id": "netherlands_utrecht", "city_name": "Utrecht"},
            {"city_id": "netherlands_den_haag", "city_name": "Den Haag"},
        ],
    },
    {
        "country_id": "germany",
        "country_name": "Germany",
        "metadata": {"region": "Europe", "culture_group": "German", "primary_language": "German"},
        "cities": [
            {"city_id": "germany_berlin", "city_name": "Berlin"},
            {"city_id": "germany_munich", "city_name": "Munich"},
            {"city_id": "germany_hamburg", "city_name": "Hamburg"},
            {"city_id": "germany_frankfurt", "city_name": "Frankfurt"},
        ],
    },
    {
        "country_id": "kenya",
        "country_name": "Kenya",
        "metadata": {"region": "East Africa", "culture_group": "Kenyan", "primary_language": "Swahili/English"},
        "cities": [
            {"city_id": "kenya_nairobi", "city_name": "Nairobi"},
            {"city_id": "kenya_mombasa", "city_name": "Mombasa"},
            {"city_id": "kenya_kisumu", "city_name": "Kisumu"},
        ],
    },
    {
        "country_id": "colombia",
        "country_name": "Colombia",
        "metadata": {"region": "South America", "culture_group": "Colombian", "primary_language": "Spanish"},
        "cities": [
            {"city_id": "colombia_bogota", "city_name": "Bogotá"},
            {"city_id": "colombia_medellin", "city_name": "Medellín"},
            {"city_id": "colombia_cali", "city_name": "Cali"},
        ],
    },
    {
        "country_id": "japan",
        "country_name": "Japan",
        "metadata": {"region": "East Asia", "culture_group": "Japanese", "primary_language": "Japanese"},
        "cities": [
            {"city_id": "japan_tokyo", "city_name": "Tokyo"},
            {"city_id": "japan_osaka", "city_name": "Osaka"},
            {"city_id": "japan_kyoto", "city_name": "Kyoto"},
        ],
    },
    {
        "country_id": "india",
        "country_name": "India",
        "metadata": {"region": "South Asia", "culture_group": "Indian", "primary_language": "Hindi/English"},
        "cities": [
            {"city_id": "india_mumbai", "city_name": "Mumbai"},
            {"city_id": "india_delhi", "city_name": "Delhi"},
            {"city_id": "india_bangalore", "city_name": "Bangalore"},
            {"city_id": "india_kolkata", "city_name": "Kolkata"},
        ],
    },
    {
        "country_id": "indonesia",
        "country_name": "Indonesia",
        "metadata": {"region": "Southeast Asia", "culture_group": "Indonesian", "primary_language": "Indonesian"},
        "cities": [
            {"city_id": "indonesia_jakarta", "city_name": "Jakarta"},
            {"city_id": "indonesia_surabaya", "city_name": "Surabaya"},
            {"city_id": "indonesia_bandung", "city_name": "Bandung"},
        ],
    },
    {
        "country_id": "philippines",
        "country_name": "Philippines",
        "metadata": {"region": "Southeast Asia", "culture_group": "Filipino", "primary_language": "Filipino/English"},
        "cities": [
            {"city_id": "philippines_manila", "city_name": "Manila"},
            {"city_id": "philippines_cebu_city", "city_name": "Cebu City"},
            {"city_id": "philippines_davao_city", "city_name": "Davao City"},
        ],
    },
    {
        "country_id": "australia",
        "country_name": "Australia",
        "metadata": {"region": "Oceania", "culture_group": "Australian", "primary_language": "English"},
        "cities": [
            {"city_id": "australia_sydney", "city_name": "Sydney"},
            {"city_id": "australia_melbourne", "city_name": "Melbourne"},
            {"city_id": "australia_brisbane", "city_name": "Brisbane"},
        ],
    },
]
WORLD_GEOGRAPHY_BY_COUNTRY_ID = {
    country["country_id"]: country
    for country in WORLD_GEOGRAPHY
}
DEFAULT_COUNTRY_ID = WORLD_GEOGRAPHY[0]["country_id"]
DEFAULT_CITY_ID = WORLD_GEOGRAPHY[0]["cities"][0]["city_id"]


def generate_startup_actor_id(role):
    """Builds one narrow startup actor id without hardcoded singleton values."""
    return f"startup_{role}_{uuid4().hex[:8]}"


def safe_input(prompt):
    """Reads one input value and exits cleanly on interruption/EOF."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print(f"\n{INPUT_INTERRUPTED_MESSAGE}")
        raise SystemExit(0)


def build_snapshot_sections(snapshot_data):
    """Builds shell-owned snapshot sections from structured actor snapshot data."""
    identity = snapshot_data["identity"]
    time_state = snapshot_data["time"]
    location = snapshot_data["location"]
    statistics = snapshot_data["statistics"]
    relationships = snapshot_data["relationships"]

    section_pairs = [
        (
            "identity",
            "Identity",
            [
                f"Name: {identity['full_name']}",
                f"Species: {identity['species']}",
                f"Sex: {identity['sex']}",
                f"Gender: {identity['gender']}",
                f"Age: {identity['age']}",
                f"Life Stage: {identity['life_stage']}",
            ],
        ),
        (
            "time",
            "Time",
            [
                f"Sim Date: Year {time_state['year']}, Month {time_state['month']}",
            ],
        ),
        (
            "location",
            "Location",
            [
                f"Planet: {location['world_body_name']}",
                f"City: {location['current_place_name']}",
                f"Country: {location['jurisdiction_place_name']}",
            ],
        ),
        (
            "statistics",
            "Statistics",
            [
                f"Health: {statistics['health']}",
                f"Happiness: {statistics['happiness']}",
                f"Intelligence: {statistics['intelligence']}",
                f"Money: ${statistics['money']}",
            ],
        ),
        (
            "relationships",
            "Relationships",
            [f"  {entry['name']} · {entry['label']}" for entry in relationships] or ["  No living family."],
        ),
    ]
    return [
        {"key": key, "title": title, "lines": lines}
        for key, title, lines in section_pairs
    ]


def format_stat_pair(left_label, left_value, right_label, right_value):
    """Builds one compact two-column stat row for profile rendering."""
    return f"  {left_label}: {left_value:<3}      {right_label}: {right_value}"


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


def wrap_text_line(text, width):
    """Wraps one line of text to the available width while preserving blank lines."""
    if width <= 1:
        return [text[:1]]
    if text == "":
        return [""]
    return textwrap.wrap(text, width=width) or [""]


def center_text(text, width):
    """Centers one line of text inside a fixed-width field."""
    if width <= 0:
        return ""
    if len(text) >= width:
        return text[:width]
    padding = width - len(text)
    left_padding = padding // 2
    right_padding = padding - left_padding
    return (" " * left_padding) + text + (" " * right_padding)


def build_centered_rule(label, width, fill_char="═"):
    """Builds one centered decorative rule with a single inline label."""
    if width <= 0:
        return ""
    decorated_label = f" {label} "
    if len(decorated_label) >= width:
        return decorated_label[:width]
    remaining = width - len(decorated_label)
    left_fill = remaining // 2
    right_fill = remaining - left_fill
    return (fill_char * left_fill) + decorated_label + (fill_char * right_fill)


def get_content_bounds(width, *, max_width=100, min_margin=2):
    """Returns a centered content column sized for readable TUI composition."""
    usable_width = max(1, width - 1)
    content_width = min(max_width, usable_width - (min_margin * 2))
    if content_width < 24:
        content_width = usable_width
    left = max(0, (usable_width - content_width) // 2)
    return left, content_width


def split_centered_columns(content_left, content_width, left_ratio=0.52, gap=3):
    """Splits one centered region into two readable columns."""
    gap = min(gap, max(1, content_width // 8))
    left_width = max(28, int(content_width * left_ratio))
    right_width = content_width - left_width - gap
    if right_width < 26:
        right_width = 26
        left_width = max(24, content_width - right_width - gap)
    if left_width + right_width + gap > content_width:
        right_width = max(20, content_width - left_width - gap)
    right_left = content_left + left_width + gap
    return left_width, right_left, right_width


def draw_text_block(stdscr, start_y, start_x, width, height, lines, *, highlight_index=None):
    """Draws a wrapped block of text inside the provided bounds."""
    y = start_y
    for index, raw_line in enumerate(lines):
        wrapped_lines = wrap_text_line(raw_line, width)
        attr = curses.A_REVERSE if highlight_index == index else curses.A_NORMAL
        for wrapped_line in wrapped_lines:
            if y >= start_y + height:
                return y
            stdscr.addnstr(y, start_x, wrapped_line, width, attr)
            y += 1
    return y


def draw_centered_text_block(stdscr, start_y, total_width, block_width, height, lines, *, highlight_index=None):
    """Draws one wrapped block inside a centered column."""
    block_width = min(block_width, max(1, total_width - 1))
    start_x = max(0, (max(1, total_width - 1) - block_width) // 2)
    return draw_text_block(
        stdscr,
        start_y,
        start_x,
        block_width,
        height,
        lines,
        highlight_index=highlight_index,
    )


def draw_truncated_block(stdscr, start_y, start_x, width, height, lines, *, highlight_index=None):
    """Draws one fixed-line block without wrapping, truncating long rows in place."""
    y = start_y
    for index, raw_line in enumerate(lines):
        if y >= start_y + height:
            return y
        attr = curses.A_REVERSE if highlight_index == index else curses.A_NORMAL
        stdscr.addnstr(y, start_x, truncate_for_width(raw_line, width).ljust(width), width, attr)
        y += 1
    return y


def get_scroll_window(lines, height, offset):
    """Returns the visible slice for a simple vertical scroll window."""
    if height <= 0:
        return [], 0, 0, 0
    total_lines = len(lines)
    max_offset = max(0, total_lines - height)
    offset = max(0, min(offset, max_offset))
    return lines[offset : offset + height], offset, max_offset, total_lines


def draw_vertical_divider(stdscr, top, left, height, char="│"):
    """Draws one light vertical divider for layout separation without boxing the whole screen."""
    if height <= 0:
        return
    for row in range(top, top + height):
        stdscr.addnstr(row, left, char, 1)


def draw_box(stdscr, top, left, height, width, *, title=None):
    """Draws one light box frame using ASCII-safe characters."""
    if height < 2 or width < 2:
        return

    inner_width = max(0, width - 2)
    horizontal = "-" * inner_width
    stdscr.addnstr(top, left, "+" + horizontal + "+", width)
    for row in range(top + 1, top + height - 1):
        stdscr.addnstr(row, left, "|", 1)
        if inner_width > 0:
            stdscr.addnstr(row, left + 1, " " * inner_width, inner_width)
        stdscr.addnstr(row, left + width - 1, "|", 1)
    stdscr.addnstr(top + height - 1, left, "+" + horizontal + "+", width)

    if title and width > 4:
        title_text = f"[ {title} ]"
        stdscr.addnstr(top, left + 2, title_text[: max(0, width - 4)], max(0, width - 4), curses.A_BOLD)


def truncate_for_width(text, width):
    """Truncates one line to fit the available width with a small ellipsis."""
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width == 1:
        return "…"
    return text[: width - 1] + "…"


def draw_panel_text(stdscr, top, left, height, width, lines, *, highlight_index=None, wrap=True):
    """Draws text inside a boxed panel, with optional wrapping or one-line truncation."""
    if height < 3 or width < 3:
        return

    y = top + 1
    inner_height = height - 2
    inner_width = width - 2
    for index, raw_line in enumerate(lines):
        rendered_lines = wrap_text_line(raw_line, inner_width) if wrap else [truncate_for_width(raw_line, inner_width)]
        attr = curses.A_REVERSE if highlight_index == index else curses.A_NORMAL
        for rendered_line in rendered_lines:
            if y >= top + 1 + inner_height:
                return
            stdscr.addnstr(y, left + 1, rendered_line.ljust(inner_width), inner_width, attr)
            y += 1


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


def build_randomized_starting_stats():
    """Builds one startup stat block using the same Human randomization ranges."""
    actor = Human("Human", "Temp", "", "Female", "Female", 1, 1)
    actor.randomize_starting_statistics()
    return normalize_creation_stats(actor.stats)


def _get_social_tier_label(closeness):
    """Returns the display tier label for a social link closeness value."""
    if closeness >= 70:
        return "Close Friend"
    if closeness >= 30:
        return "Friend"
    return "Acquaintance"


class CreationWizard:
    """Curses-driven startup flow for building one player character payload."""
    CREATION_MODES = ["questionnaire", "manual"]

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.cancelled = False
        self.step_index = 0

        self.identity_field_index = 0
        self.location_mode = "country"
        self.country_index = 0
        self.city_index = 0
        self.appearance_field_index = 0
        self.appearance_option_index = 0
        self.appearance_mode = "field"
        self.trait_index = 0
        self.stat_index = 0
        self.mode_index = 0
        self.selected_mode = None
        self.question_index = 0
        self.question_option_index = 0
        self.questionnaire_answers = []
        self.questionnaire_framing_shown = False
        self.questionnaire_reveal_shown = False
        self.questionnaire_reveal_shown = False
        self.quit_confirmation_active = False
        self.identity_first_name_error_shown = False

        self.data = {
            "first_name": "",
            "last_name": "",
            "sex": CREATION_SEX_OPTIONS[0],
            "gender": "Male",
            "country_id": DEFAULT_COUNTRY_ID,
            "city_id": DEFAULT_CITY_ID,
            "appearance": {
                "eye_color": CREATION_EYE_COLOR_OPTIONS[0],
                "hair_color": CREATION_HAIR_COLOR_OPTIONS[0],
                "skin_tone": CREATION_SKIN_TONE_OPTIONS[2],
            },
            "traits": [],
            "stats": build_randomized_starting_stats(),
        }
        self.custom_appearance_values = {
            "eye_color": "",
            "hair_color": "",
            "skin_tone": "",
        }

    def get_step_title(self):
        title_map = {
            0: "Step 1: Identity",
            1: "Step 2: Location",
            2: "Step 3: Appearance",
            3: "Step 4: Creation Mode",
        }
        if self.step_index in title_map:
            return title_map[self.step_index]
        if self.step_index == 4:
            return "Step 5: Questionnaire" if self.selected_mode == "questionnaire" else "Step 5: Stats"
        if self.step_index == 5:
            return "Step 6: Confirm" if self.selected_mode == "questionnaire" else "Step 6: Traits"
        return "Step 7: Confirm"

    def get_confirm_step_index(self):
        return 5 if self.selected_mode == "questionnaire" else 6

    def build_questionnaire_starting_stats(self):
        stats = {stat_name: 50 for stat_name in CREATION_STAT_ORDER}
        stats["stress"] = 0  # Stress is a signed stat (-50 to +50); 0 = no pressure at baseline
        stats["memory"] = 0  # Memory is a signed stat; 0 = average baseline (not seeded by questionnaire)
        return stats

    def reset_questionnaire_progress(self):
        self.question_index = 0
        self.question_option_index = 0
        self.questionnaire_answers = []
        self.questionnaire_framing_shown = False
        self.questionnaire_reveal_shown = False

    def begin_questionnaire(self):
        self.selected_mode = "questionnaire"
        self.reset_questionnaire_progress()
        self.step_index = 4

    def begin_manual(self):
        self.selected_mode = "manual"
        self.data["traits"] = []
        self.step_index = 4

    def finalize_questionnaire_results(self):
        stats = self.build_questionnaire_starting_stats()
        trait_counts = {}

        # Hard-block pairs: answers for one side subtract from the other
        BLOCKING_PAIRS = [
            ("Introverted", "Extraverted"),
            ("Disciplined", "Impulsive"),
        ]

        for option in self.questionnaire_answers:
            for stat_name, delta in option["stat_changes"].items():
                stats[stat_name] = stats.get(stat_name, 50) + delta
            suggested_trait = option.get("trait_suggest")
            if suggested_trait:
                trait_counts[suggested_trait] = trait_counts.get(suggested_trait, 0) + 1
                # Active competition: subtract from the blocked counterpart
                for pair in BLOCKING_PAIRS:
                    if suggested_trait == pair[0]:
                        trait_counts[pair[1]] = trait_counts.get(pair[1], 0) - 1
                    elif suggested_trait == pair[1]:
                        trait_counts[pair[0]] = trait_counts.get(pair[0], 0) - 1

        for stat_name in stats:
            stats[stat_name] = max(-50 if stat_name in ("stress", "memory") else 0, min(50 if stat_name in ("stress", "memory") else 100, stats[stat_name]))

        ranked_traits = []
        count_groups = {}
        for trait_name, count in trait_counts.items():
            if count > 0:  # Only include traits with positive scores
                count_groups.setdefault(count, []).append(trait_name)
        for count in sorted(count_groups.keys(), reverse=True):
            tied_traits = list(count_groups[count])
            random.shuffle(tied_traits)
            ranked_traits.extend(tied_traits)

        selected_traits = ranked_traits[:4]
        if len(selected_traits) < 4:
            remaining_pool = [trait for trait in CREATION_TRAIT_POOL if trait not in selected_traits]
            random.shuffle(remaining_pool)
            selected_traits.extend(remaining_pool[: 4 - len(selected_traits)])

        self.data["stats"] = stats
        self.data["traits"] = selected_traits

    def get_identity_fields(self):
        return [
            {"kind": "text", "key": "first_name", "label": "First Name", "optional": False},
            {"kind": "text", "key": "last_name", "label": "Last Name", "optional": False},
            {"kind": "select", "key": "sex", "label": "Sex", "options": CREATION_SEX_OPTIONS},
        ]

    def get_appearance_fields(self):
        fields = [
            {"kind": "select", "key": "eye_color", "label": "Eye Color", "options": CREATION_EYE_COLOR_OPTIONS},
            {"kind": "select", "key": "hair_color", "label": "Hair Color", "options": CREATION_HAIR_COLOR_OPTIONS},
            {"kind": "select", "key": "skin_tone", "label": "Skin Tone", "options": CREATION_SKIN_TONE_OPTIONS},
        ]
        expanded_fields = []
        for field in fields:
            expanded_fields.append(field)
            if self.data["appearance"][field["key"]] == "Other":
                expanded_fields.append(
                    {
                        "kind": "text",
                        "key": field["key"],
                        "label": f"Custom {field['label']}",
                        "optional": False,
                    }
                )
        return expanded_fields

    def get_location_country(self):
        return WORLD_GEOGRAPHY_BY_COUNTRY_ID[self.data["country_id"]]

    def get_location_cities(self):
        return self.get_location_country()["cities"]

    def sync_location_indexes(self):
        self.country_index = next(
            (
                index
                for index, country in enumerate(WORLD_GEOGRAPHY)
                if country["country_id"] == self.data["country_id"]
            ),
            0,
        )
        self.city_index = next(
            (
                index
                for index, city in enumerate(self.get_location_cities())
                if city["city_id"] == self.data["city_id"]
            ),
            0,
        )

    def set_selected_country(self, country_index):
        country = WORLD_GEOGRAPHY[country_index]
        self.country_index = country_index
        self.data["country_id"] = country["country_id"]
        cities = country["cities"]
        city_ids = {city["city_id"] for city in cities}
        if self.data["city_id"] not in city_ids:
            self.data["city_id"] = cities[0]["city_id"]
            self.city_index = 0
            return
        self.sync_location_indexes()

    def set_selected_city(self, city_index):
        cities = self.get_location_cities()
        self.city_index = city_index
        self.data["city_id"] = cities[city_index]["city_id"]

    def get_current_appearance_select_options(self):
        selected_field = self.get_active_appearance_select_field()
        return selected_field["options"]

    def get_active_appearance_select_field(self):
        fields = self.get_appearance_fields()
        current_field = fields[self.appearance_field_index]
        if current_field["kind"] == "select":
            return current_field

        for index in range(self.appearance_field_index - 1, -1, -1):
            if fields[index]["kind"] == "select":
                return fields[index]

        return fields[0]

    def get_visible_value_for_appearance(self, key):
        value = self.data["appearance"][key]
        if value == "Other":
            return self.custom_appearance_values[key] or "Other"
        return value

    def sync_gender_to_sex(self):
        sex = self.data["sex"]
        self.data["gender"] = sex if sex in {"Male", "Female"} else "Non-binary"

    def can_advance_identity(self):
        return bool(self.data["first_name"].strip()) and bool(self.data["last_name"].strip())

    def can_advance_appearance(self):
        for key, value in self.data["appearance"].items():
            if value != "Other":
                continue
            if not self.custom_appearance_values[key].strip():
                return False
        return True

    def can_advance_traits(self):
        return len(self.data["traits"]) == 4

    def build_result(self):
        appearance = {}
        for key, value in self.data["appearance"].items():
            if value == "Other":
                appearance[key] = self.custom_appearance_values[key].strip()
            else:
                appearance[key] = value
        return {
            "first_name": self.data["first_name"].strip(),
            "last_name": self.data["last_name"].strip(),
            "sex": self.data["sex"],
            "gender": self.data["gender"],
            "country_id": self.data["country_id"],
            "city_id": self.data["city_id"],
            "appearance": appearance,
            "traits": list(self.data["traits"]),
            "stats": dict(self.data["stats"]),
        }

    def render_header(self, width):
        content_left, content_width = get_content_bounds(width, max_width=108, min_margin=1)
        title_text = build_centered_rule("Character Creation", content_width)
        subtitle_text = center_text(self.get_step_title(), content_width)
        self.stdscr.addnstr(0, content_left, title_text, content_width, curses.A_BOLD)
        self.stdscr.addnstr(1, content_left, subtitle_text, content_width)
        self.stdscr.addnstr(2, content_left, "═" * content_width, content_width, curses.A_BOLD)

    def render_footer(self, height, width):
        if self.step_index == 0:
            footer_text = "[↑↓] Move   [←→] Adjust   [Enter] Continue   [Esc] Quit"
        elif self.step_index == 1:
            if self.location_mode == "country":
                footer_text = "[↑↓] Move   [Enter] Select Country   [Bsp] Back"
            else:
                footer_text = "[↑↓] Move   [Enter] Select City   [Bsp] Back"
        elif self.step_index == 2:
            footer_text = "[↑↓] Move   [←→] Adjust   [Enter] Continue   [Bsp] Back"
        elif self.step_index == 3:
            footer_text = "[↑↓] Move   [Enter] Continue   [Bsp] Back"
        elif self.step_index == 4 and self.selected_mode == "questionnaire":
            footer_text = "[↑↓] Move   [Enter] Continue   [Bsp] Back"
        elif self.step_index == 4:
            footer_text = "[↑↓] Move   [←→] Adjust   [R] Randomize   [Enter] Continue   [Bsp] Back"
        elif self.step_index == 5 and self.selected_mode == "manual":
            footer_text = "[↑↓] Move   [Space] Select   [Enter] Continue   [Bsp] Back"
        else:
            footer_text = "[Enter] Start Game   [Bsp] Back"
        content_left, content_width = get_content_bounds(width, max_width=108, min_margin=1)
        hline_char = getattr(curses, "ACS_HLINE", ord("-"))
        self.stdscr.hline(height - 2, content_left, hline_char, content_width)
        self.stdscr.addnstr(
            height - 1,
            content_left,
            center_text(footer_text, content_width),
            content_width,
            curses.A_NORMAL,
        )

    def render_identity(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=84)
        fields = self.get_identity_fields()
        lines = [
            "Create your character's identity.",
            "",
        ]
        highlight_index = None
        for index, field in enumerate(fields):
            if index == self.identity_field_index:
                highlight_index = len(lines)
            value = self.data[field["key"]]
            optional_suffix = " (optional)" if field.get("optional") else ""
            if field["kind"] == "select" and index == self.identity_field_index:
                lines.append(f"{field['label']}{optional_suffix}: \u2190 {value} \u2192")
            else:
                suffix = "_" if field["kind"] == "text" and index == self.identity_field_index else ""
                lines.append(f"{field['label']}{optional_suffix}: {value}{suffix}")
        lines.append("")
        if self.identity_first_name_error_shown:
            lines.append("First and last name are required.")
        lines.append(f"Gender defaults to: {self.data['gender']}  (chosen later in life)")
        draw_text_block(self.stdscr, 5, content_left, content_width, height - 7, lines, highlight_index=highlight_index)

    def render_appearance(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=92)
        fields = self.get_appearance_fields()
        lines = [
            "Choose appearance details.",
            "",
        ]
        highlight_index = None
        for index, field in enumerate(fields):
            if index == self.appearance_field_index:
                highlight_index = len(lines)
            if field["kind"] == "select":
                value = self.get_visible_value_for_appearance(field["key"])
                if index == self.appearance_field_index:
                    lines.append(f"{field['label']}: \u2190 {value} \u2192")
                else:
                    lines.append(f"{field['label']}: {value}")
            else:
                value = self.custom_appearance_values[field["key"]]
                suffix = "_" if index == self.appearance_field_index else ""
                if index == self.appearance_field_index:
                    field_name = field["label"].replace("Custom ", "").lower()
                    lines.append(f"Type custom {field_name}: {value}{suffix}")
                else:
                    lines.append(f"{field['label']}: {value}{suffix}")

        draw_text_block(self.stdscr, 5, content_left, content_width, height - 7, lines, highlight_index=highlight_index)

    def render_location(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=96)
        left_width, right_left, right_width = split_centered_columns(content_left, content_width, left_ratio=0.5)
        body_height = height - 7

        selected_country = self.get_location_country()
        selected_city = next(
            city for city in self.get_location_cities() if city["city_id"] == self.data["city_id"]
        )

        country_lines = [
            "Choose a birth country.",
            "",
        ]
        country_highlight_index = None
        for index, country in enumerate(WORLD_GEOGRAPHY):
            if self.location_mode == "country" and index == self.country_index:
                country_highlight_index = len(country_lines)
            country_lines.append(f"{country['country_name']}")

        city_lines = [
            f"Cities in {selected_country['country_name']}",
            "",
        ]
        city_highlight_index = None
        for index, city in enumerate(selected_country["cities"]):
            if self.location_mode == "city" and index == self.city_index:
                city_highlight_index = len(city_lines)
            city_lines.append(f"{city['city_name']}")

        city_lines.extend(
            [
                "",
                "Selection",
                f"  Country: {selected_country['country_name']}",
                f"  City: {selected_city['city_name']}",
                f"  Region: {selected_country['metadata']['region']}",
                f"  Culture: {selected_country['metadata']['culture_group']}",
                f"  Language: {selected_country['metadata']['primary_language']}",
            ]
        )

        draw_text_block(self.stdscr, 5, content_left, left_width, body_height, country_lines, highlight_index=country_highlight_index)
        draw_vertical_divider(self.stdscr, 5, right_left - 2, body_height)
        draw_text_block(self.stdscr, 5, right_left, right_width, body_height, city_lines, highlight_index=city_highlight_index)

    def render_traits(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=84)
        lines = [
            "Select 4 traits.",
            f"Selected: {len(self.data['traits'])}/4",
            "",
        ]
        highlight_index = None
        for index, trait in enumerate(CREATION_TRAIT_POOL):
            if index == self.trait_index:
                highlight_index = len(lines)
            marker = "[x]" if trait in self.data["traits"] else "[ ]"
            lines.append(f"{marker} {trait}")
        if not self.can_advance_traits():
            lines.extend(["", "Choose 4 traits to continue."])
        draw_text_block(self.stdscr, 5, content_left, content_width, height - 7, lines, highlight_index=highlight_index)

    def render_mode_selection(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=86)
        mode_descriptions = {
            "questionnaire": [
                "Answer questions about yourself",
                "Your answers determine your stats and personality traits.",
                "You will see the results but cannot change them.",
            ],
            "manual": [
                "Set everything manually",
                "Choose your own stats and pick your personality traits.",
            ],
        }
        lines = [
            "How would you like to shape your character?",
            "",
        ]
        highlight_index = None
        for index, mode_name in enumerate(self.CREATION_MODES):
            if index == self.mode_index:
                highlight_index = len(lines)
            lines.append(f"{mode_descriptions[mode_name][0]}")
            for detail_line in mode_descriptions[mode_name][1:]:
                lines.append(f"    {detail_line}")
            lines.append("")
        draw_text_block(self.stdscr, 5, content_left, content_width, height - 7, lines, highlight_index=highlight_index)

    def render_stats(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=92)
        left_width, right_left, right_width = split_centered_columns(content_left, content_width, left_ratio=0.56)
        body_height = height - 7

        left_lines = [
            "Primary Stats",
            "",
        ]
        highlight_index = None
        for index, stat_name in enumerate(CREATION_STAT_ORDER):
            if index == 3:
                left_lines.extend(["", "Secondary Stats", ""])
            if index == self.stat_index:
                highlight_index = len(left_lines)
                left_lines.append(f"{CREATION_STAT_LABELS[stat_name]}: \u2190 {self.data['stats'][stat_name]} \u2192")
            else:
                left_lines.append(f"{CREATION_STAT_LABELS[stat_name]}: {self.data['stats'][stat_name]:>3}")

        right_lines = [
            "Controls",
            "",
            "Adjust any stat from 0 to 100.",
            "",
            "[R] Randomize all stats",
            
        ]

        draw_text_block(self.stdscr, 5, content_left, left_width, body_height, left_lines, highlight_index=highlight_index)
        draw_vertical_divider(self.stdscr, 5, right_left - 2, body_height)
        draw_text_block(self.stdscr, 5, right_left, right_width, body_height, right_lines)

    def render_questionnaire_framing(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=92)
        lines = [
            "",
            "",
            "Before we begin",
            "",
            "Every person who enters the simulation is assessed.",
            "This is standard.",
            "",
            "Answer as honestly as you can. There is no record of what you choose",
            "only of who you become.",
            "",
            "",
        ]
        draw_text_block(self.stdscr, 5, content_left, content_width, height - 7, lines)

    def render_questionnaire(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=92)
        question = QUESTIONNAIRE_QUESTIONS[self.question_index]
        lines = [
            center_text(f"Question {self.question_index + 1} of {len(QUESTIONNAIRE_QUESTIONS)}", content_width).strip(),
            "",
            "",
            question["text"].upper(),
            "",
            "",
        ]
        highlight_index = None
        for index, option in enumerate(question["options"]):
            if index == self.question_option_index:
                highlight_index = len(lines)
            lines.append(option['text'])
            lines.append("")
        draw_text_block(self.stdscr, 5, content_left, content_width, height - 7, lines, highlight_index=highlight_index)

    def render_quit_confirmation(self, height, width):
        box_width = min(max(36, width // 2), 44)
        box_height = 7
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        lines = [
            "Are you sure you want to quit?",
            "",
            "[Enter] Quit   [Bsp] Back",
        ]
        draw_box(self.stdscr, top, left, box_height, box_width, title="Quit")
        draw_panel_text(self.stdscr, top, left, box_height, box_width, lines)

    def render_questionnaire_reveal(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=92)
        traits = self.data.get("traits", [])
        if len(traits) >= 4:
            trait_line = f"You are {traits[0]}, {traits[1]}, {traits[2]}, and {traits[3]}."
        elif traits:
            trait_line = "You are " + ", ".join(traits) + "."
        else:
            trait_line = ""
        lines = [
            "",
            "",
            "The assessment is complete.",
            "",
            trait_line,
            "",
            "Your life begins now.",
            "",
            "",
        ]
        draw_text_block(self.stdscr, 5, content_left, content_width, height - 7, lines)

    def render_confirm(self, height, width):
        content_left, content_width = get_content_bounds(width, max_width=92)
        result = self.build_result()
        lines = [
            "Review your character.",
            "",
            "Identity",
            f"  Name: {(result['first_name'] + ' ' + result['last_name']).strip()}",
            f"  Sex: {result['sex']}",
            f"  Gender: {result['gender']}",
            "",
            "Location",
            f"  Country: {WORLD_GEOGRAPHY_BY_COUNTRY_ID[result['country_id']]['country_name']}",
            f"  City: {next(city['city_name'] for city in WORLD_GEOGRAPHY_BY_COUNTRY_ID[result['country_id']]['cities'] if city['city_id'] == result['city_id'])}",
            "",
            "Appearance",
            f"  Eye Color: {result['appearance']['eye_color']}",
            f"  Hair Color: {result['appearance']['hair_color']}",
            f"  Skin Tone: {result['appearance']['skin_tone']}",
            "",
            "Traits",
            "  " + ", ".join(result["traits"]),
            "",
            "Stats",
        ]
        for stat_name in CREATION_STAT_ORDER:
            lines.append(f"  {CREATION_STAT_LABELS[stat_name]}: {result['stats'][stat_name]}")
        lines.append("  Money: $0")
        draw_text_block(self.stdscr, 5, content_left, content_width, height - 7, lines)

    def render(self):
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()
        if height < 16 or width < 60:
            self.stdscr.addnstr(0, 0, "Terminal too small for character creation. Resize and try again.", max(1, width - 1))
            self.stdscr.refresh()
            return

        self.render_header(width)
        if self.step_index == 0:
            self.render_identity(height, width)
        elif self.step_index == 1:
            self.render_location(height, width)
        elif self.step_index == 2:
            self.render_appearance(height, width)
        elif self.step_index == 3:
            self.render_mode_selection(height, width)
        elif self.step_index == 4:
            if self.selected_mode == "questionnaire":
                if not self.questionnaire_framing_shown:
                    self.render_questionnaire_framing(height, width)
                else:
                    self.render_questionnaire(height, width)
            else:
                self.render_stats(height, width)
        elif self.step_index == 5 and self.selected_mode == "questionnaire" and not self.questionnaire_reveal_shown:
            self.render_questionnaire_reveal(height, width)
        elif self.step_index == 5 and self.selected_mode == "manual":
            self.render_traits(height, width)
        else:
            self.render_confirm(height, width)
        self.render_footer(height, width)
        if self.quit_confirmation_active:
            self.render_quit_confirmation(height, width)
        self.stdscr.refresh()

    def handle_quit_key(self, key):
        if self.quit_confirmation_active:
            if key in BACK_KEYS:
                self.quit_confirmation_active = False
                return True
            if key in (curses.KEY_ENTER, 10, 13):
                self.running = False
                self.cancelled = True
                return True
            return True
        # Q blocked in wizard — no quit path in wizard per control contract
        return False

    def handle_identity_key(self, key):
        if key == 27:  # Esc — quit path in wizard identity step
            self.quit_confirmation_active = True
            return
        fields = self.get_identity_fields()
        current_field = fields[self.identity_field_index]
        if current_field["kind"] == "text":
            if key == curses.KEY_UP:
                self.identity_field_index = max(0, self.identity_field_index - 1)
                return
            if key in (curses.KEY_DOWN,):
                self.identity_field_index = min(len(fields) - 1, self.identity_field_index + 1)
                return
            if key in (curses.KEY_ENTER, 10, 13):
                if self.identity_field_index < len(fields) - 1:
                    self.identity_field_index += 1
                elif self.can_advance_identity():
                    self.step_index = 1
                else:
                    self.identity_first_name_error_shown = True
                return
            if key in (curses.KEY_BACKSPACE, 127, 8):
                if self.data[current_field["key"]]:
                    self.data[current_field["key"]] = self.data[current_field["key"]][:-1]
                return
            if 32 <= key <= 126:
                self.data[current_field["key"]] += chr(key)
                if current_field["key"] == "first_name":
                    self.identity_first_name_error_shown = False
                return
        if current_field["kind"] == "select":
            current_index = current_field["options"].index(self.data["sex"])
            if key in (curses.KEY_BACKSPACE, 127, 8):
                if self.identity_field_index > 0:
                    self.identity_field_index -= 1
                return
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                self.identity_field_index = max(0, self.identity_field_index - 1)
                return
            if key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.identity_field_index = min(len(fields) - 1, self.identity_field_index + 1)
                return
            if key in (curses.KEY_LEFT, ord("a"), ord("A"), ord("-")):
                current_index = max(0, current_index - 1)
                self.data["sex"] = current_field["options"][current_index]
                self.sync_gender_to_sex()
                return
            if key in (curses.KEY_RIGHT, ord("d"), ord("D"), ord("+"), ord("=")):
                current_index = min(len(current_field["options"]) - 1, current_index + 1)
                self.data["sex"] = current_field["options"][current_index]
                self.sync_gender_to_sex()
                return
            if key in (curses.KEY_ENTER, 10, 13):
                if self.can_advance_identity():
                    self.step_index = 1
                else:
                    self.identity_first_name_error_shown = True

    def handle_location_key(self, key):
        if self.location_mode == "country":
            if key in BACK_KEYS:
                self.step_index = 0
                return
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                self.set_selected_country(max(0, self.country_index - 1))
                return
            if key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.set_selected_country(min(len(WORLD_GEOGRAPHY) - 1, self.country_index + 1))
                return
            if key in (curses.KEY_ENTER, 10, 13):
                self.location_mode = "city"
                self.sync_location_indexes()
                return
            return

        cities = self.get_location_cities()
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.set_selected_city(max(0, self.city_index - 1))
            return
        if key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.set_selected_city(min(len(cities) - 1, self.city_index + 1))
            return
        if key in BACK_KEYS:
            self.location_mode = "country"
            return
        if key in (curses.KEY_ENTER, 10, 13):
            self.step_index = 2
            self.location_mode = "country"

    def handle_appearance_key(self, key):
        fields = self.get_appearance_fields()
        self.appearance_field_index = max(0, min(self.appearance_field_index, len(fields) - 1))
        current_field = fields[self.appearance_field_index]

        if key in (curses.KEY_BACKSPACE, 127, 8):
            if current_field["kind"] == "text":
                self.custom_appearance_values[current_field["key"]] = self.custom_appearance_values[current_field["key"]][:-1]
            else:
                self.step_index = 1
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.appearance_field_index = max(0, self.appearance_field_index - 1)
            return
        if key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.appearance_field_index = min(len(fields) - 1, self.appearance_field_index + 1)
            return
        if current_field["kind"] == "select":
            options = current_field["options"]
            current_value = self.data["appearance"][current_field["key"]]
            current_index = options.index(current_value)
            if key in (curses.KEY_LEFT, ord("a"), ord("A"), ord("-")):
                self.data["appearance"][current_field["key"]] = options[max(0, current_index - 1)]
                return
            if key in (curses.KEY_RIGHT, ord("d"), ord("D"), ord("+"), ord("=")):
                self.data["appearance"][current_field["key"]] = options[min(len(options) - 1, current_index + 1)]
                return
            if key in (curses.KEY_ENTER, 10, 13):
                if self.can_advance_appearance():
                    self.step_index = 3
                return
            return
        if key in (curses.KEY_ENTER, 10, 13):
            if self.appearance_field_index < len(fields) - 1:
                self.appearance_field_index += 1
            elif self.can_advance_appearance():
                self.step_index = 3
            return
        if 32 <= key <= 126:
            self.custom_appearance_values[current_field["key"]] += chr(key)

    def handle_mode_key(self, key):
        if key in BACK_KEYS:
            self.step_index = 2
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.mode_index = max(0, self.mode_index - 1)
            return
        if key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.mode_index = min(len(self.CREATION_MODES) - 1, self.mode_index + 1)
            return
        if key in (curses.KEY_ENTER, 10, 13):
            confirmed_mode = self.CREATION_MODES[self.mode_index]
            if confirmed_mode == "questionnaire":
                self.begin_questionnaire()
            else:
                self.begin_manual()
            return

    def handle_traits_key(self, key):
        if key in BACK_KEYS:
            self.step_index = 4
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.trait_index = max(0, self.trait_index - 1)
            return
        if key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.trait_index = min(len(CREATION_TRAIT_POOL) - 1, self.trait_index + 1)
            return
        if key == ord(" "):
            trait = CREATION_TRAIT_POOL[self.trait_index]
            if trait in self.data["traits"]:
                self.data["traits"].remove(trait)
            elif len(self.data["traits"]) < 4:
                self.data["traits"].append(trait)
            return
        if key in (curses.KEY_ENTER, 10, 13) and self.can_advance_traits():
            self.step_index = 6
            return

    def handle_stats_key(self, key):
        if key in BACK_KEYS:
            self.step_index = 3
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.stat_index = max(0, self.stat_index - 1)
            return
        if key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.stat_index = min(len(CREATION_STAT_ORDER) - 1, self.stat_index + 1)
            return
        if key in (ord("r"), ord("R")):
            self.data["stats"] = build_randomized_starting_stats()
            return
        if key in (curses.KEY_ENTER, 10, 13):
            self.step_index = 5
            return
        if key in (curses.KEY_LEFT, ord("a"), ord("A"), ord("-")):
            stat_name = CREATION_STAT_ORDER[self.stat_index]
            self.data["stats"][stat_name] = max(0, self.data["stats"][stat_name] - 1)
            return
        if key in (curses.KEY_RIGHT, ord("d"), ord("D"), ord("+"), ord("=")):
            stat_name = CREATION_STAT_ORDER[self.stat_index]
            self.data["stats"][stat_name] = min(100, self.data["stats"][stat_name] + 1)

    def handle_questionnaire_key(self, key):
        question = QUESTIONNAIRE_QUESTIONS[self.question_index]
        if key in BACK_KEYS:
            if self.question_index > 0:
                self.question_index -= 1
                self.questionnaire_answers.pop()
                self.question_option_index = 0
            else:
                self.step_index = 3
                self.selected_mode = None
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.question_option_index = max(0, self.question_option_index - 1)
            return
        if key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.question_option_index = min(len(question["options"]) - 1, self.question_option_index + 1)
            return
        if key in (curses.KEY_ENTER, 10, 13):
            selected_option = question["options"][self.question_option_index]
            self.questionnaire_answers.append(selected_option)
            if self.question_index >= len(QUESTIONNAIRE_QUESTIONS) - 1:
                self.finalize_questionnaire_results()
                self.step_index = 5
                self.questionnaire_reveal_shown = False
                return
            self.question_index += 1
            self.question_option_index = 0

    def handle_questionnaire_reveal_key(self, key):
        if key in (curses.KEY_ENTER, 10, 13, ord(' ')):
            # Questionnaire reveal IS the confirmation — go straight to game, skip confirm screen
            self.running = False
        if key in BACK_KEYS:
            # Backspace goes back to last question
            self.questionnaire_reveal_shown = False
            self.step_index = 4
            self.questionnaire_framing_shown = True
            if self.questionnaire_answers:
                self.questionnaire_answers.pop()
                self.question_index = max(0, len(self.questionnaire_answers))
                self.question_option_index = 0

    def handle_confirm_key(self, key):
        if key in BACK_KEYS:
            if self.selected_mode == "questionnaire":
                if self.questionnaire_answers:
                    self.questionnaire_answers.pop()
                self.question_index = len(QUESTIONNAIRE_QUESTIONS) - 1
                self.question_option_index = 0
                self.step_index = 4
            else:
                self.step_index = 5
            return None
        if key in (curses.KEY_ENTER, 10, 13):
            self.running = False
            return self.build_result()
        return None

    def run(self):
        curses.set_escdelay(25)
        curses.curs_set(0)
        self.stdscr.keypad(True)

        while self.running:
            self.render()
            key = self.stdscr.getch()
            if self.handle_quit_key(key):
                continue
            if self.step_index == 0:
                self.handle_identity_key(key)
            elif self.step_index == 1:
                self.handle_location_key(key)
            elif self.step_index == 2:
                self.handle_appearance_key(key)
            elif self.step_index == 3:
                self.handle_mode_key(key)
            elif self.step_index == 4:
                if self.selected_mode == "questionnaire":
                    if not self.questionnaire_framing_shown:
                        if key in (curses.KEY_ENTER, 10, 13, ord(' ')):
                            self.questionnaire_framing_shown = True
                    else:
                        self.handle_questionnaire_key(key)
                else:
                    self.handle_stats_key(key)
            elif self.step_index == 5 and self.selected_mode == "questionnaire" and not self.questionnaire_reveal_shown:
                self.handle_questionnaire_reveal_key(key)
                if not self.running:
                    return self.build_result()
            elif self.step_index == 5 and self.selected_mode == "manual":
                self.handle_traits_key(key)
            else:
                result = self.handle_confirm_key(key)
                if result is not None:
                    return result

        return None


class ActoraTUI:
    """Small actor-first curses shell layered on top of the existing world seams."""

    def __init__(self, world, player_id):
        self.world = world
        self.player_id = player_id
        self.screen_name = "main"
        self.running = True
        self.lineage_selection = 0
        self.continuation_selection = 0
        self.skip_selection = 0
        self.skip_custom_value = ""
        self.selected_lineage_actor_id = None
        self.lineage_filter_mode = "all"
        self.lineage_search_text = ""
        self.lineage_search_active = False
        self.main_left_scroll = 0
        self.profile_scroll = 0
        self.history_scroll = 0
        self.history_search_active = False
        self.history_search_value = ""
        self.selected_continuation_actor_id = None
        self.last_message = MAIN_IDLE_MESSAGE
        self.event_log = []
        self.last_logged_year = 0
        self.last_advance_time = 0.0
        self.pending_choice = None
        self.remaining_skip_months = 0
        self.quit_confirmation_active = False
        self.quit_from_options = False
        self.menu_popup_active = False
        self.menu_selection = 0  # 0=Browser, 1=Actions, 2=Profile
        self.options_popup_active = False
        self.options_selection = 0
        self.gender_choice_offered = False
        self.sexuality_choice_offered = False
        self.identity_popup_suppressed_for_resumed_adult = False
        self.gender_choice_age = random.randint(12, 15)
        self.sexuality_choice_age = random.randint(14, 17)
        self.meeting_event_last_total_months = 0
        self.rel_browser_focus = "filters"
        self.rel_filter_index = 0
        self.rel_browser_search_active = False
        self.rel_browser_search_text = ""
        self.browser_tab = "relationships"
        self.active_actions = []
        self.hang_out_actor_ids = []
        self.personal_subtype_options = []
        self.actions_focus = "categories"
        self.actions_category_index = 0
        self.actions_action_index = 0

    def get_focused_actor_id(self):
        return self.world.get_focused_actor_id() or self.player_id

    def get_focused_actor(self):
        return self.world.get_actor(self.get_focused_actor_id())

    def get_snapshot_data(self):
        focused_actor_id = self.get_focused_actor_id()
        focused_actor = self.world.get_actor(focused_actor_id)
        snapshot_data = focused_actor.get_snapshot_data(
            self.world.current_year,
            self.world.current_month,
            self.world,
            focused_actor_id,
        )
        normalized_actor_stats = normalize_creation_stats(focused_actor.stats)
        secondary_statistics = {
            "strength": normalized_actor_stats["strength"],
            "charisma": normalized_actor_stats["charisma"],
            "imagination": normalized_actor_stats["imagination"],
            "memory": normalized_actor_stats["memory"],
            "wisdom": normalized_actor_stats["wisdom"],
            "stress": normalized_actor_stats["stress"],
            "discipline": normalized_actor_stats["discipline"],
            "willpower": normalized_actor_stats["willpower"],
            "looks": normalized_actor_stats["looks"],
            "fertility": normalized_actor_stats["fertility"],
        }
        snapshot_data["secondary_statistics"] = secondary_statistics
        return snapshot_data

    def sync_focus_state(self):
        """Applies shell-level dead-focus flow selection before rendering."""
        focused_actor = self.get_focused_actor()
        if focused_actor is None or focused_actor.is_alive():
            if self.screen_name in {"death_ack", "continuation", "continuation_detail"}:
                self.screen_name = "main"
            return

        if self.screen_name not in {"death_ack", "continuation", "continuation_detail"}:
            self.screen_name = "death_ack"

    def get_lineage_browser_state(self):
        browser_state = self.world.get_lineage_browser_data_for(
            self.get_focused_actor_id(),
            filter_mode=self.lineage_filter_mode,
            search_text=self.lineage_search_text,
            recent_record_limit=LINEAGE_RECORD_LIMIT,
        )

        entries = browser_state["entries"]
        if not entries:
            self.lineage_selection = 0
            self.selected_lineage_actor_id = None
            browser_state["selected_detail"] = None
            return browser_state

        if self.selected_lineage_actor_id is not None:
            matching_index = next(
                (
                    index
                    for index, entry in enumerate(entries)
                    if entry["actor_id"] == self.selected_lineage_actor_id
                ),
                None,
            )
            if matching_index is not None:
                self.lineage_selection = matching_index
            else:
                self.lineage_selection = 0
                self.selected_lineage_actor_id = entries[0]["actor_id"]
        else:
            self.lineage_selection = max(0, min(self.lineage_selection, len(entries) - 1))
            self.selected_lineage_actor_id = entries[self.lineage_selection]["actor_id"]

        browser_state["selected_detail"] = self.world.get_lineage_detail_for(
            self.get_focused_actor_id(),
            self.selected_lineage_actor_id,
            recent_record_limit=LINEAGE_RECORD_LIMIT,
        )
        return browser_state

    def get_lineage_entries(self):
        return self.get_lineage_browser_state()["entries"]

    def get_lineage_detail(self):
        return self.get_lineage_browser_state()["selected_detail"]

    def set_lineage_filter_mode(self, filter_mode):
        self.lineage_filter_mode = filter_mode
        self.lineage_selection = 0
        self.selected_lineage_actor_id = None
        self.last_message = f"Lineage filter: {LINEAGE_FILTER_LABELS[filter_mode]}."

    def clear_lineage_search(self):
        if self.lineage_search_text:
            self.lineage_search_text = ""
            self.lineage_selection = 0
            self.selected_lineage_actor_id = None
            self.last_message = "Lineage search cleared."

    def get_lineage_search_status(self):
        if self.lineage_search_active:
            return f"Search: {self.lineage_search_text}_"
        if self.lineage_search_text:
            return f"Search: {self.lineage_search_text}"
        return "Search: off"

    def get_rel_browser_search_status(self):
        """Returns the search status line for the relationship browser, or None."""
        if self.rel_browser_search_active:
            return f"Search: {self.rel_browser_search_text}_"
        if self.rel_browser_search_text:
            return f"Search: {self.rel_browser_search_text}"
        return None

    def get_relationship_browser_state(self):
        focused_actor_id = self.get_focused_actor_id()
        filter_mode = REL_FILTER_OPTIONS[self.rel_filter_index]
        browser_state = self.world.get_relationship_browser_data_for(
            focused_actor_id,
            filter_mode=filter_mode,
            search_text=self.rel_browser_search_text,
            recent_record_limit=LINEAGE_RECORD_LIMIT,
        )
        entries = browser_state["entries"]
        if not entries:
            self.lineage_selection = 0
            self.selected_lineage_actor_id = None
            browser_state["selected_detail"] = None
            return browser_state

        if self.selected_lineage_actor_id is not None:
            matching_index = next(
                (
                    index
                    for index, entry in enumerate(entries)
                    if entry["actor_id"] == self.selected_lineage_actor_id
                ),
                None,
            )
            if matching_index is not None:
                self.lineage_selection = matching_index
            else:
                self.lineage_selection = 0
                self.selected_lineage_actor_id = entries[0]["actor_id"]
        else:
            self.lineage_selection = max(0, min(self.lineage_selection, len(entries) - 1))
            self.selected_lineage_actor_id = entries[self.lineage_selection]["actor_id"]

        browser_state["selected_detail"] = self.world.get_relationship_detail_for(
            focused_actor_id,
            self.selected_lineage_actor_id,
            recent_record_limit=LINEAGE_RECORD_LIMIT,
        )
        return browser_state

    def get_continuity_state(self):
        return self.world.build_continuity_state_for(self.get_focused_actor_id())

    def append_event_log_entry(self, kind, text, *, year=None, month=None, record_type=None):
        """Appends one event-log entry with normalized structure."""
        self.event_log.append(
            build_event_log_entry(
                kind,
                text,
                year=year,
                month=month,
                record_type=record_type,
            )
        )

    def append_event_log_turn(self, turn_result, months_to_advance, new_records):
        """Extends the event log from one completed advance."""
        actual_months_advanced = turn_result["months_advanced"]
        if actual_months_advanced <= 0:
            return

        if months_to_advance > 1:
            label = "Month" if months_to_advance == 1 else "Months"
            self.append_event_log_entry(
                "skip_marker",
                f"{months_to_advance} {label} Skipped",
            )

        visible_record_types = {"birth", "death"}
        merged_entries = []
        event_identity_keys = set()

        for sequence, structured_event in enumerate(turn_result["events"]):
            event_year = structured_event.get("year")
            event_month = structured_event.get("month")
            event_text = structured_event.get("text", "")
            event_key = (event_year, event_month, event_text)
            event_identity_keys.add(event_key)
            merged_entries.append(
                {
                    "sort_key": (
                        event_year if event_year is not None else -1,
                        event_month if event_month is not None else -1,
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
            if record.get("record_type") in HIDDEN_PLAYER_RECORD_TYPES:
                continue
            if record.get("record_type") not in visible_record_types:
                continue
            if self.get_focused_actor_id() not in (record.get("actor_ids") or []):
                continue

            record_key = (
                record.get("year"),
                record.get("month"),
                record.get("text"),
            )
            if record_key in event_identity_keys:
                continue

            merged_entries.append(
                {
                    "sort_key": (
                        record.get("year") if record.get("year") is not None else -1,
                        record.get("month") if record.get("month") is not None else -1,
                        structural_sequence,
                        1,
                    ),
                    "kind": "event",
                    "text": record.get("text", ""),
                    "year": record.get("year"),
                    "month": record.get("month"),
                    "record_type": record.get("record_type"),
                }
            )
            structural_sequence += 1

        merged_entries.sort(key=lambda entry: entry["sort_key"])
        for entry in merged_entries:
            entry_year = entry.get("year")
            if entry_year is not None and entry_year > self.last_logged_year:
                for year in range(self.last_logged_year + 1, entry_year + 1):
                    self.append_event_log_entry(
                        "year_header",
                        f"Year {year}",
                        year=year,
                    )
                self.last_logged_year = entry_year

            self.append_event_log_entry(
                entry["kind"],
                entry["text"],
                year=entry.get("year"),
                month=entry.get("month"),
                record_type=entry.get("record_type"),
            )

    def maybe_offer_identity_choice(self):
        actor = self.get_focused_actor()
        if actor is None or not actor.is_alive():
            return False

        lifecycle = actor.get_lifecycle_state(self.world.current_year, self.world.current_month)
        age_years = lifecycle["age_years"]
        current_gender = actor.gender or "Other"

        if self.identity_popup_suppressed_for_resumed_adult:
            return False

        if age_years >= self.gender_choice_age and not self.gender_choice_offered:
            selected_index = (
                GENDER_IDENTITY_OPTIONS.index(current_gender)
                if current_gender in GENDER_IDENTITY_OPTIONS
                else 0
            )
            self.pending_choice = {
                "title": "A moment of self-reflection",
                "text": "As you grow, you find yourself thinking more about who you are.",
                "question": "Your gender identity feels like:",
                "options": list(GENDER_IDENTITY_OPTIONS),
                "selected_index": selected_index,
                "skippable": True,
                "choice_id": "gender_identity",
                "default_value": current_gender,
            }
            self.gender_choice_offered = True
            self.last_message = "A personal choice needs your attention."
            return True

        if age_years >= self.sexuality_choice_age and not self.sexuality_choice_offered:
            self.pending_choice = {
                "title": "A new kind of awareness",
                "text": "You have started noticing things about yourself you had not thought about before.",
                "question": "You feel attracted to:",
                "options": [label for label, _ in SEXUALITY_OPTION_LABELS],
                "selected_index": 0,
                "skippable": True,
                "choice_id": "sexuality",
                "default_value": None,
            }
            self.sexuality_choice_offered = True
            self.last_message = "A personal choice needs your attention."
            return True

        return False

    def maybe_offer_meeting_event(self):
        """Fires a meeting-event popup choice when conditions and cooldown allow."""
        actor = self.get_focused_actor()
        if actor is None or not actor.is_alive():
            return False

        lifecycle = actor.get_lifecycle_state(self.world.current_year, self.world.current_month)
        current_total_months = self.world.current_year * 12 + self.world.current_month
        if current_total_months - self.meeting_event_last_total_months < MEETING_EVENT_COOLDOWN_MONTHS:
            return False

        meeting_event = get_meeting_event_for_player(lifecycle)
        if meeting_event is None:
            return False

        self.meeting_event_last_total_months = current_total_months
        self.pending_choice = {
            "title": "Someone new",
            "text": meeting_event["text"],
            "question": "Do you want to introduce yourself?",
            "options": ["Introduce yourself", "Keep to yourself"],
            "selected_index": 0,
            "skippable": False,
            "choice_id": "meeting_npc",
        }
        self.last_message = "You notice someone nearby."
        return True

    def resolve_choice(self, choice_id, selected_value):
        actor = self.get_focused_actor()
        if actor is None:
            self.pending_choice = None
            return

        if choice_id == "gender_identity":
            old_gender = actor.gender
            actor.gender = selected_value
            if selected_value != old_gender:
                self.append_event_log_entry(
                    "event",
                    f"You now identify as {selected_value}.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
            else:
                self.append_event_log_entry(
                    "event",
                    "You reflected on your identity.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
        elif choice_id == "sexuality":
            if selected_value is not None:
                actor.sexuality = selected_value
                self.append_event_log_entry(
                    "event",
                    f"You identify as {selected_value}.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
            else:
                self.append_event_log_entry(
                    "event",
                    "You are still figuring things out.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
        elif choice_id == "meeting_npc":
            if selected_value == "Introduce yourself":
                focused_actor_id = self.get_focused_actor_id()
                npc_actor_id, npc = self.world.generate_meeting_npc(focused_actor_id)
                self.world.create_social_link_pair(
                    focused_actor_id,
                    npc_actor_id,
                    closeness=15,
                    status="active",
                    closeness_history_months=0,
                )
                self.append_event_log_entry(
                    "event",
                    f"You introduced yourself to {npc.get_full_name()}.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
                self.last_message = f"You met {npc.get_full_name()}."
            else:
                self.append_event_log_entry(
                    "event",
                    "You decided to keep to yourself.",
                    year=self.world.current_year,
                    month=self.world.current_month,
                )
                self.last_message = "You kept to yourself."

        elif choice_id == "select_hang_out_target":
            if selected_value is not None:
                options_list = (self.pending_choice or {}).get("options", [])
                try:
                    selected_idx = options_list.index(selected_value)
                    target_actor_id = self.hang_out_actor_ids[selected_idx]
                except (ValueError, IndexError):
                    self.pending_choice = None
                    return
                already_queued = any(
                    a["action_type"] == "spend_time" and a["target_actor_id"] == target_actor_id
                    for a in self.active_actions
                )
                if not already_queued:
                    focused_actor = self.world.get_focused_actor()
                    free_hours = get_monthly_free_hours(focused_actor)
                    used_hours = sum(a.get("time_cost", 0) for a in self.active_actions)
                    action_cost = HANG_OUT_TIME_COST
                    if used_hours + action_cost > free_hours:
                        self.last_message = "Not enough free time. (" + str(int(free_hours - used_hours)) + "h left)"
                        self.pending_choice = None
                        return
                    target_actor = self.world.get_actor(target_actor_id)
                    target_name = target_actor.get_full_name() if target_actor else "Someone"
                    self.active_actions.append({
                        "action_type": "spend_time",
                        "target_actor_id": target_actor_id,
                        "label": f"Spend time with {target_name}",
                        "time_cost": HANG_OUT_TIME_COST,
                    })
                    self.last_message = f"Queued: Spend time with {target_name}."
                else:
                    self.last_message = "Already queued to hang out with them."
            else:
                self.last_message = "Cancelled."
            self.pending_choice = None
            return
        elif choice_id in ("select_exercise_subtype", "select_read_subtype", "select_rest_subtype"):
            if selected_value is not None:
                options_list = (self.pending_choice or {}).get("options", [])
                try:
                    selected_idx = options_list.index(selected_value)
                    subtype = self.personal_subtype_options[selected_idx]
                except (ValueError, IndexError):
                    self.pending_choice = None
                    self.personal_subtype_options = []
                    return
                focused_actor = self.world.get_focused_actor()
                free_hours = get_monthly_free_hours(focused_actor)
                used_hours = sum(a.get("time_cost", 0) for a in self.active_actions)
                if used_hours + subtype["time_cost"] > free_hours:
                    self.last_message = "Not enough free time. (" + str(int(free_hours - used_hours)) + "h left)"
                    self.pending_choice = None
                    self.personal_subtype_options = []
                    return
                self.active_actions.append({
                    "action_type": "personal",
                    "subtype_id": subtype["id"],
                    "label": subtype["label"],
                    "time_cost": subtype["time_cost"],
                    "stat_changes": subtype["stat_changes"],
                })
                self.last_message = f"Queued: {subtype['label']}."
            else:
                self.last_message = "Cancelled."
            self.pending_choice = None
            self.personal_subtype_options = []
            return

        self.pending_choice = None
        remaining = self.remaining_skip_months
        self.remaining_skip_months = 0
        if remaining > 0:
            self.advance_time(remaining)

    def open_history(self):
        self.screen_name = "history"
        self.history_scroll = 10**9
        self.history_search_active = False
        self.history_search_value = ""
        self.last_message = "Browsing event history."

    def open_profile(self):
        self.screen_name = "profile"
        self.profile_scroll = 0
        self.last_message = "Viewing full profile."

    def get_history_lines(self, width):
        """Builds the logical full-screen history line list."""
        if not self.event_log:
            return ["No events yet."]
        lines = []
        for entry in self.event_log:
            if entry["kind"] == "year_header":
                if lines:
                    lines.append("")
                lines.append(format_history_entry(entry, width))
                lines.append("")
            else:
                lines.append(format_history_entry(entry, width))
        return lines

    def get_history_search_status(self):
        if not self.history_search_active:
            return None
        typed_year = self.history_search_value or ""
        return f"Jump to year: {typed_year}_"

    def jump_history_to_year(self, typed_year):
        clamped_year = max(1, min(typed_year, self.world.current_year))
        year_header_index = None
        fallback_index = None
        for index, entry in enumerate(self.event_log):
            if entry["kind"] != "year_header":
                continue
            fallback_index = index
            if entry["year"] >= clamped_year:
                year_header_index = index
                break

        if year_header_index is None:
            year_header_index = fallback_index
        if year_header_index is None:
            self.history_scroll = 0
            self.last_message = "No history entries are available yet."
            return

        history_width = getattr(self, "_history_content_width", 80)
        self.history_scroll = len(
            expand_render_lines(self.get_history_lines(history_width)[:year_header_index], history_width)
        )
        target_year = self.event_log[year_header_index]["year"]
        self.last_message = f"Jumped to Year {target_year}."

    def scroll_history_to_bottom(self):
        """Pins history view to the latest available entry."""
        self.history_scroll = 10**9

    @property
    def history_body_height(self):
        return getattr(self, "_history_body_height", 0)

    def advance_time(self, months_to_advance):
        """Advances time using the existing world-owned simulation seam."""
        aggregated_turn_result = {
            "months_advanced": 0,
            "events": [],
            "focused_actor_alive": True,
            "continuity_state": None,
        }
        new_records = []
        focused_actor_id = self.get_focused_actor_id()

        spend_time_actions = [a for a in self.active_actions if a["action_type"] == "spend_time"]
        personal_actions_queued = [a for a in self.active_actions if a["action_type"] == "personal"]
        shared_actor_ids = {a["target_actor_id"] for a in spend_time_actions}

        first_month = True
        for _ in range(months_to_advance):
            prior_record_count = len(self.world.records)
            month_turn_result = self.world.simulate_advance_turn(self.player_id, 1)
            new_records_this_month = self.world.records[prior_record_count:]
            new_records.extend(new_records_this_month)
            aggregated_turn_result["months_advanced"] += month_turn_result["months_advanced"]
            aggregated_turn_result["events"].extend(month_turn_result["events"])
            aggregated_turn_result["focused_actor_alive"] = month_turn_result["focused_actor_alive"]
            aggregated_turn_result["continuity_state"] = month_turn_result["continuity_state"]

            if first_month:
                for action in spend_time_actions:
                    target_id = action["target_actor_id"]
                    for lnk in self.world.get_links(source_id=focused_actor_id, target_id=target_id, link_type="social"):
                        lnk_meta = lnk.get("metadata", {})
                        if lnk_meta.get("status") == "active":
                            old_cl = lnk_meta.get("closeness", 0)
                            new_cl = min(100, old_cl + 5)
                            lnk_meta["closeness"] = new_cl
                            new_role = self.world._get_social_link_category(new_cl)
                            lnk["role"] = new_role
                            for rev_lnk in self.world.get_links(source_id=target_id, target_id=focused_actor_id, link_type="social"):
                                rev_meta = rev_lnk.get("metadata", {})
                                if rev_meta.get("status") == "active":
                                    rev_meta["closeness"] = new_cl
                                    rev_lnk["role"] = new_role
                    target_actor = self.world.get_actor(target_id)
                    target_name = target_actor.get_full_name() if target_actor else "Someone"
                    self.append_event_log_entry(
                        "event",
                        f"You spent some time with {target_name}.",
                        year=self.world.current_year,
                        month=self.world.current_month,
                    )
                if spend_time_actions:
                    self.world.apply_outcome(focused_actor_id, {"stat_changes": {"happiness": 3}})
                    self.world.apply_outcome(focused_actor_id, {"stat_changes": {"stress": -2}})
                for action in personal_actions_queued:
                    self.world.apply_outcome(focused_actor_id, {"stat_changes": action["stat_changes"]})
                    self.append_event_log_entry(
                        "event",
                        action.get("event_text", f"You did: {action['label']}."),
                        year=self.world.current_year,
                        month=self.world.current_month,
                    )
                self.active_actions = [
                    a for a in self.active_actions if a["action_type"] not in ("spend_time", "personal")
                ]

            for record in new_records_this_month:
                if record.get("record_type") != "death":
                    continue
                for dead_actor_id in record.get("actor_ids", []):
                    if dead_actor_id == focused_actor_id:
                        continue
                    for lnk in self.world.get_links(source_id=focused_actor_id, target_id=dead_actor_id, link_type="social"):
                        lnk_meta = lnk.get("metadata", {})
                        if lnk_meta.get("status") != "active":
                            continue
                        closeness = lnk_meta.get("closeness", 0)
                        dead_actor = self.world.get_actor(dead_actor_id)
                        dead_name = dead_actor.get_full_name() if dead_actor else "Someone"
                        focused_actor_obj = self.world.get_actor(focused_actor_id)
                        if closeness >= 70:
                            if focused_actor_obj:
                                focused_actor_obj.modify_stat("happiness", -18)
                            self.append_event_log_entry(
                                "event",
                                f"You were devastated to hear that {dead_name}, your close friend, has passed away.",
                                year=self.world.current_year,
                                month=self.world.current_month,
                            )
                        elif closeness >= 30:
                            if focused_actor_obj:
                                focused_actor_obj.modify_stat("happiness", -8)
                            self.append_event_log_entry(
                                "event",
                                f"You learned that {dead_name}, your friend, has passed away.",
                                year=self.world.current_year,
                                month=self.world.current_month,
                            )

            if month_turn_result.get("focused_actor_alive", True):
                month_shared = shared_actor_ids if first_month else set()
                drift_events = self.world.apply_social_link_decay(focused_actor_id, month_shared)
                for drift in drift_events:
                    self.append_event_log_entry(
                        "event",
                        drift["text"],
                        year=drift["year"],
                        month=drift["month"],
                    )

            first_month = False

            if month_turn_result["months_advanced"] <= 0 or not month_turn_result["focused_actor_alive"]:
                break
            if self.maybe_offer_identity_choice():
                remaining = months_to_advance - aggregated_turn_result["months_advanced"]
                if remaining > 0:
                    self.remaining_skip_months = remaining
                break
            if self.maybe_offer_meeting_event():
                remaining = months_to_advance - aggregated_turn_result["months_advanced"]
                if remaining > 0:
                    self.remaining_skip_months = remaining
                break

        self.append_event_log_turn(aggregated_turn_result, months_to_advance, new_records)
        actual_months_advanced = aggregated_turn_result["months_advanced"]
        if actual_months_advanced == 1:
            self.last_message = "Advanced 1 month."
        elif actual_months_advanced != months_to_advance:
            if self.pending_choice is not None:
                self.last_message = "A personal choice needs your attention."
            else:
                self.last_message = f"Advanced {actual_months_advanced} of {months_to_advance} months before death."
        else:
            self.last_message = f"Advanced {actual_months_advanced} months."
        if aggregated_turn_result["continuity_state"] is not None and not aggregated_turn_result["focused_actor_alive"]:
            self.screen_name = "death_ack"

    def advance_one_month(self):
        self.advance_time(1)

    def open_skip_time(self):
        self.skip_selection = 0
        self.skip_custom_value = ""
        self.screen_name = "skip_time"
        self.last_message = "Choose how far ahead to jump."

    def get_selected_skip_months(self):
        return SKIP_MONTH_PRESETS[self.skip_selection]

    def get_custom_skip_months(self):
        if not self.skip_custom_value:
            return None
        custom_months = int(self.skip_custom_value)
        if custom_months <= 0:
            return None
        return custom_months

    def confirm_skip_selection(self):
        months_to_advance = self.get_custom_skip_months() or self.get_selected_skip_months()
        self.screen_name = "main"
        self.advance_time(months_to_advance)

    def open_lineage(self):
        self.lineage_selection = 0
        self.selected_lineage_actor_id = None
        self.lineage_search_active = False
        self.screen_name = "lineage"
        self.last_message = "Browsing lineage archive."

    def open_relationship_browser(self):
        self.lineage_selection = 0
        self.selected_lineage_actor_id = None
        self.rel_browser_focus = "filters"
        self.rel_filter_index = 0
        self.rel_browser_search_active = False
        self.rel_browser_search_text = ""
        self.screen_name = "relationship_browser"
        self.last_message = "Browsing relationships."

    def _open_menu_selection(self):
        """Opens the screen selected in the menu popup."""
        self.menu_popup_active = False
        if self.menu_selection == 0:
            self.open_browser("relationships")
        elif self.menu_selection == 1:
            self.open_actions()
        elif self.menu_selection == 2:
            self.open_profile()

    def _open_options_selection(self):
        if self.options_selection == 0:
            self.options_popup_active = False
            self.quit_confirmation_active = True
            self.quit_from_options = True
        # Items 1 and 2 (Help, Settings) are not yet implemented — do nothing

    def open_browser(self, tab="relationships"):
        """Opens the unified Browser screen on the specified tab."""
        self.browser_tab = tab
        if tab == "relationships":
            self.lineage_selection = 0
            self.selected_lineage_actor_id = None
            self.rel_browser_focus = "filters"
            self.rel_filter_index = 0
            self.rel_browser_search_active = False
            self.rel_browser_search_text = ""
            self.last_message = "Browsing relationships."
        else:
            self.history_scroll = 10**9
            self.history_search_active = False
            self.history_search_value = ""
            self.last_message = "Browsing event history."
        self.screen_name = "browser"

    def open_actions(self):
        """Opens the Actions screen."""
        self.screen_name = "actions"
        self.actions_focus = "categories"
        self.actions_category_index = 0
        self.actions_action_index = 0
        self.last_message = "Actions."

    def open_hang_out_select(self):
        """Opens the hang out overlay to select a friend to spend time with."""
        focused_actor_id = self.get_focused_actor_id()
        social_links = self.world.get_links(source_id=focused_actor_id, link_type="social")
        active_links = [l for l in social_links if l.get("metadata", {}).get("status") == "active"]
        if not active_links:
            self.last_message = "No active social connections are available for Hang Out yet."
            return

        options = []
        self.hang_out_actor_ids = []
        for link in active_links:
            target_id = link.get("target_id")
            target_actor = self.world.get_actor(target_id)
            if target_actor is None:
                continue
            meta = link.get("metadata", {})
            closeness = meta.get("closeness", 0)
            tier = _get_social_tier_label(closeness)
            already_queued = any(
                a["action_type"] == "spend_time" and a["target_actor_id"] == target_id
                for a in self.active_actions
            )
            label = f"{target_actor.get_full_name()} · {tier}"
            if already_queued:
                label += " (queued)"
            options.append(label)
            self.hang_out_actor_ids.append(target_id)

        if not options:
            self.last_message = "No active social connections are available for Hang Out yet."
            return

        self.pending_choice = {
            "title": "Hang Out",
            "text": "Choose someone to spend time with.",
            "question": "",
            "options": options,
            "selected_index": 0,
            "skippable": True,
            "choice_id": "select_hang_out_target",
            "default_value": None,
        }
        self.last_message = "Select someone to hang out with."

    def scroll_profile(self, delta):
        profile_lines = self.build_profile_lines(self.get_snapshot_data())
        visible_height = self.profile_body_height
        if visible_height <= 0:
            visible_height = 1
        _, next_offset, _, _ = get_scroll_window(profile_lines, visible_height, self.profile_scroll + delta)
        if next_offset != self.profile_scroll:
            self.profile_scroll = next_offset
            pass  # no message on scroll

    def scroll_main_left(self, delta):
        snapshot_sections = build_snapshot_sections(self.get_snapshot_data())
        left_sections = [
            section
            for section in snapshot_sections
            if section["key"] in MAIN_LEFT_SECTION_KEYS
        ]
        scrollable_lines = [self.last_message, ""]
        scrollable_lines.extend(self.build_main_left_lines(left_sections, include_time=False))
        visible_height = self.main_body_height
        if visible_height <= 0:
            visible_height = 1
        _, next_offset, _, _ = get_scroll_window(scrollable_lines, visible_height, self.main_left_scroll + delta)
        if next_offset != self.main_left_scroll:
            self.main_left_scroll = next_offset

    @property
    def main_body_height(self):
        return getattr(self, "_main_body_height", 0)

    @property
    def profile_body_height(self):
        return getattr(self, "_profile_body_height", 0)

    def build_main_left_lines(self, snapshot_sections, *, include_time):
        focused_actor_id = self.get_focused_actor_id()
        social_links = self.world.get_links(source_id=focused_actor_id, link_type="social")
        active_social_links = [
            lnk for lnk in social_links if lnk.get("metadata", {}).get("status") == "active"
        ]
        lines = []
        for section in snapshot_sections:
            if not include_time and section["key"] == "time":
                continue
            lines.append(section["title"])
            lines.extend(section["lines"])
            if section["key"] == "relationships" and active_social_links:
                for lnk in active_social_links:
                    target_id = lnk.get("target_id")
                    target_actor = self.world.get_actor(target_id)
                    if target_actor is None:
                        continue
                    meta = lnk.get("metadata", {})
                    closeness = meta.get("closeness", 0)
                    tier = _get_social_tier_label(closeness)
                    lines.append(f"  {target_actor.get_full_name()} · {tier}")
            lines.append("")
        if lines and lines[-1] == "":
            lines.pop()
        return lines

    def build_profile_lines(self, snapshot_data):
        identity = snapshot_data["identity"]
        location = snapshot_data["location"]
        appearance = snapshot_data["appearance"]
        statistics = snapshot_data["statistics"]
        secondary_statistics = snapshot_data["secondary_statistics"]
        traits = snapshot_data["traits"]
        relationships = snapshot_data["relationships"]

        lines = [
            "Identity",
            f"  Name: {identity['full_name']}",
            f"  Species: {identity['species']}",
            f"  Sex: {identity['sex']}",
            f"  Gender: {identity['gender']}",
            f"  Sexuality: {identity.get('sexuality') or 'Not yet known'}",
            f"  Age: {identity['age']}",
            f"  Life Stage: {identity['life_stage']}",
            "",
            "Appearance",
            f"  Eye Color: {appearance['eye_color']}",
            f"  Hair Color: {appearance['hair_color']}",
            f"  Skin Tone: {appearance['skin_tone']}",
            "",
            "Traits",
        ]

        if traits:
            lines.append("  " + ", ".join(traits))
        else:
            lines.append("  None")

        lines.extend(
            [
                "",
            "Primary Stats",
            format_stat_pair("Health", statistics["health"], "Happiness", statistics["happiness"]),
            format_stat_pair("Intelligence", statistics["intelligence"], "Money", f"${statistics['money']}"),
            "",
            "Secondary Stats",
            format_stat_pair("Strength", secondary_statistics["strength"], "Charisma", secondary_statistics["charisma"]),
            format_stat_pair("Imagination", secondary_statistics["imagination"], "Memory", secondary_statistics["memory"]),
            format_stat_pair("Wisdom", secondary_statistics["wisdom"], "Discipline", secondary_statistics["discipline"]),
            format_stat_pair("Willpower", secondary_statistics["willpower"], "Stress", secondary_statistics["stress"]),
            format_stat_pair("Looks", secondary_statistics["looks"], "Fertility", secondary_statistics["fertility"]),
            "",
            "Location",
            f"  Planet: {location['world_body_name']}",
            f"  City: {location['current_place_name']}",
            f"  Country: {location['jurisdiction_place_name']}",
            "",
            "Relationships",
            ]
        )

        if relationships:
            lines.extend([f"  {entry['label']}: {entry['name']}" for entry in relationships])
        else:
            lines.append("  No living family.")

        return lines

    def acknowledge_death(self):
        continuity_state = self.get_continuity_state()
        self.continuation_selection = 0
        self.selected_continuation_actor_id = None
        self.screen_name = "continuation"
        if continuity_state["had_continuity_candidates"]:
            self.last_message = "Choose who to continue as."
        else:
            self.last_message = "No one is available to continue."

    def get_selected_continuation_candidate(self):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        if not candidates:
            return None

        self.continuation_selection = max(
            0,
            min(self.continuation_selection, len(candidates) - 1),
        )
        return candidates[self.continuation_selection]

    def open_continuation_detail(self):
        selected_candidate = self.get_selected_continuation_candidate()
        if selected_candidate is None:
            return
        self.selected_continuation_actor_id = selected_candidate["actor_id"]
        self.screen_name = "continuation_detail"
        self.last_message = f"Inspecting {selected_candidate['full_name']}."

    def choose_continuation(self):
        selected_candidate = self.get_selected_continuation_candidate()
        if selected_candidate is None:
            self.running = False
            return

        successor_actor_id = selected_candidate["actor_id"]
        handoff_result = self.world.handoff_focus_to_continuation(
            self.get_focused_actor_id(),
            successor_actor_id,
        )
        self.player_id = successor_actor_id
        self.last_logged_year = 0
        self.event_log.append(
            {
                "kind": "life_separator",
                "text": f"New Life: {handoff_result['new_focused_actor_name']}",
            }
        )
        self.pending_choice = None
        self.remaining_skip_months = 0
        continued_actor = self.get_focused_actor()
        continued_lifecycle = (
            continued_actor.get_lifecycle_state(self.world.current_year, self.world.current_month)
            if continued_actor is not None
            else None
        )
        self.identity_popup_suppressed_for_resumed_adult = False
        if continued_actor is not None and continued_lifecycle is not None and continued_lifecycle["age_years"] >= 18:
            continued_actor.auto_resolve_identity()
            self.gender_choice_offered = True
            self.sexuality_choice_offered = True
            self.identity_popup_suppressed_for_resumed_adult = True
        else:
            self.gender_choice_offered = False
            self.gender_choice_offered = False
        self.sexuality_choice_offered = False
        self.gender_choice_age = random.randint(12, 15)
        self.sexuality_choice_age = random.randint(14, 17)
        self.meeting_event_last_total_months = 0
        self.selected_continuation_actor_id = None
        self.screen_name = "main"
        self.quit_confirmation_active = False
        self.last_message = f"Your story continues as {handoff_result['new_focused_actor_name']}."

    def handle_pending_choice_key(self, key):
        # Q and E are blocked while a popup is active — cannot advance or skip during a choice
        if key in (ord("q"), ord("Q"), ord("e"), ord("E")):
            return

        if self.pending_choice is None:
            return

        options = self.pending_choice["options"]
        selected_index = self.pending_choice["selected_index"]
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.pending_choice["selected_index"] = max(0, selected_index - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.pending_choice["selected_index"] = min(len(options) - 1, selected_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            selected_option = options[self.pending_choice["selected_index"]]
            if self.pending_choice["choice_id"] == "sexuality":
                selected_value = dict(SEXUALITY_OPTION_LABELS)[selected_option]
            else:
                selected_value = selected_option
            self.resolve_choice(self.pending_choice["choice_id"], selected_value)
        elif self.pending_choice.get("skippable") and key in BACK_KEYS:
            self.resolve_choice(
                self.pending_choice["choice_id"],
                self.pending_choice.get("default_value"),
            )

    def handle_main_key(self, key):
        # Q = advance month
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - self.last_advance_time < ADVANCE_THROTTLE_SECONDS:
                return
            self.last_advance_time = now
            self.advance_one_month()
        # E = skip time
        elif key in (ord("e"), ord("E")):
            self.open_skip_time()
        # [1] = Menu popup
        elif key == ord("1"):
            self.menu_popup_active = not self.menu_popup_active
            self.menu_selection = 0
        # Esc = Options popup
        elif key == 27:
            self.options_popup_active = not self.options_popup_active
            if self.options_popup_active:
                self.options_selection = 0
            else:
                self.last_message = MAIN_IDLE_MESSAGE
        # WASD = movement aliases
        elif key in (ord("w"), ord("W"), curses.KEY_UP):
            self.scroll_main_left(-1)
        elif key in (ord("s"), ord("S"), curses.KEY_DOWN):
            self.scroll_main_left(1)

    def handle_history_key(self, key):
        if self.history_search_active:
            if key == 27:
                self.history_search_active = False
                self.history_search_value = ""
                self.last_message = "Year jump canceled."
                return
            if key in (curses.KEY_ENTER, 10, 13):
                typed_year = int(self.history_search_value) if self.history_search_value else 1
                self.jump_history_to_year(typed_year)
                self.history_search_active = False
                self.history_search_value = ""
                return
            if key == curses.KEY_BACKSPACE or key in (127, 8):
                self.history_search_value = self.history_search_value[:-1]
                return
            if ord("0") <= key <= ord("9") and len(self.history_search_value) < 9:
                self.history_search_value += chr(key)
                return
            return

        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - self.last_advance_time < ADVANCE_THROTTLE_SECONDS:
                return
            self.last_advance_time = now
            self.advance_one_month()
        elif key in (ord("e"), ord("E")):
            self.open_skip_time()
        elif key in BACK_KEYS:
            self.screen_name = "main"
            self.history_search_active = False
            self.history_search_value = ""
            self.last_message = MAIN_IDLE_MESSAGE
        elif key == ord("/"):
            self.history_search_active = True
            self.history_search_value = ""
            self.last_message = "Type a year number. Enter jumps. Esc cancels."
        elif key in (curses.KEY_UP, ord("w"), ord("W")):
            self.history_scroll = max(0, self.history_scroll - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.history_scroll += 1

    def handle_profile_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - self.last_advance_time < ADVANCE_THROTTLE_SECONDS:
                return
            self.last_advance_time = now
            self.advance_one_month()
        elif key in (ord("e"), ord("E")):
            self.open_skip_time()
        elif key in BACK_KEYS:
            self.screen_name = "main"
            self.last_message = MAIN_IDLE_MESSAGE
        elif key in (curses.KEY_UP, ord("w"), ord("W")):
            self.scroll_profile(-1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.scroll_profile(1)

    def handle_lineage_key(self, key):
        if self.lineage_search_active:
            if key == 27:
                self.lineage_search_active = False
                self.last_message = "Returned to lineage."
                return
            if key in (curses.KEY_ENTER, 10, 13):
                self.lineage_search_active = False
                self.lineage_selection = 0
                self.selected_lineage_actor_id = None
                if self.lineage_search_text:
                    self.last_message = f"Lineage search: {self.lineage_search_text}."
                else:
                    self.last_message = "Lineage search cleared."
                return
            if key == curses.KEY_BACKSPACE or key in (127, 8):
                if self.lineage_search_text:
                    self.lineage_search_text = self.lineage_search_text[:-1]
                    self.lineage_selection = 0
                    self.selected_lineage_actor_id = None
                return
            if 32 <= key <= 126 and len(self.lineage_search_text) < 24:
                self.lineage_search_text += chr(key)
                self.lineage_selection = 0
                self.selected_lineage_actor_id = None
                return

        lineage_entries = self.get_lineage_entries()
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - self.last_advance_time < ADVANCE_THROTTLE_SECONDS:
                return
            self.last_advance_time = now
            self.advance_one_month()
            return
        if key in (ord("e"), ord("E")):
            self.open_skip_time()
            return
        if key in BACK_KEYS:
            self.screen_name = "main"
            self.lineage_search_active = False
            self.last_message = MAIN_IDLE_MESSAGE
            return
        if key in (ord("a"), ord("A")):
            self.set_lineage_filter_mode("all")
            return
        if key in (ord("d"), ord("D")):
            self.set_lineage_filter_mode("dead")
            return
        if key == ord("/"):
            self.lineage_search_active = True
            self.last_message = "Type to search lineage names. Enter confirms. Esc cancels search."
            return
        if not lineage_entries:
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.lineage_selection = max(0, self.lineage_selection - 1)
            self.selected_lineage_actor_id = lineage_entries[self.lineage_selection]["actor_id"]
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.lineage_selection = min(len(lineage_entries) - 1, self.lineage_selection + 1)
            self.selected_lineage_actor_id = lineage_entries[self.lineage_selection]["actor_id"]
        elif key in (curses.KEY_ENTER, 10, 13):
            self.last_message = f"Inspecting {lineage_entries[self.lineage_selection]['full_name']}."

    def handle_relationship_browser_key(self, key, *, back_to="main"):
        """Handles keys for the relationship browser tab/screen.

        back_to: screen name to return to when [B] is pressed from filters focus.
        """
        if self.rel_browser_search_active:
            if key == 27:
                self.rel_browser_search_active = False
                self.last_message = "Search canceled."
                return
            if key in (curses.KEY_ENTER, 10, 13):
                self.rel_browser_search_active = False
                self.lineage_selection = 0
                self.selected_lineage_actor_id = None
                if self.rel_browser_search_text:
                    self.last_message = f"Search: {self.rel_browser_search_text}."
                else:
                    self.last_message = "Search cleared."
                return
            if key == curses.KEY_BACKSPACE or key in (127, 8):
                if self.rel_browser_search_text:
                    self.rel_browser_search_text = self.rel_browser_search_text[:-1]
                    self.lineage_selection = 0
                    self.selected_lineage_actor_id = None
                return
            if 32 <= key <= 126 and len(self.rel_browser_search_text) < 24:
                self.rel_browser_search_text += chr(key)
                self.lineage_selection = 0
                self.selected_lineage_actor_id = None
                return

        browser_state = self.get_relationship_browser_state()
        entries = browser_state["entries"]

        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - self.last_advance_time < ADVANCE_THROTTLE_SECONDS:
                return
            self.last_advance_time = now
            self.advance_one_month()
            return
        if key in (ord("e"), ord("E")):
            self.open_skip_time()
            return

        if key == ord("/"):
            self.rel_browser_search_active = True
            self.last_message = "Type to search names. Enter confirms. Esc cancels."
            return
        if key == curses.KEY_BACKSPACE or key in (127, 8):
            if self.rel_browser_search_text:
                self.rel_browser_search_text = ""
                self.lineage_selection = 0
                self.selected_lineage_actor_id = None
                self.last_message = "Search cleared."
                return

        if self.rel_browser_focus == "filters":
            if key in BACK_KEYS:
                self.screen_name = back_to
                self.last_message = MAIN_IDLE_MESSAGE
                return
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                self.rel_filter_index = max(0, self.rel_filter_index - 1)
                self.lineage_selection = 0
                self.selected_lineage_actor_id = None
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.rel_filter_index = min(len(REL_FILTER_OPTIONS) - 1, self.rel_filter_index + 1)
                self.lineage_selection = 0
                self.selected_lineage_actor_id = None
            elif key in (9, curses.KEY_RIGHT, ord("d"), ord("D")):  # Tab or Right
                self.rel_browser_focus = "actors"
                self.last_message = "Browsing people."
        else:  # actors focus
            if key in (curses.KEY_LEFT, ord("a"), ord("A")) or key in BACK_KEYS:
                self.rel_browser_focus = "filters"
                self.last_message = "Browsing relationships."
                return
            if not entries:
                return
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                self.lineage_selection = max(0, self.lineage_selection - 1)
                self.selected_lineage_actor_id = entries[self.lineage_selection]["actor_id"]
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.lineage_selection = min(len(entries) - 1, self.lineage_selection + 1)
                self.selected_lineage_actor_id = entries[self.lineage_selection]["actor_id"]
            elif key in (curses.KEY_ENTER, 10, 13):
                if entries:
                    self.last_message = f"Inspecting {entries[self.lineage_selection]['full_name']}."

    def handle_browser_key(self, key):
        """Handles keys for the unified Browser screen (Relationships + History tabs)."""
        search_active = (
            (self.browser_tab == "relationships" and self.rel_browser_search_active)
            or (self.browser_tab == "history" and self.history_search_active)
        )
        if not search_active and key == 27:  # Esc → Options
            self.options_popup_active = True
            self.options_selection = 0
            return
        if not search_active and key == 9:  # Tab key — switch tabs
            if self.browser_tab == "relationships":
                self.browser_tab = "history"
                self.last_message = "Browsing event history."
            else:
                self.browser_tab = "relationships"
                self.last_message = "Browsing relationships."
            return
        if self.browser_tab == "relationships":
            self.handle_relationship_browser_key(key, back_to="main")
        elif self.browser_tab == "history":
            self.handle_history_key(key)

    def get_actions_categories(self):
        """Returns the categories and their available actions for the current actor."""
        focused_actor_id = self.get_focused_actor_id()
        social_links = self.world.get_links(source_id=focused_actor_id, link_type="social")
        active_social = [lnk for lnk in social_links if lnk.get("metadata", {}).get("status") == "active"]
        social_actions = []
        if active_social:
            social_actions.append({"id": "hang_out", "label": "Hang Out", "links": active_social, "time_cost": HANG_OUT_TIME_COST})
        personal_actions = [
            {"id": "exercise", "label": "Exercise", "subtypes": EXERCISE_SUBTYPES, "time_cost": EXERCISE_TIME_COST},
            {"id": "read", "label": "Read", "subtypes": READ_SUBTYPES, "time_cost": READ_TIME_COST},
            {"id": "rest", "label": "Rest", "subtypes": REST_SUBTYPES, "time_cost": REST_TIME_COST},
        ]
        return [
            {"id": "social", "label": "Social", "actions": social_actions},
            {"id": "personal", "label": "Personal", "actions": personal_actions},
        ]

    def handle_actions_key(self, key):
        """Handles keys for the Actions screen."""
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - self.last_advance_time < ADVANCE_THROTTLE_SECONDS:
                return
            self.last_advance_time = now
            self.advance_one_month()
        elif key in (ord("e"), ord("E")):
            self.open_skip_time()
        elif key in BACK_KEYS:
            if self.actions_focus == "actions":
                self.actions_focus = "categories"
                self.actions_action_index = 0
            else:
                self.screen_name = "main"
                self.last_message = MAIN_IDLE_MESSAGE
        elif key in (curses.KEY_UP, ord("w"), ord("W")):
            if self.actions_focus == "categories":
                categories = self.get_actions_categories()
                self.actions_category_index = max(0, self.actions_category_index - 1)
                self.actions_action_index = 0
            else:
                categories = self.get_actions_categories()
                cat = categories[self.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                self.actions_action_index = max(0, self.actions_action_index - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            if self.actions_focus == "categories":
                categories = self.get_actions_categories()
                self.actions_category_index = min(len(categories) - 1, self.actions_category_index + 1)
                self.actions_action_index = 0
            else:
                categories = self.get_actions_categories()
                cat = categories[self.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                self.actions_action_index = min(max(0, len(actions) - 1), self.actions_action_index + 1)
        elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
            if self.actions_focus == "categories":
                categories = self.get_actions_categories()
                cat = categories[self.actions_category_index] if categories else None
                if cat and cat["actions"]:
                    self.actions_focus = "actions"
                    self.actions_action_index = 0
        elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
            if self.actions_focus == "actions":
                self.actions_focus = "categories"
                self.actions_action_index = 0
        elif key in (curses.KEY_ENTER, 10, 13):
            if self.actions_focus == "actions":
                categories = self.get_actions_categories()
                cat = categories[self.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                if actions and self.actions_action_index < len(actions):
                    action = actions[self.actions_action_index]
                    if action["id"] == "hang_out":
                        self.open_hang_out_select()
                    elif action["id"] in ("exercise", "read", "rest"):
                        subtypes = action["subtypes"]
                        self.personal_subtype_options = subtypes
                        self.pending_choice = {
                            "title": "Choose type",
                            "text": "",
                            "question": "",
                            "options": [f"{s['label']}  {s['time_cost']}h" for s in subtypes],
                            "selected_index": 0,
                            "skippable": True,
                            "choice_id": f"select_{action['id']}_subtype",
                            "default_value": None,
                        }
                        self.last_message = f"Choose how you want to {action['label'].lower()}."


    def handle_death_ack_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            return  # Q blocked on death screen — use Esc for Options
        elif key in (curses.KEY_ENTER, 10, 13):
            self.acknowledge_death()

    def handle_skip_time_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        # Q blocked during skip time — user is actively doing a time action
        if key in (ord("q"), ord("Q")):
            return  # do nothing
        if key in BACK_KEYS:
            self.screen_name = "main"
            self.last_message = MAIN_IDLE_MESSAGE
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.skip_selection = max(0, self.skip_selection - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.skip_selection = min(len(SKIP_MONTH_PRESETS) - 1, self.skip_selection + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            self.confirm_skip_selection()
        elif key == curses.KEY_BACKSPACE or key in (127, 8):
            self.skip_custom_value = self.skip_custom_value[:-1]
        elif ord("0") <= key <= ord("9"):
            if len(self.skip_custom_value) < 4:
                self.skip_custom_value += chr(key)

    def handle_continuation_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        if key in (ord("q"), ord("Q")):
            return  # Q blocked on continuation screen — use Esc for Options
        if key in BACK_KEYS:
            self.screen_name = "death_ack"
            self.last_message = "Returned to death summary."
            return
        if not candidates:
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            self.continuation_selection = max(0, self.continuation_selection - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            self.continuation_selection = min(
                len(candidates) - 1,
                self.continuation_selection + 1,
            )
        elif key in (curses.KEY_ENTER, 10, 13):
            self.open_continuation_detail()

    def handle_continuation_detail_key(self, key):
        if key == 27:
            self.options_popup_active = True
            self.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            return  # Q blocked on continuation screen — use Esc for Options
        elif key in BACK_KEYS:
            self.screen_name = "continuation"
            self.last_message = "Returned to available lives."
        elif key in (curses.KEY_ENTER, 10, 13):
            self.choose_continuation()

    def handle_key(self, key):
        self.sync_focus_state()
        if self.quit_confirmation_active:
            if key in BACK_KEYS or key == 27:
                self.quit_confirmation_active = False
                if self.quit_from_options:
                    self.quit_from_options = False
                    self.options_popup_active = True
                return
            if key in (curses.KEY_ENTER, 10, 13):
                self.running = False
                return
            return
        if self.options_popup_active:
            OPTIONS_ITEMS = ["Quit Game", "Help / Controls", "Settings"]
            if key == 27:
                self.options_popup_active = False
            elif key in (curses.KEY_UP, ord("w"), ord("W")):
                self.options_selection = max(0, self.options_selection - 1)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.options_selection = min(len(OPTIONS_ITEMS) - 1, self.options_selection + 1)
            elif key in (curses.KEY_ENTER, 10, 13):
                self._open_options_selection()
            return
        if self.menu_popup_active:
            MENU_ITEMS = ["Browser", "Actions", "Profile"]
            if key in BACK_KEYS:
                self.menu_popup_active = False
            elif key in (curses.KEY_UP, ord("w"), ord("W")):
                self.menu_selection = max(0, self.menu_selection - 1)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.menu_selection = min(len(MENU_ITEMS) - 1, self.menu_selection + 1)
            elif key == ord("1"):
                self.menu_selection = 0
                self._open_menu_selection()
            elif key == ord("2"):
                self.menu_selection = 1
                self._open_menu_selection()
            elif key == ord("3"):
                self.menu_selection = 2
                self._open_menu_selection()
            elif key in (curses.KEY_ENTER, 10, 13):
                self._open_menu_selection()
            return
        if self.pending_choice is not None:
            self.handle_pending_choice_key(key)
            return
        if self.screen_name == "main":
            self.handle_main_key(key)
        elif self.screen_name == "profile":
            self.handle_profile_key(key)
        elif self.screen_name == "lineage":
            self.handle_lineage_key(key)
        elif self.screen_name == "relationship_browser":
            self.handle_relationship_browser_key(key)
        elif self.screen_name == "history":
            self.handle_history_key(key)
        elif self.screen_name == "browser":
            self.handle_browser_key(key)
        elif self.screen_name == "actions":
            self.handle_actions_key(key)
        elif self.screen_name == "skip_time":
            self.handle_skip_time_key(key)
        elif self.screen_name == "death_ack":
            self.handle_death_ack_key(key)
        elif self.screen_name == "continuation":
            self.handle_continuation_key(key)
        elif self.screen_name == "continuation_detail":
            self.handle_continuation_detail_key(key)

    def render_footer(self, stdscr, height, width):
        footer_hints = {
            "main": "[Q] Advance Month   [E] Skip Time  |  [1] Menu  |  [Esc] Options",
            "profile": "[↑↓] Scroll   [Bsp] Back   [Q] Advance   [Esc] Options",
            "lineage": "[↑↓] Move   [A] All   [L] Living   [D] Dead   [/] Search   [Bsp] Back   [Q] Advance",
            "relationship_browser": "[↑↓] Filter/Move   [/] Search   [Tab/→] Switch   [Bsp/←] Back   [Q] Advance",
            "history": "[↑↓] Scroll   [/] Jump to Year   [Bsp] Back   [Q] Advance",
            "browser": "[Tab] Switch Tab   [↑↓] Move   [/] Search   [Bsp] Back   [Q] Advance   [Esc] Options",
            "browser_rel_search": "Type search   [Enter] Confirm   [Esc] Cancel   [Q] Advance",
            "actions": "[↑↓] Move   [←→] Focus   [Enter] Select   [Bsp] Back   [Q] Advance   [Esc] Options",
            "history_search": "Type year [0-9]   [Enter] Continue   [Esc] Cancel   [Q] Advance",
            "lineage_search": "Type search   [Enter] Continue   [Esc] Cancel   [Q] Advance",
            "skip_time": "[↑↓] Move   [0-9] Custom   [Bksp] Erase   [Enter] Continue   [Bsp] Back   [Esc] Options",
            "death_ack": "[Enter] Continue   [Esc] Options",
            "continuation_detail": "[Enter] Continue   [Bsp] Back   [Esc] Options",
        }
        if self.screen_name == "lineage" and self.lineage_search_active:
            footer_text = footer_hints["lineage_search"]
        elif self.screen_name == "history" and self.history_search_active:
            footer_text = footer_hints["history_search"]
        elif self.screen_name == "browser" and self.browser_tab == "relationships" and self.rel_browser_search_active:
            footer_text = footer_hints["browser_rel_search"]
        elif self.screen_name == "browser" and self.browser_tab == "history" and self.history_search_active:
            footer_text = footer_hints["history_search"]
        elif self.screen_name == "continuation":
            continuity_state = self.get_continuity_state()
            if continuity_state["continuity_candidates"]:
                footer_text = "[↑↓] Move   [Enter] Continue   [Bsp] Back   [Esc] Options"
            else:
                footer_text = "[Bsp] Back   [Esc] Options"
        else:
            footer_text = footer_hints.get(self.screen_name, "")
        content_left, content_width = get_content_bounds(width, max_width=108, min_margin=1)
        full_hline = "═" * max(0, width - 1)
        stdscr.addnstr(height - 2, 0, full_hline, width - 1, curses.A_BOLD)
        stdscr.addnstr(
            height - 1,
            content_left,
            center_text(footer_text, content_width),
            content_width,
            curses.A_NORMAL,
        )

    def build_choice_popup_lines(self, choice):
        lines = [choice["text"], "", choice["question"], ""]
        option_line_indexes = []
        for index, option in enumerate(choice["options"]):
            option_line_indexes.append(len(lines))
            lines.append(f"{option}")
        lines.extend(
            [
                "",
                (
                    "[↑↓] Move   [Enter] Select   [Bsp] Skip"
                    if choice.get("skippable")
                    else "[↑↓] Move   [Enter] Select"
                ),
            ]
        )
        return lines, option_line_indexes

    def render_pending_choice(self, stdscr, height, width):
        if self.pending_choice is None:
            return

        box_width = min(max(40, width // 2), 50)
        inner_width = max(1, box_width - 2)
        popup_lines, option_line_indexes = self.build_choice_popup_lines(self.pending_choice)
        rendered_line_count = sum(len(wrap_text_line(line, inner_width)) for line in popup_lines)
        box_height = min(height - 4, max(9, rendered_line_count + 2))
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)

        draw_box(stdscr, top, left, box_height, box_width, title=self.pending_choice["title"])
        highlighted_line = option_line_indexes[self.pending_choice["selected_index"]]
        draw_panel_text(
            stdscr,
            top,
            left,
            box_height,
            box_width,
            popup_lines,
            highlight_index=highlighted_line,
        )

    def render_menu_popup(self, stdscr, height, width):
        MENU_ITEMS = ["Browser", "Actions", "Profile"]
        box_width = 32
        box_height = len(MENU_ITEMS) + 6
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        draw_box(stdscr, top, left, box_height, box_width, title="Menu")
        for i, item in enumerate(MENU_ITEMS):
            label = f"  {i+1}. {item}"
            attr = curses.A_REVERSE if i == self.menu_selection else curses.A_NORMAL
            row = top + 2 + i
            if row < height and left + 1 < width:
                stdscr.addnstr(row, left + 1, label.ljust(box_width - 2), box_width - 2, attr)
        hint_row = top + 2 + len(MENU_ITEMS) + 1
        hint = " [↑↓]  [Enter] Select  [Bsp] Back"
        if hint_row < height and left + 1 < width:
            stdscr.addnstr(hint_row, left + 1, hint.ljust(box_width - 2), box_width - 2)

    def render_options_popup(self, stdscr, height, width):
        OPTION_ITEMS = ["Quit Game", "Help / Controls", "Settings"]
        box_width = 36
        box_height = len(OPTION_ITEMS) + 6
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        draw_box(stdscr, top, left, box_height, box_width, title="Options")
        for i, item in enumerate(OPTION_ITEMS):
            prefix = "  "
            attr = curses.A_REVERSE if i == self.options_selection else curses.A_NORMAL
            if i > 0:
                attr |= curses.A_DIM
            label = f"{prefix}{item}"
            row = top + 2 + i
            if row < height and left + 1 < width:
                stdscr.addnstr(row, left + 1, label.ljust(box_width - 2), box_width - 2, attr)
        hint_row = top + 2 + len(OPTION_ITEMS) + 1
        hint = " [↑↓]  [Enter] Select  [Esc] Close"
        if hint_row < height and left + 1 < width:
            stdscr.addnstr(hint_row, left + 1, hint.ljust(box_width - 2), box_width - 2)

    def render_quit_confirmation(self, stdscr, height, width):
        box_width = min(max(36, width // 2), 44)
        box_height = 7
        top = max(2, (height - box_height) // 2)
        left = max(0, (width - box_width) // 2)
        lines = [
            "Are you sure you want to quit?",
            "",
            "[Enter] Quit   [Bsp] Back",
        ]
        draw_box(stdscr, top, left, box_height, box_width, title="Quit")
        draw_panel_text(stdscr, top, left, box_height, box_width, lines)

    def render_header(self, stdscr, width):
        focused_actor = self.get_focused_actor()
        focused_actor_name = focused_actor.get_full_name() if focused_actor is not None else "Unknown"
        chrome = build_screen_chrome(self.screen_name, self.world, focused_actor_name)
        full_hline = "═" * max(0, width - 1)
        divider = "║"

        LOGO = [
            r"           __               ",
            r" ___ _____/ /____  _______ _",
            r"/ _ `/ __/ __/ _ \/ __/ _ `/",
            r"\_,_/\__/\__/\___/_/  \_,_/ ",
        ]
        logo_w = max(len(l) for l in LOGO) + 4  # padding each side

        # Left panel content
        try:
            snapshot = self.get_snapshot_data()
            loc = snapshot.get("location", {})
            stats = snapshot.get("statistics", {})
            city = loc.get("current_place_name", "")
            country = loc.get("jurisdiction_place_name", "")
            loc_str = f"{city}, {country}" if city and country else city or country or ""
            health = stats.get("health", 0)
            money = stats.get("money", 0)
            money_str = f"${money:,.0f}" if isinstance(money, (int, float)) else str(money)
        except Exception:
            loc_str = health = money_str = ""

        left_lines = [
            chrome["date_text"],
            chrome["subtitle"],
            chrome["title"],
            "",
        ]
        right_lines = [
            loc_str,
            f"Health: {health}",
            money_str,
            "",
        ]

        panel_w = max(1, (width - logo_w - 4) // 2)

        # Row 0: top separator
        stdscr.addnstr(0, 0, full_hline, width - 1, curses.A_BOLD)

        # Rows 1-4: logo + left/right panels
        for i in range(4):
            logo_line = LOGO[i] if i < len(LOGO) else ""
            logo_padded = f"  {logo_line:<{logo_w - 2}}"
            left_text = f"{left_lines[i]:>{panel_w - 1}} " if i < len(left_lines) else " " * panel_w
            right_text = f" {right_lines[i]:<{panel_w - 1}}" if i < len(right_lines) else " " * panel_w
            row_text = f"{left_text}{divider}{logo_padded}{divider}{right_text}"
            try:
                stdscr.addnstr(i + 1, 0, row_text[:width - 1], width - 1)
            except curses.error:
                pass

        # Row 5: bottom separator (becomes body boundary)
        stdscr.addnstr(5, 0, full_hline, width - 1, curses.A_BOLD)
        # State line handled inside render_header logo layout
        pass  # state line folded into logo header

    def render_main(self, stdscr, height, width):
        snapshot_data = self.get_snapshot_data()
        snapshot_sections = build_snapshot_sections(snapshot_data)
        top = 6
        body_height = height - 8
        self._main_body_height = body_height
        content_left, content_width = get_content_bounds(width, max_width=112)
        left_width, right_left, right_width = split_centered_columns(content_left, content_width, left_ratio=0.5)
        divider_x = right_left - 2

        left_sections = [
            section
            for section in snapshot_sections
            if section["key"] in MAIN_LEFT_SECTION_KEYS
        ]
        left_lines = [self.last_message, ""]
        left_lines.extend(self.build_main_left_lines(left_sections, include_time=False))
        visible_left_lines, self.main_left_scroll, main_left_max_offset, total_left_lines = get_scroll_window(
            left_lines,
            body_height,
            self.main_left_scroll,
        )
        right_lines = expand_render_lines(build_live_feed_lines(self.event_log), right_width)
        visible_right_lines, _, _, _ = get_scroll_window(
            right_lines,
            body_height,
            max(0, len(right_lines) - body_height),
        )

        draw_text_block(stdscr, top, content_left, left_width, body_height, visible_left_lines)
        draw_vertical_divider(stdscr, top, divider_x, body_height)
        draw_text_block(stdscr, top, right_left, right_width, body_height, visible_right_lines)

        if main_left_max_offset > 0:
            scroll_label = f"More details: {self.main_left_scroll + 1}-{self.main_left_scroll + len(visible_left_lines)} / {total_left_lines}"
            stdscr.addnstr(
                min(height - 3, top + body_height - 1),
                content_left,
                truncate_for_width(scroll_label, left_width),
                left_width,
                curses.A_DIM,
            )

    def render_profile(self, stdscr, height, width):
        top = 6
        body_height = height - 8
        self._profile_body_height = body_height
        content_left, content_width = get_content_bounds(width, max_width=88)
        profile_lines = expand_render_lines(self.build_profile_lines(self.get_snapshot_data()), content_width)
        content_body_height = body_height
        if len(profile_lines) > body_height:
            content_body_height = max(1, body_height - 1)
        visible_lines, self.profile_scroll, _, total_lines = get_scroll_window(
            profile_lines,
            content_body_height,
            self.profile_scroll,
        )
        draw_text_block(stdscr, top, content_left, content_width, content_body_height, visible_lines)

        if total_lines > content_body_height:
            scroll_label = (
                f"Profile: {self.profile_scroll + 1}-"
                f"{self.profile_scroll + len(visible_lines)} / {total_lines}"
            )
            stdscr.addnstr(
                min(height - 3, top + content_body_height),
                content_left,
                truncate_for_width(scroll_label, content_width),
                content_width,
                curses.A_DIM,
            )

    def render_lineage(self, stdscr, height, width):
        browser_state = self.get_lineage_browser_state()
        lineage_entries = browser_state["entries"]
        selected_detail = browser_state["selected_detail"]

        top = 9
        body_height = height - 11
        content_left, content_width = get_content_bounds(width, max_width=112)
        left_width, right_left, right_width = split_centered_columns(content_left, content_width)
        filter_label = LINEAGE_FILTER_LABELS[browser_state["filter_mode"]]
        left_lines = [
            f"Archive • {filter_label} • {browser_state['result_count']} result(s)",
            self.get_lineage_search_status(),
            "",
        ]
        highlight_index = None
        if not lineage_entries:
            left_lines.append("No lineage entries match the current filter/search.")
        else:
            for index, entry in enumerate(lineage_entries):
                if index == self.lineage_selection:
                    highlight_index = len(left_lines)
                left_lines.append(build_lineage_row(entry))

        draw_truncated_block(
            stdscr,
            top,
            content_left,
            left_width,
            body_height,
            left_lines,
            highlight_index=highlight_index,
        )

        divider_x = right_left - 2
        draw_vertical_divider(stdscr, top, divider_x, body_height)

        if selected_detail is None:
            right_lines = [
                center_text("SELECTED PERSON", right_width),
                "",
                "No lineage detail available.",
                "",
                "Try another filter or search.",
            ]
        else:
            summary = selected_detail["summary"]
            records = selected_detail["records"]
            right_lines = []
            right_lines.append(center_text("SELECTED PERSON", right_width))
            right_lines.append("")
            right_lines.extend(build_person_card_lines(summary))
            right_lines.extend(
                [
                    "",
                    "Identity",
                    f"Species: {summary['species']}",
                    f"Sex: {summary['sex']}",
                    f"Gender: {summary['gender']}",
                    f"Condition: Health {summary['health']}   Happiness {summary['happiness']}   Intelligence {summary['intelligence']}",
                    f"Resources: ${summary['money']}",
                    "",
                    "Recent Records",
                ]
            )
            right_lines.extend(build_record_summary_lines(records))

        draw_text_block(stdscr, top, right_left, right_width, body_height, right_lines)

    def render_relationship_browser(self, stdscr, height, width):
        browser_state = self.get_relationship_browser_state()
        entries = browser_state["entries"]
        selected_detail = browser_state["selected_detail"]

        top = 9
        body_height = height - 11
        content_left, content_width = get_content_bounds(width, max_width=120)

        filter_col_width = 12
        gap = 2
        remaining_width = content_width - filter_col_width - gap
        actor_col_width = remaining_width * 5 // 10
        detail_left = content_left + filter_col_width + gap + actor_col_width + gap
        detail_width = max(20, content_width - filter_col_width - gap - actor_col_width - gap)
        actor_left = content_left + filter_col_width + gap

        filter_lines = []
        filter_highlight = None
        for idx, fkey in enumerate(REL_FILTER_OPTIONS):
            if idx == self.rel_filter_index:
                filter_highlight = len(filter_lines)
            marker = ">" if self.rel_browser_focus == "filters" and idx == self.rel_filter_index else " "
            filter_lines.append(f"{marker} {REL_FILTER_LABELS[fkey]}")

        draw_truncated_block(
            stdscr, top, content_left, filter_col_width, body_height, filter_lines,
            highlight_index=filter_highlight,
        )

        divider1_x = content_left + filter_col_width + 1
        draw_vertical_divider(stdscr, top, divider1_x, body_height)

        actor_lines = []
        actor_highlight = None
        search_status = self.get_rel_browser_search_status()
        if search_status:
            actor_lines.append(search_status)
            actor_lines.append("")
        if not entries:
            actor_lines.append("No entries.")
        else:
            search_offset = len(actor_lines)
            for index, entry in enumerate(entries):
                if index == self.lineage_selection and self.rel_browser_focus == "actors":
                    actor_highlight = search_offset + index
                actor_lines.append(build_lineage_row(entry))

        draw_truncated_block(
            stdscr, top, actor_left, actor_col_width, body_height, actor_lines,
            highlight_index=actor_highlight,
        )

        divider2_x = detail_left - 1
        draw_vertical_divider(stdscr, top, divider2_x, body_height)

        if selected_detail is None:
            right_lines = [
                center_text("SELECTED PERSON", detail_width),
                "",
                "No detail available.",
            ]
        else:
            summary = selected_detail["summary"]
            records = selected_detail["records"]
            right_lines = []
            right_lines.append(center_text("SELECTED PERSON", detail_width))
            right_lines.append("")
            right_lines.extend(build_person_card_lines(summary))
            link_type = summary.get("link_type", "family")
            if link_type == "social":
                closeness = summary.get("closeness", 0)
                social_status = summary.get("social_status", "active")
                right_lines.extend([
                    "",
                    f"Social: {summary['relationship_label']}",
                    f"Closeness: {closeness}   Status: {'past' if social_status == 'former' else social_status}",
                ])
            else:
                right_lines.extend([
                    "",
                    "Identity",
                    f"Species: {summary['species']}",
                    f"Sex: {summary['sex']}",
                    f"Condition: Health {summary['health']}   Happiness {summary['happiness']}",
                ])
            right_lines.extend(["", "Recent Records"])
            right_lines.extend(build_record_summary_lines(records))

        draw_text_block(stdscr, top, detail_left, detail_width, body_height, right_lines)

    def render_history(self, stdscr, height, width):
        top = 8
        body_height = height - 10
        self._history_body_height = body_height
        content_left, content_width = get_content_bounds(width, max_width=104)
        self._history_content_width = content_width
        history_lines = expand_render_lines(self.get_history_lines(content_width), content_width)
        search_status = self.get_history_search_status()
        if search_status:
            history_lines = [search_status, ""] + history_lines
        content_body_height = body_height
        if len(history_lines) > body_height:
            content_body_height = max(1, body_height - 1)
        visible_lines, self.history_scroll, _, total_lines = get_scroll_window(
            history_lines,
            content_body_height,
            self.history_scroll,
        )
        draw_text_block(stdscr, top, content_left, content_width, content_body_height, visible_lines)

        if total_lines > content_body_height:
            scroll_label = (
                f"History: {self.history_scroll + 1}-"
                f"{self.history_scroll + len(visible_lines)} / {total_lines}"
            )
            stdscr.addnstr(
                min(height - 3, top + content_body_height),
                content_left,
                truncate_for_width(scroll_label, content_width),
                content_width,
                curses.A_DIM,
            )

    def render_browser(self, stdscr, height, width):
        """Renders the unified Browser screen with Relationships and History tabs."""
        content_left, content_width = get_content_bounds(width, max_width=120, min_margin=1)

        # Tab bar on row 5 with a separating bottom rule (header now occupies rows 0-4)
        rel_label = "[ Relationships ]" if self.browser_tab == "relationships" else "  Relationships  "
        hist_label = "[ History ]" if self.browser_tab == "history" else "  History  "
        tab_bar = f"{rel_label}     │     {hist_label}"
        try:
            stdscr.addnstr(6, content_left, center_text(tab_bar, content_width), content_width)
            hline_char = getattr(curses, "ACS_HLINE", ord("-"))
            stdscr.hline(7, content_left, hline_char, content_width)
        except curses.error:
            pass

        if self.browser_tab == "relationships":
            self.render_relationship_browser(stdscr, height, width)
        else:
            self.render_history(stdscr, height, width)

    def render_actions(self, stdscr, height, width):
        """Renders the Actions screen: Categories | Actions | Details."""
        top = 6
        body_height = height - 8
        content_left, content_width = get_content_bounds(width, max_width=120)
        col_w = content_width // 3
        cat_left = content_left
        act_left = content_left + col_w + 1
        det_left = content_left + col_w * 2 + 2
        det_width = content_width - col_w * 2 - 2

        categories = self.get_actions_categories()
        cat_idx = self.actions_category_index
        act_idx = self.actions_action_index
        current_cat = categories[cat_idx] if categories else None
        actions = current_cat["actions"] if current_cat else []
        current_action = actions[act_idx] if actions and act_idx < len(actions) else None

        # Categories column
        for i, cat in enumerate(categories):
            label = f" {cat['label']}"
            attr = curses.A_REVERSE if (i == cat_idx and self.actions_focus == "categories") else curses.A_NORMAL
            if i == cat_idx and self.actions_focus != "categories":
                attr = curses.A_BOLD
            row = top + 1 + i
            if row < height:
                stdscr.addnstr(row, cat_left, label.ljust(col_w - 1), col_w - 1, attr)
        if not categories:
            stdscr.addnstr(top + 1, cat_left, " (none)", col_w - 1, curses.A_DIM)

        # Divider 1
        draw_vertical_divider(stdscr, top, act_left - 1, body_height)

        # Actions column — available actions + queued section
        avail_rows = max(1, body_height // 2 - 2)
        if not actions:
            stdscr.addnstr(top + 1, act_left, " (none yet)", col_w - 1, curses.A_DIM)
        else:
            for i, action in enumerate(actions):
                if i >= avail_rows:
                    break
                label = f" {action['label']}"
                attr = curses.A_REVERSE if (i == act_idx and self.actions_focus == "actions") else curses.A_NORMAL
                row = top + 1 + i
                if row < height:
                    stdscr.addnstr(row, act_left, label.ljust(col_w - 1), col_w - 1, attr)

        # Queued section divider + list
        queue_top = top + avail_rows + 2
        if queue_top < height - 2:
            try:
                stdscr.hline(queue_top - 1, act_left, getattr(curses, "ACS_HLINE", ord("-")), col_w - 1)
            except curses.error:
                pass
            stdscr.addnstr(queue_top, act_left, " Queued", col_w - 1, curses.A_BOLD)
            if self.active_actions:
                for i, queued in enumerate(self.active_actions):
                    row = queue_top + 1 + i
                    if row >= height - 1:
                        break
                    stdscr.addnstr(row, act_left, f"  {queued['label']}", col_w - 1)
            else:
                if queue_top + 1 < height - 1:
                    stdscr.addnstr(queue_top + 1, act_left, " (nothing queued)", col_w - 1, curses.A_DIM)

        # Divider 2
        draw_vertical_divider(stdscr, top, det_left - 1, body_height)

        # Details column
        focused_actor = self.world.get_focused_actor()
        free_hours = int(get_monthly_free_hours(focused_actor))
        queued_hours = int(sum(a.get("time_cost", 0) for a in self.active_actions))
        remaining_hours = free_hours - queued_hours
        if current_action:
            det_lines = [f" {current_action['label']}", ""]
            if current_action["id"] == "hang_out":
                links = current_action.get("links", [])
                if links:
                    det_lines.append(" Who you can hang out with:")
                    det_lines.append("")
                    for lnk in links:
                        target_id = lnk.get("target_id")
                        target_actor = self.world.get_actor(target_id)
                        if target_actor is None:
                            continue
                        meta = lnk.get("metadata", {})
                        closeness = meta.get("closeness", 0)
                        tier = _get_social_tier_label(closeness)
                        det_lines.append(f"  {target_actor.get_full_name()} · {tier}")
                else:
                    det_lines.append(" No active social connections yet.")
            elif current_action["id"] in ("exercise", "read", "rest"):
                det_lines.append(" Ways to spend your time:")
                det_lines.append("")
                for subtype in current_action.get("subtypes", []):
                    effects_text = format_stat_change_summary(subtype.get("stat_changes", {}))
                    det_lines.append(f"  {subtype['label']} - {subtype['time_cost']}h - {effects_text}")
            next_y = draw_text_block(stdscr, top, det_left, det_width, body_height, det_lines)
            if next_y < top + body_height:
                next_y = draw_text_block(stdscr, next_y, det_left, det_width, body_height - (next_y - top), [""])
            budget_lines = [
                (" Time Budget", curses.A_BOLD),
                (f"  {free_hours}h free", curses.A_DIM),
                (f"  {queued_hours}h queued", curses.A_DIM),
                (f"  {remaining_hours}h left", curses.A_DIM),
            ]
            y = next_y
            for raw_line, attr in budget_lines:
                for wrapped_line in wrap_text_line(raw_line, det_width):
                    if y >= top + body_height:
                        break
                    stdscr.addnstr(y, det_left, wrapped_line, det_width, attr)
                    y += 1
        else:
            stdscr.addnstr(top + 1, det_left, " Select an action", det_width, curses.A_DIM)
            budget_lines = [
                (" Time Budget", curses.A_BOLD),
                (f"  {free_hours}h free", curses.A_DIM),
                (f"  {queued_hours}h queued", curses.A_DIM),
                (f"  {remaining_hours}h left", curses.A_DIM),
            ]
            y = top + 3
            for raw_line, attr in budget_lines:
                for wrapped_line in wrap_text_line(raw_line, det_width):
                    if y >= top + body_height:
                        break
                    stdscr.addnstr(y, det_left, wrapped_line, det_width, attr)
                    y += 1

    def build_actor_inspect_detail(self, actor_id, *, relationship_label=None, recent_record_limit=INSPECT_RECORD_LIMIT):
        """Builds one shell-owned inspectability payload for an actor."""
        actor = self.world.get_actor(actor_id)
        if actor is None:
            return None

        lifecycle_year = self.world.current_year
        lifecycle_month = self.world.current_month
        if not actor.is_alive() and actor.death_year is not None and actor.death_month is not None:
            lifecycle_year = actor.death_year
            lifecycle_month = actor.death_month

        lifecycle = actor.get_lifecycle_state(lifecycle_year, lifecycle_month)
        actor_records = self.world.get_actor_records(actor_id)
        recent_records = list(reversed(filter_player_facing_records(actor_records)))[:recent_record_limit]
        return {
            "full_name": actor.get_full_name(),
            "relationship_label": relationship_label or "Connected",
            "age": lifecycle["age_years"],
            "life_stage": lifecycle["life_stage"],
            "current_place_name": self.world.get_place_name(actor.current_place_id) or "Unknown",
            "health": actor.stats["health"],
            "happiness": actor.stats["happiness"],
            "intelligence": actor.stats["intelligence"],
            "money": actor.money,
            "records": recent_records,
        }

    def render_skip_time(self, stdscr, height, width):
        custom_months = self.get_custom_skip_months()
        selected_months = self.get_selected_skip_months()
        content_left, content_width = get_content_bounds(width, max_width=76)
        lines = [
            center_text("TIME JUMP", content_width),
            "",
            self.last_message,
            "",
            "Presets",
        ]
        highlight_index = 5 + self.skip_selection
        for preset_months in SKIP_MONTH_PRESETS:
            label = "month" if preset_months == 1 else "months"
            lines.append(f"{preset_months:>2} {label}")
        lines.extend(
            [
                "",
                "Custom Months",
                (
                    f"Typed value: {self.skip_custom_value} months"
                    if self.skip_custom_value
                    else "Typed value: none"
                ),
                (
                    f"Enter will advance {custom_months} months from the custom value."
                    if custom_months is not None
                    else f"Enter will advance {selected_months} months from the selected preset."
                ),
            ]
        )
        draw_text_block(stdscr, 5, content_left, content_width, height - 7, lines, highlight_index=highlight_index)

    def render_death_ack(self, stdscr, height, width):
        continuity_state = self.get_continuity_state()
        content_left, content_width = get_content_bounds(width, max_width=74)
        death_detail = self.build_actor_inspect_detail(
            self.get_focused_actor_id(),
            relationship_label="Self",
        )
        lines = [
            "",
            center_text("DEATH", content_width),
            "",
        ]
        lines.extend(build_death_lines(continuity_state))
        if death_detail is not None:
            lines.extend(
                [
                    "",
                    "Life Summary",
                    f"Age at death: {death_detail['age']}",
                    f"Place at death: {death_detail['current_place_name']}",
                    (
                        "At death: "
                        f"Health {death_detail['health']}   Happiness {death_detail['happiness']}   "
                        f"Intelligence {death_detail['intelligence']}   Money ${death_detail['money']}"
                    ),
                    "",
                    "Recent Records",
                ]
            )
            lines.extend(build_record_summary_lines(death_detail["records"]))
        lines.extend(
            [
                "",
                center_text("Press Enter to continue.", content_width),
            ]
        )
        draw_text_block(
            stdscr,
            5,
            content_left,
            content_width,
            height - 7,
            lines,
        )

    def render_continuation(self, stdscr, height, width):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        content_left, content_width = get_content_bounds(width, max_width=96)
        lines = [
            "",
        ]
        highlight_index = None

        if not candidates:
            lines.append("No living family members were found.")
        else:
            self.continuation_selection = max(
                0,
                min(self.continuation_selection, len(candidates) - 1),
            )
            for index, candidate in enumerate(candidates):
                line = (
                    f"{candidate['full_name']} · {candidate['relationship_label']} · "
                    f"Age {candidate['age']} · {candidate.get('current_place_name') or 'Unknown'}"
                )
                if index == self.continuation_selection:
                    highlight_index = len(lines)
                lines.append(line)

        draw_text_block(stdscr, 5, content_left, content_width, height - 7, lines, highlight_index=highlight_index)

    def render_continuation_detail(self, stdscr, height, width):
        continuity_state = self.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        selected_candidate = next(
            (
                candidate
                for candidate in candidates
                if candidate["actor_id"] == self.selected_continuation_actor_id
            ),
            None,
        )
        if selected_candidate is None:
            self.screen_name = "continuation"
            self.last_message = "This person is no longer available."
            self.render_continuation(stdscr, height, width)
            return

        detail = self.build_actor_inspect_detail(
            selected_candidate["actor_id"],
            relationship_label=selected_candidate["relationship_label"],
        )
        if detail is None:
            content_left, content_width = get_content_bounds(width, max_width=86)
            render_lines(stdscr, ["Actor data unavailable."], 0, content_left, height, width)
            return
        content_left, content_width = get_content_bounds(width, max_width=86)
        lines = [
            center_text("CONTINUATION DETAIL", content_width),
            "",
            detail["full_name"],
            (
                f"{detail['relationship_label']}   Age {detail['age']}   "
                f"Location: {detail['current_place_name']}"
            ),
            (
                f"Health {detail['health']}   Happiness {detail['happiness']}   "
                f"Intelligence {detail['intelligence']}   Money ${detail['money']}"
            ),
            "",
            "Recent Records",
        ]
        lines.extend(build_record_summary_lines(detail["records"]))
        draw_text_block(stdscr, 5, content_left, content_width, height - 7, lines)

    def render(self, stdscr):
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        if height < 16 or width < 50:
            stdscr.addnstr(0, 0, "Terminal too small for Actora TUI. Resize and try again.", width - 1)
            return

        self.render_header(stdscr, width)
        if self.screen_name == "main":
            self.render_main(stdscr, height, width)
        elif self.screen_name == "profile":
            self.render_profile(stdscr, height, width)
        elif self.screen_name == "lineage":
            self.render_lineage(stdscr, height, width)
        elif self.screen_name == "relationship_browser":
            self.render_relationship_browser(stdscr, height, width)
        elif self.screen_name == "history":
            self.render_history(stdscr, height, width)
        elif self.screen_name == "browser":
            self.render_browser(stdscr, height, width)
        elif self.screen_name == "actions":
            self.render_actions(stdscr, height, width)
        elif self.screen_name == "skip_time":
            self.render_skip_time(stdscr, height, width)
        elif self.screen_name == "death_ack":
            self.render_death_ack(stdscr, height, width)
        elif self.screen_name == "continuation":
            self.render_continuation(stdscr, height, width)
        elif self.screen_name == "continuation_detail":
            self.render_continuation_detail(stdscr, height, width)

        self.render_footer(stdscr, height, width)
        self.render_pending_choice(stdscr, height, width)
        if self.menu_popup_active:
            self.render_menu_popup(stdscr, height, width)
        if self.options_popup_active:
            self.render_options_popup(stdscr, height, width)
        stdscr.refresh()

    def run(self, stdscr):
        """Runs the narrow curses shell until the user quits or the run ends."""
        curses.set_escdelay(25)
        curses.curs_set(0)
        stdscr.keypad(True)

        while self.running:
            self.sync_focus_state()
            self.render(stdscr)
            if self.quit_confirmation_active:
                self.render_quit_confirmation(stdscr, *stdscr.getmaxyx())
                stdscr.refresh()
            key = stdscr.getch()
            self.handle_key(key)


def setup_initial_world_from_character(character_data):
    """Initializes the startup world from one fully prepared character payload."""
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

    startup_jurisdiction_place_id = character_data.get("country_id") or DEFAULT_COUNTRY_ID
    startup_place_id = character_data.get("city_id") or DEFAULT_CITY_ID
    startup_country = WORLD_GEOGRAPHY_BY_COUNTRY_ID.get(startup_jurisdiction_place_id)
    if startup_country is None:
        raise ValueError(f"Unknown startup country_id '{startup_jurisdiction_place_id}'")
    if startup_place_id not in {city["city_id"] for city in startup_country["cities"]}:
        raise ValueError(
            f"Unknown or mismatched startup city_id '{startup_place_id}' for country_id '{startup_jurisdiction_place_id}'"
        )

    mother_identity_context = prepare_parent_identity_context(
        role="mother",
        player_last_name=character_data["last_name"],
        place_id=startup_place_id,
        world=world,
        culture_group=startup_country["metadata"]["culture_group"],
    )
    family_last_name = mother_identity_context["family_last_name"]
    father_identity_context = prepare_parent_identity_context(
        role="father",
        family_last_name=family_last_name,
        player_last_name=character_data["last_name"],
        place_id=startup_place_id,
        world=world,
        culture_group=startup_country["metadata"]["culture_group"],
    )

    mother_identity = generate_parent_identity_from_context(mother_identity_context)
    father_identity = generate_parent_identity_from_context(father_identity_context)

    mother_id = generate_startup_actor_id("mother")
    father_id = generate_startup_actor_id("father")
    mother_age_years = random.randint(22, 36)
    father_age_years = max(mother_age_years + random.randint(1, 5), 24)
    world.create_human_actor(
        actor_id=mother_id,
        species="Human",
        first_name=mother_identity["first_name"],
        last_name=mother_identity["last_name"],
        sex=mother_identity["sex"],
        gender=mother_identity["gender"],
        birth_year=world.current_year - mother_age_years,
        birth_month=random.randint(1, 12),
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=True,
    )
    world.create_human_actor(
        actor_id=father_id,
        species="Human",
        first_name=father_identity["first_name"],
        last_name=father_identity["last_name"],
        sex=father_identity["sex"],
        gender=father_identity["gender"],
        birth_year=world.current_year - father_age_years,
        birth_month=random.randint(1, 12),
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
        jurisdiction_place_id=startup_jurisdiction_place_id,
        randomize_stats=True,
    )
    world.add_link_pair(
        source_id=mother_id,
        target_id=father_id,
        forward_type="association",
        forward_role="coparent",
        reverse_type="association",
        reverse_role="coparent",
        forward_metadata={"bootstrap_source": "startup_coparent_association"},
        reverse_metadata={"bootstrap_source": "startup_coparent_association"},
    )

    world.bootstrap_older_siblings_for_newborn(
        mother_id=mother_id,
        father_id=father_id,
        player_birth_year=world.current_year,
        player_birth_month=1,
    )

    player_id = generate_startup_actor_id("player")
    player = world.create_human_child_with_parents(
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
    )
    player.stats = normalize_creation_stats(character_data["stats"])
    player.appearance = dict(character_data["appearance"])
    player.traits = list(character_data["traits"])
    player.money = 0
    world.set_focused_actor(player_id)

    return world, player_id


def setup_initial_world(player_first_name, player_last_name, player_sex, player_gender):
    """Compatibility wrapper that delegates to character-data startup flow."""
    default_character_data = {
        "first_name": player_first_name,
        "last_name": player_last_name,
        "sex": player_sex,
        "gender": player_gender,
        "country_id": DEFAULT_COUNTRY_ID,
        "city_id": DEFAULT_CITY_ID,
        "appearance": {
            "eye_color": "Brown",
            "hair_color": "Black",
            "skin_tone": "Medium",
        },
        "traits": [],
        "stats": build_randomized_starting_stats(),
    }
    return setup_initial_world_from_character(default_character_data)


def run_creation_wizard():
    """Runs the curses-based character creation wizard and returns character data or None."""
    def _run(stdscr):
        wizard = CreationWizard(stdscr)
        return wizard.run()

    try:
        return curses.wrapper(_run)
    except KeyboardInterrupt:
        return None



def run_game_tui(world, player_id):
    """Runs the actor-first curses TUI for ordinary play after startup creation completes."""
    tui = ActoraTUI(world, player_id)
    try:
        curses.wrapper(tui.run)
    except KeyboardInterrupt:
        pass


def start_game():
    """Runs character creation and the ordinary-play TUI."""
    character_data = run_creation_wizard()
    if character_data is None:
        return

    world, player_id = setup_initial_world_from_character(character_data)
    run_game_tui(world, player_id)


if __name__ == "__main__":
    start_game()
