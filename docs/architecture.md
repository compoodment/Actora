# CompLife Architecture Summary

**Version:** 0.28.0
**Last Updated:** 2026-03-27

This document summarizes the currently implemented structure and behavior of the CompLife repository.
It is intended to support safe patching, review, and manual verification.

## 1. Stack

- **Language:** Python
- **Interface:** Terminal
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
- `create_human_actor(actor_id, species, first_name, last_name, sex, gender, birth_year, birth_month, current_place_id=None, residence_place_id=None, randomize_stats=False)`
- `create_human_child_with_parents(child_id, first_name, last_name, sex, gender, mother_id, father_id, birth_year, birth_month, place_id, randomize_stats=False)`
- `get_actor(actor_id)`
- `advance_months(months)`
- `add_link(source_id, target_id, link_type, role, metadata=None)`
- `add_link_pair(source_id, target_id, forward_type, forward_role, reverse_type, reverse_role, forward_metadata=None, reverse_metadata=None)`
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
- `apply_outcome(actor_id, outcome)`
- `get_continuity_candidates_for(actor_id)`
- `build_continuity_state_for(actor_id)`
- `mark_actor_dead(actor_id, year=None, month=None, reason=None)`
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
- this does not yet implement archive state, mortality rules, inheritance, or broader lifecycle/death gameplay

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

`metadata` remains optional, and `World.links` remains the storage truth for current relationship data.

Current startup parent records still use directional family roles (`mother`, `father`, and reverse `child`), but startup bootstrap links created through `create_human_child_with_parents(...)` now also carry explicit semantic metadata:
- `is_origin_family` — marks that the startup link is expressing origin semantics
- `is_caregiver_family` — marks that the startup link is expressing current caregiving semantics
- `bootstrap_source="startup_family"` — marks that the link came from the current startup family bootstrap path

Current startup examples therefore look like:
- `{"source_id": "startup_player_ab12cd34", "target_id": "startup_mother_ef56gh78", "type": "family", "role": "mother", "metadata": {"is_origin_family": True, "is_caregiver_family": True, "bootstrap_source": "startup_family"}}`
- `{"source_id": "startup_mother_ef56gh78", "target_id": "startup_player_ab12cd34", "type": "family", "role": "child", "metadata": {"is_origin_family": True, "is_caregiver_family": True, "bootstrap_source": "startup_family"}}`

Reverse family links are still stored explicitly, link records still reference entity IDs present in `World.actors`, and this remains a narrow startup-family semantic clarification rather than a broader relationship framework. It does not implement adoption, guardianship, household simulation, or species-general relationship architecture.

Current continuity-candidate boundary:
- `get_continuity_candidates_for(actor_id)` scans current related links, resolves the linked living actors, excludes the actor itself, dedupes candidates, and returns small structured candidate objects
- current candidate objects contain `actor_id`, `full_name`, `link_type`, and `link_role`
- because current repo truth only has startup family links, continuity candidates are effectively drawn from the current narrow family-connected link graph
- this does not yet implement continuation choice UI, weighting, succession rules, archive state, lineage systems, or a broader connected-actor prioritization framework

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

- `create_human_actor(...)` is the current world-owned actor creation/registration path for startup actors, and it is explicitly human-backed. It directly constructs a `Human`, optionally randomizes starting stats, optionally applies current/residence place IDs, registers the actor via `add_actor(...)`, writes an `actor_entry` record with `entry_method="create_human_actor"`, and returns the created actor.
- `create_human_child_with_parents(...)` remains a narrow human-startup helper layered on top of `create_human_actor(...)`. It creates the child in the provided place, adds startup family link pairs for mother/father when IDs are provided, writes explicit origin/care/bootstrap metadata onto those directional links, and writes a `family_bootstrap` record for the current startup family-link bootstrap. No generic actor constructor, species framework, adoption system, guardianship system, or broader origin framework is currently implemented.

Basic world link helper contract:

- `add_link(...)` appends one directional link.
- `add_link_pair(...)` appends both forward and reverse directional links.
- query helpers return filtered link records without mutating world state.
- `get_link_target_ids(source_id, link_type=None, roles=None)` provides generic retrieval of linked target IDs from outgoing links with optional type/role filtering.
- `get_family_link_target_ids(...)` adds narrow semantic filtering on top of the same `World.links` store for current family-link metadata checks.
- `get_origin_parent_ids_for(entity_id)` resolves origin-marked mother/father links from outgoing family links.
- `get_caregiver_parent_ids_for(entity_id)` resolves caregiver-marked mother/father links from outgoing family links.
- `get_parent_ids_for(entity_id)` remains the compatibility wrapper for current mother/father access and falls back to bare family roles when explicit origin metadata is absent.

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
- `residence_place_id`
- `residence_place_name`

