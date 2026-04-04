import random
from collections import deque
from uuid import uuid4

from events import get_human_monthly_event_from_lifecycle
from human import Human


_CANONICAL_HUMAN_STAT_KEYS = {
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
}


def _extract_imagination_value(stats):
    """Finds the imagination-equivalent value from a human stat block."""
    if "imagination" in stats:
        return stats["imagination"]
    for stat_name, stat_value in stats.items():
        if stat_name not in _CANONICAL_HUMAN_STAT_KEYS:
            return stat_value
    return 50


def _normalize_human_stats(stats):
    """Aligns human stat keys with the shell-owned stat model."""
    source_stats = dict(stats)
    normalized_stats = {
        stat_name: stat_value
        for stat_name, stat_value in source_stats.items()
        if stat_name in _CANONICAL_HUMAN_STAT_KEYS
    }
    normalized_stats["imagination"] = _extract_imagination_value(source_stats)
    normalized_stats.setdefault("memory", random.randint(40, 70))
    normalized_stats.setdefault("stress", random.randint(5, 20))
    return normalized_stats
from identity import (
    CULTURE_NAME_POOLS,
    FALLBACK_LAST_NAME_POOL,
    FATHER_FIRST_NAME_POOL,
    MOTHER_FIRST_NAME_POOL,
)


UNSET = object()


