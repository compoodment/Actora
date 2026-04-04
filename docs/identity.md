---
title: Identity
tags: [core, identity, stable]
updated: 2026-04-04
---

# Actora Identity

What Actora is. The durable project identity and architecture anchor.

**Anti-drift reminder:** Actora should not collapse into deeper BitLife, detached god sim, or vague universe-scale handwaving. Actor-anchored, zoomable, continuous, simulation-real.

**Active guardrails** (always in effect):
- Preserve actor-anchored / zoomable-universe player contract (see DEC-001)
- Controlled state mutation — mutations flow through world-owned methods
- Origin / lineage / care semantic separation in family links

Only revise this doc when project identity or core architecture truly changes.

---

## 1. Project identity

Actora is an actor-anchored simulation framework built inside the broader Compverse direction.

Not just a narrow human life simulator. Not just a detached world-management sandbox. A continuous universe simulation designed to support focused actor play inside a larger world and universe-scale model.

The player primarily experiences the simulation through a current actor, but that actor always exists inside a larger continuous universe that doesn't stop being real just because attention is focused locally.

Actora is:
- **Actor-anchored** — player lives through a focused actor
- **Continuous** — one universe per save, one shared advancing timeline
- **Zoomable** — same-save scope from actor → city → country → world → star system → galaxy → universe
- **Layered** — different simulation depth for different scopes (high detail near player, lower detail at macro scale)
- **Context-sensitive** — rules, meaning, and availability depend on era, place, and situation
- **Foundation-first** — architecture built for the future product, not trapped in a narrow prototype

---

## 2. Core conceptual skeleton

The approved main conceptual anchors:

| Concept | What it is |
|---------|-----------|
| **Universe** | Top-level simulation container for one save. Contains everything. One shared advancing timeline. |
| **Entity** | Any tracked thing in the universe. Has identity, state, persistence. |
| **Actor** | A special Entity that can behave, change, accumulate history, and potentially be played. |
| **System** | A process/rule layer that drives simulation behavior and updates state. |
| **Metric** | A tracked or derived measurement at some scope. |
| **Record** | A preserved piece of simulation history or transition. |
| **Link** | A structured connection between things in the simulation. |
| **Context** | The conditions that determine what rules, meanings, and behavior apply. |

**Cross-cutting layers:**
- **Type** — what kind of thing something is
- **Scope** — the level at which something is viewed, simulated, or measured

---

## 3. Architecture principles

### Not human-first
Human-focused early content is fine. Human-only current implementation is fine. But architecture must not hard-bake Human as the universal being model. Actor is the broader layer. Playability is a mode or permission, not a type of being. Future actor forms may include non-human beings, synthetic beings, robots, alien beings, etc.

### Layered simulation depth
Not everything gets simulated at the same fidelity. High detail for focused/relevant actors, medium for surrounding actors and systems, lower/aggregate for macro world state. This is necessary for feasibility. Aim for believable and internally coherent, not brute-force total-detail realism.

### Universe persistence
Death of the focused actor does not terminate the universe. The universe persists beyond one life. Continuity can move through connected actors. Actor lines may be archived. The save continues.

### Separation of concerns
Keep these separate — don't flatten into one field:
- Current location
- Residence / home
- Owned property (future)
- Political jurisdiction
- Temporary occupancy

### Structural transitions
Birth, death, archive, continuation, and lineage are major simulation transitions — not throwaway flavor text. They should produce or alter Records, Links, and related state.

### Context-sensitive behavior
Actor behavior should eventually be shaped by skills, traits, pressures, history, context, uncertainty, error, imperfect information, and limited perception. Not idealized perfect decision logic.

---

## 4. Protected future directions

These don't need implementation now, but architecture must not trap us away from them:

- **Timeline/era context** — different eras meaningfully alter what exists, is available, is legal, is normal. Local calendars may differ by place/civilization.
- **Galaxy-scale spatial hierarchy** — galaxy → star system → world body → country → city → property/site/vessel. Don't trap in single-planet assumptions.
- **Multiple interaction styles** — direct actor play, observer/follow, actor switching, broader system observation, scope shifting. All within one continuous save, not separate games.
- **UI-agnostic simulation** — terminal is a temporary shell, not the permanent form. Core simulation must work independently of any specific presentation.
- **Records and links as structural concepts** — history is not disposable UI text. Links include family, household, ownership, employment, organizational membership, political belonging, guardianship, obligation, etc.
- **Inventory, ownership, property** — protected future concerns even if implementation is later.

---

## 5. Controlled state mutation

Core rule: subsystems should prefer producing structured outcomes over performing broad direct state mutation. Systems are producers of effects, not free-for-all state editors.

**Time mutation:** only the simulation step boundary advances shared simulation time.

**Universe simulation step boundary:**
- The authoritative boundary for shared state mutation and time progression
- Systems produce structured outcomes → Universe collects and applies them in a controlled phase
- Only the Universe simulation step advances time, applies state mutation, creates structural records, finalizes effects

**Direction of travel** (as Actora grows):
- Stats → controlled stat-application paths
- Relationships → controlled link mutation paths
- Records → controlled record-writing paths
- Money/resources → controlled domain application, not scattered edits

**Anti-pattern:** scattered direct mutation across many subsystems independently editing actor stats, relationships, money, records, or world state in ad hoc ways.

---

## Glossary

These terms have specific meanings in Actora. Use them consistently across all docs.

| Term | Meaning |
|------|---------|
| **Actor** | Any simulation subject (human or otherwise). The player controls one at a time. |
| **Focused actor** | The actor the player currently controls. |
| **Continuation** | After the focused actor dies, choosing a connected living actor to continue as. |
| **Link** | A world-owned relationship record between two entities (family, social, association). |
| **Social link** | A non-family relationship with a closeness score (0-100). Types: acquaintance, friend, close_friend. |
| **Place** | A location in the world hierarchy (earth → country → city). |
| **Spatial identity** | An actor's current location, residence, jurisdiction, and temporary occupancy — kept separate. |
| **Commitment** | A long-running state like education, job, or travel — not an ordinary one-month action. |
| **Action** | Something the player's actor can do. Classified by time-shape, not abstract buckets. |
| **Structural status** | Whether an actor is "active" or "dead" — the narrow lifecycle state. |
| **Record** | A world-owned structured event/history entry (event, birth, death, family_bootstrap, actor_entry). |
| **Life stage** | Derived from age: Infant → Child → Teenager → Young Adult → Adult → Elder. |
| **Trait** | One of 10 personality descriptors (pick 3 at creation). Affects event eligibility and time budget (sleep hours). Current pool pending redesign (DEC-020). |
| **Stat** | One of 11 numeric attributes (health, happiness, intelligence + 8 secondary). |
| **Shell** | The persistent TUI frame: header, footer, screen body. |
| **Browser** | The tabbed screen containing Relationships and History tabs. |
