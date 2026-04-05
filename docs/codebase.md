---
title: Codebase
tags: [implementation, reference, stable]
updated: 2026-04-04
through: v0.49.0
verified: 2026-04-04
---

# Actora Codebase

Current repo implementation truth. What the code looks like right now.
**Last verified against actual code:** 2026-04-04

**Version:** 0.45.0+
**Last Updated:** 2026-04-02

This document summarizes the currently implemented structure and behavior of the Actora repository.
It is intended to support safe patching, review, and manual verification, alongside [[controls]] and [[screens]] for interface-specific rules.

## 1. Stack

- **Language:** Python
- **Interface:** Terminal with a curses-based startup character creation wizard and a curses TUI shell for ordinary play. Shell v2 (v0.48.0): 5-row header chrome (title, screen/actor/date, state line with location+health+money, separators), body, footer with primary commands. Split Life View, dedicated profile screen, tabbed Browser (Relationships tab + History tab replacing older separate lineage/history screens), a dedicated Actions screen with social action support, death/continuation interrupts, skip-time utility flow, and meeting/social event popups
- **Structure:** Small modular prototype with separated simulation and rendering responsibilities

## 2. Current File Structure

    ./
    ├── main.py          (4388 lines - TUI, creation wizard, shell, rendering)
    ├── world.py          (2135 lines - simulation state, links, places, records, social links, mortality, advancement)
    ├── identity.py       (299 lines - name pools, culture-aware identity generation)
    ├── human.py          (295 lines - Human model, lifecycle, spatial, snapshot)
    ├── events.py         (388 lines - human monthly events, meeting events)
    └── docs/
        ├── architecture
        └── [[changelog]]

## 3. Core Objects

### World (`world.py`)
The `World` class stores shared simulation state, including world-owned focus, links, places, records, and the current simulation-step boundary.

Current fields:
- `current_year`
- `current_month`
- `actors`
- `links` (list of world-owned entity links)
- `places` (dictionary of world-owned place records)
- `records` (list of world-owned structured simulation records)
- `focused_actor_id`

Current methods:

- `add_actor(actor_id, actor_obj)`
- `set_focused_actor(actor_id)`
- `get_focused_actor_id()`
- `get_focused_actor()`
- `_build_record(record_type, scope, text, year, month, actor_ids=None, tags=None, metadata=None)`
- `add_record(record_type, scope, text, year, month, actor_ids=None, tags=None, metadata=None)`
- `get_records(scope=None, actor_id=None, record_type=None)`
- `get_actor_records(actor_id, record_type=None)`
- `get_latest_record(actor_id=None, record_type=None)`
- `get_records_by_tag(tag, actor_id=None)`
- `generate_actor_id(role)`
- `update_actor_spatial_identity(actor_id, *, current_place_id=UNSET, residence_place_id=UNSET, jurisdiction_place_id=UNSET, temporary_occupancy_place_id=UNSET)`
- `create_human_actor(actor_id, species, first_name, last_name, sex, gender, birth_year, birth_month, current_place_id=None, residence_place_id=None, jurisdiction_place_id=None, temporary_occupancy_place_id=None, randomize_stats=False)`
- `create_human_child_with_parents(child_id, first_name, last_name, sex, gender, mother_id, father_id, birth_year, birth_month, place_id, jurisdiction_place_id=None, temporary_occupancy_place_id=None, randomize_stats=False, family_link_source="startup_family", birth_record_type="family_bootstrap", birth_record_text=None, birth_record_tags=None, birth_record_metadata=None)`
- `get_actor(actor_id)`
- `_build_link_record(source_id, target_id, link_type, role, metadata=None)`
- `advance_months(months)`
- `add_link(source_id, target_id, link_type, role, metadata=None)`
- `add_link_pair(source_id, target_id, forward_type, forward_role, reverse_type, reverse_role, forward_metadata=None, reverse_metadata=None)`
- `get_links(source_id=None, target_id=None, entity_id=None, direction="both", link_type=None, role=None, roles=None)`
- `get_outgoing_links(source_id, link_type=None, role=None)`
- `get_incoming_links(target_id, link_type=None, role=None)`
- `get_related_links(entity_id, link_type=None, role=None)`
- `get_linked_ids(entity_id, direction="both", link_type=None, role=None)`
- `get_link_target_ids(source_id, link_type=None, roles=None)`
- `get_family_link_target_ids(source_id, roles=None, require_origin_family=None, require_caregiver_family=None, bootstrap_source=None)`
- `get_origin_parent_ids_for(entity_id)`
- `get_caregiver_parent_ids_for(entity_id)`
- `get_parent_ids_for(entity_id)` (human-specific compatibility wrapper)
- `get_sibling_ids_for(actor_id)`
- `add_place(place_id, name, kind, parent_place_id=None, metadata=None)`
- `get_place(place_id)`
- `get_place_name(place_id)`
- `get_place_kind(place_id)`
- `get_child_places(parent_place_id)`
- `get_place_lineage(place_id, include_self=True)`
- `get_nearest_place_of_kind(place_id, kind, include_self=True)`
- `apply_outcome(actor_id, outcome)`
- `get_continuity_candidates_for(actor_id)`
- `get_lineage_browser_data_for(actor_id, *, filter_mode="all", search_text="", recent_record_limit=5)`
- `build_continuity_state_for(actor_id)`
- `handoff_focus_to_continuation(from_actor_id, successor_actor_id)`
- `handoff_focus_to_continuation(...)` - controlled focus-switch after focused actor death
- `mark_actor_dead(...)` - structural death transition with preserved death record
- `build_monthly_mortality_profile_for(...)` - extension seam for health/lifestyle mortality tuning
- `resolve_monthly_mortality()` - baseline old-age mortality across all living actors
- `_get_social_link_category(closeness)` - derives social role from closeness value (acquaintance/friend/close_friend)
- `create_social_link_pair(...)` - creates bidirectional social links with closeness metadata
- `generate_meeting_npc(player_id, ...)` - generates and registers a plausible NPC for meeting events with culture-aware names/stats/traits
- `_get_social_tier_label(closeness)` - display label for social closeness tier
- `_build_relationship_social_entry(...)` - builds one relationship entry for a social-linked actor
- `get_relationship_entries_for(actor_id, filter_mode)` - relationship browser entries (family + social, with filter support: all/family/friends/past/living/dead)
- `get_relationship_detail_for(actor_id, linked_actor_id, ...)` - detailed relationship inspect data
- `get_relationship_browser_data_for(...)` - full browser payload for TUI relationship tab
- `apply_social_link_decay(focused_actor_id, ...)` - monthly closeness decay with history-based resistance; archives links at closeness 0 with `status: former`
- `bootstrap_older_siblings_for_newborn(...)` - startup sibling generation
- `resolve_monthly_family_events(focused_actor_id)` - monthly family birth/event simulation
- `simulate_advance_turn(player_id, months_to_advance)` - authoritative simulation-step boundary

