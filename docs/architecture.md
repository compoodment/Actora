# Actora Architecture Summary

**Version:** 0.36.7
**Last Updated:** 2026-03-29

This document summarizes the currently implemented structure and behavior of the Actora repository.
It is intended to support safe patching, review, and manual verification.

## 1. Stack

- **Language:** Python
- **Interface:** Terminal with a narrow curses TUI shell for ordinary play, structured lineage/archive browsing, death/continuation interrupts, and skip-time utility flow
- **Structure:** Small modular prototype with separated simulation and rendering responsibilities

## 2. Current File Structure

    ./
    ├── main.py
    ├── world.py
    ├── identity.py
    ├── human.py
    ├── events.py
    ├── banners.py
    └── docs/
        ├── architecture.md
        └── changelog.md

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
- `update_actor_spatial_identity(actor_id, *, current_place_id=UNSET, residence_place_id=UNSET, jurisdiction_place_id=UNSET, temporary_occupancy_place_id=UNSET)`
- `create_human_actor(actor_id, species, first_name, last_name, sex, gender, birth_year, birth_month, current_place_id=None, residence_place_id=None, jurisdiction_place_id=None, temporary_occupancy_place_id=None, randomize_stats=False)`
- `create_human_child_with_parents(child_id, first_name, last_name, sex, gender, mother_id, father_id, birth_year, birth_month, place_id, jurisdiction_place_id=None, temporary_occupancy_place_id=None, randomize_stats=False)`
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
- `mark_actor_dead(actor_id, year=None, month=None, reason=None)`
- `build_monthly_mortality_profile_for(actor_id)`
- `resolve_monthly_mortality()`
- `simulate_advance_turn(player_id, months_to_advance)`

### Human (`human.py`)
The `Human` class represents an individual simulation subject.

Current stored fields:
- `species`
- `first_name`
- `last_name`
- `sex`
- `gender`
- `birth_year`
- `birth_month`
- `stats` (dictionary containing `health`, `happiness`, `intelligence`)
- `money`
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

Current structural-state details:
- `structural_status` is the current storage truth for narrow actor structural state and currently uses `"active"` / `"dead"`
- `is_alive()` derives living state from `structural_status` instead of duplicating a separate stored boolean
- `death_year`, `death_month`, and `death_reason` remain `None` until a controlled structural death transition is applied
- this still does not implement archive state, inheritance, or broader lifecycle/death gameplay beyond the current baseline old-age mortality rule

Current stat-mutation boundary details:
- `modify_stat(...)` supports keys currently present in `self.stats` (`health`, `happiness`, `intelligence`) and applies clamped mutation in the inclusive range 0-100.
- `modify_stat(...)` supports `"money"` through the separate unbounded money path (`self.money += change`).
- Any unsupported stat name now fails explicitly with `ValueError` (including the bad stat name) instead of being silently ignored.

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

Current startup parent records still use directional family roles (`mother`, `father`, and reverse `child`), but startup bootstrap links created through `create_human_child_with_parents(...)` now also carry explicit semantic metadata:
- `is_origin_family` — marks that the startup link is expressing origin semantics
- `is_caregiver_family` — marks that the startup link is expressing current caregiving semantics
- `bootstrap_source="startup_family"` — marks that the link came from the current startup family bootstrap path

Current startup examples therefore look like:
- `{"source_id": "startup_player_ab12cd34", "target_id": "startup_mother_ef56gh78", "type": "family", "role": "mother", "metadata": {"is_origin_family": True, "is_caregiver_family": True, "bootstrap_source": "startup_family"}}`
- `{"source_id": "startup_mother_ef56gh78", "target_id": "startup_player_ab12cd34", "type": "family", "role": "child", "metadata": {"is_origin_family": True, "is_caregiver_family": True, "bootstrap_source": "startup_family"}}`
- `{"source_id": "startup_mother_ef56gh78", "target_id": "startup_father_ij90kl12", "type": "association", "role": "coparent", "metadata": {"bootstrap_source": "startup_coparent_association"}}`

Reverse family links are still stored explicitly, link records still reference entity IDs present in `World.actors`, and this remains a narrow startup-family semantic clarification rather than a broader relationship framework. It does not implement adoption, guardianship, household simulation, or species-general relationship architecture.

