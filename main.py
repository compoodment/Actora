import random
from uuid import uuid4

from world import World
from banners import COMPLIFE_TITLE_BANNER, TIME_ADVANCED_BANNER, QUIT_BANNER
from identity import prepare_parent_identity_context, generate_parent_identity_from_context

EVENT_DETAIL_THRESHOLD = 8
EVENT_RECENT_DISPLAY_LIMIT = 5

INPUT_INTERRUPTED_MESSAGE = "Input interrupted. Exiting CompLife."


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


def render_snapshot(snapshot_data):
    """Renders one structured current-state snapshot to the terminal."""
    identity = snapshot_data["identity"]
    time_state = snapshot_data["time"]
    location = snapshot_data["location"]
    statistics = snapshot_data["statistics"]
    relationships = snapshot_data["relationships"]
    structural = snapshot_data["structural"]

    print(f"\n--- {identity['full_name']} ---")

    print("\n--- Identity ---")
    print(f"  Full Name: {identity['full_name']}")
    print(f"  Species: {identity['species']}")
    print(f"  Sex: {identity['sex']}")
    print(f"  Gender: {identity['gender']}")

    print("\n--- Time ---")
    print(f"  Age: {time_state['age']}")
    print(f"  Life Stage: {time_state['life_stage']}")
    print(f"  Year: {time_state['year']}")
    print(f"  Month: {time_state['month']}")

    print("\n--- Location ---")
    print(f"  World Body: {location['world_body_name']}")

    print("\n--- Statistics ---")
    print(f"  Health: {statistics['health']}")
    print(f"  Happiness: {statistics['happiness']}")
    print(f"  Intelligence: {statistics['intelligence']}")
    print(f"  Money: ${statistics['money']}")

    print("\n--- Relationships ---")
    print("  Family:")
    print(f"    Mother: {relationships['mother_name']}")
    print(f"    Father: {relationships['father_name']}")

    print("\n--- Structural State ---")
    print(f"  Status: {structural['structural_status']}")
    if structural["death_year"] is not None and structural["death_month"] is not None:
        print(f"  Death: Year {structural['death_year']}, Month {structural['death_month']}")
    if structural["death_reason"]:
        print(f"  Death Reason: {structural['death_reason']}")
    print("--------------------")