### Human (`human.py`)
The `Human` class represents an individual simulation subject.

Current stored fields:
- `species`
- `first_name`
- `last_name`
- `sex`
- `gender`
- `sexuality` (`None` until emergence during play for the focused player; randomized for generated NPC humans)
- `birth_year`
- `birth_month`
- `stats` (dictionary containing: `health`, `happiness`, `intelligence`, `memory`, `stress`, `strength`, `charisma`, `imagination`, `wisdom`, `discipline`, `willpower`, `looks`, `fertility`) — implemented in code as of v0.48.2/v0.48.3
- `money`
- `appearance` (dictionary containing `eye_color`, `hair_color`, `skin_tone`)
- `traits` (list of list of 4 personality traits from the 12-trait pool (Driven, Chill, Curious, Social, Disciplined, Impulsive, Empathetic, Resilient, Introverted, Extraverted, Restless, Ambitious). Each trait has mechanical definitions in TRAIT_DEFINITIONS)
- `current_place_id`
- `residence_place_id`
- `jurisdiction_place_id`
- `temporary_occupancy_place_id`
- `structural_status`
- `death_year`
- `death_month`
- `death_reason`

Current responsibilities:
- identity storage
- birth-date storage
- derived name access (`get_full_name()`)
- derived lifecycle access (`get_lifecycle_state(...)`)
- stat modification (`modify_stat(...)`)
- spatial access/query boundary (`get_spatial_state(world)`)
- structural life/death state query (`is_alive()`, `get_structural_state()`)
- structured current-state snapshot data (`get_snapshot_data(current_year, current_month, world, actor_id)`)
- startup-default and generated appearance/trait storage for actor-facing profile display and future systems

Current Life View snapshot relationship details:
- snapshot `relationships` is now a list of living linked-family entries with shape `{"label": "...", "name": "..."}` rather than a fixed parent-name dictionary
- relationship entries are derived from the actor's current outgoing `family` links, deduped by linked actor ID, and dead relatives are omitted
- current label derivation stays intentionally narrow and human-readable (`Mother`, `Father`, `Brother` / `Sister` / `Sibling`, `Son` / `Daughter` / `Child`)

Current structural-state details:
- `structural_status` is the current storage truth for narrow actor structural state and currently uses `"active"` / `"dead"`
- `is_alive()` derives living state from `structural_status` instead of duplicating a separate stored boolean
- `death_year`, `death_month`, and `death_reason` remain `None` until a controlled structural death transition is applied
- this still does not implement archive state, inheritance, or broader lifecycle/death gameplay beyond the current baseline old-age mortality rule

Current stat-mutation boundary details:
- `modify_stat(...)` supports any key present in `self.stats` (currently `health`, `happiness`, `intelligence`, `memory`, `stress`, `strength`, `charisma`, `imagination`, `wisdom`, `discipline`, `willpower`, `looks`, `fertility`) and applies clamped mutation in the inclusive range 0-100.
- `modify_stat(...)` supports `"money"` through the separate unbounded money path (`self.money += change`).
- Any unsupported stat name now fails explicitly with `ValueError` (including the bad stat name) instead of being silently ignored.

Current startup creation flow details:
- `start_game()` now prints the title banner in plain text, then enters curses for a dedicated `CreationWizard`, then builds the world from the returned character payload, and only then hands control to the ordinary-play TUI.
- `CreationWizard` lives in `main.py` and currently owns six startup steps: identity, location, appearance, traits, stats, and confirmation.
- startup character payloads now include `first_name`, `last_name`, `sex`, `gender`, `country_id`, `city_id`, `appearance`, `traits`, and `stats`
- player startup world creation now routes through `setup_initial_world_from_character(...)`, which hydrates the full real-world place registry from module-level `WORLD_GEOGRAPHY`, while the older `setup_initial_world(...)` still exists as a compatibility wrapper for callers that pass only the older four identity values

## 4. Relationships

Relationship truth is owned by `World.links`.

Minimal link record shape:

```
{
    "source_id": "...",
    "target_id": "...",
    "type": "...",
    "role": "...",
    "metadata": {}
}
```

`metadata` remains an optional input when constructing links, and `World.links` remains the storage truth for current relationship data. Stored link records are now normalized so `metadata` is always present as a dictionary.

Current family parent/child records still use directional family roles (`mother`, `father`, and reverse `child`), but child creation through `create_human_child_with_parents(...)` now carries explicit semantic metadata for both startup bootstrap and later family births:
- `is_origin_family` - marks that the link is expressing origin semantics
- `is_caregiver_family` - marks that the link is expressing current caregiving semantics
- `bootstrap_source="startup_family"` or `bootstrap_source="family_birth"` - marks whether the link came from startup bootstrap or later family birth flow

Current family examples therefore look like:
- `{"source_id": "startup_player_ab12cd34", "target_id": "startup_mother_ef56gh78", "type": "family", "role": "mother", "metadata": {"is_origin_family": True, "is_caregiver_family": True, "bootstrap_source": "startup_family"}}`
- `{"source_id": "startup_mother_ef56gh78", "target_id": "startup_player_ab12cd34", "type": "family", "role": "child", "metadata": {"is_origin_family": True, "is_caregiver_family": True, "bootstrap_source": "startup_family"}}`
- `{"source_id": "family_child_qr34st56", "target_id": "startup_player_ab12cd34", "type": "family", "role": "sibling", "metadata": {"is_close_family": True, "family_relation": "sibling", "bootstrap_source": "shared_parents"}}`
- `{"source_id": "startup_mother_ef56gh78", "target_id": "startup_father_ij90kl12", "type": "association", "role": "coparent", "metadata": {"bootstrap_source": "startup_coparent_association"}}`

