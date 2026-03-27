Actora Master Context v9

Purpose

This document is the durable identity and architecture anchor for Actora.

It defines what Actora fundamentally is, what the project is trying to become, and which approved architectural truths should guide future planning, review, and implementation.

This is a stable source document.
It should stay focused on durable truth rather than temporary brainstorming or patch-level chatter.


1. Project identity

Actora is an actor-anchored simulation framework built inside the broader Compverse direction.

It is not just a narrow human life simulator, and it is not just a detached world-management sandbox.
It is a continuous universe simulation designed to support focused actor play inside a larger world and universe-scale model.

Early implementations may remain grounded, simplified, and example-driven.
However, the architecture should be built to support the broader future product rather than forcing the project to escape a narrow prototype later.

Actora should be understood as:
- actor-anchored
- player-centered through the current focused actor
- universe-scale in architectural direction
- continuous within one save/universe
- layered in simulation depth
- context-sensitive in rules and meaning
- flexible in future presentation, scope, and interaction styles

The player primarily experiences the simulation through a current actor, but that actor always exists inside a larger continuous universe state that does not stop being real just because attention is focused locally.


2. Core framing

Actora is centered on the idea that a player primarily lives through a current actor within a much larger simulation container.

The current actor matters.
Their history matters.
Their relationships, possessions, context, opportunities, and life path matter.

At the same time, that actor exists inside a broader universe that also contains:
- other actors
- other entities
- systems
- metrics
- records
- links
- context layers
- major timeline and structural transitions

The project therefore must support both:
- intimate actor-anchored simulation
- broader world/universe-scale simulation structure

The player should be able to remain inside one continuous universe save while shifting attention across different scopes of the same simulation rather than treating actor play and broader observation as separate unrelated games.

The world is bigger than the focused actor, but the focused actor still matters most as the primary emotional anchor of play.


3. Universe model

A Universe is:
- one save
- one simulation container
- one shared simulation state
- one shared simulation history
- one shared current universe time
- the container for all actors, entities, systems, metrics, records, links, and context belonging to that save
- the continuous play space in which actor lives, line continuation, archive history, and broader-scope observation all occur

A Universe is not just a file.
It is the active simulation container and the continuing play-space context.

One universe should have one shared advancing timeline.
Advancing time advances that universe as a whole.

A universe may later contain:
- multiple places
- multiple countries
- multiple world bodies
- multiple civilizations
- different eras of history
- unusual cross-context interactions
- wider spatial hierarchy above ordinary world scale

But those all still belong to the same universe if they share the same continuing simulation state and time progression.

The death of a currently focused actor should not be treated as automatic universe termination.
The universe persists beyond one life, one line, or one moment of play focus.


4. Core conceptual skeleton

The approved main conceptual skeleton for Actora is:

- Universe
- Entity
- Actor
- System
- Metric
- Record
- Link
- Context

These are the durable conceptual anchors.

Universe — Simulation Root

The Universe is the top-level container of the simulation.

A Universe instance contains and governs the full simulation state, including:

• the shared advancing timeline  
• the entity registry  
• the system execution environment  
• simulation records and metrics  
• link structures between entities  
• broader contextual state

Actors, places, objects, organizations, and future entity types exist within a Universe and cannot exist outside it.

One Universe operates with one shared advancing timeline.  
All simulation steps occur within a Universe context.

The prototype currently runs a single Universe instance, but the architecture intentionally allows for the possibility of multiple Universes in the future.

Foundational cross-cutting layers also include:
- Type
- Scope

These do not replace the main conceptual skeleton.
They help describe what kind of thing something is and the level at which something is viewed, simulated, or measured.

4.1 Universe
The top-level simulation container for one save.

4.2 Entity
A broad tracked thing that exists in a universe.
An entity has identity, state, and persistence, but does not necessarily act.

4.3 Actor
A special kind of entity that can behave, change meaningfully over time, accumulate history, influence and be influenced, and potentially be followed or played.

4.4 System
A process/rule layer that drives simulation behavior and updates state.

4.5 Metric
A tracked or derived measurement describing conditions or results at some scope.

4.6 Record
A preserved piece of simulation history, reference state, or transition history.

4.7 Link
A structured connection between things in the simulation.

4.8 Context
The structured conditions that determine what rules, meanings, opportunities, availability, and behavior apply.

4.9 Type
A foundational cross-cutting layer that helps distinguish what kind of thing something is without flattening everything into weak strings.

4.10 Scope
A foundational cross-cutting layer that helps distinguish the level at which something is viewed, simulated, measured, or presented.

4.11 How these relate
A Universe contains all other concepts. Entities are the broad tracked things within a universe. Actors are a special kind of Entity that can behave and accumulate history. Systems operate on Entities and Actors to drive simulation behavior and update state. Metrics describe conditions or results at some scope within a universe. Records preserve history produced by transitions, events, and meaningful state changes. Links are structured connections between any tracked things in the simulation. Context shapes what rules, meanings, availability, and behavior apply to a given situation. Type and Scope cut across all of the above, helping distinguish what kind of thing something is and at what level it is viewed or simulated.

