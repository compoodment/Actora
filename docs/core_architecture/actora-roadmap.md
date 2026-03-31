---
title: Actora Roadmap
role: sequencing-and-dependency-order
stability: high
tags: [roadmap, sequencing, planning]
---

Actora Roadmap v10

1. Roadmap framing

Actora is an actor-anchored, continuous universe simulation being built foundation-first inside the broader Compverse direction.

The prototype may remain simple, terminal-first, and example-driven for now, but the roadmap should follow the architecture of the intended product rather than hard-baking a narrow prototype shape that must later be escaped.

Actora is not only a grounded life simulator and not only a detached world-management sandbox.
It is a layered simulation framework intended to support focused actor play inside a larger world and universe-scale model, while remaining compatible with broader same-save scope shifting over time.

The roadmap is organized around four principles:

1. Foundation before expansion
Structural simulation layers come before content-heavy or high-visibility systems.

2. Dependency order over novelty
Systems are introduced only when their prerequisites are already stable enough to support them honestly.

3. Architectural durability over short-term convenience
Early implementation should avoid assumptions that would block later growth, continuity, or scale-shifting within the same simulation.

4. Current truth over hype
The project should not pretend future ideas are already implemented, and should not let temporary presentation convenience define the architecture.

This roadmap is not trying to turn Actora into a pile of disconnected sub-games.
It exists to preserve a coherent path toward one continuous simulation where actor life remains the emotional anchor even as broader scope becomes relevant.


2. Current durable architecture direction

The roadmap assumes the following approved baseline:

- Universe / Entity / Actor / System / Metric / Record / Link / Context are the main conceptual skeleton
- Type and Scope are foundational cross-cutting layers
- Universe is the top-level simulation container for timeline, entities, links, records, systems, and context
- one universe should have one shared advancing timeline
- one universe should function as a continuous play space, not only a passive state container
- Entity is the universal simulation object layer
- Actor is the main player-centered being layer
- Actor is a specialized entity capable of agency, lifecycle progression, and playable focus
- playability is a mode, not a type
- the architecture should not be framed as human-first
- actor-centered play should remain primary even when broader-scope observation or action exists
- layered simulation depth is a hard principle
- the terminal prototype is temporary; the core should remain UI-agnostic
- era/timeline context is a major availability and mechanics layer
- galaxy-level hierarchy protection is explicit long-term direction
- ownership/property/inventory are protected future architecture concerns
- ownership should remain conceptually separate from residence, current location, and occupancy
- birth/death/archive/lineage/continuity are major structural transitions
- continuity beyond a single actor life is protected
- the architecture should remain compatible with continued play through relevant connected actors within the same universe
- controlled state mutation is a protected architectural direction: systems should prefer returning structured outcomes over performing broad direct mutation, and only the simulation step boundary should advance world time
- Link is the universal relationship layer connecting entities across systems (family, ownership, residence, organizational affiliation, role assignment, and more)
- links should remain category-agnostic and extensible rather than hard-coded to specific relationship types
- same-save shifting of attention across actor and broader simulation scope is protected, even if exact scope behavior remains a later implementation concern
- broader-scope play should remain part of the same continuing simulation rather than splitting into detached parallel systems

The roadmap should remain compatible with these baseline truths.


3. How to read this roadmap

This roadmap is a dependency-order document, not a progress tracker.

Use it to answer:
- what comes before what
- what must remain deferred
- what layers are allowed to depend on other layers
- what kinds of proposals are structurally early or late
- how the clarified continuous-simulation product identity should still obey dependency order

Do not use it as the primary source for:
- the exact currently shipped code version
- which patch number landed last
- implementation history
- repo-local file truth

Those belong in repo truth, especially the codebase, repo documentation, and the repo [[changelog]].

A roadmap layer may be introduced, tightened, or cleaned up across multiple code versions.
That does not require the roadmap itself to change unless sequencing or architectural dependency order changed meaningfully.

Minor and patch-level cleanup versions may occur between larger roadmap layers when they preserve dependency order and do not materially change sequencing.
Not every cleanup version requires a roadmap revision.

The roadmap should be read in light of the approved product identity:
Actora is one continuing simulation, not a pile of disconnected actor, world, and macro systems stitched together after the fact.


4. Backbone sequence