class World:
    """Represents the game world and manages its state."""
    def __init__(self, start_year, start_month=1):
        self.current_year = start_year
        self.current_month = start_month
        self.actors = {} # Stores actor objects by their unique ID (e.g., "player")
        self.links = []
        self.places = {}
        self.records = []
        self.focused_actor_id = None
        self._used_npc_last_names = set()

    def add_place(self, place_id, name, kind, parent_place_id=None, metadata=None):
        """Adds a place record to the world-owned place registry."""
        self.places[place_id] = {
            "place_id": place_id,
            "name": name,
            "kind": kind,
            "parent_place_id": parent_place_id,
            "metadata": metadata if metadata is not None else {},
        }

    def get_place(self, place_id):
        """Returns a place record by place ID."""
        return self.places.get(place_id)

    def get_place_name(self, place_id):
        """Returns a place name by place ID, or None when unresolved."""
        place = self.get_place(place_id)
        return place["name"] if place else None

    def get_place_kind(self, place_id):
        """Returns a place kind by place ID, or None when unresolved."""
        place = self.get_place(place_id)
        return place["kind"] if place else None

    def get_child_places(self, parent_place_id):
        """Returns direct child place records for one parent place ID."""
        return [
            place
            for place in self.places.values()
            if place.get("parent_place_id") == parent_place_id
        ]

    def get_place_lineage(self, place_id, include_self=True):
        """Returns the current parent chain from a place upward through its ancestors."""
        if place_id is None:
            return []

        if include_self:
            current_place = self.get_place(place_id)
        else:
            current_place = self.get_place(place_id)
            current_place = self.get_place(current_place["parent_place_id"]) if current_place else None

        lineage = []
        visited_place_ids = set()
        while current_place is not None:
            current_place_id = current_place.get("place_id")
            if current_place_id in visited_place_ids:
                break
            visited_place_ids.add(current_place_id)
            lineage.append(current_place)
            parent_place_id = current_place.get("parent_place_id")
            current_place = self.get_place(parent_place_id) if parent_place_id is not None else None
        return lineage

    def get_nearest_place_of_kind(self, place_id, kind, include_self=True):
        """Returns the nearest place in the lineage matching the requested kind."""
        for place in self.get_place_lineage(place_id, include_self=include_self):
            if place.get("kind") == kind:
                return place
        return None

    def add_actor(self, actor_id, actor_obj):
        """Adds an actor to the world."""
        self.actors[actor_id] = actor_obj

    def update_actor_spatial_identity(
        self,
        actor_id,
        *,
        current_place_id=UNSET,
        residence_place_id=UNSET,
        jurisdiction_place_id=UNSET,
        temporary_occupancy_place_id=UNSET,
    ):
        """Applies a narrow world-owned spatial identity update for one actor."""
        actor = self.get_actor(actor_id)
        if actor is None:
            raise ValueError(f"update_actor_spatial_identity: unknown actor_id '{actor_id}'")

        requested_updates = {
            "current_place_id": current_place_id,
            "residence_place_id": residence_place_id,
            "jurisdiction_place_id": jurisdiction_place_id,
            "temporary_occupancy_place_id": temporary_occupancy_place_id,
        }

        changed_fields = {}
        for field_name, requested_value in requested_updates.items():
            if requested_value is UNSET:
                continue
            if requested_value is not None and self.get_place(requested_value) is None:
                raise ValueError(
                    f"update_actor_spatial_identity: unknown place_id '{requested_value}' "
                    f"for field '{field_name}'"
                )

            previous_value = getattr(actor, field_name)
            if previous_value == requested_value:
                continue

            setattr(actor, field_name, requested_value)
            changed_fields[field_name] = {
                "old": previous_value,
                "new": requested_value,
            }

        return {
            "actor_id": actor_id,
            "changed": bool(changed_fields),
            "changed_fields": changed_fields,
        }

    def set_focused_actor(self, actor_id):
        """Sets the world-owned currently focused actor ID."""
        if actor_id not in self.actors:
            raise ValueError(f"set_focused_actor: unknown actor_id '{actor_id}'")
        self.focused_actor_id = actor_id

    def get_focused_actor_id(self):
        """Returns the current world-owned focused actor ID, or None."""
        return self.focused_actor_id

    def get_focused_actor(self):
        """Returns the current world-owned focused actor object, or None."""
        if self.focused_actor_id is None:
            return None
        return self.get_actor(self.focused_actor_id)

    def _build_record(
        self,
        record_type,
        scope,
        text,
        year,
        month,
        actor_ids=None,
        tags=None,
        metadata=None,
    ):
        """Builds one normalized structured record without mutating the record store."""
        return {
            "record_type": record_type,
            "scope": scope,
            "text": text,
            "year": year,
            "month": month,
            "actor_ids": list(actor_ids) if actor_ids is not None else [],
            "tags": list(tags) if tags is not None else [],
            "metadata": dict(metadata) if metadata is not None else {},
        }

    def add_record(
        self,
        record_type,
        scope,
        text,
        year,
        month,
        actor_ids=None,
        tags=None,
        metadata=None,
    ):
        """Appends one normalized structured record to the world-owned record store."""
        record = self._build_record(
            record_type=record_type,
            scope=scope,
            text=text,
            year=year,
            month=month,
            actor_ids=actor_ids,
            tags=tags,
            metadata=metadata,
        )
        self.records.append(record)
        return record

    def get_records(self, scope=None, actor_id=None, record_type=None):
        """Returns stored records filtered by optional scope, actor, and record type."""
        filtered_records = self.records
        if scope is not None:
            filtered_records = [record for record in filtered_records if record.get("scope") == scope]
        if actor_id is not None:
            filtered_records = [
                record for record in filtered_records if actor_id in record.get("actor_ids", [])
            ]
        if record_type is not None:
            filtered_records = [
                record for record in filtered_records if record.get("record_type") == record_type
            ]
        return filtered_records

    def get_actor_records(self, actor_id, record_type=None):
        """Returns records for one actor by delegating to the world record store helper."""
        return self.get_records(actor_id=actor_id, record_type=record_type)

    def generate_actor_id(self, role):
        """Builds one narrow world-owned actor ID for generated family actors."""
        return f"{role}_{uuid4().hex[:8]}"

    def get_latest_record(self, actor_id=None, record_type=None):
        """Returns the latest matching record from the insertion-ordered world record store."""
        for record in reversed(self.records):
            if actor_id is not None and actor_id not in record.get("actor_ids", []):
                continue
            if record_type is not None and record.get("record_type") != record_type:
                continue
            return record
        return None

    def get_records_by_tag(self, tag, actor_id=None):
        """Returns records whose tags contain the requested tag, optionally filtered by actor."""
        filtered_records = []
        for record in self.records:
            if tag not in record.get("tags", []):
                continue
            if actor_id is not None and actor_id not in record.get("actor_ids", []):
                continue
            filtered_records.append(record)
        return filtered_records

    def create_human_actor(
        self,
        actor_id,
        species,
        first_name,
        last_name,
        sex,
        gender,
        birth_year,
        birth_month,
        current_place_id=None,
        residence_place_id=None,
        jurisdiction_place_id=None,
        temporary_occupancy_place_id=None,
        randomize_stats=False,
    ):
        """Creates and registers a Human actor in the world."""
        actor = Human(
            species=species,
            first_name=first_name,
            last_name=last_name,
            sex=sex,
            gender=gender,
            birth_year=birth_year,
            birth_month=birth_month,
        )
        if randomize_stats:
            actor.randomize_starting_statistics()
        actor.stats = _normalize_human_stats(actor.stats)
        self.add_actor(actor_id, actor)
        self.update_actor_spatial_identity(
            actor_id,
            current_place_id=current_place_id,
            residence_place_id=residence_place_id,
            jurisdiction_place_id=jurisdiction_place_id,
            temporary_occupancy_place_id=temporary_occupancy_place_id,
        )
        self.add_record(
            record_type="actor_entry",
            scope="actor",
            text=f"{actor.get_full_name()} entered the simulation.",
            year=birth_year,
            month=birth_month,
            actor_ids=[actor_id],
            tags=["actor_entry"],
            metadata={
                "species": species,
                "entry_method": "create_human_actor",
            },
        )
        return actor

    def create_human_child_with_parents(
        self,
        child_id,
        first_name,
        last_name,
        sex,
        gender,
        mother_id,
        father_id,
        birth_year,
        birth_month,
        place_id,
        jurisdiction_place_id=None,
        temporary_occupancy_place_id=None,
        randomize_stats=False,
        family_link_source="startup_family",
        birth_record_type="family_bootstrap",
        birth_record_text=None,
        birth_record_tags=None,
        birth_record_metadata=None,
    ):
        """Creates a human child actor and optional mother/father family links."""
        child = self.create_human_actor(
            actor_id=child_id,
            species="Human",
            first_name=first_name,
            last_name=last_name,
            sex=sex,
            gender=gender,
            birth_year=birth_year,
            birth_month=birth_month,
            current_place_id=place_id,
            residence_place_id=place_id,
            jurisdiction_place_id=jurisdiction_place_id,
            temporary_occupancy_place_id=temporary_occupancy_place_id,
            randomize_stats=randomize_stats,
        )

        child_family_metadata = {
            "is_origin_family": True,
            "is_caregiver_family": True,
            "bootstrap_source": family_link_source,
        }

        if mother_id is not None:
            self.add_link_pair(
                source_id=child_id,
                target_id=mother_id,
                forward_type="family",
                forward_role="mother",
                reverse_type="family",
                reverse_role="child",
                forward_metadata=dict(child_family_metadata),
                reverse_metadata=dict(child_family_metadata),
            )
        if father_id is not None:
            self.add_link_pair(
                source_id=child_id,
                target_id=father_id,
                forward_type="family",
                forward_role="father",
                reverse_type="family",
                reverse_role="child",
                forward_metadata=dict(child_family_metadata),
                reverse_metadata=dict(child_family_metadata),
            )

        sibling_ids = self._link_child_to_existing_siblings(child_id)

        actor_ids = [child_id]
        if mother_id is not None:
            actor_ids.append(mother_id)
        if father_id is not None:
            actor_ids.append(father_id)
        actor_ids.extend(sibling_ids)
        deduped_actor_ids = list(dict.fromkeys(actor_ids))
        record_text = birth_record_text
        if record_text is None:
            record_text = f"{child.get_full_name()} was born into the family."
        self.add_record(
            record_type=birth_record_type,
            scope="actor",
            text=record_text,
            year=birth_year,
            month=birth_month,
            actor_ids=deduped_actor_ids,
            tags=list(birth_record_tags) if birth_record_tags is not None else ["family", "birth"],
            metadata={
                "mother_id": mother_id,
                "father_id": father_id,
                "sibling_ids": sibling_ids,
                "entry_method": "create_human_child_with_parents",
                "family_link_source": family_link_source,
                **(birth_record_metadata or {}),
            },
        )

        return child

    def _link_child_to_existing_siblings(self, child_id):
        """Creates direct sibling links between one child and the family's other children."""
        sibling_ids = self.get_sibling_ids_for(child_id)
        for sibling_id in sibling_ids:
            if self.get_links(
                source_id=child_id,
                target_id=sibling_id,
                link_type="family",
                roles=["sibling"],
            ):
                continue
            self.add_link_pair(
                source_id=child_id,
                target_id=sibling_id,
                forward_type="family",
                forward_role="sibling",
                reverse_type="family",
                reverse_role="sibling",
                forward_metadata={
                    "is_close_family": True,
                    "family_relation": "sibling",
                    "bootstrap_source": "shared_parents",
                },
                reverse_metadata={
                    "is_close_family": True,
                    "family_relation": "sibling",
                    "bootstrap_source": "shared_parents",
                },
            )

        return sibling_ids

    def get_sibling_ids_for(self, actor_id):
        """Returns sibling actor IDs inferred from shared origin parents."""
        actor = self.get_actor(actor_id)
        if actor is None:
            raise ValueError(f"get_sibling_ids_for: unknown actor_id '{actor_id}'")

        parent_ids = self.get_parent_ids_for(actor_id)
        actor_parent_ids = {
            parent_id
            for parent_id in (parent_ids["mother_id"], parent_ids["father_id"])
            if parent_id is not None
        }
        if not actor_parent_ids:
            return []

        sibling_ids = []
        for other_actor_id in sorted(self.actors):
            if other_actor_id == actor_id:
                continue
            other_parent_ids = self.get_parent_ids_for(other_actor_id)
            other_parent_set = {
                parent_id
                for parent_id in (other_parent_ids["mother_id"], other_parent_ids["father_id"])
                if parent_id is not None
            }
            if actor_parent_ids.intersection(other_parent_set):
                sibling_ids.append(other_actor_id)
        return sibling_ids

    def _generate_human_child_identity(self, family_last_name):
        """Builds one narrow placeholder identity for a generated sibling or newborn."""
        if random.random() < 0.5:
            return {
                "first_name": random.choice(MOTHER_FIRST_NAME_POOL),
                "last_name": family_last_name,
                "sex": "Female",
                "gender": "Female",
            }
        return {
            "first_name": random.choice(FATHER_FIRST_NAME_POOL),
            "last_name": family_last_name,
            "sex": "Male",
            "gender": "Male",
        }

    def _get_actor_age_in_months(self, actor_id, year=None, month=None):
        """Returns one actor's age in months against the requested simulation date."""
        actor = self.get_actor(actor_id)
        if actor is None:
            raise ValueError(f"_get_actor_age_in_months: unknown actor_id '{actor_id}'")
        age_year = self.current_year if year is None else year
        age_month = self.current_month if month is None else month
        return actor.get_age_in_months(age_year, age_month)

    def _resolve_coparent_pair_roles(self, actor_id_a, actor_id_b):
        """Resolves the current mother/father assignment for a coparent pair when possible."""
        actor_a = self.get_actor(actor_id_a)
        actor_b = self.get_actor(actor_id_b)
        if actor_a is None or actor_b is None:
            return None

        if actor_a.sex == "Female" and actor_b.sex == "Male":
            return {"mother_id": actor_id_a, "father_id": actor_id_b}
        if actor_a.sex == "Male" and actor_b.sex == "Female":
            return {"mother_id": actor_id_b, "father_id": actor_id_a}
        return None

    def _get_children_for_parents(self, mother_id, father_id):
        """Returns current children who match the provided current mother/father IDs."""
        child_ids = []
        for actor_id in sorted(self.actors):
            parent_ids = self.get_parent_ids_for(actor_id)
            if parent_ids["mother_id"] == mother_id and parent_ids["father_id"] == father_id:
                child_ids.append(actor_id)
        return child_ids

    def _build_family_birth_profile_for(self, mother_id, father_id):
        """Builds a narrow monthly birth profile for one current coparent pair."""
        mother = self.get_actor(mother_id)
        father = self.get_actor(father_id)
        if mother is None or father is None:
            return None
        if not mother.is_alive() or not father.is_alive():
            return None

        mother_age_months = mother.get_age_in_months(self.current_year, self.current_month)
        father_age_months = father.get_age_in_months(self.current_year, self.current_month)
        if mother_age_months < (18 * 12) or mother_age_months > (43 * 12):
            return None
        if father_age_months < (18 * 12) or father_age_months > (60 * 12):
            return None

        current_child_ids = self._get_children_for_parents(mother_id, father_id)
        child_count = len(current_child_ids)
        youngest_child_age_months = None
        if current_child_ids:
            youngest_child_age_months = min(
                self._get_actor_age_in_months(child_id)
                for child_id in current_child_ids
            )
            if youngest_child_age_months < 12:
                return None

        if mother_age_months <= (30 * 12):
            mother_factor = 1.0
        elif mother_age_months <= (35 * 12):
            mother_factor = 0.72
        elif mother_age_months <= (40 * 12):
            mother_factor = 0.36
        else:
            mother_factor = 0.14

        if father_age_months <= (40 * 12):
            father_factor = 1.0
        elif father_age_months <= (50 * 12):
            father_factor = 0.8
        else:
            father_factor = 0.55

        spacing_factor = 1.0
        if youngest_child_age_months is not None and youngest_child_age_months < 24:
            spacing_factor = 0.45

        family_size_factor = max(0.2, 1.0 - (0.22 * child_count))
        monthly_birth_probability = 0.0055 * mother_factor * father_factor * spacing_factor * family_size_factor
        if monthly_birth_probability <= 0:
            return None

        return {
            "mother_id": mother_id,
            "father_id": father_id,
            "current_child_ids": current_child_ids,
            "child_count": child_count,
            "mother_age_years": mother.get_age(self.current_year, self.current_month),
            "father_age_years": father.get_age(self.current_year, self.current_month),
            "youngest_child_age_months": youngest_child_age_months,
            "monthly_birth_probability": monthly_birth_probability,
            "rule": "narrow_family_birth",
        }

    def _create_family_child_birth(self, mother_id, father_id, *, birth_year, birth_month, birth_source):
        """Creates one real family child actor for a current coparent pair."""
        mother = self.get_actor(mother_id)
        father = self.get_actor(father_id)
        if mother is None or father is None:
            raise ValueError("_create_family_child_birth: unresolved parents")

        family_last_name = mother.last_name or father.last_name
        identity = self._generate_human_child_identity(family_last_name)
        child_id = self.generate_actor_id("family_child")
        child = self.create_human_child_with_parents(
            child_id=child_id,
            first_name=identity["first_name"],
            last_name=identity["last_name"],
            sex=identity["sex"],
            gender=identity["gender"],
            mother_id=mother_id,
            father_id=father_id,
            birth_year=birth_year,
            birth_month=birth_month,
            place_id=mother.residence_place_id or mother.current_place_id or father.current_place_id,
            jurisdiction_place_id=(
                mother.jurisdiction_place_id
                or father.jurisdiction_place_id
            ),
            randomize_stats=True,
            family_link_source=birth_source,
            birth_record_type="birth",
            birth_record_text=f"{identity['first_name']} {identity['last_name']} was born into the family.",
            birth_record_tags=["family", "birth"],
            birth_record_metadata={"birth_source": birth_source},
        )
        return child_id, child

    def bootstrap_older_siblings_for_newborn(
        self,
        *,
        mother_id,
        father_id,
        player_birth_year,
        player_birth_month,
    ):
        """Creates a small plausible set of older siblings before the player is born."""
        mother = self.get_actor(mother_id)
        father = self.get_actor(father_id)
        if mother is None or father is None:
            raise ValueError("bootstrap_older_siblings_for_newborn: unresolved parents")

        mother_age_months = mother.get_age_in_months(player_birth_year, player_birth_month)
        father_age_months = father.get_age_in_months(player_birth_year, player_birth_month)
        if mother_age_months < (20 * 12) or father_age_months < (20 * 12):
            return []
        if random.random() < 0.58:
            return []

        max_possible_count = 1
        if mother_age_months >= (29 * 12):
            max_possible_count = 2
        if mother_age_months >= (35 * 12) and random.random() < 0.3:
            max_possible_count = 3
        sibling_count = random.randint(1, max_possible_count)

        birth_points = []
        months_before_player = random.randint(14, 36)
        for _ in range(sibling_count):
            sibling_total_months = (player_birth_year * 12) + player_birth_month - months_before_player
            if sibling_total_months <= ((mother.birth_year * 12) + mother.birth_month + (18 * 12)):
                break
            birth_year, birth_month = divmod(sibling_total_months - 1, 12)
            birth_points.append((birth_year, birth_month + 1))
            months_before_player += random.randint(18, 36)

        created_sibling_ids = []
        for birth_year, birth_month in reversed(birth_points):
            sibling_id, _ = self._create_family_child_birth(
                mother_id,
                father_id,
                birth_year=birth_year,
                birth_month=birth_month,
                birth_source="startup_family",
            )
            created_sibling_ids.append(sibling_id)

        return created_sibling_ids

    def resolve_monthly_family_events(self, focused_actor_id=None):
        """Runs narrow family background simulation such as later sibling births."""
        coparent_pairs = []
        seen_pairs = set()
        for link in self.get_links(link_type="association", roles=["coparent"]):
            source_id = link.get("source_id")
            target_id = link.get("target_id")
            pair_key = tuple(sorted((source_id, target_id)))
            if None in pair_key or pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            coparent_pairs.append(pair_key)

        background_events = []
        surfaced_events = []
        for actor_id_a, actor_id_b in coparent_pairs:
            parent_roles = self._resolve_coparent_pair_roles(actor_id_a, actor_id_b)
            if parent_roles is None:
                continue

            birth_profile = self._build_family_birth_profile_for(
                parent_roles["mother_id"],
                parent_roles["father_id"],
            )
            if birth_profile is None:
                continue
            if random.random() >= birth_profile["monthly_birth_probability"]:
                continue

            child_id, child = self._create_family_child_birth(
                parent_roles["mother_id"],
                parent_roles["father_id"],
                birth_year=self.current_year,
                birth_month=self.current_month,
                birth_source="family_birth",
            )
            sibling_ids = self.get_sibling_ids_for(child_id)
            event_payload = {
                "event_id": "family_sibling_birth",
                "type": "family_birth",
                "actor_id": child_id,
                "child_id": child_id,
                "child_name": child.get_full_name(),
                "mother_id": parent_roles["mother_id"],
                "father_id": parent_roles["father_id"],
                "sibling_ids": sibling_ids,
                "year": self.current_year,
                "month": self.current_month,
                "rule": birth_profile["rule"],
                "quiet_by_default": True,
            }
            background_events.append(event_payload)

            if focused_actor_id in sibling_ids:
                relationship_label = "Sister" if child.sex == "Female" else "Brother"
                surfaced_events.append(
                    {
                        "event_id": "family_sibling_birth",
                        "text": f"Your family welcomed a new {relationship_label.lower()}, {child.first_name}.",
                        "outcome": {"stat_changes": {}},
                        "tags": ["family", "birth", "sibling"],
                        "year": self.current_year,
                        "month": self.current_month,
                    }
                )

        return {
            "background_events": background_events,
            "surfaced_events": surfaced_events,
        }
    
    def get_actor(self, actor_id):
        """Returns an actor object from the world by ID."""
        return self.actors.get(actor_id)

    def _build_link_record(self, source_id, target_id, link_type, role, metadata=None):
        """Builds one normalized directional link record without mutating the link store."""
        # status defaults to "active" for all link types; callers may override via metadata
        merged_metadata = {"status": "active"}
        if metadata is not None:
            merged_metadata.update(metadata)
        return {
            "source_id": source_id,
            "target_id": target_id,
            "type": link_type,
            "role": role,
            "metadata": merged_metadata,
        }

    def add_link(self, source_id, target_id, link_type, role, metadata=None):
        """Adds a directional link record between two entities."""
        link_record = self._build_link_record(
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
            role=role,
            metadata=metadata,
        )
        self.links.append(link_record)
        return link_record

    def add_link_pair(
        self,
        source_id,
        target_id,
        forward_type,
        forward_role,
        reverse_type,
        reverse_role,
        forward_metadata=None,
        reverse_metadata=None,
    ):
        """Adds two explicit directional links representing a bidirectional relationship."""
        self.add_link(source_id, target_id, forward_type, forward_role, forward_metadata)
        self.add_link(target_id, source_id, reverse_type, reverse_role, reverse_metadata)

    def get_links(
        self,
        source_id=None,
        target_id=None,
        entity_id=None,
        direction="both",
        link_type=None,
        role=None,
        roles=None,
    ):
        """Returns stored links filtered by endpoint, direction, type, and role."""
        if entity_id is not None and direction not in ("outgoing", "incoming", "both"):
            raise ValueError(f"get_links: unsupported direction '{direction}'")

        filtered = self.links
        if source_id is not None:
            filtered = [link for link in filtered if link.get("source_id") == source_id]
        if target_id is not None:
            filtered = [link for link in filtered if link.get("target_id") == target_id]
        if entity_id is not None:
            if direction == "outgoing":
                filtered = [link for link in filtered if link.get("source_id") == entity_id]
            elif direction == "incoming":
                filtered = [link for link in filtered if link.get("target_id") == entity_id]
            else:
                filtered = [
                    link
                    for link in filtered
                    if link.get("source_id") == entity_id or link.get("target_id") == entity_id
                ]
        if link_type is not None:
            filtered = [link for link in filtered if link.get("type") == link_type]

        role_filter = set(roles) if roles is not None else None
        if role is not None:
            filtered = [link for link in filtered if link.get("role") == role]
        elif role_filter is not None:
            filtered = [link for link in filtered if link.get("role") in role_filter]
        return filtered

    def get_outgoing_links(self, source_id, link_type=None, role=None):
        """Returns links where the specified entity is the source."""
        return self.get_links(source_id=source_id, link_type=link_type, role=role)

    def get_incoming_links(self, target_id, link_type=None, role=None):
        """Returns links where the specified entity is the target."""
        return self.get_links(target_id=target_id, link_type=link_type, role=role)

    def get_related_links(self, entity_id, link_type=None, role=None):
        """Returns all incoming and outgoing links for an entity."""
        return self.get_links(entity_id=entity_id, direction="both", link_type=link_type, role=role)

    def get_linked_ids(self, entity_id, direction="both", link_type=None, role=None):
        """Returns IDs linked to an entity based on direction and optional filters."""
        linked_ids = []

        if direction in ("outgoing", "both"):
            outgoing_links = self.get_links(
                entity_id=entity_id,
                direction="outgoing",
                link_type=link_type,
                role=role,
            )
            linked_ids.extend(link["target_id"] for link in outgoing_links)

        if direction in ("incoming", "both"):
            incoming_links = self.get_links(
                entity_id=entity_id,
                direction="incoming",
                link_type=link_type,
                role=role,
            )
            linked_ids.extend(link["source_id"] for link in incoming_links)

        deduped_linked_ids = []
        seen_ids = set()
        for linked_id in linked_ids:
            if linked_id not in seen_ids:
                seen_ids.add(linked_id)
                deduped_linked_ids.append(linked_id)

        return deduped_linked_ids

    def get_link_target_ids(self, source_id, link_type=None, roles=None):
        """Returns target IDs from outgoing links with optional type/role filtering."""
        outgoing_links = self.get_links(
            source_id=source_id,
            link_type=link_type,
            roles=roles,
        )

        deduped_target_ids = []
        seen_ids = set()
        for link in outgoing_links:
            target_id = link.get("target_id")
            if target_id is not None and target_id not in seen_ids:
                seen_ids.add(target_id)
                deduped_target_ids.append(target_id)

        return deduped_target_ids

    # --- Social link helpers ---

    _NPC_TRAIT_POOL = [
        "Curious", "Calm", "Fussy", "Bold", "Shy",
        "Cheerful", "Stubborn", "Gentle", "Restless", "Alert",
    ]

    def _get_social_link_category(self, closeness):
        """Returns the social link role for a given closeness value (0–100)."""
        if closeness >= 70:
            return "close_friend"
        if closeness >= 30:
            return "friend"
        return "acquaintance"

    def create_social_link_pair(
        self,
        actor_a_id,
        actor_b_id,
        *,
        closeness,
        status="active",
        closeness_history_months=0,
    ):
        """Creates a bidirectional social link between two actors.

        The link role is derived from closeness:
          acquaintance (1–29), friend (30–69), close_friend (70–100).
        """
        category = self._get_social_link_category(closeness)
        metadata = {
            "closeness": closeness,
            "status": status,
            "closeness_history_months": closeness_history_months,
        }
        self.add_link_pair(
            source_id=actor_a_id,
            target_id=actor_b_id,
            forward_type="social",
            forward_role=category,
            reverse_type="social",
            reverse_role=category,
            forward_metadata=dict(metadata),
            reverse_metadata=dict(metadata),
        )
        return category

    def generate_meeting_npc(self, player_id, *, culture_group=None):
        """Generates and registers a plausible NPC for a meeting event.

        Age is within ±5 years of the player (minimum 8).
        Stats are seeded in normal human ranges.
        Name is drawn from the player's culture group when resolvable.
        """
        player = self.get_actor(player_id)
        if player is None:
            raise ValueError(f"generate_meeting_npc: unknown player_id '{player_id}'")

        if culture_group is None:
            jurisdiction_place = self.get_place(player.jurisdiction_place_id)
            if jurisdiction_place:
                culture_group = jurisdiction_place.get("metadata", {}).get("culture_group")

        player_age = player.get_age(self.current_year, self.current_month)
        age_min = max(8, player_age - 5)
        age_max = max(8, player_age + 5)
        npc_age = random.randint(age_min, age_max)
        npc_birth_year = self.current_year - npc_age
        npc_birth_month = random.randint(1, 12)

        npc_sex = random.choice(["Male", "Female"])
        culture_pool = CULTURE_NAME_POOLS.get(culture_group or "", {})
        if npc_sex == "Female":
            first_name_pool = culture_pool.get("mother_first_names", MOTHER_FIRST_NAME_POOL)
        else:
            first_name_pool = culture_pool.get("father_first_names", FATHER_FIRST_NAME_POOL)
        last_name_pool = culture_pool.get("last_names", FALLBACK_LAST_NAME_POOL)

        first_name = random.choice(first_name_pool)
        player_last_name = player.last_name if player else None
        available_last_names = [
            name for name in last_name_pool
            if name != player_last_name and name not in self._used_npc_last_names
        ]
        if not available_last_names:
            available_last_names = [name for name in last_name_pool if name != player_last_name]
        if not available_last_names:
            available_last_names = last_name_pool
        last_name = random.choice(available_last_names)
        self._used_npc_last_names.add(last_name)

        npc_actor_id = self.generate_actor_id("npc")
        npc = self.create_human_actor(
            actor_id=npc_actor_id,
            species="Human",
            first_name=first_name,
            last_name=last_name,
            sex=npc_sex,
            gender=npc_sex,
            birth_year=npc_birth_year,
            birth_month=npc_birth_month,
            current_place_id=player.current_place_id,
            residence_place_id=player.residence_place_id,
            jurisdiction_place_id=player.jurisdiction_place_id,
        )

        npc.stats.update({
            "health": random.randint(70, 100),
            "happiness": random.randint(50, 100),
            "intelligence": random.randint(35, 75),
            "strength": random.randint(30, 70),
            "charisma": random.randint(30, 70),
            "imagination": random.randint(30, 70),
            "memory": random.randint(40, 70),
            "stress": random.randint(5, 20),
            "wisdom": random.randint(20, 60),
            "discipline": random.randint(20, 60),
            "willpower": random.randint(30, 70),
            "looks": random.randint(30, 80),
            "fertility": random.randint(40, 90),
        })
        npc.stats = _normalize_human_stats(npc.stats)
        npc.traits = random.sample(self._NPC_TRAIT_POOL, 3)

        return npc_actor_id, npc

    # --- End social link helpers ---

    def get_family_link_target_ids(
        self,
        source_id,
        roles=None,
        require_origin_family=None,
        require_caregiver_family=None,
        bootstrap_source=None,
    ):
        """Returns family target IDs filtered by current optional semantic metadata."""
        outgoing_family_links = self.get_links(
            source_id=source_id,
            link_type="family",
            roles=roles,
        )

        if require_origin_family is not None:
            outgoing_family_links = [
                link
                for link in outgoing_family_links
                if link.get("metadata", {}).get("is_origin_family") is require_origin_family
            ]

        if require_caregiver_family is not None:
            outgoing_family_links = [
                link
                for link in outgoing_family_links
                if link.get("metadata", {}).get("is_caregiver_family") is require_caregiver_family
            ]

        if bootstrap_source is not None:
            outgoing_family_links = [
                link
                for link in outgoing_family_links
                if link.get("metadata", {}).get("bootstrap_source") == bootstrap_source
            ]

        deduped_target_ids = []
        seen_ids = set()
        for link in outgoing_family_links:
            target_id = link.get("target_id")
            if target_id is not None and target_id not in seen_ids:
                seen_ids.add(target_id)
                deduped_target_ids.append(target_id)

        return deduped_target_ids

    def get_origin_parent_ids_for(self, entity_id):
        """Returns mother/father IDs from outgoing family links explicitly marked as origin links."""
        mother_ids = self.get_family_link_target_ids(
            entity_id,
            roles=["mother"],
            require_origin_family=True,
        )
        father_ids = self.get_family_link_target_ids(
            entity_id,
            roles=["father"],
            require_origin_family=True,
        )
        return {
            "mother_id": mother_ids[0] if mother_ids else None,
            "father_id": father_ids[0] if father_ids else None,
        }

    def get_caregiver_parent_ids_for(self, entity_id):
        """Returns mother/father IDs from outgoing family links explicitly marked as caregiver links."""
        mother_ids = self.get_family_link_target_ids(
            entity_id,
            roles=["mother"],
            require_caregiver_family=True,
        )
        father_ids = self.get_family_link_target_ids(
            entity_id,
            roles=["father"],
            require_caregiver_family=True,
        )
        return {
            "mother_id": mother_ids[0] if mother_ids else None,
            "father_id": father_ids[0] if father_ids else None,
        }

    def get_parent_ids_for(self, entity_id):
        """Human-specific wrapper resolving mother and father IDs from family links."""
        origin_parent_ids = self.get_origin_parent_ids_for(entity_id)
        if origin_parent_ids["mother_id"] is not None or origin_parent_ids["father_id"] is not None:
            return origin_parent_ids

        mother_ids = self.get_link_target_ids(entity_id, link_type="family", roles=["mother"])
        father_ids = self.get_link_target_ids(entity_id, link_type="family", roles=["father"])
        return {
            "mother_id": mother_ids[0] if mother_ids else None,
            "father_id": father_ids[0] if father_ids else None,
        }

    def advance_months(self, months):
        """Advances the world's time by a specified number of months."""
        self.current_month += months
        while self.current_month > 12:
            self.current_year += 1
            self.current_month -= 12
        while self.current_month < 1:
            self.current_year -= 1
            self.current_month += 12

    def _format_year_month(self, year, month):
        """Formats a year/month pair as a compact lineage-friendly date string."""
        if year is None or month is None:
            return None
        year_prefix = "-" if year < 0 else ""
        year_body = f"{abs(year):04d}"
        return f"{year_prefix}{year_body}-{month:02d}"

    def _get_sibling_relationship_label(self, actor_id, linked_actor_id):
        """Returns a direct simple sibling label when two actors share origin parents."""
        sibling_ids = self.get_sibling_ids_for(actor_id)
        if linked_actor_id not in sibling_ids:
            return None

        linked_actor = self.get_actor(linked_actor_id)
        if linked_actor is None:
            return "Sibling"
        if linked_actor.sex == "Female":
            return "Sister"
        if linked_actor.sex == "Male":
            return "Brother"
        return "Sibling"

    def _get_family_role_label_for(self, role, linked_actor):
        """Builds one display-ready family relationship label for world-owned surfaces."""
        if role == "mother":
            return "Mother"
        if role == "father":
            return "Father"
        if role == "sibling":
            if linked_actor is not None:
                if linked_actor.sex == "Female":
                    return "Sister"
                if linked_actor.sex == "Male":
                    return "Brother"
            return "Sibling"
        if role == "child":
            if linked_actor is not None:
                if linked_actor.sex == "Female":
                    return "Daughter"
                if linked_actor.sex == "Male":
                    return "Son"
            return "Child"
        return str(role).replace("_", " ").title()

    def _build_family_event_context_for(self, actor_id):
        """Builds the current living-family context for family-aware monthly events."""
        actor = self.get_actor(actor_id)
        if actor is None:
            raise ValueError(f"_build_family_event_context_for: unknown actor_id '{actor_id}'")

        sibling_entries = []
        seen_sibling_ids = set()
        for sibling_id in self.get_sibling_ids_for(actor_id):
            if sibling_id in seen_sibling_ids:
                continue
            sibling = self.get_actor(sibling_id)
            if sibling is None or not sibling.is_alive():
                continue
            sibling_entries.append(
                {
                    "name": sibling.get_full_name(),
                    "role": self._get_family_role_label_for("sibling", sibling),
                    "role_key": "sibling",
                }
            )
            seen_sibling_ids.add(sibling_id)

        parent_entries = []
        parent_ids = self.get_parent_ids_for(actor_id)
        for role in ("mother", "father"):
            parent_id = parent_ids[f"{role}_id"]
            if parent_id is None:
                continue
            parent = self.get_actor(parent_id)
            if parent is None or not parent.is_alive():
                continue
            parent_entries.append(
                {
                    "name": parent.get_full_name(),
                    "role": self._get_family_role_label_for(role, parent),
                    "role_key": role,
                }
            )

        return {
            "siblings": sibling_entries,
            "parents": parent_entries,
        }

    def _build_lineage_relationship_label(self, actor_id, linked_actor_id, links):
        """Builds one display-ready relationship label for lineage surfaces."""
        sibling_label = self._get_sibling_relationship_label(actor_id, linked_actor_id)
        if sibling_label is not None:
            return sibling_label

        actor_perspective_links = [
            link for link in links
            if link.get("source_id") == actor_id and link.get("target_id") == linked_actor_id
        ]
        defining_link_pool = actor_perspective_links or links
        defining_link = sorted(defining_link_pool, key=self._get_continuity_link_sort_key)[0]
        link_role = defining_link.get("role")
        if link_role:
            return str(link_role).replace("_", " ").title()
        link_type = defining_link.get("type")
        return str(link_type).replace("_", " ").title() if link_type else "Connected"

    def _derive_family_branch_label(self, actor_id, links):
        """Builds one honest lightweight family-side label from current family-link truth."""
        outgoing_roles = {
            link.get("role")
            for link in links
            if link.get("source_id") == actor_id and link.get("type") == "family"
        }
        incoming_roles = {
            link.get("role")
            for link in links
            if link.get("target_id") == actor_id and link.get("type") == "family"
        }

        if "mother" in outgoing_roles:
            return "Maternal"
        if "father" in outgoing_roles:
            return "Paternal"
        if "child" in incoming_roles:
            return "Descendant"
        return None

    def _build_lineage_entry(self, actor_id, linked_actor_id, links):
        """Builds one lineage entry for a family-linked actor connected to the current actor."""
        linked_actor = self.get_actor(linked_actor_id)
        if linked_actor is None or not links:
            return None

        lifecycle_year = self.current_year
        lifecycle_month = self.current_month
        if (
            not linked_actor.is_alive()
            and linked_actor.death_year is not None
            and linked_actor.death_month is not None
        ):
            lifecycle_year = linked_actor.death_year
            lifecycle_month = linked_actor.death_month

        lifecycle = linked_actor.get_lifecycle_state(lifecycle_year, lifecycle_month)
        current_place_name = self.get_place_name(linked_actor.current_place_id) or "Unknown"
        birth_date = self._format_year_month(linked_actor.birth_year, linked_actor.birth_month)
        death_date = self._format_year_month(linked_actor.death_year, linked_actor.death_month)

        return {
            "actor_id": linked_actor_id,
            "full_name": linked_actor.get_full_name(),
            "relationship_label": self._build_lineage_relationship_label(actor_id, linked_actor_id, links),
            "family_branch_label": self._derive_family_branch_label(actor_id, links),
            "is_alive": linked_actor.is_alive(),
            "structural_status": linked_actor.structural_status,
            "age": lifecycle["age_years"],
            "life_stage": lifecycle["life_stage"],
            "birth_date": birth_date,
            "death_date": death_date,
            "death_reason": linked_actor.death_reason,
            "current_place_name": current_place_name,
        }

    def get_lineage_entries_for(self, actor_id, *, filter_mode="all", search_text=""):
        """Returns family-linked lineage entries for one actor, including optional filtering/search."""
        if actor_id not in self.actors:
            raise ValueError(f"get_lineage_entries_for: unknown actor_id '{actor_id}'")

        lineage_links = {}
        for link in self.get_links(entity_id=actor_id):
            if link.get("type") != "family":
                continue

            linked_actor_id = None
            if link.get("source_id") == actor_id:
                linked_actor_id = link.get("target_id")
            elif link.get("target_id") == actor_id:
                linked_actor_id = link.get("source_id")

            if linked_actor_id is None or linked_actor_id == actor_id:
                continue

            lineage_links.setdefault(linked_actor_id, []).append(link)

        lineage_entries = []
        normalized_search = (search_text or "").strip().casefold()
        for linked_actor_id, links in lineage_links.items():
            lineage_entry = self._build_lineage_entry(actor_id, linked_actor_id, links)
            if lineage_entry is None:
                continue
            if filter_mode == "living" and not lineage_entry["is_alive"]:
                continue
            if filter_mode == "dead" and lineage_entry["is_alive"]:
                continue
            if normalized_search and normalized_search not in lineage_entry["full_name"].casefold():
                continue
            lineage_entries.append(lineage_entry)

        return sorted(
            lineage_entries,
            key=lambda entry: (
                entry.get("full_name", "").casefold(),
                entry.get("relationship_label", ""),
                entry.get("actor_id", ""),
            ),
        )

    def get_lineage_detail_for(self, actor_id, linked_actor_id, recent_record_limit=5):
        """Returns one lineage detail payload backed by the current actor/link/record truth."""
        if actor_id not in self.actors:
            raise ValueError(f"get_lineage_detail_for: unknown actor_id '{actor_id}'")

        lineage_entries = self.get_lineage_entries_for(actor_id)
        selected_entry = next(
            (entry for entry in lineage_entries if entry["actor_id"] == linked_actor_id),
            None,
        )
        if selected_entry is None:
            raise ValueError(
                f"get_lineage_detail_for: actor_id '{linked_actor_id}' is not a lineage entry for '{actor_id}'"
            )

        linked_actor = self.get_actor(linked_actor_id)
        actor_records = self.get_actor_records(linked_actor_id)
        recent_records = actor_records[-recent_record_limit:]
        record_summaries = [
            {
                "year": record.get("year"),
                "month": record.get("month"),
                "record_type": record.get("record_type"),
                "text": record.get("text"),
            }
            for record in reversed(recent_records)
        ]

        return {
            "summary": {
                "actor_id": linked_actor_id,
                "full_name": linked_actor.get_full_name(),
                "relationship_label": selected_entry["relationship_label"],
                "family_branch_label": selected_entry.get("family_branch_label"),
                "species": linked_actor.species,
                "sex": linked_actor.sex,
                "gender": linked_actor.gender,
                "is_alive": linked_actor.is_alive(),
                "structural_status": linked_actor.structural_status,
                "age": selected_entry["age"],
                "life_stage": selected_entry["life_stage"],
                "birth_date": selected_entry["birth_date"],
                "death_date": selected_entry["death_date"],
                "death_reason": selected_entry["death_reason"],
                "current_place_name": selected_entry["current_place_name"],
                "health": linked_actor.stats["health"],
                "happiness": linked_actor.stats["happiness"],
                "intelligence": linked_actor.stats["intelligence"],
                "money": linked_actor.money,
            },
            "records": record_summaries,
        }

    def get_lineage_browser_data_for(self, actor_id, *, filter_mode="all", search_text="", recent_record_limit=5):
        """Builds one structured lineage-browser payload for the TUI shell."""
        lineage_entries = self.get_lineage_entries_for(
            actor_id,
            filter_mode=filter_mode,
            search_text=search_text,
        )

        selected_detail = None
        if lineage_entries:
            selected_detail = self.get_lineage_detail_for(
                actor_id,
                lineage_entries[0]["actor_id"],
                recent_record_limit=recent_record_limit,
            )

        return {
            "actor_id": actor_id,
            "filter_mode": filter_mode,
            "search_text": search_text,
            "entries": lineage_entries,
            "result_count": len(lineage_entries),
            "selected_detail": selected_detail,
        }

    def _get_social_tier_label(self, closeness):
        """Returns the display tier label for a social link closeness value."""
        if closeness >= 70:
            return "Close Friend"
        if closeness >= 30:
            return "Friend"
        return "Acquaintance"

    def _build_relationship_social_entry(self, actor_id, linked_actor_id, link):
        """Builds one relationship entry for a social-link-connected actor."""
        linked_actor = self.get_actor(linked_actor_id)
        if linked_actor is None:
            return None

        lifecycle_year = self.current_year
        lifecycle_month = self.current_month
        if (
            not linked_actor.is_alive()
            and linked_actor.death_year is not None
            and linked_actor.death_month is not None
        ):
            lifecycle_year = linked_actor.death_year
            lifecycle_month = linked_actor.death_month

        lifecycle = linked_actor.get_lifecycle_state(lifecycle_year, lifecycle_month)
        current_place_name = self.get_place_name(linked_actor.current_place_id) or "Unknown"
        birth_date = self._format_year_month(linked_actor.birth_year, linked_actor.birth_month)
        death_date = self._format_year_month(linked_actor.death_year, linked_actor.death_month)
        meta = link.get("metadata", {})
        closeness = meta.get("closeness", 0)
        social_status = meta.get("status", "active")

        return {
            "actor_id": linked_actor_id,
            "full_name": linked_actor.get_full_name(),
            "relationship_label": self._get_social_tier_label(closeness),
            "family_branch_label": None,
            "is_alive": linked_actor.is_alive(),
            "structural_status": linked_actor.structural_status,
            "age": lifecycle["age_years"],
            "life_stage": lifecycle["life_stage"],
            "birth_date": birth_date,
            "death_date": death_date,
            "death_reason": linked_actor.death_reason,
            "current_place_name": current_place_name,
            "link_type": "social",
            "social_status": social_status,
            "closeness": closeness,
        }

    def get_relationship_entries_for(self, actor_id, filter_mode="all"):
        """Returns relationship entries (family + social) for the relationship browser."""
        if actor_id not in self.actors:
            raise ValueError(f"get_relationship_entries_for: unknown actor_id '{actor_id}'")

        entries = []
        seen_actor_ids = set()

        if filter_mode in ("all", "family", "living", "dead"):
            family_entries = self.get_lineage_entries_for(actor_id, filter_mode="all", search_text="")
            for entry in family_entries:
                entry = dict(entry)
                entry.setdefault("link_type", "family")
                entry.setdefault("social_status", None)
                entry.setdefault("closeness", None)
                seen_actor_ids.add(entry["actor_id"])
                if filter_mode == "living" and not entry["is_alive"]:
                    continue
                if filter_mode == "dead" and entry["is_alive"]:
                    continue
                entries.append(entry)

        if filter_mode in ("all", "friends", "former", "living", "dead"):
            social_links = self.get_links(source_id=actor_id, link_type="social")
            for link in social_links:
                target_id = link.get("target_id")
                if target_id is None or target_id in seen_actor_ids:
                    continue
                meta = link.get("metadata", {})
                social_status = meta.get("status", "active")
                if filter_mode == "friends" and social_status != "active":
                    continue
                if filter_mode == "former" and social_status != "former":
                    continue
                entry = self._build_relationship_social_entry(actor_id, target_id, link)
                if entry is None:
                    continue
                if filter_mode == "living" and not entry["is_alive"]:
                    continue
                if filter_mode == "dead" and entry["is_alive"]:
                    continue
                seen_actor_ids.add(target_id)
                entries.append(entry)

        return sorted(
            entries,
            key=lambda e: (
                e.get("full_name", "").casefold(),
                e.get("relationship_label", ""),
                e.get("actor_id", ""),
            ),
        )

    def get_relationship_detail_for(self, actor_id, linked_actor_id, recent_record_limit=5):
        """Returns one relationship detail payload for a family or social link actor."""
        if actor_id not in self.actors:
            raise ValueError(f"get_relationship_detail_for: unknown actor_id '{actor_id}'")

        entries = self.get_relationship_entries_for(actor_id)
        selected_entry = next(
            (e for e in entries if e["actor_id"] == linked_actor_id),
            None,
        )
        if selected_entry is None:
            return None

        linked_actor = self.get_actor(linked_actor_id)
        if linked_actor is None:
            return None

        actor_records = self.get_actor_records(linked_actor_id)
        recent_records = actor_records[-recent_record_limit:]
        record_summaries = [
            {
                "year": record.get("year"),
                "month": record.get("month"),
                "record_type": record.get("record_type"),
                "text": record.get("text"),
            }
            for record in reversed(recent_records)
        ]

        return {
            "summary": {
                "actor_id": linked_actor_id,
                "full_name": linked_actor.get_full_name(),
                "relationship_label": selected_entry["relationship_label"],
                "family_branch_label": selected_entry.get("family_branch_label"),
                "species": linked_actor.species,
                "sex": linked_actor.sex,
                "gender": linked_actor.gender,
                "is_alive": linked_actor.is_alive(),
                "structural_status": linked_actor.structural_status,
                "age": selected_entry["age"],
                "life_stage": selected_entry["life_stage"],
                "birth_date": selected_entry["birth_date"],
                "death_date": selected_entry["death_date"],
                "death_reason": selected_entry["death_reason"],
                "current_place_name": selected_entry["current_place_name"],
                "health": linked_actor.stats["health"],
                "happiness": linked_actor.stats["happiness"],
                "intelligence": linked_actor.stats["intelligence"],
                "money": linked_actor.money,
                "link_type": selected_entry.get("link_type", "family"),
                "social_status": selected_entry.get("social_status"),
                "closeness": selected_entry.get("closeness"),
            },
            "records": record_summaries,
        }

    def get_relationship_browser_data_for(self, actor_id, *, filter_mode="all", search_text="", recent_record_limit=5):
        """Builds one structured relationship-browser payload for the TUI shell."""
        entries = self.get_relationship_entries_for(actor_id, filter_mode=filter_mode)
        if search_text:
            normalized = search_text.strip().casefold()
            entries = [e for e in entries if normalized in e["full_name"].casefold()]
        selected_detail = None
        if entries:
            selected_detail = self.get_relationship_detail_for(
                actor_id,
                entries[0]["actor_id"],
                recent_record_limit=recent_record_limit,
            )
        return {
            "actor_id": actor_id,
            "filter_mode": filter_mode,
            "entries": entries,
            "result_count": len(entries),
            "selected_detail": selected_detail,
        }

    def apply_social_link_decay(self, focused_actor_id, shared_actor_ids=None):
        """Applies one month of closeness decay to active social links for the focused actor.

        shared_actor_ids: actor IDs that had a shared event this month (no decay for those).
        Returns a list of drift event dicts with keys: text, year, month.
        """
        if shared_actor_ids is None:
            shared_actor_ids = set()

        drift_events = []
        social_links = self.get_links(source_id=focused_actor_id, link_type="social")
        for link in social_links:
            meta = link.get("metadata", {})
            if meta.get("status") != "active":
                continue

            target_id = link.get("target_id")
            closeness = meta.get("closeness", 0)
            history_months = meta.get("closeness_history_months", 0)

            new_history = history_months + 1
            meta["closeness_history_months"] = new_history

            reverse_links = self.get_links(source_id=target_id, target_id=focused_actor_id, link_type="social")
            for rev_link in reverse_links:
                rev_meta = rev_link.get("metadata", {})
                if rev_meta.get("status") == "active":
                    rev_meta["closeness_history_months"] = new_history

            if target_id in shared_actor_ids:
                continue

            if new_history > 60:
                if new_history % 4 != 0:
                    continue
            elif new_history > 24:
                if new_history % 2 != 0:
                    continue

            closeness = max(0, closeness - 1)
            meta["closeness"] = closeness
            new_role = self._get_social_link_category(closeness)
            link["role"] = new_role

            for rev_link in reverse_links:
                rev_meta = rev_link.get("metadata", {})
                if rev_meta.get("status") == "active":
                    rev_meta["closeness"] = closeness
                    rev_link["role"] = new_role

            if closeness <= 0:
                meta["status"] = "former"
                link["role"] = "former"
                for rev_link in reverse_links:
                    rev_meta = rev_link.get("metadata", {})
                    rev_meta["status"] = "former"
                    rev_link["role"] = "former"

                target_actor = self.get_actor(target_id)
                target_name = target_actor.get_full_name() if target_actor else "Someone"
                drift_events.append({
                    "text": f"You and {target_name} have drifted apart.",
                    "year": self.current_year,
                    "month": self.current_month,
                })

        return drift_events

    def apply_outcome(self, actor_id, outcome):
        """Applies event outcome stat changes to the target actor, if found."""
        actor_obj = self.get_actor(actor_id)
        if not actor_obj:
            return

        stat_changes = outcome.get("stat_changes", {}) if outcome else {}
        for stat_name, change_value in stat_changes.items():
            actor_obj.modify_stat(stat_name, change_value)

    def _get_continuity_link_sort_key(self, link):
        """Returns the deterministic current ordering key for candidate-defining links."""
        role_priority_map = {
            "child": 0,
            "sibling": 1,
            "mother": 2,
            "father": 2,
        }
        return (
            link.get("type") or "",
            role_priority_map.get(link.get("role"), 9),
            link.get("role") or "",
            link.get("source_id") or "",
            link.get("target_id") or "",
        )

    def _build_continuity_candidate(self, actor_id, candidate_actor_id, links):
        """Builds one normalized continuity-candidate object from deterministic link context."""
        if candidate_actor_id is None or candidate_actor_id == actor_id:
            return None

        candidate_actor = self.get_actor(candidate_actor_id)
        if candidate_actor is None or not candidate_actor.is_alive():
            return None
        if not links:
            return None

        valid_links = []
        for link in links:
            link_type = link.get("type")
            if link_type == "social":
                social_status = link.get("metadata", {}).get("status", "active")
                if social_status != "active":
                    continue
            valid_links.append(link)

        if not valid_links:
            return None

        actor_perspective_links = [
            link for link in valid_links
            if link.get("source_id") == actor_id and link.get("target_id") == candidate_actor_id
        ]
        defining_link_pool = actor_perspective_links or valid_links
        defining_link = sorted(defining_link_pool, key=self._get_continuity_link_sort_key)[0]
        link_type = defining_link.get("type")
        link_role = defining_link.get("role")
        family_role_labels = {
            "mother": "Mother",
            "father": "Father",
            "child": "Child",
            "sibling": "Sibling",
        }
        sibling_label = self._get_sibling_relationship_label(actor_id, candidate_actor_id)
        if sibling_label is not None:
            relationship_label = sibling_label
        elif link_type == "family" and link_role in family_role_labels:
            relationship_label = family_role_labels[link_role]
        else:
            relationship_label = f"{link_type}/{link_role}" if link_role else str(link_type)
        lifecycle = candidate_actor.get_lifecycle_state(self.current_year, self.current_month)
        current_place_name = self.get_place_name(candidate_actor.current_place_id)
        return {
            "actor_id": candidate_actor_id,
            "full_name": candidate_actor.get_full_name(),
            "link_type": link_type,
            "link_role": link_role,
            "relationship_label": relationship_label,
            "relationship_priority": self._get_continuity_relationship_priority(
                actor_id,
                candidate_actor_id,
                link_type,
                link_role,
            ),
            "family_branch_label": self._derive_family_branch_label(actor_id, links),
            "structural_status": candidate_actor.structural_status,
            "is_alive": True,
            "age": lifecycle["age_years"],
            "life_stage": lifecycle["life_stage"],
            "current_place_name": current_place_name,
        }

    def _get_continuity_relationship_priority(self, actor_id, candidate_actor_id, link_type, link_role):
        """Returns a small closeness ordering for current continuation candidates."""
        if candidate_actor_id in self.get_sibling_ids_for(actor_id):
            return 1
        if link_type == "family" and link_role == "child":
            return 0
        if link_type == "family" and link_role in {"mother", "father"}:
            return 2
        if link_type == "family":
            return 3
        return 9

    def _get_continuity_candidate_sort_key(self, candidate):
        """Returns the deterministic current ordering key for continuity candidates."""
        return (
            candidate.get("relationship_priority", 9),
            candidate.get("full_name", "").casefold(),
            candidate.get("link_type") or "",
            candidate.get("link_role") or "",
            candidate.get("actor_id") or "",
        )

    def get_continuity_candidates_for(self, actor_id):
        """Returns structured living linked-actor continuity candidates for one actor."""
        if actor_id not in self.actors:
            raise ValueError(f"get_continuity_candidates_for: unknown actor_id '{actor_id}'")

        candidate_links = {}
        related_links = self.get_links(entity_id=actor_id)

        for link in related_links:
            candidate_actor_id = None

            if link.get("source_id") == actor_id:
                candidate_actor_id = link.get("target_id")
            elif link.get("target_id") == actor_id:
                candidate_actor_id = link.get("source_id")

            if candidate_actor_id is None or candidate_actor_id == actor_id:
                continue

            candidate_links.setdefault(candidate_actor_id, []).append(link)

        candidates = []
        for candidate_actor_id, links in candidate_links.items():
            candidate = self._build_continuity_candidate(actor_id, candidate_actor_id, links)
            if candidate is not None:
                candidates.append(candidate)

        return sorted(candidates, key=self._get_continuity_candidate_sort_key)

    def build_continuity_state_for(self, actor_id):
        """Builds a structured continuity-state snapshot for one actor."""
        actor = self.get_actor(actor_id)
        if actor is None:
            raise ValueError(f"build_continuity_state_for: unknown actor_id '{actor_id}'")

        continuity_candidates = self.get_continuity_candidates_for(actor_id)
        return {
            "actor_id": actor_id,
            "focus_actor_name": actor.get_full_name(),
            "focus_actor_structural_status": actor.structural_status,
            "focus_actor_death_year": actor.death_year,
            "focus_actor_death_month": actor.death_month,
            "focus_actor_death_reason": actor.death_reason,
            "is_dead": not actor.is_alive(),
            "universe_continues": True,
            "continuity_candidates": continuity_candidates,
            "continuity_candidate_ids": [candidate["actor_id"] for candidate in continuity_candidates],
            "had_continuity_candidates": bool(continuity_candidates),
        }

    def handoff_focus_to_continuation(self, from_actor_id, successor_actor_id):
        """Validates and switches focus from one dead actor to one living continuation target."""
        actor = self.get_actor(from_actor_id)
        if actor is None:
            raise ValueError(f"handoff_focus_to_continuation: unknown from_actor_id '{from_actor_id}'")
        if actor.is_alive():
            raise ValueError(
                f"handoff_focus_to_continuation: actor_id '{from_actor_id}' is not dead"
            )

        successor_actor = self.get_actor(successor_actor_id)
        if successor_actor is None:
            raise ValueError(
                f"handoff_focus_to_continuation: unknown successor_actor_id '{successor_actor_id}'"
            )
        if not successor_actor.is_alive():
            raise ValueError(
                f"handoff_focus_to_continuation: successor_actor_id '{successor_actor_id}' is not alive"
            )

        continuity_state = self.build_continuity_state_for(from_actor_id)
        if successor_actor_id not in continuity_state["continuity_candidate_ids"]:
            raise ValueError(
                "handoff_focus_to_continuation: successor_actor_id "
                f"'{successor_actor_id}' is not a valid continuity candidate for '{from_actor_id}'"
            )

        self.set_focused_actor(successor_actor_id)
        return {
            "previous_actor_id": from_actor_id,
            "previous_actor_name": actor.get_full_name(),
            "new_focused_actor_id": successor_actor_id,
            "new_focused_actor_name": successor_actor.get_full_name(),
        }

    def mark_actor_dead(self, actor_id, year=None, month=None, reason=None):
        """Marks one actor dead through a controlled world-owned structural transition path."""
        actor = self.get_actor(actor_id)
        if actor is None:
            raise ValueError(f"mark_actor_dead: unknown actor_id '{actor_id}'")
        if not actor.is_alive():
            raise ValueError(f"mark_actor_dead: actor_id '{actor_id}' is already dead")

        transition_year = self.current_year if year is None else year
        transition_month = self.current_month if month is None else month
        transition_reason = reason or "Unspecified"

        actor.structural_status = "dead"
        actor.death_year = transition_year
        actor.death_month = transition_month
        actor.death_reason = transition_reason

        continuity_state = self.build_continuity_state_for(actor_id)
        death_record_text = f"{actor.get_full_name()} died."
        if transition_reason != "Unspecified":
            death_record_text = f"{death_record_text} Cause: {transition_reason}."
        self.add_record(
            record_type="death",
            scope="actor",
            text=death_record_text,
            year=transition_year,
            month=transition_month,
            actor_ids=[actor_id],
            tags=["death", "structural_transition"],
            metadata={
                "reason": transition_reason,
                "had_focus": self.focused_actor_id == actor_id,
                "continuity_candidate_ids": continuity_state["continuity_candidate_ids"],
                "entry_method": "World.mark_actor_dead",
            },
        )
        return {
            "type": "death",
            "actor_id": actor_id,
            "year": transition_year,
            "month": transition_month,
            "reason": transition_reason,
        }

    def _get_monthly_old_age_death_probability(self, lifecycle_state):
        """Returns the current baseline monthly old-age death probability for one actor."""
        if lifecycle_state.get("life_stage_model") != "human_default":
            return 0.0

        age_months = lifecycle_state["age_months"]
        threshold_points = (
            (65 * 12, 0.0005),
            (75 * 12, 0.0025),
            (85 * 12, 0.0100),
            (95 * 12, 0.0350),
            (105 * 12, 0.1200),
            (115 * 12, 0.3500),
            (120 * 12, 1.0000),
        )

        if age_months < threshold_points[0][0]:
            return 0.0
        if age_months >= threshold_points[-1][0]:
            return threshold_points[-1][1]

        for lower_point, upper_point in zip(threshold_points, threshold_points[1:]):
            lower_age_months, lower_probability = lower_point
            upper_age_months, upper_probability = upper_point
            if age_months < upper_age_months:
                span_months = upper_age_months - lower_age_months
                progress = (age_months - lower_age_months) / span_months
                probability_delta = upper_probability - lower_probability
                return lower_probability + (probability_delta * progress)
        return 0.0

    def build_monthly_mortality_profile_for(self, actor_id):
        """Builds the current simulation-owned mortality profile for one living actor."""
        actor = self.get_actor(actor_id)
        if actor is None:
            raise ValueError(f"build_monthly_mortality_profile_for: unknown actor_id '{actor_id}'")
        if not actor.is_alive():
            return None

        lifecycle_state = actor.get_lifecycle_state(self.current_year, self.current_month)
        old_age_probability = self._get_monthly_old_age_death_probability(lifecycle_state)
        if old_age_probability <= 0:
            return None

        return {
            "actor_id": actor_id,
            "reason": "Old age",
            "monthly_death_probability": old_age_probability,
            "rule": "baseline_old_age",
            "lifecycle_state": lifecycle_state,
        }

    def resolve_monthly_mortality(self):
        """Applies one month of mortality checks across all living actors."""
        structural_transitions = []
        for actor_id in sorted(self.actors):
            actor = self.get_actor(actor_id)
            if actor is None or not actor.is_alive():
                continue

            mortality_profile = self.build_monthly_mortality_profile_for(actor_id)
            if mortality_profile is None:
                continue

            death_probability = mortality_profile["monthly_death_probability"]
            if death_probability < 1.0 and random.random() >= death_probability:
                continue

            structural_transition = self.mark_actor_dead(
                actor_id,
                year=self.current_year,
                month=self.current_month,
                reason=mortality_profile["reason"],
            )
            structural_transition["rule"] = mortality_profile["rule"]
            structural_transition["age_years"] = mortality_profile["lifecycle_state"]["age_years"]
            structural_transition["age_months"] = mortality_profile["lifecycle_state"]["age_months"]
            structural_transitions.append(structural_transition)

        return structural_transitions

    def simulate_advance_turn(self, player_id: str, months_to_advance: int) -> dict:
        """
        World-owned authoritative simulation-step boundary.
        Advances time month-by-month, collects events, applies outcomes, and writes event records.
        """
        collected_structured_events = []
        focused_actor_id = self.get_focused_actor_id() or player_id
        if self.get_focused_actor_id() is None and focused_actor_id in self.actors:
            self.set_focused_actor(focused_actor_id)
        if focused_actor_id not in self.actors:
            raise ValueError(f"simulate_advance_turn: unknown actor_id '{focused_actor_id}'")

        structural_transition = None
        continuity_state = None
        focused_actor = self.get_actor(focused_actor_id)
        months_advanced = 0
        recent_event_ids = deque(maxlen=3)

        if focused_actor is not None and not focused_actor.is_alive():
            continuity_state = self.build_continuity_state_for(focused_actor_id)
            return {
                "months_advanced": months_advanced,
                "events": collected_structured_events,
                "had_any_events": False,
                "focused_actor_id": focused_actor_id,
                "focused_actor_alive": False,
                "structural_transition": structural_transition,
                "continuity_state": continuity_state,
                "advancement_blocked": True,
                "advancement_block_reason": "focused_actor_dead",
            }

        for _ in range(months_to_advance):
            self.advance_months(1)
            months_advanced += 1

            monthly_structural_transitions = self.resolve_monthly_mortality()
            focused_actor_transition = next(
                (
                    transition
                    for transition in monthly_structural_transitions
                    if transition["actor_id"] == focused_actor_id
                ),
                None,
            )
            if focused_actor_transition is not None:
                structural_transition = focused_actor_transition

            focused_actor = self.get_actor(focused_actor_id)
            if focused_actor is None or not focused_actor.is_alive():
                continuity_state = self.build_continuity_state_for(focused_actor_id)
                break

            family_event_result = self.resolve_monthly_family_events(focused_actor_id=focused_actor_id)
            for surfaced_event in family_event_result["surfaced_events"]:
                self.apply_outcome(focused_actor_id, surfaced_event.get("outcome"))
                self.add_record(
                    record_type="event",
                    scope="actor",
                    text=surfaced_event.get("text"),
                    year=surfaced_event.get("year"),
                    month=surfaced_event.get("month"),
                    actor_ids=[focused_actor_id],
                    tags=surfaced_event.get("tags") or [],
                    metadata={
                        "event_id": surfaced_event.get("event_id"),
                        "entry_method": "World.resolve_monthly_family_events",
                    },
                )
                collected_structured_events.append(surfaced_event)
                surfaced_event_id = surfaced_event.get("event_id")
                if surfaced_event_id:
                    recent_event_ids.append(surfaced_event_id)

            lifecycle_state_for_event = focused_actor.get_lifecycle_state(
                self.current_year,
                self.current_month,
            )
            family_context_for_event = self._build_family_event_context_for(focused_actor_id)
            actor_traits_for_event = list(getattr(focused_actor, "traits", []) or [])
            structured_event_for_month = get_human_monthly_event_from_lifecycle(
                lifecycle_state_for_event,
                self.current_year,
                self.current_month,
                family_context=family_context_for_event,
                recent_event_ids=recent_event_ids,
                actor_traits=actor_traits_for_event,
            )
            if structured_event_for_month:
                self.apply_outcome(focused_actor_id, structured_event_for_month.get("outcome"))
                self.add_record(
                    record_type="event",
                    scope="actor",
                    text=structured_event_for_month.get("text"),
                    year=structured_event_for_month.get("year"),
                    month=structured_event_for_month.get("month"),
                    actor_ids=[focused_actor_id],
                    tags=structured_event_for_month.get("tags") or [],
                    metadata={
                        "event_id": structured_event_for_month.get("event_id"),
                        "entry_method": "World.simulate_advance_turn",
                    },
                )
                collected_structured_events.append(structured_event_for_month)
                structured_event_id = structured_event_for_month.get("event_id")
                if structured_event_id:
                    recent_event_ids.append(structured_event_id)

        focused_actor = self.get_actor(focused_actor_id)
        focused_actor_alive = focused_actor.is_alive() if focused_actor is not None else False
        if focused_actor is not None and not focused_actor_alive:
            continuity_state = self.build_continuity_state_for(focused_actor_id)

        return {
            "months_advanced": months_advanced,
            "events": collected_structured_events,
            "had_any_events": bool(collected_structured_events),
            "focused_actor_id": focused_actor_id,
            "focused_actor_alive": focused_actor_alive,
            "structural_transition": structural_transition,
            "continuity_state": continuity_state,
            "advancement_blocked": False,
            "advancement_block_reason": None,
        }

def simulate_advance_turn(world, player_id: str, months_to_advance: int) -> dict:
    """Compatibility wrapper delegating to the world-owned simulation-step boundary."""
    return world.simulate_advance_turn(player_id, months_to_advance)