Reverse family links are still stored explicitly, direct sibling links are now also stored explicitly once siblings exist, link records still reference entity IDs present in `World.actors`, and this remains a narrow family semantic clarification rather than a broader relationship framework. It does not implement adoption, guardianship, household simulation, or species-general relationship architecture.

Current monthly family-event context details:
- `World._build_family_event_context_for(actor_id)` currently derives living `siblings` and `parents` lists for the focused actor before monthly event selection
- each family-context member currently carries `name`, display `role`, and narrow matching key `role_key`
- current family-aware monthly events only become eligible when at least one required living family role is present, and event text can render `{family_name}` / `{family_role}` placeholders from the chosen relative

### Social Links (v0.45.0+)

Social link truth is also owned by `World.links`, using `type: "social"` with roles derived from closeness:
- `acquaintance` (closeness 1-29)
- `friend` (closeness 30-69)
- `close_friend` (closeness 70-100)

Social link metadata shape:
```
{
    "closeness": 50,
    "status": "active",
    "closeness_history_months": 0,
    "met_year": 1,
    "met_month": 1,
    "met_place_id": "..."
}
```

Social link behaviors:
- `create_social_link_pair(...)` creates bidirectional social links with closeness and meeting context
- `generate_meeting_npc(...)` creates a plausible NPC with culture-aware names, randomized stats/traits, and registers them in the world
- `apply_social_link_decay(...)` runs monthly closeness decay with history-based resistance (longer friendships decay slower); when closeness reaches 0, the link is archived with `metadata.status = "former"` and a drift event fires
- Friend deaths affect player happiness scaled to closeness
- Continuation candidates exclude former social links (`metadata.status != "active"`)
- Player-facing label for archived/former social ties is `Past`

Current social link rendering:
- Life View left panel shows social links as `name · tier` entries in the Relationships section
- Relationship Browser (replacing Lineage Browser) shows family + social links with filter sidebar: All / Family / Friends / Past / Living / Dead
- Actions screen provides "Spend time with friend" social action

Current continuity-candidate boundary:
- `get_continuity_candidates_for(actor_id)` scans current related links, resolves the linked living actors, excludes the actor itself, dedupes candidates, and returns small structured candidate objects
- current candidate objects contain `actor_id`, `full_name`, `link_type`, `link_role`, `relationship_label`, `structural_status`, `is_alive`, `age`, `life_stage`, and `current_place_name`
- sibling candidates are now recognized from shared-parent truth and rendered with direct simple labels (`Brother` / `Sister`) instead of generic link text
- family parents/children now also use direct fallback labels (`Mother`, `Father`, `Child`, `Sibling`) before any generic `type/role` rendering path
- current candidate labeling and ordering are deterministic: candidate-defining link context is chosen by a stable link sort key, and final candidate ordering now applies a small closeness priority before (`full_name`, `link_type`, `link_role`, `actor_id`) so siblings rank ahead of less-close linked actors
- continuity candidate gathering now delegates through the generic world-owned `get_links(...)` seam, so current candidates can come from any stored link type even though startup only seeds family links plus one direct parent-to-parent `association/coparent` pair
- `handoff_focus_to_continuation(...)` is the current world-owned validation/mutation seam for switching focus after the focused actor is dead
- `get_lineage_entries_for(actor_id, *, filter_mode="all", search_text="")` and `get_lineage_detail_for(actor_id, linked_actor_id, recent_record_limit=5)` now provide the lineage/archive access seam on top of the current actor/link/record truth without splitting dead actors into a separate physical archive store
- `get_lineage_browser_data_for(...)` now adds one small world-owned browser payload for the TUI so filtering/search/detail selection do not have to be reconstructed as ad hoc shell string hacks
- lineage entries now also expose a lightweight `family_branch_label` when it can be derived honestly from current directional family-link roles (`mother` => maternal, `father` => paternal, reverse `child` => descendant); this is intentionally narrow and is not a full genealogy/tree system
- this still does not implement weighting, succession rules, archive state, full lineage systems, or a broader connected-actor prioritization framework

Record storage truth is owned by `World.records`.

Minimal record shape:

```
{
    "record_type": "...",
    "scope": "...",
    "text": "...",
    "year": 1,
    "month": 1,
    "actor_ids": [],
    "tags": [],
    "metadata": {}
}
```

Current record helper contract:

- `_build_record(...)` is the internal normalization helper behind `add_record(...)`. It builds one record dictionary with the explicit current shape (`record_type`, `scope`, `text`, `year`, `month`, `actor_ids`, `tags`, `metadata`) and normalizes optional fields so `actor_ids`/`tags` are always lists and `metadata` is always a dictionary.
- `add_record(...)` delegates record construction to `_build_record(...)`, appends the normalized record to `World.records`, and returns the created record.
- `get_records(scope=None, actor_id=None, record_type=None)` returns stored records filtered by optional scope, actor membership, and record type without changing insertion order.
- `get_actor_records(actor_id, record_type=None)` is a narrow world-owned wrapper over `get_records(...)` for actor-scoped access without repeating ad hoc filtering elsewhere.
- `get_latest_record(actor_id=None, record_type=None)` scans the current insertion-ordered record store from newest to oldest and returns the latest matching record or `None`.
- `get_records_by_tag(tag, actor_id=None)` returns insertion-ordered records whose `tags` contain the requested tag, with optional actor membership filtering.

These helpers are layered directly on top of the existing `World.records` list, and the current record shape is explicitly normalized through the world layer before storage. They do not add indexes, record IDs, persistence, schema validation frameworks, archive systems, memory systems, or history UI.

Current structural-death record details:
- `mark_actor_dead(...)` writes a `death` record with `tags=["death", "structural_transition"]`
- current death-record metadata includes `reason`, `had_focus`, `continuity_candidate_ids`, and `entry_method="World.mark_actor_dead"`
- this makes death a preserved structural record rather than only terminal text

Actor entry helpers:

