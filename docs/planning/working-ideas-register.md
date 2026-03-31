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
Title: Non-family relationships — first social layer
Status: Next structural move (confirmed)
Priority: P1
Roadmap fit: social foundation before social space systems and education
Summary: Friendships, acquaintances, rivals — the first non-family relationship layer. Dependency for social space systems, education context, and peer-driven events.
Why it matters: Without non-family relationships, education and social systems have no social substrate to build on.
Next action: scope and implement


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
- player-facing text must never use internal/architecture language (operator guide section 18)

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


Date: 2026-03-30
Role: broad working idea intake, staging, parking, interview-derived design retention, and rewrite-pressure tracking for Actora
Authority level: flexible working layer, not durable architecture truth
Interpretation rule: stable source docs win over this file; verified repo truth wins on what is already implemented
Usage rule: preserve substantial design material and conversation-derived pressure here instead of flattening everything into short-term task summaries


=== CURRENT WORKING READ ===

Verified repo truth is through v0.40.1. The backbone is materially stronger than it was at the start of this development arc.

Foundation layers realized:
- World-owned actor registry, link storage, place registry (with parent-place hierarchy), record storage, simulation-step boundary
- Structured snapshot/output contracts with shell-owned rendering
- Centralized event outcome application through World.apply_outcome(...)
- Explicit spatial identity separation (current_place, residence, jurisdiction, temporary_occupancy)
- Controlled spatial identity mutation through World.update_actor_spatial_identity(...)
- Structural death/continuity foundation with world-owned mark_actor_dead, continuity candidates, and handoff validation
- Ordinary old-age mortality through world-owned monthly resolution
- Family continuity substrate: older siblings at startup, later sibling births, direct sibling links
- Identity generation context seam (still placeholder-level beneath the clean interface)

Actor model depth:
- 11 stats (health, happiness, intelligence + strength, charisma, creativity, wisdom, discipline, willpower, looks, fertility)
- Appearance traits (eye color, hair color, skin tone with Other/free-text)
- Personality traits (pick 3 from pool: Curious, Calm, Fussy, Bold, Shy, Cheerful, Stubborn, Gentle, Restless, Alert)
- Sexuality (emerges through event-choice at ~14-17, randomized for NPCs)
- Gender (defaults to sex at birth, choosable at ~12-15 through event-choice popup)

TUI surfaces:
- Life View (split: left identity/stats/relationships, right accumulating event feed)
- Profile screen ([P]) showing full actor detail
- Lineage Browser ([L]) with filters, search, detail pane
- History Browser ([H]) with year separators, ★/✦ markers, year-jump, scrolling
- Skip Time ([S]) with presets and custom input
- Death interrupt with life summary, two-step continuation inspection
- Character creation wizard (5-step curses flow: Identity → Appearance → Traits → Stats → Confirm)
- Event-choice popup overlay for interactive prompts during play

Event system:
- 120 events total (100 general + 20 trait-gated)
- Family-aware dynamic name insertion using existing link data
- 3-event cooldown prevents repetition
- Trait-gated events (required_traits field)
- Event-choice framework for gender/sexuality emergence
- Skip-time pauses for major choices, resumes after resolution

The current pressure is no longer "does the prototype run" or "does the TUI exist." It is: what real content and domain systems should be added next now that the actor, TUI, and event foundations are materially credible.


=== ACTIVE NEAR-TERM PRESSURES ===

ID: IDEA-119
Created: 2026-03-30
Last Reviewed: 2026-03-30
Title: Real location content — actual countries, cities, culture context
Status: Materially realized in v0.40.0
Priority: P1
Roadmap fit: place foundation content + identity generation realism (backbone 4.10 area)
Summary: v0.40.0 replaced "Starter Country/Starter City" with 12 real countries and 39 cities, added culture-group metadata to places, culture-aware name generation with 400+ names across 12 cultures, and a creation wizard Location step for country/city selection.
Why it matters: Future systems (education, identity generation, events) now have real geographic context to build on.
Risks: name pools are generic/surface-level; deeper regional/ethnic/era variation is a later concern (IDEA-091)
Next action: preserve as realized milestone; name pool depth tracked in live-issues

