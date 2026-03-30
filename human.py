import random # Keep random here for randomize_starting_statistics


def _get_relationship_label_from_role(role, linked_actor):
    """Builds one display-ready family relationship label for snapshot rendering."""
    if role == "mother":
        return "Mother"
    if role == "father":
        return "Father"
    if role == "sibling":
        if linked_actor is not None:
            if linked_actor.sex == "Male":
                return "Brother"
            if linked_actor.sex == "Female":
                return "Sister"
        return "Sibling"
    if role == "child":
        if linked_actor is not None:
            if linked_actor.sex == "Male":
                return "Son"
            if linked_actor.sex == "Female":
                return "Daughter"
        return "Child"
    return str(role).replace("_", " ").title()


class Human:
    def __init__(self, species, first_name, last_name, sex, gender, birth_year, birth_month=1):
        self.species = species
        self.first_name = first_name
        self.last_name = last_name
        self.sex = sex
        self.gender = gender
        self.birth_year = birth_year
        self.birth_month = birth_month
        self.stats = {
            "health": 100, # Default values, will be randomized for player
            "happiness": 100, # Default values
            "intelligence": 50 # Default values
        }
        self.money = 0
        self.current_place_id = None
        self.residence_place_id = None
        self.jurisdiction_place_id = None
        self.temporary_occupancy_place_id = None
        self.structural_status = "active"
        self.death_year = None
        self.death_month = None
        self.death_reason = None

    def get_full_name(self):
        """Derives and returns the full name of the human."""
        return f"{self.first_name} {self.last_name}".strip()

    def randomize_starting_statistics(self):
        """Randomizes health, happiness, and intelligence for a new human infant."""
        self.stats["health"] = random.randint(85, 100) # Tighter range for human infant
        self.stats["happiness"] = random.randint(80, 100) # Tighter range for human infant
        self.stats["intelligence"] = random.randint(45, 60) # Tighter range for human infant
        self.money = 0 # Money remains fixed at 0

    def get_lifecycle_state(self, current_year, current_month):
        """
        Provides a structured dictionary of derived lifecycle state for the human.
        This is the formal access boundary for lifecycle facts.
        """
        age_years_calc = current_year - self.birth_year
        if current_month < self.birth_month:
            age_years_calc -= 1
        age_years_calc = max(0, age_years_calc)

        total_months_current = (current_year * 12) + current_month
        total_months_birth = (self.birth_year * 12) + self.birth_month
        age_months_calc = max(0, total_months_current - total_months_birth)

        if age_years_calc < 3: # 0-2
            life_stage_calc = "Infant"
        elif age_years_calc < 10: # 3-9
            life_stage_calc = "Child"
        elif age_years_calc < 18: # 10-17
            life_stage_calc = "Teenager"
        elif age_years_calc < 25: # 18-24
            life_stage_calc = "Young Adult"
        elif age_years_calc < 65: # 25-64
            life_stage_calc = "Adult"
        else: # 65+
            life_stage_calc = "Elder"

        return {
            "age_years": age_years_calc,
            "age_months": age_months_calc,
            "life_stage": life_stage_calc,
            "life_stage_model": "human_default"
        }

    def get_age(self, current_year, current_month):
        """Calculates the current age of the human based on year and month."""
        lifecycle = self.get_lifecycle_state(current_year, current_month)
        return lifecycle["age_years"]

    def get_age_in_months(self, current_year, current_month):
        """Calculates the current age of the human in months."""
        lifecycle = self.get_lifecycle_state(current_year, current_month)
        return lifecycle["age_months"]

    def get_human_life_stage(self, current_year, current_month):
        """Determines the human-default life stage based on age."""
        lifecycle = self.get_lifecycle_state(current_year, current_month)
        return lifecycle["life_stage"]

    def get_spatial_state(self, world):
        """Provides a structured, read-only view of actor place identity and context."""
        current_place = world.get_place(self.current_place_id)
        residence_place = world.get_place(self.residence_place_id)
        jurisdiction_place = world.get_place(self.jurisdiction_place_id)
        temporary_occupancy_place = world.get_place(self.temporary_occupancy_place_id)
        current_world_body = world.get_nearest_place_of_kind(self.current_place_id, "world_body")

        current_place_name = world.get_place_name(self.current_place_id)
        residence_place_name = world.get_place_name(self.residence_place_id)
        jurisdiction_place_name = world.get_place_name(self.jurisdiction_place_id)
        temporary_occupancy_place_name = world.get_place_name(self.temporary_occupancy_place_id)

        return {
            "current_place_id": self.current_place_id,
            "current_place_name": current_place_name,
            "current_place_kind": current_place["kind"] if current_place else None,
            "residence_place_id": self.residence_place_id,
            "residence_place_name": residence_place_name,
            "residence_place_kind": residence_place["kind"] if residence_place else None,
            "jurisdiction_place_id": self.jurisdiction_place_id,
            "jurisdiction_place_name": jurisdiction_place_name,
            "jurisdiction_place_kind": jurisdiction_place["kind"] if jurisdiction_place else None,
            "temporary_occupancy_place_id": self.temporary_occupancy_place_id,
            "temporary_occupancy_place_name": temporary_occupancy_place_name,
            "temporary_occupancy_place_kind": (
                temporary_occupancy_place["kind"] if temporary_occupancy_place else None
            ),
            "current_world_body_id": current_world_body["place_id"] if current_world_body else None,
            "current_world_body_name": current_world_body["name"] if current_world_body else None,
        }

    def is_alive(self):
        """Returns True only when the human is currently structurally active/alive."""
        return self.structural_status == "active"

    def get_structural_state(self):
        """Returns a structured read-only view of current structural life/death state."""
        return {
            "structural_status": self.structural_status,
            "is_alive": self.is_alive(),
            "death_year": self.death_year,
            "death_month": self.death_month,
            "death_reason": self.death_reason,
        }

    def get_snapshot_data(self, current_year, current_month, world, actor_id):
        """Returns the current human snapshot as structured shell-renderable data."""
        lifecycle = self.get_lifecycle_state(current_year, current_month)
        spatial_state = self.get_spatial_state(world)
        structural_state = self.get_structural_state()
        family_links = world.get_links(entity_id=actor_id, link_type="family")

        relationship_entries = []
        seen_actor_ids = set()
        for link in family_links:
            if link.get("source_id") != actor_id:
                continue

            linked_actor_id = link.get("target_id")
            if linked_actor_id is None or linked_actor_id in seen_actor_ids:
                continue

            linked_actor = world.get_actor(linked_actor_id)
            if linked_actor is None or not linked_actor.is_alive():
                continue

            relationship_entries.append(
                {
                    "label": _get_relationship_label_from_role(link.get("role"), linked_actor),
                    "name": linked_actor.get_full_name(),
                }
            )
            seen_actor_ids.add(linked_actor_id)

        return {
            "identity": {
                "full_name": self.get_full_name(),
                "species": self.species,
                "sex": self.sex,
                "gender": self.gender,
                "age": lifecycle["age_years"],
                "life_stage": lifecycle["life_stage"],
            },
            "time": {
                "year": current_year,
                "month": current_month,
            },
            "location": {
                "world_body_name": spatial_state["current_world_body_name"] or "Unknown",
                "current_place_name": spatial_state["current_place_name"] or "Unknown",
                "current_place_kind": spatial_state["current_place_kind"],
                "jurisdiction_place_name": spatial_state["jurisdiction_place_name"] or "Unknown",
                "jurisdiction_place_kind": spatial_state["jurisdiction_place_kind"],
            },
            "statistics": {
                "health": self.stats["health"],
                "happiness": self.stats["happiness"],
                "intelligence": self.stats["intelligence"],
                "money": self.money,
            },
            "relationships": relationship_entries,
            "structural": structural_state,
        }

    # --- Stat Management Helper Methods ---
    def modify_stat(self, stat_name, change):
        """Modifies a specified stat, clamping between 0 and 100 if applicable."""
        if stat_name in self.stats:
            current_value = self.stats[stat_name]
            new_value = current_value + change
            self.stats[stat_name] = min(100, max(0, new_value))
        elif stat_name == "money":
            self.money += change
        else:
            raise ValueError(f"modify_stat: unknown stat_name '{stat_name}'")
    # --- End Stat Management Helper Methods ---