- `update_actor_spatial_identity(...)` is the current world-owned mutation seam for actor spatial identity. It validates actor existence, validates any provided non-`None` place IDs against the world place registry, allows explicit `None` where current structure permits it, leaves unspecified fields untouched through an internal `UNSET` sentinel, and returns a small structured change summary.
- `create_human_actor(...)` is the current world-owned actor creation/registration path for startup actors, and it is explicitly human-backed. It directly constructs a `Human`, optionally randomizes starting stats, registers the actor via `add_actor(...)`, applies any startup spatial identity through `update_actor_spatial_identity(...)`, writes an `actor_entry` record with `entry_method="create_human_actor"`, and returns the created actor.
- `create_human_child_with_parents(...)` remains a narrow human-family helper layered on top of `create_human_actor(...)`. It creates the child in the provided place, currently assigns the same place as both current and residence, optionally assigns separate jurisdiction and temporary occupancy context, adds explicit mother/father family link pairs when IDs are provided, creates direct sibling links from shared-parent truth, and writes either startup-bootstrap or ordinary birth records depending on the caller. No generic actor constructor, species framework, adoption system, guardianship system, or broader origin framework is currently implemented.

Basic world link helper contract:

- `_build_link_record(...)` is the internal normalization seam for one link dictionary. It always produces the standard shape (`source_id`, `target_id`, `type`, `role`, `metadata`) and normalizes `metadata` to a dictionary.
- `add_link(...)` delegates through `_build_link_record(...)`, appends one normalized directional link, and returns the created link record.
- `add_link_pair(...)` remains the explicit bidirectional helper and now naturally flows through the same normalized `add_link(...)` path for both records.
- `get_links(...)` is the small general world-owned query seam. It filters by optional `source_id`, `target_id`, `entity_id` plus `direction`, `link_type`, `role`, or `roles` without mutating world state.
- `get_outgoing_links(...)`, `get_incoming_links(...)`, and `get_related_links(...)` are thin wrappers over `get_links(...)`.
- `get_link_target_ids(source_id, link_type=None, roles=None)` provides generic retrieval of linked target IDs from outgoing links with optional type/role filtering.
- `get_family_link_target_ids(...)` adds narrow semantic filtering on top of the same `World.links` store for current family-link metadata checks.
- `get_origin_parent_ids_for(entity_id)` resolves origin-marked mother/father links from outgoing family links.
- `get_caregiver_parent_ids_for(entity_id)` resolves caregiver-marked mother/father links from outgoing family links.
- `get_parent_ids_for(entity_id)` remains the compatibility wrapper for current mother/father access and falls back to bare family roles when explicit origin metadata is absent.

Basic world place helper contract:

- `add_place(...)` stores place records in the world-owned registry with explicit `parent_place_id`.
- `get_place(...)`, `get_place_name(...)`, and `get_place_kind(...)` remain the narrow direct lookup helpers.
- `get_child_places(parent_place_id)` returns the current direct child place records for one parent.
- `get_place_lineage(place_id, include_self=True)` walks from a place upward through its parent chain and returns that current lineage.
- `get_nearest_place_of_kind(place_id, kind, include_self=True)` resolves the closest matching place in that lineage and is the current ancestry-aware lookup seam.
- This remains intentionally small and does not introduce travel, property, jurisdiction, movement, or map systems.

## Lifecycle System

Lifecycle state is derived, not stored. `Human.get_lifecycle_state(current_year, current_month)` returns a dictionary with `age_years`, `age_months`, `life_stage`, and `life_stage_model`. Life stages progress through: `Infant > Child > Teenager > Young Adult > Adult > Elder`. All lifecycle-dependent systems (events, mortality, identity emergence) consume this derived state rather than raw age fields.

## 5. Derived State

The following values are derived rather than persistently stored:
- full name (via `get_full_name()`)
- age in years
- age in months
- life stage
- current alive/dead boolean read (`is_alive()` derived from `structural_status`)

Current lifecycle derivation depends on:

- `World.current_year`
- `World.current_month`
- `Human.birth_year`
- `Human.birth_month`

Lifecycle access is formalized through `Human.get_lifecycle_state(current_year, current_month)`, which returns a dictionary containing:

- `age_years`
- `age_months`
- `life_stage`
- `life_stage_model` (currently `"human_default"`)

Legacy helpers (`get_age`, `get_age_in_months`, `get_human_life_stage`) remain for compatibility but internally delegate to `get_lifecycle_state`. Future systems should use `get_lifecycle_state` directly.

Spatial access/query is formalized through `Human.get_spatial_state(world)`, which returns a dictionary containing:

- `current_place_id`
- `current_place_name`
- `current_place_kind`
- `residence_place_id`
- `residence_place_name`
- `residence_place_kind`
- `jurisdiction_place_id`
- `jurisdiction_place_name`
- `jurisdiction_place_kind`
- `temporary_occupancy_place_id`
- `temporary_occupancy_place_name`
- `temporary_occupancy_place_kind`
- `current_world_body_id`
- `current_world_body_name`

This helper is read-only and does not mutate human or world state. It keeps current location, residence, governing jurisdiction, and temporary occupancy separate without introducing travel, property, or politics simulation behavior.

Current structural-state access is formalized through `Human.get_structural_state()`, which returns a dictionary containing:

- `structural_status`
- `is_alive`
- `death_year`
- `death_month`
- `death_reason`

Current snapshot access is formalized through `Human.get_snapshot_data(current_year, current_month, world, actor_id)`, which returns a structured dictionary with the current shell-rendered sections:

- `identity` (`full_name`, `species`, `sex`, `gender`, `sexuality`, `age`, `life_stage`)
- `time` (`year`, `month`)
- `location` (`world_body_name`, `current_place_name`, `current_place_kind`, `jurisdiction_place_name`, `jurisdiction_place_kind`)
- `statistics` (`health`, `happiness`, `intelligence`, `money`)
- `secondary_statistics` (`strength`, `charisma`, `imagination`, `memory`, `wisdom`, `discipline`, `willpower`, `stress`, `looks`, `fertility`)
- `relationships` (list of living-family entries with `label` and `name`)
- `structural` (`structural_status`, `is_alive`, `death_year`, `death_month`, `death_reason`)

This helper is read-only, resolves living family relationships through current world links, resolves `world_body_name` through place ancestry rather than assuming the current place is itself a world body, and preserves the current `"Unknown"` fallback for unresolved place names. The shell keeps Life View narrow by rendering only the primary `statistics` block there, while the dedicated profile screen consumes both `statistics` and `secondary_statistics`.

## 6. Module Responsibilities

