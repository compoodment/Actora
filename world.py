from events import get_human_monthly_event_from_lifecycle
from human import Human

class World:
    """Represents the game world and manages its state."""
    def __init__(self, start_year, start_month=1):
        self.current_year = start_year
        self.current_month = start_month
        self.actors = {} # Stores actor objects by their unique ID (e.g., "player")
        self.links = []
        self.places = {}
        self.records = []

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

    def add_actor(self, actor_id, actor_obj):
        """Adds an actor to the world."""
        self.actors[actor_id] = actor_obj

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
        if current_place_id is not None:
            actor.current_place_id = current_place_id
        if residence_place_id is not None:
            actor.residence_place_id = residence_place_id
        self.add_actor(actor_id, actor)
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
        randomize_stats=False,
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
            randomize_stats=randomize_stats,
        )

        startup_family_metadata = {
            "is_origin_family": True,
            "is_caregiver_family": True,
            "bootstrap_source": "startup_family",
        }

        if mother_id is not None:
            self.add_link_pair(
                source_id=child_id,
                target_id=mother_id,
                forward_type="family",
                forward_role="mother",
                reverse_type="family",
                reverse_role="child",
                forward_metadata=dict(startup_family_metadata),
                reverse_metadata=dict(startup_family_metadata),
            )
        if father_id is not None:
            self.add_link_pair(
                source_id=child_id,
                target_id=father_id,
                forward_type="family",
                forward_role="father",
                reverse_type="family",
                reverse_role="child",
                forward_metadata=dict(startup_family_metadata),
                reverse_metadata=dict(startup_family_metadata),
            )

        actor_ids = [child_id]
        if mother_id is not None:
            actor_ids.append(mother_id)
        if father_id is not None:
            actor_ids.append(father_id)
        self.add_record(
            record_type="family_bootstrap",
            scope="actor",
            text=(
                f"{child.get_full_name()} was bootstrapped with current startup family links."
            ),
            year=birth_year,
            month=birth_month,
            actor_ids=actor_ids,
            tags=["family", "bootstrap"],
            metadata={
                "mother_id": mother_id,
                "father_id": father_id,
                "entry_method": "create_human_child_with_parents",
            },
        )

        return child
    
    def get_actor(self, actor_id):
        """Returns an actor object from the world by ID."""
        return self.actors.get(actor_id)

    def add_link(self, source_id, target_id, link_type, role, metadata=None):
        """Adds a directional link record between two entities."""
        link_record = {
            "source_id": source_id,
            "target_id": target_id,
            "type": link_type,
            "role": role,
        }
        if metadata is not None:
            link_record["metadata"] = metadata
        self.links.append(link_record)

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

    def get_outgoing_links(self, source_id, link_type=None, role=None):
        """Returns links where the specified entity is the source."""
        filtered = [link for link in self.links if link.get("source_id") == source_id]
        if link_type is not None:
            filtered = [link for link in filtered if link.get("type") == link_type]
        if role is not None:
            filtered = [link for link in filtered if link.get("role") == role]
        return filtered

    def get_incoming_links(self, target_id, link_type=None, role=None):
        """Returns links where the specified entity is the target."""
        filtered = [link for link in self.links if link.get("target_id") == target_id]
        if link_type is not None:
            filtered = [link for link in filtered if link.get("type") == link_type]
        if role is not None:
            filtered = [link for link in filtered if link.get("role") == role]
        return filtered

    def get_related_links(self, entity_id, link_type=None, role=None):
        """Returns all incoming and outgoing links for an entity."""
        related = [
            link
            for link in self.links
            if link.get("source_id") == entity_id or link.get("target_id") == entity_id
        ]
        if link_type is not None:
            related = [link for link in related if link.get("type") == link_type]
        if role is not None:
            related = [link for link in related if link.get("role") == role]
        return related

    def get_linked_ids(self, entity_id, direction="both", link_type=None, role=None):
        """Returns IDs linked to an entity based on direction and optional filters."""
        linked_ids = []

        if direction in ("outgoing", "both"):
            outgoing_links = self.get_outgoing_links(entity_id, link_type=link_type, role=role)
            linked_ids.extend(link["target_id"] for link in outgoing_links)

        if direction in ("incoming", "both"):
            incoming_links = self.get_incoming_links(entity_id, link_type=link_type, role=role)
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
        role_filter = set(roles) if roles is not None else None
        outgoing_links = self.get_outgoing_links(source_id, link_type=link_type)
        if role_filter is not None:
            outgoing_links = [link for link in outgoing_links if link.get("role") in role_filter]

        deduped_target_ids = []
        seen_ids = set()
        for link in outgoing_links:
            target_id = link.get("target_id")
            if target_id is not None and target_id not in seen_ids:
                seen_ids.add(target_id)
                deduped_target_ids.append(target_id)

        return deduped_target_ids

    def get_family_link_target_ids(
        self,
        source_id,
        roles=None,
        require_origin_family=None,
        require_caregiver_family=None,
        bootstrap_source=None,
    ):
        """Returns family target IDs filtered by current optional semantic metadata."""
        role_filter = set(roles) if roles is not None else None
        outgoing_family_links = self.get_outgoing_links(source_id, link_type="family")

        if role_filter is not None:
            outgoing_family_links = [
                link for link in outgoing_family_links if link.get("role") in role_filter
            ]

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

    def apply_outcome(self, actor_id, outcome):
        """Applies event outcome stat changes to the target actor, if found."""
        actor_obj = self.get_actor(actor_id)
        if not actor_obj:
            return

        stat_changes = outcome.get("stat_changes", {}) if outcome else {}
        for stat_name, change_value in stat_changes.items():
            actor_obj.modify_stat(stat_name, change_value)

    def simulate_advance_turn(self, player_id: str, months_to_advance: int) -> dict:
        """
        World-owned authoritative simulation-step boundary.
        Advances time month-by-month, collects events, applies outcomes, and writes event records.
        """
        collected_structured_events = []
        for _ in range(months_to_advance):
            self.advance_months(1)
            current_player_for_event = self.get_actor(player_id)
            if current_player_for_event is None:
                raise ValueError(f"simulate_advance_turn: unknown actor_id '{player_id}'")
            lifecycle_state_for_event = current_player_for_event.get_lifecycle_state(
                self.current_year,
                self.current_month,
            )
            structured_event_for_month = get_human_monthly_event_from_lifecycle(
                lifecycle_state_for_event,
                self.current_year,
                self.current_month,
            )
            if structured_event_for_month:
                self.apply_outcome(player_id, structured_event_for_month.get("outcome"))
                self.add_record(
                    record_type="event",
                    scope="actor",
                    text=structured_event_for_month.get("text"),
                    year=structured_event_for_month.get("year"),
                    month=structured_event_for_month.get("month"),
                    actor_ids=[player_id],
                    tags=structured_event_for_month.get("tags") or [],
                    metadata={
                        "event_id": structured_event_for_month.get("event_id"),
                        "entry_method": "World.simulate_advance_turn",
                    },
                )
                collected_structured_events.append(structured_event_for_month)

        return {
            "months_advanced": months_to_advance,
            "events": collected_structured_events,
            "had_any_events": bool(collected_structured_events),
        }

def simulate_advance_turn(world, player_id: str, months_to_advance: int) -> dict:
    """Compatibility wrapper delegating to the world-owned simulation-step boundary."""
    return world.simulate_advance_turn(player_id, months_to_advance)
