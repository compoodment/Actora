# Actora Changelog

## Version 0.33.1 (Patch) - 2026-03-28
- **Alive-Play Snapshot Structural-State Removal:**
    - Removed the ordinary-play `Structural State` section from terminal snapshot rendering in `main.py` so alive-state is no longer redundantly exposed as front UI.
    - Preserved backend structural actor state, structural death data, and continuity/death handling logic.
    - Preserved current snapshot identity/time/location/statistics/family output and current continuity rendering paths.
    - Did not introduce the fuller death-transition UI, archive browser, richer continuation paging, or time-layout redesign.

## Version 0.33.0 (Minor) - 2026-03-27
- **Spatial Identity Separation Strengthening:**
    - Added explicit actor-level `jurisdiction_place_id` and `temporary_occupancy_place_id` storage alongside the existing `current_place_id` and `residence_place_id`.
    - Extended `World.create_human_actor(...)` and `World.create_human_child_with_parents(...)` so jurisdiction and temporary occupancy can be set at creation time without changing the broader place architecture.
    - Updated startup world setup so startup mother, startup father, and startup player still live in `"earth_city_01"` while now also explicitly carrying `jurisdiction_place_id = "earth_country_01"` and leaving temporary occupancy unset.
    - Extended `Human.get_spatial_state(...)` to return separate structured current-place, residence-place, jurisdiction-place, temporary-occupancy, and ancestry-resolved current-world-body values.
    - Updated snapshot data/rendering so the shell still shows `World Body` and `Current Place`, and now also shows one clean `Jurisdiction` line.
    - Preserved current startup flow, place hierarchy, link foundation, continuity handoff behavior, and the absence of travel, property, and politics simulation systems.

## Version 0.32.0 (Minor) - 2026-03-27
- **Structured Place / Place-Hierarchy Strengthening:**
    - Added a small world-owned place query seam in `world.py` with `get_child_places(...)`, `get_place_lineage(...)`, and `get_nearest_place_of_kind(...)`.
    - Updated startup world setup in `main.py` to create a minimal honest place hierarchy: one `world_body`, one `country`, and one `city`, wired through `parent_place_id`.
    - Reassigned startup mother, father, and player `current_place_id` / `residence_place_id` values to the startup city rather than the world body.
    - Updated `Human.get_spatial_state(...)` and `Human.get_snapshot_data(...)` so snapshot `World Body` display resolves through place ancestry when the current place is lower-level, and added one explicit `Current Place` display line in the shell snapshot.
    - Preserved startup flow, continuity handoff flow, existing link behavior, and the current shell loop.
    - Did not introduce travel, movement simulation, property/household systems, country-depth simulation, politics/jurisdiction systems, spatial-identity expansion, or map UI.

## Version 0.31.0 (Minor) - 2026-03-27
- **Link Foundation Strengthening:**
    - Added `_build_link_record(...)` in `world.py` so world-owned links are normalized at creation time and always store `metadata` as a dictionary.
    - Updated `add_link(...)` to delegate through the normalized link builder and kept `add_link_pair(...)` on the same path through `add_link(...)`.
    - Added the small general world-owned link query helper `get_links(...)` with optional filtering by source, target, entity plus direction, link type, role, and roles.
    - Refactored existing link lookup helpers into thin wrappers where sensible on top of `get_links(...)`, and routed continuity candidate gathering through the stronger generic query seam.
    - Updated `main.py` startup setup to add a direct parent-to-parent `association/coparent` link pair alongside the existing family links.
    - Preserved existing startup family links, current parent snapshot rendering, `get_parent_ids_for(...)`, and current continuity handoff behavior.
    - Did not introduce marriage, romance, org/property systems, lineage browsing, or broader social-graph expansion.