This is not a full ontology. It is a baseline orientation to prevent different sessions from interpreting the skeleton in contradictory ways.


5. Actor-centered but not human-first

Actora should not be framed as human-first in architecture.

Human-focused early examples or demo content are acceptable.
Human-only current implementation truth may also be acceptable at specific phases.
But the architecture should not hard-bake Human or Person as the universal top-level being model.

Actor is the broader player-centered being layer.
Playability should be treated as a mode, state, or permission, not as the fundamental type of being.

This means:
- an actor may be playable, followable, autonomous, or background-simulated at different levels
- Human is not the only meaningful future actor form
- future actor forms may include non-human beings, synthetic beings, robots, alien beings, and other context-valid actor types

The architecture should remain safe for broader actor types even when early content remains narrower.


6. Layered simulation depth

Layered simulation depth is a hard principle.

Actora should not assume that every actor, entity, or system must be simulated at the same level of detail.

The long-term model should support at least the idea of:
- higher-detail simulation for the currently focused or directly relevant actor layer
- medium-detail simulation for meaningful surrounding actors, entities, and systems
- lower-detail or aggregate simulation for broader world conditions, populations, and macro systems

This is necessary for feasibility, scale, and coherence.

Actora should pursue believable and internally coherent simulation, not brute-force total-detail realism.
The project should avoid architectural choices that assume universal full-detail simulation for everything.


7. Timeline and era context

Timeline and era context are major architecture concerns, not minor flavor notes.

A universe has one shared current universe time.
That time exists within broader timeline and era context.

Era and timeline context affect things such as:
- what exists
- what is available
- what is possible
- what is legal
- what is normal
- what systems, institutions, opportunities, items, technologies, and actions are present or absent

Timeline-aware world state is a protected future direction.
The project should preserve the ability for different eras to meaningfully alter world conditions and available actions.

The architecture should also remain safe for long-term expansion toward broad historical and future timeline ranges, including larger timeline horizons if they become relevant later.

Local calendar representations may later differ by place, world body, civilization, or context, but these remain interpretations layered on top of shared universe time rather than independent authoritative simulation clocks.


8. Galaxy and spatial hierarchy protection

The long-term spatial model must remain extensible enough to support hierarchy above ordinary local world assumptions.

Protected long-term hierarchy direction includes:
- galaxy
- star system / solar system
- world body / celestial body
- country
- city
- property / site / vessel / station

This does not mean all such layers must be implemented early.
It means the architecture must not casually trap the project in a single-planet, single-country, or purely local location model.

Actora should preserve the ability for universe simulation to operate across multiple spatial scales and contexts.


9. Ownership, residence, and location separation

Ownership, residence, and immediate location should remain separate concepts.

The model should explicitly protect long-term separation between:
- current location
- residence/home/household
- owned property
- political affiliation or jurisdiction
- temporary occupancy or vessel/station context

The architecture should not flatten all of these into one generic location field.
This separation is important for future systems involving property, household life, movement, political structure, access, and simulation realism.

Inventory, ownership, and property are protected future architecture concerns even if full implementation remains later.


10. Records, links, and history

Actora must treat history as structurally important.

Records should not be reduced to disposable UI text.
Important changes, transitions, and simulation-relevant history should be able to exist as preserved records.

Links are also structurally important.
Many meaningful simulation realities are not isolated objects but structured connections between things.

Examples of future-important link types may include:
- family links
- household links
- ownership links
- residence links
- employment links
- organizational membership
- political belonging
- item possession or access
- guardianship
- obligation or debt

History should also be allowed to exist at multiple scopes later, such as:
- actor history
- family or household history
- universe history
- archive or lineage records


11. Major structural transitions

Actora should treat major actor transitions as structural transitions, not throwaway flavor.

This includes long-term support for transitions such as:
- birth
- creation / activation / spawn
- death
- archive status
- lineage continuation
- continuity through other relevant connected actors
- major status changes affecting playability or simulation role

Death in particular should not be treated as just another event line.
It affects actor state, record layers, links, ownership consequences later, and potentially lineage, archive status, or future continuity of play within the same universe.

Birth, death, archive, continuity, and lineage are major simulation transitions.

Major structural transitions should eventually produce or alter Records, Links, and related state depending on context. This is a structural expectation, not an immediate implementation requirement.

The end of one actor’s life should not automatically mean the end of the universe save.
Actor lines may be archived, continuity may move through relevant connected actors, and the larger universe should remain capable of continuing beyond a single life.


12. Context-sensitive behavior

Actor behavior should eventually be shaped by more than flat random events.

