---
title: Roadmap
tags: [core, reference, stable]
updated: 2026-04-04
---

# Actora Roadmap

Dependency order. What must come before what.

This is a sequencing document, not a progress tracker. For what's actually implemented, see `codebase.md` and `changelog.md`. For project identity, see `identity.md`.

Foundation before expansion. Dependency order over novelty. Don't build later systems before their prerequisites are stable.

---

## Backbone sequence

The durable dependency ladder. Earlier layers may already exist in the repo. Later layers may still be pending. That doesn't change the order.

### 1. Simulation Step Foundation
Authoritative simulation-step boundary for shared time progression and controlled turn advancement. Without this, time progression and event handling get scattered across shell code.

### 2. Turn Result / Output Contract Foundation
Return structured outcomes from simulation work instead of embedding presentation logic into lower-level systems. Actora should render results differently across terminal and future interfaces without changing simulation truth.

### 3. Derived Lifecycle Foundation
Keep age, life stage, and similar lifecycle info derived rather than loosely stored. Many downstream systems depend on lifecycle state — if it drifts across files, event rules and domain systems contradict.

### 4. Event Foundation
Events as structured simulation outcomes, not flavor-only text. Lifecycle-aware generation, structured results, simulation/rendering separation.

### 5. Current Actor Structural Cleanup
Clean actor internals, clear responsibilities, safe derived access patterns before links, places, and domain systems depend on actor state.

### 6. Link Foundation
Expand from narrow family relationships into a broader link model: non-family connections, future-safe for ownership, residence, organizational, and role-related links.

Depends on: event foundation, actor cleanup, lifecycle derivation.

### 7. Structured Place Foundation
Replace vague location strings with structured place entities. Preserve long-term extensibility toward galaxy → star system → world body → country → city → property/site/vessel.

Depends on: stable simulation/output contract, actor and link foundations.

### 8. Spatial Identity Separation
Formally separate: current location, residence/home, owned property, political jurisdiction, temporary occupancy. These must not be flattened into one generic field.

Depends on: structured place, stronger link model.

### 9. Controlled State Mutation Foundation
Formal framework for applying state changes instead of ad hoc mutation across files. Systems produce structured outcomes → universe collects and applies them.

Depends on: actor, event, link, place foundations all real enough to justify it.

### 10. Identity Generation System
Context-sensitive identity generation. Names, family identity patterns responding to world context (place, culture, era) rather than global fixed pools.

Depends on: actor/link foundations, structured place/context maturity.

---

## Mid-stage domain layers

Valid and likely, but must follow the backbone. Listed in rough dependency order.

**Stats/Traits/Skills foundation** — stat redesign (13 stats, DEC-021), trait pool redesign (12 traits, DEC-022), Skills/Talents architecture (DEC-023). These are actor-level foundations that most domain systems depend on. In progress.

**Action System (first wave)** — time-budget model + sub-type selections. Precedes Education. Depends on Stats/Traits foundation.

**Education / Training** — after action system first wave ships.

**Work / Role** — after education/training or equivalent readiness rules exist.

**Economic / Market / Organization** — after work/role, links, records, place, state-mutation foundations. Economy is a real pillar, but don't smuggle it in before prerequisites exist.

**Health / Condition** — after lifecycle, events, links, controlled state change are strong enough.

**Property / Household / Inventory** — after structured place and spatial identity separation.

**Travel / Movement** — after structured places and spatial identity separation. Don't assume all travel is terrestrial.

**Country / Political Layer** — after structured places and movement foundations. Country is not the top of the world model.

**Multi-world / Vessel / Station** — after structured places and movement rules are mature.

**Star System / Interplanetary** — after multi-world support proves necessary.

**Galactic Layer** — after all lower spatial layers are proven.

**Alliance / Inter-country** — after country systems exist.

**Personal Clock / Multi-clock Time** — only if month-based foundation becomes a proven limitation.

**Exceptional Cross-context Systems** — time-travel or similar rule-bending only after ordinary world/context foundations are mature.

**Social Perception / Reputation / Opportunity** — multi-axis perception, reputation, discovery, rumor. After stronger actor/context/link/record foundations. Real vision component, not immediate foundation work.

---

## Don't build yet

Valid long-term possibilities that must remain deferred until prerequisites exist:

- Deep romance mechanics
- Friendship-drama systems
- Trait/personality depth before behavior and context layers are ready
- Health/illness depth before lifecycle/event/link/state foundations are ready
- Education before actor/event/link foundations are stable
- Jobs before actor-state and readiness rules exist
- Property ownership before structured places and spatial identity separation
- Household depth before residence/home and ownership are distinct
- Inventory/items before ownership and transaction foundations
- Travel/migration before structured places and movement foundations
- Country systems before place and movement layers are ready
- Alliance/diplomacy before country systems exist
- Vessel/station gameplay before non-fixed place support
- Multi-world / space-travel before lower spatial layers are proven
- Macroeconomy as a substitute for stronger foundations
- Save/load complexity as a major feature direction
- Web/app migration as a substitute for core architecture
- Large event content packs without stronger event structure
- Daily/hourly simulation by default
- Route/logistics/infrastructure simulation
- Political depth without place and movement foundations
- Full multi-species content before actor-safe architecture is protected
- Context-sensitive identity generation before structured place and context systems
