import random
from uuid import uuid4

from world import World
from banners import ACTORA_TITLE_BANNER, TIME_ADVANCED_BANNER, QUIT_BANNER
from identity import prepare_parent_identity_context, generate_parent_identity_from_context

EVENT_DETAIL_THRESHOLD = 8
EVENT_RECENT_DISPLAY_LIMIT = 5

INPUT_INTERRUPTED_MESSAGE = "Input interrupted. Exiting Actora."


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
    print(f"  Current Place: {location['current_place_name']}")

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


def render_turn_events(turn_result):
    """Renders structured event output for one simulated turn."""
    print("\n--- Events ---")
    if not turn_result["had_any_events"]:
        print("  - No notable events occurred during this period.")
        return

    total_events = len(turn_result["events"])
    if total_events <= EVENT_DETAIL_THRESHOLD:
        for structured_event in turn_result["events"]:
            print(
                f"  - [Year {structured_event['year']}, Month {structured_event['month']}] "
                f"{structured_event['text']}"
            )
        return

    recent_events = turn_result["events"][-EVENT_RECENT_DISPLAY_LIMIT:]
    omitted_count = total_events - len(recent_events)

    print(f"  - {total_events} notable events occurred during this period.")
    print(f"  - Showing the most recent {len(recent_events)} events:")
    for structured_event in recent_events:
        print(
            f"    - [Year {structured_event['year']}, Month {structured_event['month']}] "
            f"{structured_event['text']}"
        )

    if omitted_count > 0:
        print(f"  - ... {omitted_count} older events omitted.")


def render_continuity_state(continuity_state):
    """Renders the current dead-focus continuity state."""
    print("\n--- Continuity ---")
    print("  - Structural Transition: Focus is currently dead.")
    print(f"  - Previous Focus: {continuity_state['focus_actor_name']}")

    death_year = continuity_state["focus_actor_death_year"]
    death_month = continuity_state["focus_actor_death_month"]
    if death_year is not None and death_month is not None:
        print(f"  - Death: Year {death_year}, Month {death_month}")
    if continuity_state["focus_actor_death_reason"]:
        print(f"  - Death Reason: {continuity_state['focus_actor_death_reason']}")

    print("  - The universe continues.")
    if continuity_state["had_continuity_candidates"]:
        print("  - Select a living connected actor to continue:")
        for index, candidate in enumerate(continuity_state["continuity_candidates"], 1):
            print(
                f"    {index}) {candidate['full_name']} "
                f"[{candidate['relationship_label']}]"
            )
    else:
        print("  - No living connected continuation candidates were found.")
    print("--------------------")


def prompt_for_continuation_choice(continuity_state):
    """Prompts for one valid continuation target index or clean quit."""
    candidate_count = len(continuity_state["continuity_candidates"])
    while True:
        choice_raw = safe_input(
            f"Choose a continuation target (1-{candidate_count}) or type 'quit': "
        ).strip().lower()
        if choice_raw == "quit":
            return None

        try:
            selected_index = int(choice_raw)
        except ValueError:
            print("Invalid input: Please enter a number or 'quit'.")
            continue

        if 1 <= selected_index <= candidate_count:
            return continuity_state["continuity_candidates"][selected_index - 1]["actor_id"]

        print("Invalid input: Please choose one of the listed continuation options.")


def resolve_dead_focus(world):
    """Handles continuation handoff or clean run end when the focused actor is dead."""
    focused_actor_id = world.get_focused_actor_id()
    if focused_actor_id is None:
        return True

    focused_actor = world.get_actor(focused_actor_id)
    if focused_actor is None or focused_actor.is_alive():
        return True

    continuity_state = world.build_continuity_state_for(focused_actor_id)
    render_continuity_state(continuity_state)

    if not continuity_state["had_continuity_candidates"]:
        print("This run has ended because no valid continuation target exists.")
        return False

    successor_actor_id = prompt_for_continuation_choice(continuity_state)
    if successor_actor_id is None:
        print(QUIT_BANNER)
        return False

    handoff_result = world.handoff_focus_to_continuation(
        focused_actor_id,
        successor_actor_id,
    )
    print(
        f"Focus moved from {handoff_result['previous_actor_name']} "
        f"to {handoff_result['new_focused_actor_name']}."
    )

    new_focused_actor_id = handoff_result["new_focused_actor_id"]
    new_focused_actor = world.get_actor(new_focused_actor_id)
    render_snapshot(
        new_focused_actor.get_snapshot_data(
            world.current_year,
            world.current_month,
            world,
            new_focused_actor_id,
        )
    )
    return True


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
    world.add_place(
        place_id="earth_country_01",
        name="Starter Country",
        kind="country",
        parent_place_id="earth",
        metadata={},
    )
    world.add_place(
        place_id="earth_city_01",
        name="Starter City",
        kind="city",
        parent_place_id="earth_country_01",
        metadata={},
    )

    startup_place_id = "earth_city_01"

    mother_identity_context = prepare_parent_identity_context(
        role="mother",
        player_last_name=player_last_name,
        place_id=startup_place_id,
        world=world,
    )
    family_last_name = mother_identity_context["family_last_name"]
    father_identity_context = prepare_parent_identity_context(
        role="father",
        family_last_name=family_last_name,
        player_last_name=player_last_name,
        place_id=startup_place_id,
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
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
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
        current_place_id=startup_place_id,
        residence_place_id=startup_place_id,
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
        place_id=startup_place_id,
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
        if not resolve_dead_focus(world):
            return

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
            final_player_state.get_snapshot_data(
                world.current_year,
                world.current_month,
                world,
                focused_actor_id,
            )
        )
        render_turn_events(turn_result)

        if turn_result["structural_transition"] is not None:
            transition = turn_result["structural_transition"]
            if transition["type"] == "death":
                print(
                    f"  - Structural Transition: {final_player_state.get_full_name()} died in "
                    f"Year {transition['year']}, Month {transition['month']}."
                )

        if turn_result["continuity_state"] is not None and not turn_result["advancement_blocked"]:
            render_continuity_state(turn_result["continuity_state"])

        if turn_result["advancement_blocked"]:
            if not resolve_dead_focus(world):
                return


def start_game():
    print(ACTORA_TITLE_BANNER)

    player_first_name, player_last_name, player_sex, player_gender = create_character()
    world, player_id, player = setup_initial_world(player_first_name, player_last_name, player_sex, player_gender)
    game_loop(world, player_id, player)


if __name__ == "__main__":
    start_game()