Current continuity-candidate boundary:
- `get_continuity_candidates_for(actor_id)` scans current related links, resolves the linked living actors, excludes the actor itself, dedupes candidates, and returns small structured candidate objects
- current candidate objects contain `actor_id`, `full_name`, `link_type`, `link_role`, `relationship_label`, `structural_status`, `is_alive`, `age`, `life_stage`, and `current_place_name`
- current candidate labeling and ordering are deterministic: candidate-defining link context is chosen by a stable link sort key, and final candidate ordering uses (`full_name`, `link_type`, `link_role`, `actor_id`) rather than relying on incidental link iteration order
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
- `create_human_child_with_parents(...)` remains a narrow human-startup helper layered on top of `create_human_actor(...)`. It creates the child in the provided place, currently assigns the same startup place as both current and residence, optionally assigns separate jurisdiction and temporary occupancy context, adds startup family link pairs for mother/father when IDs are provided, writes explicit origin/care/bootstrap metadata onto those directional links, and writes a `family_bootstrap` record for the current startup family-link bootstrap. No generic actor constructor, species framework, adoption system, guardianship system, or broader origin framework is currently implemented.

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

- `identity` (`full_name`, `species`, `sex`, `gender`, `age`, `life_stage`)
- `time` (`year`, `month`)
- `location` (`world_body_name`, `current_place_name`, `current_place_kind`, `jurisdiction_place_name`, `jurisdiction_place_kind`)
- `statistics` (`health`, `happiness`, `intelligence`, `money`)
- `relationships` (`mother_name`, `father_name`)
- `structural` (`structural_status`, `is_alive`, `death_year`, `death_month`, `death_reason`)

This helper is read-only, resolves parent names through world semantic link/actor lookup helpers, resolves `world_body_name` through place ancestry rather than assuming the current place is itself a world body, and preserves the current `"Unknown"` fallback for unresolved parents and unresolved place names. The shell currently renders one added `Jurisdiction` line from this expanded spatial state so snapshot output stays narrow.

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
- rendering TUI snapshots from structured snapshot data
- converting structured event results into display text
- rendering the shell-owned dead-focus interrupt and continuation handoff flow when present
- rendering lineage list/detail browsing without typed command words

Current shell-level functions:
- `build_snapshot_sections(...)` — shell-owned transformation from structured snapshot data into TUI-ready section lines
- `build_event_lines(...)` — shell-owned event summary formatting with the current detail/summary thresholds
- `build_death_lines(...)` — shell-owned dead-focus interrupt copy assembly
- `build_screen_chrome(...)` — shell-owned title/subtitle/date chrome assembly for the current TUI screen
- `draw_text_block(...)` — small curses text rendering helper with wrapping support
- `ActoraTUI` — narrow curses shell object managing the split Life View, styled header/footer chrome, lineage list/detail, skip-time selection, death acknowledgment, continuation selection, simple left-pane scrolling, and safe footer rendering that avoids writing into the terminal’s last column
- `safe_input(prompt)` — narrow shared CLI input boundary helper that exits cleanly on `EOFError` and `KeyboardInterrupt`
- `create_character()` — character creation prompts and input validation
- `setup_initial_world(...)` — World creation, parent identity generation, startup actor entry delegation through world-owned helpers (`create_human_actor(...)` and `create_human_child_with_parents(...)`), and initial focused-actor assignment through `World.set_focused_actor(...)`
- `run_game_tui(...)` — curses wrapper entry point for ordinary play
- `start_game()` — top-level orchestration (banner, then delegates to the above)

Current startup flow is human-only. `create_character()` returns player first/last name plus sex/gender, and `setup_initial_world(...)` no longer carries a dead `player_species` parameter. Interactive CLI input now exits cleanly through the shared `safe_input(...)` helper when input is interrupted or closed (`KeyboardInterrupt` / `EOFError`) instead of surfacing a traceback. Startup actor IDs are now generated through the narrow `generate_startup_actor_id(...)` helper in `main.py` rather than reusing fixed singleton strings for mother, father, and player. Current startup IDs follow the `startup_<role>_<suffix>` pattern, such as `startup_mother_ab12cd34`, `startup_father_ef56gh78`, and `startup_player_ij90kl12`. Startup actor spatial identity is now applied through the world-owned `update_actor_spatial_identity(...)` seam instead of direct field pokes inside actor creation. Once startup completes, ordinary play now lives inside a narrow curses shell: the split `Life View` keeps identity/location/stats/relationships on the left, keeps recent activity visible on the right, allows simple left-side vertical scrolling under terminal-height pressure, still opens lineage with `L`, and still preserves the dead-focus interrupt before any continuation choices are shown.