## Version 0.30.0 (Minor) - 2026-03-27
- **Continuation Handoff Flow / Continuity Link Refinement:**
    - Tightened continuity candidate data in `world.py` so candidates now carry deterministic display-ready fields including `relationship_label`, `structural_status`, and `is_alive`.
    - Made continuity candidate ordering deterministic instead of relying on incidental link iteration order.
    - Added world-owned continuation handoff validation through `World.handoff_focus_to_continuation(...)`, which only accepts living existing actors that are valid current continuity candidates for the dead focused actor.
    - Hardened `World.simulate_advance_turn(...)` so ordinary advancement no longer proceeds as if nothing happened when the focused actor is already dead; it now returns a blocked turn result with continuity state instead of advancing time or faking normal play.
    - Updated `main.py` to render dead-focus continuity state clearly, show deterministic numbered continuation options, allow successor selection, switch focus cleanly inside the same world state, and end the run cleanly when no valid continuation candidates exist.
    - Preserved startup flow, character creation flow, living focused-actor month advancement behavior, current event generation flow, current event record-writing flow, world-owned stores, and the absence of automatic mortality, archive, inheritance, or lineage systems.

## Version 0.28.0 (Minor) - 2026-03-27
- **Death / Continuity Structural Transition Foundation:**
    - Added narrow structural actor-state storage in `human.py` through `structural_status`, `death_year`, `death_month`, and `death_reason`.
    - Added `Human.is_alive()` and `Human.get_structural_state()` so living/dead state is derived cleanly from one stored structural status instead of duplicated truth.
    - Added world-owned focused actor tracking through `focused_actor_id`, `set_focused_actor(...)`, `get_focused_actor_id()`, and `get_focused_actor()`.
    - Added a controlled world-owned death transition path through `World.mark_actor_dead(...)`.
    - Added structured continuity candidate resolution from living linked actors through `get_continuity_candidates_for(...)` and `build_continuity_state_for(...)`.
    - Extended the turn result contract with `focused_actor_id`, `focused_actor_alive`, `structural_transition`, and `continuity_state`.
    - Added narrow structural-state snapshot rendering and continuity-aware terminal rendering seams in `main.py`.
    - Added preserved `death` records with structural-transition metadata including reason, focus state, and continuity candidate IDs.
    - Preserved current startup flow, month advancement, event flow, and terminal-first shell behavior.
    - Did not introduce automatic mortality, archive behavior, inheritance, lineage UI, continuation chooser UI, or broader actor/entity refactors.

## Version 0.27.1 (Patch) - 2026-03-26
- **Post-v0.27.0 Docs / Planning Sync:**
    - Synced repo-local architecture and planning docs to the already-landed v0.27.0 startup actor ID cleanup.
    - Updated architecture notes to reflect the narrow `generate_startup_actor_id(...)` helper and the removal of fixed startup singleton IDs.
    - Updated planning docs so singleton startup actor IDs are no longer treated as pending work and the next-step read is based on v0.27.0 repo truth.
    - Did not change runtime behavior beyond the already-implemented v0.27.0 code state.

## Version 0.27.0 (Patch) - 2026-03-26
- **Singleton Startup Actor ID Cleanup:**
    - Replaced the hardcoded singleton startup actor IDs (`"mother"`, `"father"`, `"player"`) with a narrow startup-only ID generation helper in `main.py`.
    - Preserved current one-family startup behavior, startup family link wiring, parent/player visible behavior, snapshot behavior, event flow, and terminal flow.
    - Did not introduce broader family bootstrap redesign, sibling support, persistence work, or a generic global ID framework.

## Version 0.26.0 (Patch) - 2026-03-26
- **CLI Input Boundary Hardening:**
    - Added a narrow shared input boundary helper in `main.py` so interactive CLI input exits cleanly on `EOFError` and `KeyboardInterrupt` instead of crashing with a traceback.
    - Covered character creation prompts and the main loop advance/quit prompt through the same clean-exit path.
    - Preserved current prompt wording, validation behavior, typed `quit` behavior, startup flow, snapshot rendering, simulation flow, and event rendering.
    - Did not introduce broader CLI redesign, identity changes, lifecycle changes, or unrelated architecture work.

## Version 0.25.0 (Patch) - 2026-03-25
- **Unknown-Stat Mutation Hardening:**
    - Hardened `Human.modify_stat(...)` so unsupported stat names now fail explicitly instead of being silently ignored.
    - Preserved current supported stat mutation behavior for `health`, `happiness`, `intelligence`, and `money`.
    - Preserved current startup flow, snapshot flow, event flow, and terminal behavior.
    - Did not introduce new stats, a broader stat framework, or unrelated runtime/input changes.