The backbone sequence is the durable dependency ladder for Actora.
Earlier layers may already exist in the repo. Later layers may still be pending.
That does not change the order.

4.1 Simulation Step Foundation

Purpose
Establish an authoritative simulation-step boundary for shared time progression and controlled turn advancement.

Why it belongs early
Without a real simulation-step boundary, time progression, event handling, and later system interaction all get scattered across shell code and ad hoc helper calls.

Should protect
- one place for authoritative shared time advancement
- separation between simulation behavior and terminal presentation
- future-safe support for broader system orchestration

4.2 Turn Result / Output Contract Foundation

Purpose
Return structured outcomes from simulation work instead of embedding presentation logic into lower-level systems.

Why it belongs early
Actora should be able to render results differently across terminal and future interfaces without changing simulation truth.

Should protect
- structured result shapes
- output contracts over direct printing
- cleaner review and verification of behavior-preserving changes

4.3 Derived Lifecycle Foundation

Purpose
Keep age, age-in-months, life stage, and similar actor lifecycle information derived rather than loosely stored and recalculated inconsistently.

Why it belongs early
Many downstream systems depend on lifecycle state. If lifecycle logic drifts across files, event rules and later domain systems become contradictory.

Should protect
- formal lifecycle derivation access
- one-source-of-truth age/life-stage logic
- compatibility with future life-stage expansion

4.4 Event Foundation

Purpose
Establish events as structured simulation outcomes rather than flavor-only text.

Why it belongs here
Events already sit in the core loop. They need to be structurally reliable before links, places, records, and later systems depend on them.

Should protect
- lifecycle-aware event generation
- structured event results
- simulation/rendering separation
- compatibility with future richer conditions and outcomes

4.5 Current Actor Structural Cleanup

Purpose
Keep the current actor implementation honest and structurally safe while avoiding model fragility.

Why it belongs here
Before links, places, and domain systems depend on actor state, the current actor model needs proper structured internals, clear responsibilities, and safe derived access patterns.

Should protect
- clear actor responsibilities
- centralized stat mutation
- compatibility with later actor-safe architecture
- honesty about current implementation limits without making the architecture human-first

This layer may still be realized through narrower concrete implementation at specific phases, but the roadmap should not harden that temporary narrowness into permanent project identity.

4.6 Link Foundation

Purpose
Expand from a narrow relationship foundation into a broader link model capable of supporting non-family and nontrivial structural connections.

Why it belongs here
A lot of future simulation depends on links between things rather than isolated object attributes. Actora is actor-anchored, but not actor-isolated. A stronger link layer should exist before deeper household, property, organizational, and social systems are attempted.

Depends on
- event foundation
- current actor structural cleanup
- centralized lifecycle derivation rules

Should include
- broader link categories beyond family
- clean structural support for non-family connections
- future-safe support for ownership, residence, organizational, and role-related links later
- link data that downstream systems can depend on safely

Should not include yet
- romance depth systems
- compatibility modeling complexity
- marriage/divorce/legal frameworks
- social drama content expansion
- social network analytics

4.7 Structured Place Foundation

Purpose
Replace vague location strings with structured place entities while preserving long-term support for a broader spatial hierarchy.

Why it belongs here
Once actors, lifecycle rules, events, and links are structurally stronger, the simulation can safely stop treating place as loose text. Place becomes real data at this stage, but only at a foundational level.

Depends on
- stable simulation/output contract
- actor and link foundations
- event framework capable of referencing places cleanly

Architectural direction preserved by this layer
The long-term place/world model should remain extensible enough to support:
- galaxy
- star system / solar system
- world body / celestial body
- country
- city
- property / site / vessel / station

Early implementation does not need to build all of these layers, but it should avoid assumptions that would make them impossible later.

Should not include yet
- travel gameplay
- country simulation depth
- property systems
- vessel/station gameplay
- multi-world or space-travel implementation
- spatial scope added just because it sounds exciting

4.8 Spatial Identity Separation

Purpose
Formally separate current location, residence/home, owned property, political jurisdiction/affiliation, and temporary occupancy context into distinct concepts.

Why it belongs here
Structured place alone is not enough. The simulation should not collapse where something is, where it resides, what it owns, what political layer it belongs to, and whether it is temporarily occupying a vessel/station into one generic location field. This separation must happen before travel, property, or politics go deeper.