This helper is read-only and does not mutate human or world state.

Current structural-state access is formalized through `Human.get_structural_state()`, which returns a dictionary containing:

- `structural_status`
- `is_alive`
- `death_year`
- `death_month`
- `death_reason`

Current snapshot access is formalized through `Human.get_snapshot_data(current_year, current_month, world, actor_id)`, which returns a structured dictionary with the current shell-rendered sections:

- `identity` (`full_name`, `species`, `sex`, `gender`)
- `time` (`age`, `life_stage`, `year`, `month`)
- `location` (`world_body_name`)
- `statistics` (`health`, `happiness`, `intelligence`, `money`)
- `relationships` (`mother_name`, `father_name`)
- `structural` (`structural_status`, `is_alive`, `death_year`, `death_month`, `death_reason`)

This helper is read-only, resolves parent names through world semantic link/actor lookup helpers, and preserves the current `"Unknown"` fallback for unresolved parents and unresolved current place names.

## 6. Module Responsibilities

### `main.py`
Responsible for:
- startup flow
- terminal shell orchestration
- character creation flow
- initial world setup flow
- main input loop
- post-turn rendering orchestration
- rendering terminal snapshots from structured snapshot data
- converting structured event results into display text
- rendering structural transition / continuity output when present in turn results

Current shell-level functions:
- `render_snapshot(...)` — terminal rendering of the structured current-state snapshot returned by `Human.get_snapshot_data(...)`
- `safe_input(prompt)` — narrow shared CLI input boundary helper that exits cleanly on `EOFError` and `KeyboardInterrupt`
- `create_character()` — character creation prompts and input validation
- `setup_initial_world(...)` — World creation, parent identity generation, startup actor entry delegation through world-owned helpers (`create_human_actor(...)` and `create_human_child_with_parents(...)`), and initial focused-actor assignment through `World.set_focused_actor(...)`
- `game_loop(...)` — main input/advancement/display loop
- `start_game()` — top-level orchestration (banner, then delegates to the above)

Current startup flow is human-only. `create_character()` returns player first/last name plus sex/gender, and `setup_initial_world(...)` no longer carries a dead `player_species` parameter. Interactive CLI input now exits cleanly through the shared `safe_input(...)` helper when input is interrupted or closed (`KeyboardInterrupt` / `EOFError`) instead of surfacing a traceback. Startup actor IDs are now generated through the narrow `generate_startup_actor_id(...)` helper in `main.py` rather than reusing fixed singleton strings for mother, father, and player. Current startup IDs follow the `startup_<role>_<suffix>` pattern, such as `startup_mother_ab12cd34`, `startup_father_ef56gh78`, and `startup_player_ij90kl12`. The current shell also now renders a narrow structural-state section in snapshots and is capable of rendering structural transition / continuity result blocks when those keys are present.

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
- month advancement
- centralized application of event stat outcomes (`World.apply_outcome(...)`)
- world-owned continuity candidate resolution from the current link graph
- world-owned structural death transition handling (`World.mark_actor_dead(...)`)
- world-owned authoritative simulation-step boundary via `World.simulate_advance_turn(...)`, which advances month-by-month, derives lifecycle state from the current player, requests monthly event data through the current human-scoped event seam, applies outcomes centrally, writes event records, and assembles the structured turn result

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
- this patch does not add mortality events or automatic death triggers during ordinary play

### `banners.py`
Responsible for:
- `COMPLIFE_TITLE_BANNER`
- `TIME_ADVANCED_BANNER`
- `QUIT_BANNER`

## 7. Simulation Boundary

`World.simulate_advance_turn(player_id, months_to_advance)` is the authoritative simulation-step boundary in `world.py`.

A thin module-level `simulate_advance_turn(world, player_id, months_to_advance)` compatibility wrapper still delegates directly to the world-owned method to preserve existing call stability where needed.

Current behavior:
- advances time month-by-month
- ensures the current focused actor ID is available for turn-result reporting
- retrieves the current player from the world
- requests monthly structured event data from `events.py`
- applies each returned event outcome centrally through `World.apply_outcome(...)`
- writes one preserved world-owned `event` record for each triggered monthly event after outcome application
- collects complete structured event results returned by `events.py`
- returns a structured result dictionary
- returns continuity-ready keys even when no structural transition occurred during the turn