ID: IDEA-120
Created: 2026-03-30
Last Reviewed: 2026-03-30
Title: Event-choice framework + gender/sexuality identity emergence
Status: Materially realized in v0.39.0
Priority: P1
Roadmap fit: actor identity deepening + interactive event infrastructure
Summary: v0.39.0 added the event-choice popup overlay framework and used it for gender identity emergence at puberty (~12-15) and sexuality emergence (~14-17). Skip-time pauses for major choices and resumes after resolution. Identity flags reset on continuation.
Why it matters: The actor now discovers who they are during play. The choice framework is reusable infrastructure for future interactive events.
Risks: overreading the first-pass prompts as if gradual sexuality signals, culture-driven identity, or Profile-editing life events were already implemented
Next action: preserve as realized milestone; deferred depth listed in live-issues

ID: IDEA-121
Created: 2026-03-30
Last Reviewed: 2026-03-30
Title: Traits wired into events
Status: Materially realized in v0.39.1
Priority: P1
Roadmap fit: actor-deepening follow-through making creation choices meaningful
Summary: v0.39.1 added the required_traits field to the event system and 20 trait-gated events (2 per trait). Traits now affect which events can trigger.
Why it matters: Character creation choices now have gameplay consequences instead of being decorative.
Risks: only 2 events per trait means trait-specific content can still repeat noticeably
Next action: preserve as realized milestone; more trait events should follow naturally as content expands


=== ACTIVE DESIGN GUARDRAILS ===

ID: IDEA-102 — Preserve actor-anchored / zoomable-universe player contract
Status: Active anti-drift guardrail
Core: One continuous universe simulation, actor-anchored, same-save scope zoom, full sandbox default, continuity through connected actors, economy/politics as pillars.

ID: IDEA-108 — Terminal UI reveal flow / death-transition intent
Status: Partially realized, ongoing guardrail
Core: Alive-state stays implicit, death interrupts first, continuation after acknowledgment, archived actors should remain explorable later.

ID: IDEA-103 — Multi-axis social perception / reputation / opportunity layer
Status: Active later-layer design pressure (P2)
Core: Multiple perception axes, not one karma score. Depends on stronger actor/context/social foundations.

ID: IDEA-104 — Operator tooling / scenario testing seam
Status: Active later support/tooling pressure (P2)
Core: Reusable dev/test tooling should follow enough real system growth to justify it.

ID: IDEA-077 — Entity registry vs actor view layering
Status: Parked conceptual guardrail (P2)
Core: Distinguish broad entity registry from narrower actor-oriented access layers.

ID: IDEA-091 — Identity generation realism / context-awareness
Status: Visible later seam (P2)
Core: Identity generation still uses global pools. Needs place/culture/era context.

ID: IDEA-045 — Controlled state mutation foundation
Status: Partially realized, guardrail
Core: Systems should prefer structured outcomes over direct mutation. Spatial mutation is centralized; broader domain mutation should follow.

ID: IDEA-076 — Origin / lineage / care semantic separation
Status: Partially realized, guardrail
Core: Startup-family origin/care/bootstrap semantics are explicit. Broader adoption/guardianship/household remain later.


=== COMPLETED MILESTONES (CONDENSED) ===

