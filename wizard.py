import curses
import random

from human import Human
from ui import (
    build_centered_rule,
    center_text,
    draw_box,
    draw_panel_text,
    draw_text_block,
    draw_vertical_divider,
    get_content_bounds,
    split_centered_columns,
)
from world import (
    DEFAULT_CITY_ID,
    DEFAULT_COUNTRY_ID,
    WORLD_GEOGRAPHY,
    WORLD_GEOGRAPHY_BY_COUNTRY_ID,
)


CREATION_SEX_OPTIONS = ["Male", "Female", "Intersex"]
CREATION_EYE_COLOR_OPTIONS = ["Brown", "Blue", "Green", "Hazel", "Gray", "Amber", "Other"]
CREATION_HAIR_COLOR_OPTIONS = ["Black", "Brown", "Blonde", "Red", "Auburn", "Other"]
CREATION_SKIN_TONE_OPTIONS = ["Light", "Fair", "Medium", "Olive", "Tan", "Brown", "Dark", "Other"]
CREATION_TRAIT_POOL = ["Driven", "Chill", "Curious", "Social", "Disciplined", "Impulsive", "Empathetic", "Resilient", "Introverted", "Extraverted", "Restless", "Ambitious"]
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
    "wisdom",
    "discipline",
    "willpower",
    "looks",
    "fertility",
    "memory",
    "stress",
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


def build_randomized_starting_stats():
    """Builds one startup stat block using the same Human randomization ranges."""
    actor = Human("Human", "Temp", "", "Female", "Female", 1, 1)
    actor.randomize_starting_statistics()
    return normalize_creation_stats(actor.stats)


def format_stat_change_summary(stat_changes):
    parts = []
    for stat_name, amount in stat_changes.items():
        label = CREATION_STAT_LABELS.get(stat_name, stat_name.replace("_", " ").title())
        sign = "+" if amount > 0 else "-"
        parts.append(f"{sign}{label}")
    return " ".join(parts)


class CreationWizard:
    """Curses-driven startup flow for building one player character payload."""
    CREATION_MODES = ["questionnaire", "manual"]

    def __init__(self, stdscr, back_keys=(curses.KEY_BACKSPACE, 127, 8)):
        self.stdscr = stdscr
        self.back_keys = back_keys
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
        stats["stress"] = 0
        stats["memory"] = 0
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
            if count > 0:
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
                lines.append(f"{field['label']}{optional_suffix}: ← {value} →")
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
                    lines.append(f"{field['label']}: ← {value} →")
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
            if stat_name in ("memory", "stress") and (index == 0 or CREATION_STAT_ORDER[index - 1] not in ("memory", "stress")):
                left_lines.append("")
            if index == self.stat_index:
                highlight_index = len(left_lines)
                left_lines.append(f"{CREATION_STAT_LABELS[stat_name]}: ← {self.data['stats'][stat_name]} →")
            else:
                left_lines.append(f"{CREATION_STAT_LABELS[stat_name]}: {self.data['stats'][stat_name]:>3}")

        right_lines = [
            "Controls",
            "",
            "Adjust any stat from 0 to 100.",
            "Memory and Stress: -50 to +50.",
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
            lines.append(option["text"])
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
            if key in self.back_keys:
                self.quit_confirmation_active = False
                return True
            if key in (curses.KEY_ENTER, 10, 13):
                self.running = False
                self.cancelled = True
                return True
            return True
        return False

    def handle_identity_key(self, key):
        if key == 27:
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
            if key in self.back_keys:
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
        if key in self.back_keys:
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
        if current_field["kind"] != "text":
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                self.appearance_field_index = max(0, self.appearance_field_index - 1)
                return
            if key in (curses.KEY_DOWN, ord("s"), ord("S")):
                self.appearance_field_index = min(len(fields) - 1, self.appearance_field_index + 1)
                return
        else:
            if key in (curses.KEY_UP, curses.KEY_DOWN):
                self.appearance_field_index = max(0, self.appearance_field_index - 1) if key == curses.KEY_UP else min(len(fields) - 1, self.appearance_field_index + 1)
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
                if self.data["appearance"][current_field["key"]] == "Other":
                    next_index = self.appearance_field_index + 1
                    if next_index < len(fields) and fields[next_index]["kind"] == "text":
                        self.appearance_field_index = next_index
                        return
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
        if key in self.back_keys:
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
        if key in self.back_keys:
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
        if key in self.back_keys:
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
            _min = -50 if stat_name in ("stress", "memory") else 0
            self.data["stats"][stat_name] = max(_min, self.data["stats"][stat_name] - 1)
            return
        if key in (curses.KEY_RIGHT, ord("d"), ord("D"), ord("+"), ord("=")):
            stat_name = CREATION_STAT_ORDER[self.stat_index]
            _max = 50 if stat_name in ("stress", "memory") else 100
            self.data["stats"][stat_name] = min(_max, self.data["stats"][stat_name] + 1)

    def handle_questionnaire_key(self, key):
        question = QUESTIONNAIRE_QUESTIONS[self.question_index]
        if key in self.back_keys:
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
        if key in (curses.KEY_ENTER, 10, 13, ord(" ")):
            self.running = False
        if key in self.back_keys:
            self.questionnaire_reveal_shown = False
            self.step_index = 4
            self.questionnaire_framing_shown = True
            if self.questionnaire_answers:
                self.questionnaire_answers.pop()
                self.question_index = max(0, len(self.questionnaire_answers))
                self.question_option_index = 0

    def handle_confirm_key(self, key):
        if key in self.back_keys:
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
                        if key in self.back_keys:
                            self.step_index = 3
                        elif key in (curses.KEY_ENTER, 10, 13, ord(" ")):
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
