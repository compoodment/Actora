from events import get_human_monthly_event_from_lifecycle
from human import Human


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

    def _build_link_record(self, source_id, target_id, link_type, role, metadata=None):
        """Builds one normalized directional link record without mutating the link store."""
        return {
            "source_id": source_id,
            "target_id": target_id,
            "type": link_type,
            "role": role,
            "metadata": dict(metadata) if metadata is not None else {},
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
        return (
            link.get("type") or "",
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

        actor_perspective_links = [
            link for link in links
            if link.get("source_id") == actor_id and link.get("target_id") == candidate_actor_id
        ]
        defining_link_pool = actor_perspective_links or links
        defining_link = sorted(defining_link_pool, key=self._get_continuity_link_sort_key)[0]
        link_type = defining_link.get("type")
        link_role = defining_link.get("role")
        relationship_label = f"{link_type}/{link_role}" if link_role else str(link_type)
        return {
            "actor_id": candidate_actor_id,
            "full_name": candidate_actor.get_full_name(),
            "link_type": link_type,
            "link_role": link_role,
            "relationship_label": relationship_label,
            "structural_status": candidate_actor.structural_status,
            "is_alive": True,
        }

    def _get_continuity_candidate_sort_key(self, candidate):
        """Returns the deterministic current ordering key for continuity candidates."""
        return (
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
        self.add_record(
            record_type="death",
            scope="actor",
            text=f"{actor.get_full_name()} died.",
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

        if focused_actor is not None and not focused_actor.is_alive():
            continuity_state = self.build_continuity_state_for(focused_actor_id)
            return {
                "months_advanced": 0,
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
            lifecycle_state_for_event = focused_actor.get_lifecycle_state(
                self.current_year,
                self.current_month,
            )
            structured_event_for_month = get_human_monthly_event_from_lifecycle(
                lifecycle_state_for_event,
                self.current_year,
                self.current_month,
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

        focused_actor = self.get_actor(focused_actor_id)
        focused_actor_alive = focused_actor.is_alive() if focused_actor is not None else False
        if focused_actor is not None and not focused_actor_alive:
            continuity_state = self.build_continuity_state_for(focused_actor_id)

        return {
            "months_advanced": months_to_advance,
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