v0.28.0 — Death/continuity structural transition foundation
v0.29.0 — Actora rename
v0.30.0 — First playable continuity handoff flow
v0.31.0 — Link foundation strengthening
v0.32.0 — Structured place/place-hierarchy strengthening
v0.33.0 — Spatial identity separation strengthening
v0.34.0 — Controlled spatial identity mutation boundary
v0.35.0 — Dead-focus transition flow tightening
v0.35.1–v0.35.4 — Time cleanup, identity options, continuation inspectability, lineage foundation
v0.36.0–v0.36.7 — Actor-first TUI foundation, footer fix, style, lineage browser, repo cleanup, visual system, Life View
v0.36.8 — Ordinary mortality / old-age death truth
v0.36.9 — Family continuity groundwork
v0.37.0 — Death/continuation inspectability follow-through
v0.37.1 — Scrollable event history log
v0.37.2 — Life View relationships + event expansion + family-aware events
v0.37.3–v0.37.7 — UX cleanup, event cooldown, history markers, playtest fixes, event dedup, life separator
v0.38.0 — Actor stats deepening + profile screen
v0.38.1 — Character creation wizard + appearance + traits
v0.39.0 — Event-choice framework + gender/sexuality identity emergence
v0.39.1 — Traits wired into events (20 trait-gated events)
v0.40.0 — Real location content (12 countries, 39 cities, culture-aware name generation)
v0.40.1 — Questionnaire-based character creation mode (16 personality questions)

Completed IDEAs (no longer active): IDEA-100, IDEA-105, IDEA-106, IDEA-107, IDEA-109, IDEA-110, IDEA-111, IDEA-112, IDEA-113, IDEA-114, IDEA-115, IDEA-116, IDEA-117, IDEA-118 (Slice 1+2)
Also completed: IDEA-097, IDEA-098, IDEA-099 (CLI hardening, singleton IDs, rename)


=== CLARIFIED DESIGN READ (PRESERVED WORDING) ===

Actora is a single continuous universe simulation where the player primarily lives as the current actor, but can zoom across scopes, continue through connected lives, and interact with real economic, political, spatial, and later social systems inside the same save.

Core clarified points:
- one save = one universe simulation
- actor life is still the emotional anchor
- full custom sandbox setup is the default start
- the intended zoom ladder is actor → city → country → world → star system → galaxy → universe
- exact inspectable information is allowed throughout the simulation
- death is a structural transition, not a fail-state philosophy
- continuity through relevant connected actors rather than strict child-only succession
- economy is a pillar, politics/world conditions are a pillar
- companies should eventually exist as real hybrid simulation things
- earliest practical era: modern + near future
- earliest practical place: world / country / city
- later social systems should use multiple perception axes rather than a single karma meter
- traits: structured (birth) + emergent (develop over time through events/systems)
- gender deferred to puberty, sexuality emerges through events
- Space=select/toggle, Enter=proceed, B=back across all TUI surfaces
- player-facing text must never use internal/architecture language (operator guide section 18)
- 12 real countries with culture-aware name generation; names should match the birth location

Anti-drift read:
Actora should not quietly collapse back into "deeper BitLife," "detached god sim," "spreadsheet world sim with humans taped on," or vague universe-scale handwaving. The intended shape is actor-anchored, zoomable, continuous, and simulation-real.


=== DEFERRED IDEAS (PARKED) ===

- Gradual sexuality signal events (3-5 small events building toward suggestion)
- Culture/location-driven identity context for gender/sexuality prompts
- Gender/sexuality changeable through Profile triggering life event ("came out as...")
- "Other" sexuality integration with future romance event logic
- Full event-choice framework expansion for non-identity choices (jobs, school, etc.)
- Sibling/family birth probability tuning
- Archive depth beyond current lineage browser


=== NEXT BEST USE ===

1. Use IDEA-119 (real location content) as the next implementation target
2. After location content, evaluate education foundation as the first mid-stage domain layer
3. Keep design guardrails active for anti-drift
4. Do not force stable-doc revisions unless a real contradiction appears


=== ONE-LINE SUMMARY ===

Actora has a materially strong prototype through v0.40.0 with real actor depth, real geography, and culture-aware identity — and the next honest move is likely the education foundation as the first mid-stage domain layer.