Depends on
- structured place foundation
- stronger link model
- actor/entity backbone mature enough to attach spatial identity correctly

Should include
- formal separation between:
  - current location
  - residence/home/household
  - owned property
  - political jurisdiction/affiliation
  - temporary occupancy/vessel/station context

Should not include yet
- full travel mechanics
- full country simulation
- property gameplay depth
- alliance systems

4.9 Controlled State Mutation Foundation

Purpose
Establish a formal framework for applying simulation state changes instead of allowing increasingly ad hoc mutation across files.

Why it belongs here
As more systems exist together, uncontrolled state mutation becomes rewrite bait. The project needs a clean rule for how meaningful changes are applied before deeper domain layers are added.

Depends on
- actor, event, link, and place foundations all being real enough to justify a mutation framework

Should include
- a clear mutation approach for cross-system state change
- cleaner protection against hidden side effects
- future-safe support for more complex interactions between systems

Should not include yet
- full save/load
- deep transaction/audit systems unless truly needed
- architecture theater with no practical effect

4.10 Identity Generation System

Purpose
Introduce a structured identity-generation layer responsible for creating new actors using simulation context instead of static placeholder rules.

Why it belongs here
Early prototype pools are acceptable scaffolding, but a mature simulation should generate identities in ways that reflect world context. Names, family identity patterns, and similar generation logic should eventually respond to structured simulation context rather than global fixed pools.

Depends on
- stronger actor and link foundations
- structured place and context maturity
- controlled state mutation direction being real enough to support cleaner actor-creation paths

Should include
- context-sensitive name generation
- family identity generation rules shaped by simulation context
- future-safe support for place-, culture-, era-, or world-sensitive identity generation

Should not include yet
- fake context realism built on weak foundations
- broad culture simulation without supporting systems
- terminal UX expansion as a substitute for stronger simulation context


5. Mid-stage domain layers

These layers are valid and likely, and several of them are part of the intended long-term pillars of the product.
They should still follow the backbone work above rather than leap ahead of it.

Education / Training Foundation
Add education, training, and structured skill-development systems only after actor, event, link, and state-mutation foundations are stable.

Work / Role Foundation
Add jobs, roles, income, and work-state logic only after education/training or equivalent readiness rules can exist cleanly.

Economic / Market / Organization Foundation
Add firms, organizations, markets, investment structures, and broader economic interaction only after work/role, links, records, place, and state-mutation foundations are strong enough to support them without fake spreadsheet theater. Economy is a real future pillar of Actora, but it should not be smuggled in before its structural prerequisites exist.

Health / Condition Foundation
Add health and illness as real systems only after lifecycle derivation, events, links, and controlled state change are strong enough to carry them.

Property / Household / Inventory Foundation
Add owned places, residence logic, household depth, inventory, and item ownership only after structured place and spatial identity separation exist.

Travel / Movement Foundation
Add travel and movement logic only after structured places and spatial identity separation are stable. Long-term movement should not assume all travel is terrestrial or confined to one world body.

Country / Political Layer
Add countries as a separate political layer only after structured places and movement foundations exist. Country is not the top of the long-term world model. Politics and world conditions are real future pillars, but should still be added in dependency order rather than as premature macro-feature dressing.

Multi-world / Vessel / Station Expansion
Add support for non-fixed sites, multiple world-body contexts, vessels, and stations only after structured places and movement rules are mature.

Star System / Interplanetary Layer
Add structured support above world bodies at the star-system or solar-system level only after multi-world support proves necessary.

Galactic Layer
Reserve structured support for the broadest spatial tier only after all lower spatial layers are already proven.

Alliance / Inter-country Layer
Add supra-country political structures only after country systems and broader world structure actually exist.

Personal Clock / Multi-clock Time Layer
Support more granular or parallel time structures only if the month-based foundation becomes a proven limitation. Calendar systems remain separate from internal simulation time.

Exceptional Cross-context Systems
Add rare rule-bending layers such as time-travel or other exceptional cross-context bridges only after ordinary world/context foundations are already mature.

Social Perception / Reputation / Opportunity Layer
Add multi-axis social perception, reputation, discovery, rumor, misinformation, and opportunity-generation systems only after stronger actor/context/link/record foundations exist. This is a real later vision component, but it should not be promoted into immediate foundation work.