## Version 0.24.0 (Minor) - 2026-03-24
- **Simulation Step Ownership / Boundary Foundation:**
    - Moved the authoritative simulation-step boundary into the world layer so time advancement, structured event collection, centralized outcome application, record writing, and structured turn-result assembly are owned together.
    - Preserved the current turn result contract (`months_advanced`, `events`, `had_any_events`) and current event result shapes.
    - Preserved current startup flow, snapshot flow, event flow, terminal behavior, and current grounded human-only event coverage.
    - Did not introduce Universe implementation, multi-system orchestration, or a broad simulation-engine rewrite.

## Version 0.23.0 (Minor) - 2026-03-23
- **Identity Generation Context Prep:**
    - Added a structured context-prep seam to the current identity-generation layer so startup identity generation no longer depends only on loose placeholder-style inputs.
    - Routed current startup identity generation through the cleaner seam while preserving current visible behavior and fallback pool usage.
    - Kept the current identity layer honest about its present limitations; this patch does not implement place-aware, culture-aware, era-aware, or world-aware identity generation.
    - Did not redesign broader actor creation, startup flow, or non-human identity generation.

## Version 0.22.0 (Minor) - 2026-03-23
- **Event Boundary Honesty Foundation:**
    - Hardened the current monthly event seam so the implementation boundary is more honest about the event layer’s current human-only scope.
    - Reduced unnecessary direct coupling in the event path where practical without redesigning the wider simulation flow.
    - Preserved the current structured event contract, including `outcome.stat_changes` as the sole mutation payload location.
    - Preserved current grounded human event content and later-life coverage.
    - Did not introduce species-general event architecture, non-human event content, or broader actor/entity framework work.

## Version 0.21.0 (Minor) - 2026-03-20
- **Origin / Care Semantics Foundation:**
    - Added explicit metadata to current startup parent/child family links so origin meaning, caregiving meaning, and startup bootstrap provenance are no longer implied only by bare family roles.
    - Added narrow world helper access for cleaner origin/caregiver retrieval on top of the existing `World.links` store.
    - Preserved current startup family behavior, snapshot behavior, and terminal behavior.
    - Did not introduce adoption systems, household systems, broader relationship redesign, or entity-layer rewrites.

## Version 0.20.0 (Minor) - 2026-03-20
- **Later-Life Human Event Coverage:**
    - Expanded the human event pool beyond Infant and Child so ordinary play no longer goes quiet simply because the event content ends after the Child stage.
    - Added grounded later-life human events for the post-Child portion of the currently implemented lifecycle system.
    - Preserved the current structured event contract, including `outcome.stat_changes` as the sole mutation payload location.
    - Did not introduce species-general event architecture, broader lifecycle redesign, or unrelated simulation-framework work.

## Version 0.19.0 (Patch) - 2026-03-20
- **Event Result Contract Cleanup:**
    - Removed the redundant top-level `stat_changes` field from structured event results returned by `get_monthly_event(...)`.
    - Kept `outcome.stat_changes` as the single authoritative mutation payload consumed by the simulation step.
    - Preserved event generation behavior, event rendering behavior, startup flow, and terminal behavior.
    - Did not introduce event-content expansion, broader mutation-framework work, or species-general event support.

## Version 0.18.0 (Minor) - 2026-03-20
- **Snapshot Output Contract Foundation:**
    - Added `Human.get_snapshot_data(...)` as a structured current-state snapshot helper.
    - Removed direct snapshot terminal printing from `Human`.
    - Updated `main.py` to render snapshots from structured snapshot data instead of printing from the model layer.
    - Preserved current visible snapshot content, startup flow, event flow, and terminal behavior.
    - Did not introduce a broader UI framework or presentation system.