### `main.py`
Responsible for:
- plain-text startup flow
- plain-text to curses TUI orchestration
- character creation flow
- initial world setup flow
- curses-driven actor-first ordinary play flow
- screen-level visual-system orchestration for the current TUI
- post-turn rendering orchestration
- shell-owned post-turn identity-choice emergence checks
- rendering TUI snapshots from structured snapshot data
- converting structured event results into display text
- rendering the shell-owned dead-focus interrupt and continuation handoff flow when present
- rendering lineage list/detail browsing without typed command words
- rendering a tabbed Browser shell (Relationships tab + History tab) that replaced the older separate lineage and history screens
- rendering a dedicated Actions screen with Social and Personal action categories, sub-type picker popups, time budget display, and pending action queue
- rendering meeting event popups where the player can choose to introduce themselves or keep to themselves
- social action queueing ("Spend time with friend") and resolution on month advance

Current shell-level functions:
- `build_snapshot_sections(...)` - shell-owned transformation from structured snapshot data into TUI-ready section lines
- `build_event_log_entry(...)` / `format_history_entry(...)` - shell-owned live-feed and full-history entry shaping for the accumulating event log
- `build_death_lines(...)` - shell-owned dead-focus interrupt copy assembly
- `build_screen_chrome(...)` - shell-owned title/subtitle/date chrome assembly for the current TUI screen, including the history browser
- `draw_text_block(...)` - small curses text rendering helper with wrapping support
- `ActoraTUI` — curses shell object managing the split Life View, dedicated profile screen, accumulating live event feed, tabbed Browser (Relationships + History), dedicated Actions screen with social action support, styled header/footer chrome, lineage list/detail, skip-time selection, death acknowledgment, two-step continuation inspection/selection, meeting event popups, simple left-pane/profile/history scrolling, a shell-owned pending-choice popup overlay for major player-facing decisions, and safe footer rendering that avoids writing into the terminal's last column
- `EXERCISE_SUBTYPES`, `READ_SUBTYPES`, `REST_SUBTYPES` — module-level sub-type definition lists with `id`, `label`, `time_cost`, `stat_changes`, `event_text`
- `EXERCISE_TIME_COST`, `READ_TIME_COST`, `REST_TIME_COST` — module-level time cost constants
- `format_stat_change_summary(stat_changes)` — formats stat changes as plain "+Stat" labels for display
- `TRAIT_DEFINITIONS` — module-level dict mapping trait name → `{"sleep_modifier": float}` for all 12 traits
- `HANG_OUT_TIME_COST = 4` — module-level constant for Hang Out action time cost in hours
- `get_monthly_free_hours(actor)` — module-level helper; computes monthly free hours from actor traits: `720 - (8 + sleep_modifier_sum) * 30 - 120`
- `safe_input(prompt)` - narrow shared CLI input boundary helper that exits cleanly on `EOFError` and `KeyboardInterrupt`
- `CreationWizard` - curses-based character creation wizard with identity, location, appearance, and creation-mode steps, followed by either a questionnaire branch (questionnaire, confirmation) or a manual branch (stats, traits, confirmation)
- `setup_initial_world_from_character(character_data)` - primary world creation flow from one fully prepared startup character payload
- `setup_initial_world(...)` - compatibility wrapper that delegates into `setup_initial_world_from_character(...)`
- `run_creation_wizard()` - curses wrapper that runs `CreationWizard` and returns character data or `None`
- `run_game_tui(...)` - curses wrapper entry point for ordinary play
- `start_game()` - top-level orchestration (delegates to creation wizard and TUI)

Current startup flow is human-only. `start_game()` runs the curses-based `CreationWizard`, builds the world through `setup_initial_world_from_character(...)`, and only then hands control to the ordinary-play shell. Interactive CLI input still exits cleanly through the shared `safe_input(...)` helper when input is interrupted or closed (`KeyboardInterrupt` / `EOFError`) instead of surfacing a traceback. Startup actor IDs are now generated through the narrow `generate_startup_actor_id(...)` helper in `main.py` rather than reusing fixed singleton strings for mother, father, and player. Current startup IDs follow the `startup_<role>_<suffix>` pattern, such as `startup_mother_ab12cd34`, `startup_father_ef56gh78`, and `startup_player_ij90kl12`. Startup actor spatial identity is now applied through the world-owned `update_actor_spatial_identity(...)` seam instead of direct field pokes inside actor creation. Startup parent ages now vary within a narrow adult range, some worlds now generate older siblings before the player is born through `World.bootstrap_older_siblings_for_newborn(...)`, and only-child worlds still remain possible. Once startup completes, ordinary play now lives inside a curses shell: the split `Life View` keeps identity/location/primary stats/relationships (including social links as `name · tier`) on the left, keeps an accumulating live event feed on the right, opens a dedicated full-detail `Profile` screen via Menu, allows simple left-side/profile/history vertical scrolling under terminal-height pressure, opens the tabbed Browser via `[1]` Menu (Relationships tab or History tab), opens the dedicated Actions screen via `[1]` Menu, still preserves the dead-focus interrupt before any continuation choices are shown, and now allows shell-owned popup choices to interrupt long skips for major identity-emergence moments during adolescence and meeting events for social link creation.

### `identity.py`
Responsible for:
- approved parent first-name pools (`MOTHER_FIRST_NAME_POOL`, `FATHER_FIRST_NAME_POOL`)
- culture-aware parent naming pools (`CULTURE_NAME_POOLS`)
- approved fallback surname pool (`FALLBACK_LAST_NAME_POOL`)
- family surname resolution via `resolve_family_last_name(player_last_name)`
- structured identity-generation context prep via `prepare_parent_identity_context(...)`
- parent identity assembly via `generate_parent_identity_from_context(identity_context)`
- compatibility parent identity assembly via `generate_parent_identity(role, family_last_name, generation_context=None)`

Current boundary:
- returns small structured identity dictionaries for current mother/father generation
- now exposes a small structured context-prep seam so startup identity generation no longer depends only on loose positional inputs
- now resolves startup parent names through culture-specific first-name and surname pools when a supported `culture_group` is present, with the older global pools preserved as fallback
- does not construct `Human` objects
- does not yet implement era-aware or world-simulated identity generation beyond current startup culture selection
- remains human-only for the current startup identity path