6. Roadmap sequencing logic

The roadmap follows a strict dependency order.

First: stabilize the simulation core
The earliest layers define how time advances, how results are returned, and how derived lifecycle state is handled. Without this, every later system gets built into unstable control flow.

Second: stabilize the event and record framework
Events already exist in the loop. They must become structurally reliable before downstream systems depend on them. Record/history handling also needs stronger grounding early because history is central to actor continuity, archive behavior, and long-term simulation meaning.

Third: clean up the actor model
Before links, places, and domain systems start depending on actor state, the actor model internals should use proper data structures with validated access rather than fragile string-based patterns.

Fourth: strengthen links between things
Actora is actor-anchored, but future realism depends heavily on structured links such as family, ownership, residence, organization, obligation, and other connections. A stronger link foundation should exist before deeper downstream systems.

Fifth: make place real, then separate spatial identity
Once places exist as data, the project must distinguish being somewhere, residing somewhere, owning somewhere, politically belonging somewhere, and temporarily occupying somewhere before deeper travel, property, or politics are added.

Sixth: formalize state changes
When several foundational systems exist together, the project needs a cleaner way to apply state change. This reduces rewrite risk and contradiction.

Seventh: expand into domain systems
Only after the above foundations are sufficiently established should the project add education, work, economy, health, property, travel, political/world systems, social perception systems, and later exceptional cross-context mechanics.

Actora is intended to support broader same-save scope shifting over time, but that should not be used as an excuse to build macro systems before their prerequisites exist.
The correct path is still: foundation first, then domain layers, then larger-scope richness.

Foundation being “sufficiently established” should not be treated as “frozen forever.”
If a real missing prerequisite seam is discovered later, corrective foundation work may still be justified.
That does not destroy the roadmap; it means dependency truth won over momentum theater.

This order preserves architectural cleanliness, limits rework, keeps the terminal layer from becoming the permanent shape of the simulation, and protects the product from splitting into disconnected actor-sim / world-sim / economy-sim fragments.


7. Long-term architectural guardrails

Foundation-first
Do not add expansion systems before their prerequisites are stable.

Month-based core time
Internal simulation remains month-based unless a later, proven need justifies more complex time architecture.

One universe, one advancing timeline
A universe save should have one shared advancing timeline. Future alternate outcomes should not be casually smuggled in without explicit branching or separate-universe design.

One universe is a continuous play space
A universe should not be treated only as a state container. It is the continuing play space in which actor lives, continuity, archives, and broader-scope interaction remain connected.

Calendar systems are not internal sim time
Calendars remain future display/worldbuilding layers that interpret simulation time rather than define core internal time logic. Different places, worlds, or civilizations may later expose different local calendar representations, but these remain layered on top of shared universe time rather than replacing it.

Derived state remains derived
Age and life stage should remain derived rather than stored directly unless a future architectural need justifies a deliberate exception.

Derived state access should converge
Derived actor-state should be accessed through formal helpers, a derivation boundary, or a consistent query pattern rather than recalculated ad hoc across files.

Snapshot and event separation
Current-state snapshot output should remain separate from events, results, and turn history.

Output contracts over direct printing
Simulation systems should return structured results rather than embedding presentation logic.

Terminal UI is not the architecture
The terminal interface is a temporary shell. Core simulation logic should remain usable independently of terminal rendering. Terminal convenience should not justify duplicated state, formatting-driven contracts, or simulation logic embedded in presentation code.

Layered simulation depth is a hard principle
Not every actor, entity, or system should be simulated at the same depth. The architecture should remain compatible with higher-detail focused simulation and more abstract broader-world simulation.

Actor-anchored play remains primary
Even when broader-scope observation or action exists, the product should not lose the actor as its primary emotional anchor.

Same-save scope breadth is protected
The architecture should remain compatible with shifting attention across actor, local, regional, world, and broader spatial scope inside the same continuing simulation. This is architectural direction, not a demand to implement every scope layer early.

Broader-scope play should not become detached sub-games
World observation, political layers, economic layers, and other broader-scope systems should remain part of the same continuing simulation rather than drifting into disconnected parallel game structures.

Structured places, not loose location text
Place should eventually be modeled as structured data rather than open-ended strings.