## Version 0.17.0 (Minor) - 2026-03-20
- **Human Actor Construction Naming Honesty:**
    - Renamed the current world-owned constructor seam from `create_actor(...)` to `create_human_actor(...)`.
    - Updated startup actor creation and current human child bootstrap to delegate through `create_human_actor(...)`.
    - Updated actor-entry record metadata so the recorded entry method matches the renamed constructor seam.
    - Preserved actor-safe registry naming, record/query layers, startup behavior, event flow, and terminal behavior.
    - Did not introduce a generic actor constructor, species framework, or broader origin system.

## Version 0.16.1 (Patch) - 2026-03-19
- **Docs Formatting Repair:**
    - Repaired repository-local changelog formatting only.
    - Did not change runtime behavior or implemented simulation structure.

## Version 0.16.0 (Patch) - 2026-03-18
- **Record Structure Stabilization:**
    - Added an internal `_build_record(...)` helper to normalize the world-owned record shape before storage.
    - Updated `add_record(...)` to delegate record construction through the normalization helper.
    - Preserved the existing record store, query helpers, and record-writing behavior introduced in v0.14.0 and v0.15.0.
    - Did not introduce record IDs, indexing, persistence, archive systems, memory systems, or history UI.

## Version 0.15.0 (Patch) - 2026-03-18
- **Record Access / Query Foundation:**
    - Added narrow world-owned record query helpers on top of `World.records`.
    - Added `get_actor_records(...)`, `get_latest_record(...)`, and `get_records_by_tag(...)` for cleaner record access without ad hoc filtering across future systems.
    - Preserved the existing record store and record-writing behavior introduced in v0.14.0.
    - Included small low-risk cleanup of closely related residue where applicable.
    - Did not introduce archive systems, memory systems, history UI, or record indexing complexity.

## Version 0.14.0 (Minor) - 2026-03-17
- **Records / History Foundation:**
    - Added world-owned structured record storage via `World.records`.
    - Added `add_record(...)` and `get_records(...)` helpers for preserved simulation history.
    - Actor entry through `create_actor(...)` now writes an `actor_entry` record.
    - Current human startup family bootstrap through `create_human_child_with_parents(...)` now writes a `family_bootstrap` record.
    - Triggered monthly events are now also preserved as structured `event` records in addition to current terminal rendering.
    - Preserved current visible startup, snapshot, advancement, event output, and quit behavior.
    - Did not introduce archive systems, memory systems, save/load, or broad history UI.

## Version 0.13.0 (Minor) - 2026-03-17
- **Actor Entry / Origin Foundation:**
    - Added `World.create_actor(...)` as the canonical world-owned actor entry helper.
    - Added `World.create_human_child_with_parents(...)` as a narrow human-startup helper layered on top of `create_actor(...)`.
    - Refactored startup world setup to use world-owned actor entry instead of direct inline Human construction and repeated setup glue.
    - Preserved current visible startup behavior, parent generation behavior, place assignment behavior, link outcome, event flow, and snapshot behavior.
    - Did not introduce a full origin system, species framework, or broader entity architecture.

## Version 0.12.0 (Patch) - 2026-03-17
- **Human-Lock Cleanup Foundation:**
    - Renamed world actor registry and access API from person-shaped naming to actor-safe naming (`World.actors`, `add_actor(...)`, `get_actor(...)`).
    - Added generic world-core link target retrieval helper `get_link_target_ids(...)` so relationship/origin-style retrieval is no longer expressed only through mother/father-specific access.
    - Kept `get_parent_ids_for(...)` as a narrow human-specific wrapper over the generic helper to preserve current `Mother`/`Father` snapshot display behavior.
    - Updated architecture documentation to reflect actor-safe registry naming and the generic relationship retrieval seam beneath human interpretation.
    - Corrected stale fallback surname pool naming in docs to `FALLBACK_LAST_NAME_POOL`.
    - Removed stale old-path header residue from `human.py`.