Current return keys:
- `months_advanced`
- `events` (list of structured event results, each containing `event_id`, `text`, `outcome`, `tags`, `year`, `month`)
- `had_any_events`
- `focused_actor_id`
- `focused_actor_alive`
- `structural_transition`
- `continuity_state`

Current return-contract notes:
- `structural_transition` is currently `None` during ordinary advancement because this patch does not yet introduce automatic mortality rules
- `continuity_state` is currently `None` during ordinary advancement unless the focused actor is already dead when the turn result is assembled
- this patch prepares the turn-result contract for structural death/continuity handling without pretending full death gameplay is already implemented

This function does not perform terminal input, output, or presentation formatting. Terminal presentation remains in `main.py` and consumes the returned structured result.

## 8. Current Turn Flow

1. Display ASCII art welcome title.
2. Run character creation (`create_character()`).
3. Set up initial world state (`setup_initial_world(...)`).
4. Set the startup player as the world-owned focused actor.
5. Display the initial focused-actor snapshot.
6. Enter the game loop (`game_loop(...)`).
7. Read player input.
8. Resolve months to advance (or quit).
9. Call `World.simulate_advance_turn(...)`.
10. Advance time internally month-by-month.
11. Apply triggered event outcomes through `World.apply_outcome(...)`.
12. Collect triggered structured events.
13. Render updated focused-actor snapshot.
14. Render event output by combining structured `year`, `month`, and raw event `text`.
    - Small event counts are shown as full dated lines.
    - Large event counts are summarized with a total count, a recent-event subset, and an omitted-older-events line.
    - Triggered monthly events are also preserved as structured world-owned records in addition to current terminal rendering.
15. If present, render structural transition / continuity output.
16. Return to step 7.

## 9. Current Gameplay Behavior

### Character Creation
Current player creation includes:
- required first name
- optional last name
- sex selection (numbered choice: Male/Female)
- gender selection (numbered choice: Male/Female/Non-binary)

### Initial World Setup
Current initialization behavior:
- initial world setup creates starter place `"earth"` (`name="Earth"`, `kind="world_body"`)
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
- startup mother, startup father, and startup player each receive `current_place_id = "earth"` and `residence_place_id = "earth"` during setup
- startup actor IDs now follow the `startup_<role>_<suffix>` pattern instead of fixed singleton IDs, while preserving the current one-family startup shape and parent/player lookup behavior
- parent birth months are randomized from 1-12
- the startup player is set as the current world-owned focused actor

### Time Advancement
Current advancement behavior:
- Enter advances 1 month
- positive integer advances that many months
- `quit` exits (via `return` from `game_loop`)
- invalid input reprompts safely

### Events
Current event behavior:
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
- this patch does not yet introduce ordinary-play death events or automatic mortality

### Snapshot
Current snapshots display:
- identity (full name, species, sex, gender)
- time (age, life stage, year, month)
- location (current world body only, resolved through `Human.get_snapshot_data(...)`, which currently reads `Human.get_spatial_state(world)` and world place helpers)
- residence remains internal and is not rendered in the snapshot yet
- statistics (health, happiness, intelligence, money)
- family references (mother, father), still resolved from the world layer
- structural state (`status`, optional death date, optional death reason)

### Structural Transition / Continuity Foundation
Current structural-transition behavior:
- `World.mark_actor_dead(...)` provides a controlled world-owned death transition path
- the actor remains in `World.actors` after death
- the world does not end when an actor dies
- focus does not auto-switch during the death transition
- a preserved `death` record is written for the actor
- continuity state can be built from the current linked living actors through `World.build_continuity_state_for(...)`
- current continuity candidates are returned as small structured objects with `actor_id`, `full_name`, `link_type`, and `link_role`
- current terminal rendering can display continuity information if a turn result contains it

Current limitations:
- no automatic mortality system yet
- no continuation chooser UI yet
- no archive behavior yet
- no inheritance/estate consequences yet
- no lineage browser yet
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
- advancement input still works
- quit still works
- snapshot output still renders correctly
- origin/care/bootstrap family-link semantics remain explicit in `World.links` without implying broader relationship systems
- events still trigger and display correctly (with correct date prefixes rendered by main.py)
- month-by-month advancement still behaves correctly
- focused actor assignment works correctly at startup
- direct structural death transition testing correctly updates actor state, preserves the actor in `World.actors`, writes a `death` record, and returns sensible continuity candidates from living linked actors