### `world.py`
Responsible for:
- `World` model definition
- shared world state
- world-owned focused actor tracking (`focused_actor_id` plus focus helper methods)
- world-owned link storage and retrieval helpers (`World.links` and link helper/query methods), including narrow origin/caregiver access layered on the current family link metadata
- world-owned social link creation, closeness-based role derivation, NPC generation for meeting events, and monthly closeness decay with history-based resistance
- world-owned relationship browser data assembly (family + social entries, filter modes, detail inspect)
- world-owned place storage and minimal hierarchy/query helpers (`World.places` plus direct lookup, child lookup, lineage, and nearest-kind resolution)
- month advancement
- centralized application of event stat outcomes (`World.apply_outcome(...)`)
- world-owned continuity candidate resolution from the current link graph (excluding former social links)
- world-owned narrow family birth simulation for current coparent pairs using explicit simple age/spacing/family-size heuristics
- world-owned structural death transition handling (`World.mark_actor_dead(...)`)
- world-owned authoritative simulation-step boundary via `World.simulate_advance_turn(...)`, which advances month-by-month for the current living focused actor, requests monthly event data through the current human-scoped event seam, applies outcomes centrally, writes event records, runs social link decay, and assembles the structured turn result

### `human.py`
Responsible for:
- `Human` model definition
- human-derived calculations (including `get_lifecycle_state`)
- randomized starting statistics (`self.stats`)
- stat updates through `modify_stat(...)` (clamped supported stats, unbounded money, explicit `ValueError` on unsupported stat names)
- narrow structural-state storage (`structural_status`, `death_year`, `death_month`, `death_reason`)
- structural-state query helpers (`is_alive()`, `get_structural_state()`)
- structured current-state snapshot data assembly without terminal printing

### `events.py`
Responsible for:
- human-scoped monthly event content (`HUMAN_MONTHLY_EVENTS`)
- filtering the current human event pool from derived lifecycle state (`_get_human_eligible_events(...)`)
- returning complete structured event results through the implementation-facing helper `get_human_monthly_event_from_lifecycle(...)`
- preserving the existing public compatibility wrapper `get_monthly_event(...)` for the current event contract
- meeting event generation for social link creation (`get_meeting_event_for_player(...)`)

Current event boundary truth:
- current monthly event content remains explicitly human-scoped
- the derived-lifecycle helper seam reduces unnecessary direct coupling to the concrete `Human` model inside event selection
- this seam clarification does not mean species-general event support now exists
- the structured monthly event contract is unchanged: `event_id`, `text`, `outcome`, `tags`, `year`, and `month`
- there is still no top-level `stat_changes`; `outcome["stat_changes"]` remains the sole authoritative mutation payload
- ordinary-play mortality now comes from `world.py` structural checks rather than event payloads

### (banners removed)
`banners.py` has been removed. Startup and exit no longer render ASCII art banners; the TUI handles all presentation.

## 7. Simulation Boundary

`World.simulate_advance_turn(player_id, months_to_advance)` is the authoritative simulation-step boundary in `world.py`.

A thin module-level `simulate_advance_turn(world, player_id, months_to_advance)` compatibility wrapper still delegates directly to the world-owned method to preserve existing call stability where needed.

Current behavior:
- advances time month-by-month
- ensures the current focused actor ID is available for turn-result reporting
- uses the current focused actor as the event/snapshot advancement subject once focus exists
- resolves baseline old-age mortality across all living actors after each month advances
- requests monthly structured event data from `events.py`
- applies each returned event outcome centrally through `World.apply_outcome(...)`
- writes one preserved world-owned `event` record for each triggered monthly event after outcome application
- collects complete structured event results returned by `events.py`
- returns a structured result dictionary
- refuses ordinary advancement when the current focused actor is already dead and instead returns continuity-ready blocked-turn state

Current return keys:
- `months_advanced`
- `events` (list of structured event results, each containing `event_id`, `text`, `outcome`, `tags`, `year`, `month`)
- `had_any_events`
- `focused_actor_id`
- `focused_actor_alive`
- `structural_transition`
- `continuity_state`
- `advancement_blocked`
- `advancement_block_reason`

Current return-contract notes:
- `structural_transition` contains the focused actor death transition when the focused actor dies during advancement
- `continuity_state` is currently present when advancement is blocked because the focused actor is dead
- `advancement_block_reason` is currently `"focused_actor_dead"` for the dead-focus blocked path
- `months_advanced` reports real completed advancement, which may be lower than the requested skip when death interrupts the focused actor
- this patch now supports narrow playable continuation handoff with baseline automatic old-age mortality while still avoiding archive behavior or broader continuity systems

This function does not perform terminal input, output, or presentation formatting. Terminal presentation remains in `main.py` and consumes the returned structured result.

## 8. Current Turn Flow

1. Display ASCII art welcome title.
2. Run the curses startup wizard (`run_creation_wizard()` / `CreationWizard`) and collect the startup character payload.
3. Set up initial world state (`setup_initial_world_from_character(...)`).
4. Set the startup player as the world-owned focused actor.
5. Enter the curses shell (`run_game_tui(...)` / `ActoraTUI.run(...)`).
6. Render the initial `Life View` focused-actor snapshot screen.
7. Read one key-driven TUI action.
8. Resolve advance, skip-time, profile, browser (relationships/history), actions, continuation selection, back, or quit.
9. If the player requests a larger jump, resolve the shell-owned skip-time selection first.
10. Call `World.simulate_advance_turn(...)` when advancing.
11. Advance time internally month-by-month.
12. Apply triggered event outcomes through `World.apply_outcome(...)`.
13. Collect triggered structured events.
14. Run social link closeness decay via `World.apply_social_link_decay(...)`.
15. Check for meeting events and offer social introduction popups.
16. Fold triggered monthly events plus newly written relevant `birth` / `death` / `drift` records into the shell-owned event log while filtering hidden scaffolding records such as `actor_entry` and `family_bootstrap`.
17. If a major adolescence identity-emergence choice becomes due, open the shell-owned popup choice overlay and pause ordinary navigation.
18. If skip-time was interrupted by that choice, resume the remaining skipped months after the choice is resolved.
19. Re-render the updated `Life View`, `Profile`, `Browser`, `Actions`, or other active shell surface as needed.
20. If the focused actor is dead, render the dedicated death interrupt first.
21. Require acknowledgment before rendering any continuation choices.
22. Resolve continuation handoff or end the run cleanly.
23. Return to step 7.

## 9. Current Gameplay Behavior