Hierarchy-capable spatial model
The long-term place/world model should remain extensible enough to support:
- galaxy
- star system / solar system
- world body / celestial body
- country
- city
- property / site / vessel / station

This is architectural direction, not early implementation scope.

Spatial identity separation
The model should preserve long-term separation between:
- current location
- residence/home
- owned property
- political jurisdiction/affiliation
- temporary occupancy/vessel/station context

These should not be flattened into a single generic location field.

Politics remains its own layer
Countries and alliances should remain separate political layers, not flattened into location strings.

Travel should remain future-safe
Long-term movement should not assume all travel is terrestrial, local, or confined to a single world body.

Context matters
Species, era, place, technology/civilization, legality/social conditions, and broader social perception pressures should be treated as real future architecture concerns, not incidental flavor.

Type and Scope matter
The architecture should remain safe for explicit type/template handling and explicit scope handling. Type should help distinguish what kind of thing something is without flattening everything into dumb strings, and Scope should help distinguish the level at which something is viewed, simulated, or measured.

Controlled state mutation
Systems should prefer returning structured outcomes over performing broad direct mutation across actor/world state. Only the simulation step boundary should advance world time. Over time, state application should become more centralized by domain rather than scattered ad hoc across files.

Continuity beyond one actor life is protected
Birth, death, archive, and continued play through relevant connected actors should remain compatible with the architecture. The end of one actor’s life should not automatically imply end-of-save philosophy.

Persistence remains deferred but should not be sabotaged
Save/load should not be treated as an early feature direction, but foundational systems should avoid designs that make later persistence ambiguous, fragile, or awkward.

Actor-safe architecture is protected
Current implementation truth may remain narrower than the future model at specific phases, but the architecture should not harden a human-only conceptual skeleton into permanent project identity.

Records and links matter
History should not be flattened into throwaway UI text, structured links between things should not be ignored, and record/history scope should remain compatible with actor-level, archive-level, lineage-level, and wider universe-level uses later.

Major transitions are structural
Birth/creation, death, archive state, lineage continuation, continuity shifts, and major status changes should be treated as structural transitions, not just flavor text.

Future interaction flexibility is protected
The simulation core should remain compatible with direct play, guided play, observer/follow styles, actor switching at the current universe time, and broader system observation later without requiring the product to split into separate game identities.

Expansion follows proven need
Broader systems such as education, work, economy, travel, countries, alliances, social perception, and multi-clock time should be added only when their dependencies are satisfied and their architectural need is clear.


8. Do not build yet

The following systems are valid long-term possibilities but should remain deferred until their prerequisites exist:

- deep romance mechanics
- friendship-drama systems
- trait/personality depth before the underlying behavior and context layers are ready
- health/illness depth before lifecycle/event/link/state foundations are ready
- school/education systems before actor/event/link foundations are stable
- job/work systems before actor-state and downstream readiness rules exist
- property ownership gameplay before structured places and spatial identity separation exist
- household simulation depth before residence/home and ownership are distinct
- inventory/item catalogs before ownership and transaction foundations are real
- travel and migration systems before structured places and movement foundations exist
- country systems before place and movement layers are ready
- alliance/diplomacy systems before country systems exist
- vessel/station gameplay before structured non-fixed place support exists
- multi-world or space-travel implementation before lower spatial layers are proven
- macroeconomy or detailed finance systems as a substitute for stronger foundations
- save/load complexity as a major feature direction
- web/app migration as a substitute for core architecture
- large event content packs without stronger event structure
- daily or hourly simulation by default
- route/logistics/infrastructure simulation
- political depth systems without place and movement foundations
- full multi-species gameplay content before actor-safe architecture is protected
- exceptional cross-context systems before ordinary universe/context systems are mature
- context-sensitive identity generation before structured place and context systems exist

The roadmap preserves these as later possibilities without allowing them to distort foundational development order.


9. How to use this roadmap

Use this roadmap as the sequencing anchor for Actora.

It should answer:
- what comes next structurally
- what must remain deferred
- which dependencies must exist first
- whether a proposal strengthens the foundation or merely distracts from it

When a patch idea sounds exciting but does not fit the dependency order, the roadmap should win.
When project truth changes in a meaningful way, the roadmap may be revised deliberately rather than drifting silently.