## Version 0.11.0 (Minor) - 2026-03-16
- **Identity Generation Foundation:**
    - Extracted parent identity generation into new `identity.py`.
    - Moved approved mother/father first-name pools and fallback surname pool logic out of `main.py`.
    - Added narrow structured helpers: `resolve_family_last_name(player_last_name)` and `generate_parent_identity(role, family_last_name)`.
    - Updated startup world setup to consume structured parent identity data while keeping `Human` construction in `main.py`.
    - Preserved current visible startup behavior, including prompts/input flow, parent sex/gender assignment, parent birth-month randomization, fallback surname behavior, place assignment, and family link creation.
    - Did not introduce place-aware, culture-aware, or era-aware naming logic.

## Version 0.10.0 (Minor) - 2026-03-16
- **Controlled State Mutation Foundation:**
    - Updated `events.py` so `get_monthly_event(...)` returns structured outcomes instead of directly mutating actor state.
    - Added `World.apply_outcome(...)` in `world.py` as a small centralized mutation path for current event stat changes.
    - Updated `simulate_advance_turn(...)` to apply event outcomes during the simulation step while still collecting structured event results for rendering.
    - Preserved visible gameplay behavior, snapshot structure, and terminal event output format.
    - Did not introduce a large generic mutation framework.

## Version 0.9.2 (Patch) - 2026-03-16
- **Spatial Access Boundary & Changelog Consistency Cleanup:**
    - Added `Human.get_spatial_state(world)` as a formal spatial access/query helper.
    - Added `World.get_place_kind(place_id)` for consistent place-kind lookup.
    - Updated snapshot rendering to read current location through the spatial-state helper without changing visible output.
    - Cleaned recent changelog entry consistency/formatting.

## Version 0.9.1 (Patch) - 2026-03-16
- **Architecture/Changelog Consistency Cleanup:**
    - Cleaned up repository architecture/changelog wording after v0.9.0.
    - Clarified spatial identity separation wording without changing implemented behavior.
    - Preserved current behavior where residence remains internal and snapshots still show only current world-body location.
    - No gameplay behavior changed.

## Version 0.9.0 (Minor) - 2026-03-16
- **Spatial Identity Separation Foundation**:
    - Kept `Human.residence_place_id` as a stored internal actor field.
    - Snapshot continues to display only current world-body location at this stage.
    - Preserved startup assignment behavior where mother, father, and player receive both `current_place_id` and `residence_place_id`.

## Version 0.8.1 (Patch) - 2026-03-16
- **Snapshot Place-Name Lookup Cleanup:**
    - Snapshot location rendering now reuses `World.get_place_name(...)` in `Human.display_snapshot(...)`.
    - Unknown location fallback behavior is preserved (`"Unknown"` when no place name resolves).
    - Architecture docs now explicitly describe starter place creation (`"earth"`) and `current_place_id` assignment during initial setup for mother, father, and player.
    - No gameplay behavior changed.

## Version 0.8.0 (Minor) - 2026-03-16
- **Structured Place Foundation:**
    - Added world-owned place registry via `World.places` in `world.py`.
    - Added place helpers: `add_place(...)`, `get_place(...)`, and `get_place_name(...)`.
    - Removed loose `World.location` storage.
    - Added `Human.current_place_id` for actor-level current place references.
    - Updated initial world setup to create starter place `"earth"` and assign it to mother, father, and player.
    - Updated snapshot location rendering to resolve world body display through the place registry.
    - Preserved existing gameplay flow without expanding into travel, residence, ownership, or politics systems.

## Version 0.7.0 (Minor) - 2026-03-16
- **Link Foundation Expansion:**
    - Added world-owned link storage via `World.links` in `world.py`.
    - Added world link helpers: `add_link(...)`, `add_link_pair(...)`, `get_outgoing_links(...)`, `get_incoming_links(...)`, `get_related_links(...)`, `get_linked_ids(...)`, and `get_parent_ids_for(...)`.
    - Moved relationship truth out of `Human` and into `World`.
    - Removed `mother_id`/`father_id` constructor inputs and relationship storage/helpers from `Human`.
    - Updated `Human.display_snapshot(...)` to resolve parent IDs through `world.get_parent_ids_for(human_id)`.
    - Updated initial world setup to create explicit forward and reverse family links (`player -> mother`, `mother -> player`, `player -> father`, `father -> player`).
    - Preserved existing gameplay flow and snapshot layout while enabling structurally general non-family link categories.