### Character Creation
Current player creation includes:
- a curses-based `CreationWizard` with Identity, Location, Appearance, and Creation Mode, then either a questionnaire branch (`Questionnaire`, `Confirm`) or a manual branch (`Stats`, `Traits`, `Confirm`)
- Identity step with required first name and last name, and sex selection (`Male`, `Female`, `Intersex`)
- Location step with country selection first, then city selection within the chosen country; the selected `country_id` / `city_id` are stored in the startup payload
- gender defaults to match sex and is deferred to puberty emergence during play
- Appearance step with eye color, hair color, and skin tone; each appearance field supports `Other`, which requires a custom free-text value before continuing
- Creation Mode step with a choice between questionnaire-based generation and manual setup
- Questionnaire branch with 16 one-at-a-time prompts that derive startup stats and traits automatically (NOTE: currently broken — outputs 3 traits from old pool instead of 4 from new pool; needs design interview)
- Manual branch with a Stats step for 0-100 adjustment across all 13 stats (`health`, `happiness`, `intelligence`, `memory`, `stress`, `strength`, `charisma`, `imagination`, `wisdom`, `discipline`, `willpower`, `looks`, `fertility`) plus `[R]` to randomize all startup stats
- Manual Traits step requiring exactly 4 traits from the new pool: `Driven`, `Chill`, `Curious`, `Social`, `Disciplined`, `Impulsive`, `Empathetic`, `Resilient`, `Introverted`, `Extraverted`, `Restless`, `Ambitious`
- Confirm step showing the full character summary, with `Enter` to start the game and `Backspace` to go back
- current wizard controls are step-specific: `Enter` to proceed, `Backspace` to go back/delete, `↑↓` to navigate, `←→` to adjust stats, `Space` to toggle (multi-select traits only), `Esc` to quit from identity step, `R` to randomize stats

### Initial World Setup
Current initialization behavior:
- initial world setup creates `"earth"` plus the full startup place registry from `WORLD_GEOGRAPHY`: 12 real countries and their configured real cities, with country metadata for `region`, `culture_group`, and `primary_language`
- player is created in Year 1, Month 1 with startup stats copied from the creation payload
- player, parents, and bootstrapped older siblings all begin in the selected real startup city/country
- two parent actors are created through `World.create_human_actor(...)`
- current actor entry through `create_human_actor(...)` writes preserved `actor_entry` records with `entry_method="create_human_actor"`
- current human startup family bootstrap through `create_human_child_with_parents(...)` writes one preserved `family_bootstrap` record
- player is created through `World.create_human_child_with_parents(...)` (current startup scenario: human child with mother/father bootstrap)
- startup family links between player and parents are created by `World.create_human_child_with_parents(...)` with the same explicit directional outcome (`player -> parent` and `parent -> player`)
- those startup family links now explicitly mark origin semantics, caregiver semantics, and `bootstrap_source="startup_family"` while still living only in `World.links`
- parent first names are randomized from approved internal mother/father pools
- parent last names inherit the player last name when provided
- if player last name is blank, parent last names use a random fallback from `FALLBACK_LAST_NAME_POOL`
- startup mother, startup father, and startup player each receive `current_place_id = "earth_city_01"` and `residence_place_id = "earth_city_01"` during setup
- those same startup actors also receive `jurisdiction_place_id = "earth_country_01"` during setup while `temporary_occupancy_place_id` remains unset (`None`)
- those startup spatial assignments now flow through `World.update_actor_spatial_identity(...)`, which leaves unspecified fields unchanged and fails explicitly on unknown actor IDs or unknown non-`None` place IDs
- startup actor IDs now follow the `startup_<role>_<suffix>` pattern instead of fixed singleton IDs, while preserving the current one-family startup shape and parent/player lookup behavior
- parent birth months are randomized from 1-12
- the startup player is set as the current world-owned focused actor

### Time Advancement
Current advancement behavior:
- `Q` advances 1 month from any non-input screen
- `E` opens a shell-owned skip-time screen from any non-input screen
- the skip-time screen currently offers clear preset jumps (`1`, `3`, `6`, `12`, `24`, `60` months) plus a small numeric custom-month input path
- `Enter` in the skip-time screen advances using the typed custom month count when present; otherwise it advances using the currently highlighted preset
- skip-time selection remains shell-owned and still delegates actual advancement to `World.simulate_advance_turn(...)`, so larger jumps continue to process month-by-month internally
- if a pending identity-emergence choice interrupts a longer skip, remaining skipped months are resumed after the choice is resolved
- `[1]` opens Menu popup (Browser / Actions / Profile)
- `Esc` opens Options popup (Quit Game / Help / Settings)
- `Backspace` is the universal Back key on all navigation screens
- ordinary play no longer requires typed `lineage`, `back`, or `quit` command words

### Events
Current event behavior:
- Life View keeps an accumulating compact live event feed in the stable right-hand pane while ordinary-play identity/location/primary stats/relationships stay on the left
- events are processed monthly
- 50% chance to generate an event each month
- events are filtered by life stage, min_age_months, and max_age_months
- trait-gated events can also require one or more matching actor traits through `required_traits`
- family-aware events can require living family context and dynamically render `{family_role}` into event text using the chosen living relative
- `get_human_monthly_event_from_lifecycle(...)` is the implementation-facing seam for the current human-only event layer
- `get_monthly_event(...)` remains as a compatibility wrapper for the same structured monthly event contract
- monthly event results still contain `event_id`, `text`, `outcome`, `tags`, `year`, and `month`, or `None`
- there is still no top-level `stat_changes` field on event results
- `outcome["stat_changes"]` is still the single authoritative mutation payload for monthly event stat effects
- later-life practical event coverage still extends across the currently implemented post-Child human stages (`Teenager`, `Young Adult`, `Adult`, `Elder`)
- the clarified seam remains honest about current human-only content and does not claim species-general event support
- `World.simulate_advance_turn(...)` applies each returned event outcome centrally via `World.apply_outcome(...)` while collecting structured results
- `main.py` maintains a shell-owned event log that merges triggered monthly events with newly written relevant `birth` and `death` records
- the Life View live feed is compact and omits normal date prefixes, but still inserts year headers and skip markers as the run progresses
- the full-screen `History` browser opened with `H` renders the same accumulated log in detailed form with date prefixes, year separators, and scrolling
- `family_bootstrap` and `actor_entry` records are filtered from current player-facing event surfaces while remaining preserved in world storage
- `birth` and `death` records carry `★` and `✦` markers in both the live feed and the full history browser
- a 3-event cooldown prevents the same event from repeating within the most recent three triggered events during one advancement
- ordinary-play death remains structural rather than event-text-driven; later cause-specific event layers still do not exist