### `identity.py`
Responsible for:
- approved parent first-name pools (`MOTHER_FIRST_NAME_POOL`, `FATHER_FIRST_NAME_POOL`)
- approved fallback surname pool (`FALLBACK_LAST_NAME_POOL`)
- family surname resolution via `resolve_family_last_name(player_last_name)`
- structured identity-generation context prep via `prepare_parent_identity_context(...)`
- parent identity assembly via `generate_parent_identity_from_context(identity_context)`
- compatibility parent identity assembly via `generate_parent_identity(role, family_last_name, generation_context=None)`

Current boundary:
- returns small structured identity dictionaries for current mother/father generation
- now exposes a small structured context-prep seam so startup identity generation no longer depends only on loose positional inputs
- still resolves current names through placeholder/global pools beneath that seam
- does not construct `Human` objects
- does not yet implement place-aware, culture-aware, era-aware, or world-aware identity generation
- remains human-only for the current startup identity path

### `world.py`
Responsible for:
- `World` model definition
- shared world state
- world-owned focused actor tracking (`focused_actor_id` plus focus helper methods)
- world-owned link storage and retrieval helpers (`World.links` and link helper/query methods), including narrow origin/caregiver access layered on the current family link metadata
- world-owned place storage and minimal hierarchy/query helpers (`World.places` plus direct lookup, child lookup, lineage, and nearest-kind resolution)
- month advancement
- centralized application of event stat outcomes (`World.apply_outcome(...)`)
- world-owned continuity candidate resolution from the current link graph
- world-owned structural death transition handling (`World.mark_actor_dead(...)`)
- world-owned authoritative simulation-step boundary via `World.simulate_advance_turn(...)`, which advances month-by-month for the current living focused actor, requests monthly event data through the current human-scoped event seam, applies outcomes centrally, writes event records, and assembles the structured turn result

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

Current event boundary truth:
- current monthly event content remains explicitly human-scoped
- the derived-lifecycle helper seam reduces unnecessary direct coupling to the concrete `Human` model inside event selection
- this seam clarification does not mean species-general event support now exists
- the structured monthly event contract is unchanged: `event_id`, `text`, `outcome`, `tags`, `year`, and `month`
- there is still no top-level `stat_changes`; `outcome["stat_changes"]` remains the sole authoritative mutation payload
- ordinary-play mortality now comes from `world.py` structural checks rather than event payloads

### `banners.py`
Responsible for:
- plain-text startup title branding shown before curses begins (`ACTORA_TITLE_BANNER`)
- plain-text exit branding shown after curses has exited (`QUIT_BANNER`)

Current banner-boundary truth:
- `banners.py` is no longer an in-play UI surface
- it currently exists only for non-curses startup/exit presentation
- the old time-advance banner path is gone because ordinary advancement and skip-time now live inside the TUI

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
2. Run character creation (`create_character()`).
3. Set up initial world state (`setup_initial_world(...)`).
4. Set the startup player as the world-owned focused actor.
5. Enter the curses shell (`run_game_tui(...)` / `ActoraTUI.run(...)`).
6. Render the initial focused-actor snapshot screen.
7. Read one key-driven TUI action.
8. Resolve advance, lineage browse, continuation selection, back, or quit.
9. If the player requests a larger jump, resolve the shell-owned skip-time selection first.
10. Call `World.simulate_advance_turn(...)` when advancing.
11. Advance time internally month-by-month.
12. Apply triggered event outcomes through `World.apply_outcome(...)`.
13. Collect triggered structured events.
14. Re-render the updated focused-actor snapshot screen.
15. Render event output by combining structured `year`, `month`, and raw event `text`.
    - Small event counts are shown as full dated lines.
    - Large event counts are summarized with a total count, a recent-event subset, and an omitted-older-events line.
    - Triggered monthly events are also preserved as structured world-owned records in addition to current terminal rendering.