## Version 0.6.4 (Patch) - 2026-03-17
- **Initialization Name-Pool Correction:**
    - Replaced temporary parent first-name pools with approved mother/father pools.
    - Replaced single fallback surname behavior with randomized fallback from `LAST_NAME_POOL` when player last name is blank.
    - Preserved player-entered first and last names exactly as entered.
    - Preserved startup flow, snapshot structure, parent birth-month randomization, simulation loop, event behavior, and advancement behavior.

## Version 0.6.3 (Patch) - 2026-03-17
- **Character / World Initialization Polish:**
    - Replaced hardcoded parent placeholder names with randomized first names from small fixed internal pools.
    - Parent last names now inherit the player surname when one is provided during character creation.
    - Added a clean fallback parent surname (`Smith`) when the player leaves last name blank.
    - Parent birth months are now randomized (1-12) instead of always defaulting to January.
    - Preserved startup flow, relationship model, snapshot structure/order, advancement behavior, quit flow, and player starting-stat randomization.

## Version 0.6.2 (Patch) - 2026-03-16
- **Terminal Event Presentation Cleanup:**
    - Improved post-advancement event rendering in `main.py` for long skips that trigger many events.
    - Small event counts still render as full dated event lines.
    - Large event counts now render in compact form with:
        - a total events summary line,
        - a limited recent subset of dated events,
        - and a clear older-events-omitted line.
    - Preserved simulation behavior exactly: event generation, eligibility, effects, time advancement, input handling, quit flow, snapshot content, and high-level output order.

## Version 0.6.1 (Patch) - 2026-03-15
- **Human Model Structural Cleanup:**
    - Replaced direct `Human` stat fields with a consolidated `self.stats` dictionary containing `health`, `happiness`, and `intelligence`.
    - Kept `money` as a separate top-level field and preserved unbounded money mutation behavior in `modify_stat(...)`.
    - Preserved silent-ignore behavior for unknown stat names in `modify_stat(...)`.
    - Replaced nested family relationship storage with a list of structured relationship records containing `type`, `role`, and `target_id`.
    - Added relationship helpers on `Human`: `add_relationship(...)`, `get_relationships(...)`, and `get_parent_ids()`.
    - Updated snapshot rendering to read stats from `self.stats` and resolve parent display through `get_parent_ids()` while preserving existing output format and behavior.
    - Preserved current gameplay behavior, including event effects/text, input handling, quit flow, and output ordering.

## Version 0.6.0 (Minor) - 2026-03-14
- **Event System Foundation:**
    - Moved event definitions from `get_monthly_event()` to a module-level data structure (`ALL_EVENTS`) in `events.py`.
    - Implemented a clear event generation pipeline in `get_monthly_event()` (lifecycle evaluation, filtering, chance roll, selection, stat application).
    - `get_monthly_event()` now returns complete structured event results (dict with `event_id`, raw `text`, `stat_changes`, `tags`, `year`, `month`) or `None`.
    - `simulate_advance_turn()` in `world.py` updated to collect these complete structured event results without mutating or decorating them.
    - `main.py` now renders terminal event lines by combining the structured `year`, `month`, and raw `text` fields from event results.
    - Preserved all validated gameplay behavior: input handling, advancement, snapshot output, monthly event chance, stat mutation, lifecycle filtering, and Infant/Child event content pool.

## Version 0.5.7 (Patch) - 2026-03-14
- **Docs Sync After Structural Cleanup:**
    - Updated `docs/architecture.md` to reflect the current repository structure after v0.5.6:
        - `world.py` and `banners.py` now listed in file structure.
        - Module responsibilities updated to reflect `World` and `simulate_advance_turn(...)` in `world.py`.
        - `main.py` responsibilities updated to reflect decomposed shell functions.
        - `banners.py` responsibilities documented.
        - Turn flow updated to include startup, character creation, and world setup steps.
    - Added missing v0.5.6 changelog entry.

