---
title: Working Ideas Register
role: flexible-idea-intake-and-staging
stability: low
layer: planning
relates_to: [actora-roadmap, actionable-summary]
---

Actora Working Ideas Register v52 | 2026-03-31 | Flexible idea intake, staging, and design retention.
Authority: flexible working layer — stable docs win, repo truth wins on implementation.


=== CURRENT WORKING READ ===

Verified repo truth is through v0.44.1. The backbone is materially strong and the TUI is polished.

Foundation layers realized:
- World-owned actor registry, link storage, place registry (with parent-place hierarchy), record storage, simulation-step boundary
- Structured snapshot/output contracts with shell-owned rendering
- Centralized event outcome application through World.apply_outcome(...)
- Explicit spatial identity separation (current_place, residence, jurisdiction, temporary_occupancy)
- Structural death/continuity foundation with world-owned mark_actor_dead, continuity candidates, and handoff validation
- Ordinary old-age mortality through world-owned monthly resolution
- Family continuity substrate: older siblings at startup, later sibling births, direct sibling links
- 12 real countries, 39 cities, culture-aware name generation (400+ names)

Actor model depth:
- 11 stats (health, happiness, intelligence + strength, charisma, creativity, wisdom, discipline, willpower, looks, fertility)
- Appearance traits (eye color, hair color, skin tone with Other/free-text)
- Personality traits (pick 3 from pool of 10)
- Sexuality (emerges through event-choice at ~14-17)
- Gender (defaults to sex at birth, choosable at ~12-15 through event-choice popup)

TUI surfaces (polished through v0.44.1):
- Life View (split: left identity/stats/relationships scrollable, right accumulating event feed)
- Profile screen ([P]), Lineage Browser ([L]), History Browser ([H]), Skip Time ([S])
- Death interrupt with life summary, two-step continuation inspection
- Character creation wizard (Identity → Location → Appearance → Mode → Stats/Questionnaire → Traits → Confirm)
- Event-choice popup overlay (Space-only confirm; Enter fully blocked during popup)
- All ←→ adjustable fields render ← value → when active

Event system:
- 120 events total (100 general + 20 trait-gated)
- Family-aware dynamic name insertion, 3-event cooldown, trait-gated events (required_traits field)
- Event-choice framework for gender/sexuality emergence

The current pressure: what real content and domain systems should be added next now that the actor, TUI, and event foundations are materially credible.


=== ACTIVE NEAR-TERM PRESSURES ===

ID: IDEA-122
Created: 2026-03-31
Title: Non-family relationships + action foundation — first social layer
Status: Implemented (v0.45.0)
Priority: P1
[[actora-roadmap|Actora Roadmap]] fit: social foundation before social space systems and education
Summary: Acquaintance/friend/close_friend link types with numeric closeness score (0-100). Player-initiated meeting via popup choice. Closeness decay with history-based resistance. Drift events + former link status. Friend death stat impact. Relationship Browser replaces Lineage Browser ([L] hotkey, filter sidebar). Friends in Life View left panel. Action queue with "Spend time with friend" resolving on advance.
Status notes: Implemented in two Claude Code passes. Playtesting and polish pass expected after.

ID: IDEA-123
Created: 2026-03-31
Title: Action system — full design spec
Status: Interview complete, not yet specced for implementation
Priority: P1 (next after relationship polish)
[[actora-roadmap|Actora Roadmap]] fit: player agency layer, dependency for all domain systems
Summary from interview:
- Two action types: instant (happens now, no queue) and monthly (queued, resolves on advance)
- Actions are categorized: social, personal development, career, etc.
- Dynamic availability based on life situation, location, age, relationships, prerequisites
- Prerequisites silently hidden — unavailable actions don't show at all (age-gated, location-gated)
- Long commitments (education, job) are NOT in the action queue — they live in Profile as a "commitments" section
- Surprise opportunities: popup if urgent (1-month window), persistent "opportunities section" if open-ended. Location of that section TBD.
- No forced constraints — player chooses freely even if overcommitting (for now)
- Action atoms: "call a friend", "go to the club" (social + stat changes + random events), "go to the gym", etc.
- Venues/locations surface available actions (club in your city = action available)
- Actions get their own screen/page (not crammed into Life View left panel)
- Queued/pending actions visible in their own panel, not mixed into Life View sections
- Social actions like "hang out" can optionally bring a friend — friend can decline based on context
- Eventually: spiral side-quest chains where you are forced through a sequence of decisions with branching outcomes
- Some future actions will span multiple months (space mission etc.) — shown as active commitments
Why it matters: Without an action system, the game is purely passive — player just watches events tick by. Actions are what make it a life simulation.
Deferred from this spec: prerequisites (needs venue system), multi-month actions, action skip-time caps, opportunity section placement, cancel-action mechanic


=== ACTIVE DESIGN GUARDRAILS ===

ID: IDEA-102 — Preserve actor-anchored / zoomable-universe player contract
Status: Active anti-drift guardrail
Core: One continuous universe simulation, actor-anchored, same-save scope zoom, full sandbox default, continuity through connected actors, economy/politics as pillars.

ID: IDEA-103 — Multi-axis social perception / reputation / opportunity layer
Status: Active later-layer design pressure (P2)
Core: Multiple perception axes, not one karma score. Depends on stronger actor/context/social foundations.

ID: IDEA-104 — Operator tooling / scenario testing seam
Status: Active later support/tooling pressure (P2)

ID: IDEA-091 — Identity generation realism / context-awareness
Status: Visible later seam (P2)
Core: Identity generation still uses global pools. Needs place/culture/era context.

ID: IDEA-045 — Controlled state mutation foundation
Status: Partially realized, guardrail

ID: IDEA-076 — Origin / lineage / care semantic separation
Status: Partially realized, guardrail


=== COMPLETED MILESTONES (CONDENSED) ===

v0.28.0–v0.35.4 — Death/continuity, rename, handoff, link/place/spatial strengthening, continuation inspectability
v0.36.0–v0.36.7 — Actor-first TUI foundation, style, lineage browser, visual system, Life View
v0.36.8–v0.37.7 — Mortality, family continuity, death inspectability, history, relationships, UX cleanup
v0.38.0–v0.38.1 — Stats deepening, profile screen, creation wizard
v0.39.0–v0.39.1 — Event-choice framework, gender/sexuality emergence, traits wired into events
v0.40.0–v0.40.1 — Real location content (12 countries/39 cities), questionnaire creation mode
v0.41.0–v0.44.1 — TUI polish: banners removed, selection behavior, footer labels, popup Enter block, arrow standard

Completed IDEAs: IDEA-045(partial), IDEA-076(partial), IDEA-097–IDEA-121


=== CLARIFIED DESIGN READ ===
See [[vision-and-systems]] for full creative intent and system vision. Key anti-drift summary: Actora should not collapse into deeper BitLife, detached god sim, or vague universe-scale handwaving. Actor-anchored, zoomable, continuous, simulation-real.


=== DEFERRED IDEAS (PARKED) ===

- Gradual sexuality signal events (3-5 small events building toward suggestion)
- Culture/location-driven identity context for gender/sexuality prompts
- Gender/sexuality changeable through Profile triggering life event
- "Other" sexuality integration with future romance event logic
- Full event-choice expansion for non-identity choices (jobs, school, etc.)
- Sibling/family birth probability tuning
- Archive depth beyond current lineage browser


=== ONE-LINE SUMMARY ===

Actora has a materially strong TUI-driven prototype through v0.44.1 — next move is non-family relationships as the first social layer before education.