16. If the focused actor is dead, render the dedicated death interrupt first.
17. Require acknowledgment before rendering any continuation choices.
18. Resolve continuation handoff or end the run cleanly.
19. Return to step 7.

## 9. Current Gameplay Behavior

### Character Creation
Current player creation includes:
- required first name
- optional last name
- sex selection (numbered choice: Male/Female/Intersex)
- gender selection (numbered choice: Male/Female/Non-binary/Agender/Genderfluid/Other)
- free-text gender entry when `Other` is selected

### Initial World Setup
Current initialization behavior:
- initial world setup creates a minimal startup place hierarchy: `"earth"` (`name="Earth"`, `kind="world_body"`) -> `"earth_country_01"` (`name="Starter Country"`, `kind="country"`) -> `"earth_city_01"` (`name="Starter City"`, `kind="city"`)
- player is created in Year 1, Month 1 with randomized starting stats
- two parent records are created through `World.create_human_actor(...)`
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
- `A` or `Enter` advances 1 month from the persistent actor screen
- `S` opens a shell-owned skip-time screen from the persistent actor screen
- the skip-time screen currently offers clear preset jumps (`1`, `3`, `6`, `12`, `24`, `60` months) plus a small numeric custom-month input path
- `Enter` in the skip-time screen advances using the typed custom month count when present; otherwise it advances using the currently highlighted preset
- skip-time selection remains shell-owned and still delegates actual advancement to `World.simulate_advance_turn(...)`, so larger jumps continue to process month-by-month internally
- `L` opens lineage browsing from the persistent actor screen
- `B` is the visible back hint in skip-time and lineage, while `Esc` remains a compatibility path
- `Q` exits the run from the TUI
- ordinary play no longer requires typed `lineage`, `back`, or `quit` command words

### Events
Current event behavior:
- Life View keeps recent activity visible in a stable right-hand pane while ordinary-play identity/location/stats/relationships stay on the left
- events are processed monthly
- 50% chance to generate an event each month
- events are filtered by life stage, min_age_months, and max_age_months
- `get_human_monthly_event_from_lifecycle(...)` is the implementation-facing seam for the current human-only event layer
- `get_monthly_event(...)` remains as a compatibility wrapper for the same structured monthly event contract
- monthly event results still contain `event_id`, `text`, `outcome`, `tags`, `year`, and `month`, or `None`
- there is still no top-level `stat_changes` field on event results
- `outcome["stat_changes"]` is still the single authoritative mutation payload for monthly event stat effects
- later-life practical event coverage still extends across the currently implemented post-Child human stages (`Teenager`, `Young Adult`, `Adult`, `Elder`)
- the clarified seam remains honest about current human-only content and does not claim species-general event support
- `World.simulate_advance_turn(...)` applies each returned event outcome centrally via `World.apply_outcome(...)` while collecting structured results
- `main.py` renders display text by combining structured `year`, `month`, and raw `text`
- only triggered events are displayed
- small event counts are shown with full dated event lines
- large event counts are compacted with a total summary, recent-event subset, and omitted-older-events line
- fully quiet turns show a fallback line
- ordinary-play death remains structural rather than event-text-driven; later cause-specific event layers still do not exist

### Snapshot
Current snapshots display:
- identity (full name, species, sex, gender, age, life stage)
- time (simulation date only: year and month)
- location (ancestry-resolved world body plus current place plus one clean jurisdiction line, resolved through `Human.get_snapshot_data(...)`, which currently reads `Human.get_spatial_state(world)` and world place helpers)
- residence remains internal and is not rendered in the snapshot yet
- temporary occupancy remains internal and is not rendered in the snapshot yet
- statistics (health, happiness, intelligence, money)
- family references (mother, father), still resolved from the world layer
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
- `main.py` now renders a dedicated dead-focus interrupt led by `You are dead.`, shows current death context when available, requires acknowledgment before showing continuation choices, and renders each continuation candidate with relationship label, age, life stage, and current place before switching focus through the world-owned handoff method
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

Current event pool: 32 grounded human-only events across Infant (8), Child (8), Teenager (4), Young Adult (4), Adult (4), and Elder (4) life stages.

## 11. Patching Rules

When patching this repository:
- preserve validated behavior unless the patch explicitly changes it
- keep simulation logic separate from terminal rendering
- keep changes narrow and reviewable
- update `docs/changelog.md` when implemented behavior changes
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