The long-term direction should allow behavior to be shaped by:
- skills
- traits
- pressures
- history
- context
- uncertainty
- error
- imperfect information
- misjudgment
- limited perception or memory

This does not imply immediate implementation of a full behavior brain.
It does imply that future actor behavior should remain compatible with bounded, context-sensitive, imperfect simulation rather than idealized perfect decision logic.

Context also means that different kinds of actors may not share the same exact meaning for skills, traits, life histories, pressures, or opportunities.


13. Multiple future interaction styles

Actora should remain compatible with multiple future interaction styles within one continuous simulation.

Protected future possibilities include:
- direct actor play
- guided or lightly influenced actor play
- observer/follow play
- actor switching at the current universe time
- broader system observation
- broader system influence at later stages
- different information-density or immersion styles in the UI
- scope shifting between local actor life and broader world/universe views inside the same save

The simulation core should not be built in a way that requires a rewrite for each future interaction style.

Actora should preserve the ability to support different presentation, focus, and control styles over time without assuming that actor play, broader observation, and larger-scope interaction must become hard-separated boxed modes or separate games.


14. Presentation direction

The current prototype may remain terminal-first.
That is a practical implementation choice, not the final intended presentation.

The core simulation should remain UI-agnostic.
The terminal should be treated as a temporary shell rather than the permanent form of the product.

Actora should remain compatible with future presentation forms such as:
- text-first interaction
- panel-based UI
- visual actor/world views
- map or scope-switching interfaces
- inventory, lineage, archive, and record-driven interfaces
- mixed micro-to-macro observation and control views

The architecture should not hard-code presentation restrictions into the simulation core.


15. Feasible simulation over brute-force realism

Actora should aim for simulation that is:
- coherent
- believable
- layered
- computationally sane

The goal is not to simulate everything at maximum microscopic fidelity.
The goal is to build a simulation model that feels real enough, behaves consistently enough, and supports meaningful player-centered play inside broader systems.

The architecture should prefer:
- meaningful structure
- selective fidelity
- strong records and links
- layered abstraction
- future-safe expansion

over:
- universal detail for everything
- fake complexity with weak structure
- brute-force population simulation
- UI-driven architectural shortcuts


16. Stable baseline summary

Actora is an actor-anchored simulation within a layered, continuous, universe-scale framework.

Its stable architecture should protect for:
- a universe-based save model
- one continuous universe play space per save
- a non-human-first conceptual skeleton
- actor-anchored play inside broader simulation
- continuity beyond a single actor life
- layered simulation depth
- one universe with one shared advancing timeline
- explicit timeline/era context
- explicit galaxy/spatial hierarchy protection
- separation of ownership from residence, current location, and occupancy
- records and links as structural concepts
- Type and Scope as foundational cross-cutting layers
- major lifecycle, archive, and continuity transitions
- UI-agnostic simulation foundations
- future interaction flexibility within the same continuing simulation
- feasible simulation rather than brute-force realism


17. What this document should not do

This document should not become:
- a parking lot for every brainstorm
- a patch-by-patch implementation log
- a giant workflow manual
- a substitute for the roadmap
- a substitute for the working ideas register

18. Controlled State Mutation and Simulation Boundaries

Actora should avoid broad, scattered direct mutation of actor and world state across many subsystems.

Core rule
- subsystems should prefer producing structured outcomes over performing broad direct state mutation
- systems are producers of effects or intent, not free-for-all state editors

Time mutation rule
- only the simulation step boundary should advance shared simulation time
- no subsystem should directly mutate shared simulation time

Universe simulation step boundary
- the Universe simulation step is the authoritative boundary for shared state mutation and time progression
- systems should produce structured outcomes rather than freely mutating actor or world state
- the Universe collects those outcomes during the simulation step and applies them in a controlled mutation phase
- only the Universe simulation step may advance simulation time, apply authoritative shared state mutation, create structural records, and finalize system effects

Direction of travel
- as Actora grows, state mutation should become increasingly centralized by domain
- stats should move toward controlled stat-application paths
- relationships should move toward controlled link or relationship mutation paths
- record creation should move toward controlled record-writing paths
- money and other resource-like values should move toward controlled domain application rather than scattered edits

This does not mean Actora should build a giant mutation engine immediately.
It means future foundations should be shaped so that:
- systems return structured outcomes cleanly
- hidden side effects are reduced
- mutation domains become easier to centralize over time

Anti-pattern to avoid
- scattered direct mutation across many subsystems, such as multiple unrelated systems independently editing actor stats, relationships, money, records, or shared world state in ad hoc ways
- this pattern becomes increasingly hard to reason about, test, balance, and extend as the simulation grows

Connection to existing architecture philosophy
- this reinforces output contracts over direct printing
- it matches the broader Actora preference for structured representations over loose, ambiguous state handling
- it supports layered simulation depth by making system interaction more legible and less chaotic

It should stay focused on durable identity and architecture truth.