def create_character():
    """Handles the character creation flow and returns player details."""
    print("\n--- Character Creation ---")

    while True:
        player_first_name = safe_input("Enter your character's first name: ").strip()
        if player_first_name:
            break
        print("First name cannot be empty. Please enter a name.")

    player_last_name = safe_input("Enter your character's last name (optional): ").strip()

    sex_options = ["Male", "Female"]
    print("\nSelect biological sex:")
    for i, option in enumerate(sex_options, 1):
        print(f"  {i}) {option}")
    while True:
        try:
            choice = int(safe_input(f"Enter choice (1-{len(sex_options)}): ").strip())
            if 1 <= choice <= len(sex_options):
                player_sex = sex_options[choice - 1]
                break
            else:
                print("Invalid number. Please choose from the options.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    gender_options = ["Male", "Female", "Non-binary"]
    print("\nSelect gender identity:")
    for i, option in enumerate(gender_options, 1):
        print(f"  {i}) {option}")
    while True:
        try:
            choice = int(safe_input(f"Enter choice (1-{len(gender_options)}): ").strip())
            if 1 <= choice <= len(gender_options):
                player_gender = gender_options[choice - 1]
                break
            else:
                print("Invalid number. Please choose from the options.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print("--------------------------")
    return player_first_name, player_last_name, player_sex, player_gender


def setup_initial_world(player_first_name, player_last_name, player_sex, player_gender):
    """Initializes the world and sets up the player and parents."""
    world = World(start_year=1, start_month=1)
    world.add_place(
        place_id="earth",
        name="Earth",
        kind="world_body",
        parent_place_id=None,
        metadata={},
    )

    mother_identity_context = prepare_parent_identity_context(
        role="mother",
        player_last_name=player_last_name,
        place_id="earth",
        world=world,
    )
    family_last_name = mother_identity_context["family_last_name"]
    father_identity_context = prepare_parent_identity_context(
        role="father",
        family_last_name=family_last_name,
        player_last_name=player_last_name,
        place_id="earth",
        world=world,
    )

    mother_identity = generate_parent_identity_from_context(mother_identity_context)
    father_identity = generate_parent_identity_from_context(father_identity_context)

    mother_id = generate_startup_actor_id("mother")
    father_id = generate_startup_actor_id("father")
    world.create_human_actor(
        actor_id=mother_id,
        species="Human",
        first_name=mother_identity["first_name"],
        last_name=mother_identity["last_name"],
        sex=mother_identity["sex"],
        gender=mother_identity["gender"],
        birth_year=world.current_year - 25,
        birth_month=random.randint(1, 12),
        current_place_id="earth",
        residence_place_id="earth",
    )
    world.create_human_actor(
        actor_id=father_id,
        species="Human",
        first_name=father_identity["first_name"],
        last_name=father_identity["last_name"],
        sex=father_identity["sex"],
        gender=father_identity["gender"],
        birth_year=world.current_year - 27,
        birth_month=random.randint(1, 12),
        current_place_id="earth",
        residence_place_id="earth",
    )

    player_id = generate_startup_actor_id("player")
    player = world.create_human_child_with_parents(
        child_id=player_id,
        first_name=player_first_name,
        last_name=player_last_name,
        sex=player_sex,
        gender=player_gender,
        mother_id=mother_id,
        father_id=father_id,
        birth_year=world.current_year,
        birth_month=1,
        place_id="earth",
        randomize_stats=True,
    )
    world.set_focused_actor(player_id)

    return world, player_id, player


def game_loop(world, player_id, player):
    """Contains the main game loop for advancing time and displaying results."""
    focused_actor_id = world.get_focused_actor_id() or player_id
    focused_actor = world.get_actor(focused_actor_id)
    render_snapshot(focused_actor.get_snapshot_data(world.current_year, world.current_month, world, focused_actor_id))

    while True:
        months_to_advance = 0
        while True: # Input validation loop
            choice_raw = safe_input("Press Enter for the next month, type a number to skip months, or type 'quit': ").strip().lower()

            if choice_raw == '': # Empty input -> 1 month
                months_to_advance = 1
                break
            elif choice_raw == 'quit': # Exact 'quit' -> exit game
                print(QUIT_BANNER)
                return # Use return to terminate
            else:
                try:
                    num_months = int(choice_raw)
                    if num_months > 0: # Positive integers > 0 -> advance that many months
                        months_to_advance = num_months
                        break
                    else: # 0 or negative integers -> invalid
                        print("Invalid input: Please enter a positive number greater than 0.")
                except ValueError: # Non-numeric input (floats, mixed text, other non-numeric) -> invalid
                    print("Invalid input: Please enter a number or 'quit'.")

        turn_result = world.simulate_advance_turn(player_id, months_to_advance)

        print(TIME_ADVANCED_BANNER)
        focused_actor_id = turn_result["focused_actor_id"]
        final_player_state = world.get_actor(focused_actor_id)
        render_snapshot(
            final_player_state.get_snapshot_data(world.current_year, world.current_month, world, focused_actor_id)
        )

        print("\n--- Events ---")
        if not turn_result["had_any_events"]:
            print("  - No notable events occurred during this period.")
        else:
            total_events = len(turn_result["events"])

            if total_events <= EVENT_DETAIL_THRESHOLD:
                for structured_event in turn_result["events"]:
                    # Main.py renders terminal event lines by combining structured year, month, raw event text
                    print(f"  - [Year {structured_event['year']}, Month {structured_event['month']}] {structured_event['text']}")
            else:
                recent_events = turn_result["events"][-EVENT_RECENT_DISPLAY_LIMIT:]
                omitted_count = total_events - len(recent_events)

                print(f"  - {total_events} notable events occurred during this period.")
                print(f"  - Showing the most recent {len(recent_events)} events:")
                for structured_event in recent_events:
                    print(f"    - [Year {structured_event['year']}, Month {structured_event['month']}] {structured_event['text']}")

                if omitted_count > 0:
                    print(f"  - ... {omitted_count} older events omitted.")

        if turn_result["structural_transition"] is not None:
            transition = turn_result["structural_transition"]
            if transition["type"] == "death":
                print(
                    f"  - Structural Transition: {final_player_state.get_full_name()} died in "
                    f"Year {transition['year']}, Month {transition['month']}."
                )

        if turn_result["continuity_state"] is not None:
            continuity_state = turn_result["continuity_state"]
            print("\n--- Continuity ---")
            print("  - The universe continues.")
            if continuity_state["had_continuity_candidates"]:
                print("  - Connected continuation candidates:")
                for candidate in continuity_state["continuity_candidates"]:
                    print(
                        f"    - {candidate['full_name']} "
                        f"[{candidate['link_type']}/{candidate['link_role']}]"
                    )
            else:
                print("  - No living connected continuation candidates were found.")
        print("--------------------")


def start_game():
    print(COMPLIFE_TITLE_BANNER)

    player_first_name, player_last_name, player_sex, player_gender = create_character()
    world, player_id, player = setup_initial_world(player_first_name, player_last_name, player_sex, player_gender)
    game_loop(world, player_id, player)


if __name__ == "__main__":
    start_game()
