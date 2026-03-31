---
title: Working Ideas Register
role: flexible-idea-intake-and-staging
stability: low
tags: [planning, ideas, flexible]
---

Actora Working Ideas Register v52

Date: 2026-03-31
Role: broad working idea intake, staging, parking, interview-derived design retention, and rewrite-pressure tracking for Actora
Authority level: flexible working layer, not durable architecture truth
Interpretation rule: stable source docs win over this file; verified repo truth wins on what is already implemented
Usage rule: preserve substantial design material and conversation-derived pressure here instead of flattening everything into short-term task summaries


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
Status: Specced, ready to implement (v0.45.0)
Priority: P1
[[actora-roadmap|Actora Roadmap]] fit: social foundation before social space systems and education
Summary: Acquaintance/friend/close_friend link types with numeric closeness score (0-100). Player-initiated meeting (event offers choice, no silent collection). Closeness increases via shared events, decays over time (long relationships decay slower). Drift events fire when closeness hits 0; link archived with status:former (universal — applies to family too). Friend deaths affect player stats scaled to closeness. Relationship Browser replaces Lineage Browser ([R] hotkey) with persistent filter sidebar (All/Family/Friends/Acquaintances/Former/Living/Dead). Active actions panel in Life View: first action is "Spend time with [friend]", queues and resolves on advance. NPCs generated at meeting moment with plausible context-seeded personality/stats.
Why it matters: Without non-family relationships, education and social systems have no social substrate to build on. Action queue is the seed for the full action system.
Design decisions locked:
- `former` is a link status field, not a separate type — applies universally (friend, family, etc.)
- [R] = Relationship Browser (replaces [L] Lineage)
- Closeness score visible to player (number + derived label) for now
- Meeting is always player-initiated — no silent actor collection
- All introduced NPCs are real full actors (compressed/uncompressed tiers deferred to education milestone)
- Action skip-time limits and multi-month active actions deferred
Deferred:
- Rival/negative relationship types
- Pre-populated world NPCs (true "existed before")
- Actor simulation depth tiers (compressed vs full)
- Family tree visual
- Cap on Life View relationship display
- Action system depth beyond "spend time with friend"


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


=== CLARIFIED DESIGN READ (PRESERVED WORDING) ===

Actora is a single continuous universe simulation where the player primarily lives as the current actor, but can zoom across scopes, continue through connected lives, and interact with real economic, political, spatial, and later social systems inside the same save.

Core clarified points:
- one save = one universe simulation; actor life is the emotional anchor
- full custom sandbox setup is the default; death is a structural transition not a fail-state
- zoom ladder: actor → city → country → world → star system → galaxy → universe
- economy and politics are pillars, not garnish
- social systems: multiple perception axes, not a single karma meter
- traits: structured (birth) + emergent (develop over time)
- gender deferred to puberty, sexuality emerges through events
- Space=select, Enter=proceed, B=back, all ←→ fields show ← value → when active
- Enter must never confirm popup overlays — Space only
- player-facing text must never use internal/architecture language ([[operator-guide|Operator Guide]] section 18)

Anti-drift read:
Actora should not collapse into "deeper BitLife," "detached god sim," or vague universe-scale handwaving. Actor-anchored, zoomable, continuous, simulation-real.


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