## Version 0.5.6 (Patch) - 2026-03-14
- **Structural Code Cleanup:**
    - Extracted `World` and `simulate_advance_turn(...)` from `main.py` into new `world.py`.
    - Extracted ASCII banner constants from `main.py` into new `banners.py`.
    - Decomposed `start_game()` into smaller shell-level functions in `main.py`:
        - `create_character()`
        - `setup_initial_world(...)`
        - `game_loop(...)`
    - Preserved all existing terminal behavior, prompts, output ordering, advancement flow, event display, and quit behavior exactly.

## Version 0.5.5 (Minor) - 2026-03-14
- **Person to Human Naming Correction:**
    - Renamed the concrete implemented model class from `Person` to `Human`.
    - Renamed the module `comp_life/person.py` to `comp_life/human.py`.
    - Updated all imports and code references across `main.py` and `events.py` to use the new `Human` class and `human` module.
    - Updated documentation (`docs/architecture.md`) to reflect `Human` / `human.py` for the concrete model.
    - Preserved all existing character creation, lifecycle math, event filtering, and overall game behavior exactly.

## Version 0.5.4 (Minor) - 2026-03-14
- **Derived Lifecycle Cleanup:**
    - Introduced `Person.get_lifecycle_state(current_year, current_month)` as a formal access boundary for derived lifecycle state.
    - This method returns a structured dictionary containing `age_years`, `age_months`, `life_stage`, and `life_stage_model` ("human_default").
    - Refactored `Person.get_age()`, `Person.get_age_in_months()`, and `Person.get_human_life_stage()` to delegate to `get_lifecycle_state()`.
    - Updated `Person.display_snapshot()` to use `get_lifecycle_state()` for lifecycle-derived values.
    - Modified `events.py` to call `person.get_lifecycle_state()` once and use its result for event filtering, replacing separate direct lifecycle calls.
    - Preserved all existing age math, life-stage thresholds, snapshot values, and event eligibility behavior exactly.
    - Refreshed `docs/architecture.md` to accurately reflect the current repository structure and responsibilities.

## Version 0.5.3 (Minor) - 2026-03-12
- **Structured Turn Result Contract:**
    - `simulate_advance_turn(...)` function now returns a stable, structured dictionary (`months_advanced`, `events`, `had_any_events`) instead of a raw list of event messages.
    - This enforces a cleaner separation between simulation logic and terminal rendering.
    - `start_game()` now consumes this structured result to render post-turn output.
    - Preserves all previously validated advancement, event, and output behavior exactly.

## Version 0.5.2 (Minor) - 2026-03-12
- **Simulation Boundary Extraction:**
    - Introduced `simulate_advance_turn(world, player_id, months_to_advance)` as a reusable simulation-step boundary in `main.py`.
    - This function encapsulates month-by-month advancement, event collection, and data return, while remaining completely free of terminal I/O.
    - Terminal input handling and output rendering remain in `start_game()`.
    - Cleaner separation of concerns: terminal layer is now a shell, simulation logic is isolated and testable.
    - All validated advancement behavior, event triggering, and display preserved exactly.

## Version 0.5.1 (Patch) - 2026-03-12
- **Terminal Presentation & Event Frequency Polish:**
    - Replaced ASCII title and time advanced banners with refined versions.
    - Added a new ASCII quit banner that displays when the player exits via "quit".
    - Updated the time advance prompt text to: "Press Enter for the next month, type a number to skip months, or type 'quit': "
    - Implemented a 50% chance for monthly event generation in `events.py`.
    - Ensured `events.py` returns an empty list when no event is triggered (by chance or due to lack of suitable events).
    - Modified `main.py` to only display triggered events (no silent filler messages for quiet months).
    - Added a single fallback line ("No notable events occurred during this period.") when no events occur during the entire advancement turn.

## Version 0.5.0 (Minor) - 2026-03-12
- **Customizable Month Advancement & Dated Events:**
    - Implemented customizable month advancement: Pressing Enter advances 1 month, typing a positive integer advances that many months, and typing 'quit' exits the game.
    - Added robust input validation to reject invalid inputs (0, negative numbers, floats, non-numeric strings).
    - Ensures internal processing remains month-by-month even for multi-month skips.
    - All displayed event messages now include the simulation date in `[Year X, Month Y]` format.
    - Updated prompt text to: "Press Enter for 1 month, type a number to advance multiple months, or type 'quit': ".
    - Improved post-advancement display sequence (banner, snapshot, then collected dated events).