### Snapshot
Current snapshots display:
- identity (full name, species, sex, gender, sexuality, age, life stage)
- time (simulation date only: year and month)
- location (ancestry-resolved world body plus current place plus one clean jurisdiction line, resolved through `Human.get_snapshot_data(...)`, which currently reads `Human.get_spatial_state(world)` and world place helpers)
- residence remains internal and is not rendered in the snapshot yet
- temporary occupancy remains internal and is not rendered in the snapshot yet
- Life View statistics (health, happiness, intelligence, money)
- Profile screen secondary statistics (`strength`, `charisma`, `imagination`, `memory`, `wisdom`, `discipline`, `willpower`, `stress`, `looks`, `fertility`)
- relationships as a list of all living linked family entries with sex-aware labels (`Mother`, `Father`, `Brother`, `Sister`, `Son`, `Daughter`, `Sibling`, `Child`), plus social link entries displayed as `name · tier`
- dead relatives are excluded from Life View relationship output; former social links (status `former`) are also excluded
- `No living family.` is shown when the current living-family relationship list is empty
- structural state remains internal to the current ordinary-play snapshot flow and is not rendered during ordinary alive play; structural death/continuity handling is surfaced separately when relevant
- the curses shell now adds restrained chrome through a styled title/date header, bracketed section emphasis, screen-specific framing, and simple left-pane scrolling without restoring the older large shell banners inside ordinary play

### Structural Transition / Continuity Foundation
Current structural-transition behavior:
- `World.mark_actor_dead(...)` provides a controlled world-owned death transition path
- the actor remains in `World.actors` after death
- the world does not end when an actor dies
- focus does not auto-switch during the death transition itself
- a preserved `death` record is written for the actor
- baseline old-age mortality is now resolved monthly through `World.resolve_monthly_mortality()`
- `World.build_monthly_mortality_profile_for(...)` is the current extension seam for future health/lifestyle/place tuning without moving mortality into the shell
- continuity state can be built from the current linked living actors through `World.build_continuity_state_for(...)`
- current continuity candidates are returned in deterministic order with display-ready relationship metadata
- ordinary month advancement does not proceed once the focused actor is dead
- `main.py` now renders a dedicated dead-focus interrupt led by `You are dead.`, shows current death context when available, adds a brief life-summary retrospective (age/place/stats plus recent meaningful records), and still requires acknowledgment before showing any continuation choices
- `main.py` now renders continuation candidates as compact name/relationship/age/place rows, opens a dedicated continuation-detail inspect view on `Enter`, and only hands off focus after explicit confirmation from that detail screen
- player-facing record surfaces in `main.py` now filter out implementation scaffolding records such as `actor_entry` and `family_bootstrap` while preserving those records in world storage
- `main.py` now exposes lineage browsing through the curses shell so family-linked alive/dead actors can be inspected through a highlighted list + detail flow backed by current actors/links/records
- if no valid continuation candidates exist, the shell reports that cleanly and leaves the run only through explicit quit

Current limitations:
- only one baseline mortality cause exists so far: `Old age`
- no archive behavior yet
- no inheritance/estate consequences yet
- no broader connected-actor prioritization system yet

## 10. Event Foundation

The current event system is:
- passive
- monthly
- lifecycle-aware (uses `get_lifecycle_state`-derived data)
- explicitly human-content-scoped at the implementation layer
- structured (human monthly content plus structured results with `event_id`, `text`, `outcome`, `tags`, `year`, `month`)
- stat-effect capable

This remains a narrow honesty-focused seam clarification. It does not implement species-general event architecture, non-human event content, or a broader entity/event framework.

Monthly event content is currently human-scoped in `events.py`.

Current event-definition details:
- `HUMAN_MONTHLY_EVENTS` remains a flat pool of dictionaries
- each event definition now uses explicit `outcome={"stat_changes": {...}}` storage instead of internal `stat` / `change` shorthand
- event definitions can optionally declare `family_context=True` plus `family_roles=[...]`
- event definitions can optionally declare `required_traits=[...]`
- some monthly events intentionally have empty stat changes for pure life texture

Current event-selection details:
- `get_human_monthly_event_from_lifecycle(...)` still applies the same 50% monthly trigger gate and lifecycle filtering
- lifecycle filtering now also respects family-context requirements when present
- event selection now also accepts `actor_traits` and filters out trait-gated events when the actor does not match
- family-aware events render living relative context into the selected event text at selection time through `{family_role}` substitution
- the external structured event contract remains unchanged (`event_id`, `text`, `outcome`, `tags`, `year`, `month`)

Current event pool: 120 grounded human-only events including 20 trait-gated events (2 per personality trait) and 11 family-aware events with dynamic name insertion. Events support optional `required_traits` filtering so trait-gated events only trigger for actors who have the matching personality trait. Event selection also supports family-context input so family-aware events only become eligible when the needed living family roles exist. A 3-event cooldown prevents the same event from triggering within the last 3 triggered events during one advancement.

Meeting events: `get_meeting_event_for_player(lifecycle_state)` provides a separate event path for social link creation. When triggered, the player receives a popup choice to introduce themselves or keep to themselves. If the player chooses to meet, `World.generate_meeting_npc(...)` creates a plausible NPC with culture-aware naming, and a social link is established.

## 11. Patching Rules

When patching this repository:
- preserve validated behavior unless the patch explicitly changes it
- keep simulation logic separate from terminal rendering
- keep changes narrow and reviewable
- update `[[changelog]]` when implemented behavior changes
- keep module and function responsibilities clear

## 12. Manual Verification Focus

After patching, verify:
- startup still works
- character creation still works
- TUI advancement input still works
- TUI multi-month skip input still works
- quit still works
- snapshot output still renders correctly in the curses shell
- origin/care/bootstrap family-link semantics remain explicit in `World.links` without implying broader relationship systems
- events still trigger and display correctly (with correct date prefixes rendered by main.py)
- month-by-month advancement still behaves correctly
- larger skip requests still behave correctly while advancing internally month-by-month
- focused actor assignment works correctly at startup
- lineage browsing still works through the shell without typed command words
- direct structural death transition testing correctly updates actor state, preserves the actor in `World.actors`, writes a `death` record, and returns sensible continuity candidates from living linked actors