## Version 0.4.1 (Patch) - 2026-03-12
- **Terminal Presentation Polish:**
    - Replaced plain startup title/welcome with ASCII art title banner.
    - Replaced plain `--- Time Advanced ---` heading with ASCII art banner.
    - Improved advance prompt text: "Life unfolds... Press Enter to advance one month, or type 'quit' to end your journey: ".
    - Removed "Month X:" prefix from event entries in the `--- Events ---` section for cleaner display.
    - Made character creation's first name input required.

## Version 0.4.0 (Minor) - 2026-03-11
- **Enhanced Human Character Creation:**
    - Integrated `species` as a core identity field in the `Person` class, fixed to `"Human"` for this patch.
    - `Person.name` attribute removed; full name is now derived via `Person.get_full_name()` from `first_name` and `last_name`.
    - `Person.display_snapshot` updated to show `Full Name`, `Species`, `Sex`, and `Gender` in the `--- Identity ---` section.
    - Character creation flow in `main.py` now uses menu-driven input with numbered choices and validation for `sex` (Male/Female) and `gender` (Male/Female/Non-binary).
    - First name and last name inputs are now optional (can be left empty).
    - Parent `Person` objects updated to align with new identity fields.
    - This establishes a more robust and future-expandable identity and creation system.

## Version 0.3.0 (Minor) - 2026-03-11
- **Enhanced Event System & Presentation:**
    - Event processing and presentation are now strictly separated: `get_monthly_event` processes events and applies effects, `main.py` displays event messages (as a list) under a new `--- Events ---` section *after* the updated life snapshot.
    - `get_monthly_event` now returns a *list* of event messages (even if only one), and `main.py` iterates through this list for display.
    - Removed `Person.event_log`; event messages are displayed immediately per turn without storing a per-person log.
    - Removed implementation-detail text (e.g., `(Health +1)`) from visible event messages.
- **UI & Stat Refinements:**
    - Renamed snapshot section from `Stats` to `Statistics`.
    - Player's starting `health`, `happiness`, and `intelligence` are now randomized via `Person.randomize_starting_statistics()` immediately after player creation in `main.py`. Tighter, human infant-appropriate ranges are used (Health: 85-100, Happiness: 80-100, Intelligence: 45-60). `money` remains 0.
- **Expanded Monthly Event Pool:**
    - Expanded event pool to 16 beginner-friendly events, exclusively focused on "Infant" (8 events) and "Child" (8 events) life stages.
    - Events are monthly-appropriate, include positive, neutral, and mild negative scenarios, and are filtered by `life_stages`, `min_age_months`, and `max_age_months` to ensure appropriateness.

## Version 0.1.0 (Minor) - 2026-03-11
- **Cleanup Patch:**
    - Improved stat handling: Added `Person.modify_stat()` helper method for centralized stat changes with clamping.
    - Event system cleaned up: Removed old prototype events; `events.py` now contains only a placeholder `process_random_event` function that returns a message string.
    - Corrected event message printing: `events.py` now only returns event messages, `main.py` is responsible for printing, preventing duplicate output.
    - Fixed `SyntaxError` in `main.py`'s `World` class `__init__` method regarding the `location` parameter.
    - Refined life snapshot display in `Person.display_snapshot` for clarity: Age and Year/Month on separate lines, `--- Stats ---` and `--- Family ---` headers.
    - Changed starting money in `Person.__init__` to $0.
    - Introduced `Person.get_human_life_stage` for derived life stage, displayed in snapshot.
    - Introduced `World.advance_months(1)` for 1-month progression, removed redundant `Year X, Month Y` from input prompt and simplified advancement heading.
    - Consolidated top-level World location display into the `Person.display_snapshot` method.
    - Introduced `Person.relationships` dictionary with `family` category for `mother_id` and `father_id`, explicitly displayed in snapshot.
