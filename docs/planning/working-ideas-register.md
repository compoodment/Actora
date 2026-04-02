---
title: Working Ideas Register
role: flexible-idea-intake-and-staging
stability: low
layer: planning
relates_to: [actora-roadmap, actionable-summary]
tags: [planning, ideas, design, staging]
---

Actora Working Ideas Register v53 | 2026-04-02 | Flexible idea intake, staging, and design retention.
Authority: flexible working layer — stable docs win, repo truth wins on implementation.


=== CURRENT WORKING READ ===

Verified repo truth is through v0.45.0 plus follow-through polish. The backbone is materially strong, and the current pressure has shifted from generic polish toward shell/navigation follow-through + action-system scoping.

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

TUI surfaces (current broad shape):
- Life View (split: left identity/stats/relationships scrollable, right accumulating event feed)
- Profile screen ([P]), Browser shell (`Relationships` + `History`), Skip Time ([S]), Actions screen ([T])
- Death interrupt with life summary, two-step continuation inspection
- Character creation wizard (Identity → Location → Appearance → Mode → Stats/Questionnaire → Traits → Confirm)
- Event-choice popup overlay (Space-only confirm; Enter fully blocked during popup)
- All ←→ adjustable fields render ← value → when active

Event system:
- 120 events total (100 general + 20 trait-gated)
- Family-aware dynamic name insertion, 3-event cooldown, trait-gated events (required_traits field)
- Event-choice framework for gender/sexuality emergence

The current pressure: finish shell/navigation follow-through cleanly enough that it stops distorting judgment, then move into the next real structural system layer (actions).


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
- Actions is the main actor-action hub, but not the only place actions can exist. Domain-specific surfaces (for example education or company management later) can still expose their own in-context actions.
- Actions should show the actor's actionable life surface broadly: available actions, active actions, and commitments.
- Actions are for actor-specific actions, not profile editing or misc shell/system actions.
- Two action types remain in play conceptually: instant and monthly, but the more useful unresolved seam may be action/time shape rather than rigid label buckets alone.
- Long commitments (education, job contracts, travel, later similar long-running states) are not ordinary one-month actions; they should live as ongoing commitments that affect what else the actor can do.
- Not every action should necessarily carry time cost; some can remain effectively immediate/negligible for now. The future cap/constraint model should emerge from what an action actually consumes and touches, not from premature abstract slot rules.
- Dynamic availability should eventually come from many axes: age/life stage, location, relationships, traits, commitments, opportunities, etc.
- Early implementation should lean primarily on age/life-stage gating and avoid overfitting actions to immature foundation layers.
- Visibility direction is broader than previously framed: actions should often be shown unless they are fundamentally inapplicable (life stage, location, era, similar hard locks). Discovery/unlock/opportunity-driven visibility can grow later.
- No forced constraints — player chooses freely even if overcommitting (for now).
- First meaningful implementation categories should stay narrow: social and self-improvement.
- Actor skills are a newly surfaced seam worth retaining: distinct from stats/traits/commitments, later actions and systems may need learned capabilities / proficiencies that can grow over time.
- Avoid first-wave dependence on venue-heavy/location-object systems; the place layer is not mature enough for that yet.
- Actions get their own screen/page (not crammed into Life View left panel), but should not become a monopoly surface for every domain-specific action forever.
- Social maintenance should support both passive and active playstyles:
  - ordinary relationship upkeep should not be fully manual
  - some baseline maintenance should happen through threshold/system logic rather than spammy explicit events
  - active social actions should provide stronger or more directed upkeep, and batch social actions remain desirable for low-micromanagement play
- The same passive-vs-active philosophy should extend beyond relationships: jobs and other ordinary life systems should not force tedious micromanagement just to remain functional.
- Social actions like "hang out" can optionally bring a friend — friend can decline based on context.
- Eventually: spiral side-quest chains where you are forced through a sequence of decisions with branching outcomes.
- Some future actions will span multiple months (space mission etc.) — shown as active commitments.
Why it matters: Without an action system, the game is purely passive — player just watches events tick by. Actions are what make it a life simulation.
Deferred from this spec: venue-heavy action logic, deep work simulation, romance, crime, stamina/energy economy, complex scheduling, and the still-unresolved exact monthly queue shape / cancel rules / opportunity section placement.

ID: IDEA-124
Created: 2026-04-01
Title: Ethnicity, trait inheritance, and sibling similarity
Status: Parked — document now, implement when dependencies are ready
Priority: P2
Roadmap fit: extends IDEA-091 (identity generation realism, roadmap layer 4.10) + actor model depth
Summary:
- Ethnicity as a choosable field in character creation (single or mixed). Player's ethnicity should inform parent ethnicity — parents could be mixed themselves or the source of the mix.
- Traits and stats are partly inherited from parents — player creation results should reflect a believable blend of both parents' characteristics (not purely random).
- Siblings should show family resemblance in traits/appearance but with natural variation — sometimes similar, sometimes noticeably different.
Depends on: structured identity generation context (IDEA-091), culture-aware name generation (realized in v0.40.0)
Deferred until: identity generation system is mature enough to support contextual seeding


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

Actora has a materially strong TUI-driven prototype through v0.45.0 plus follow-through polish — immediate design pressure is shell/navigation follow-through, and the next real structural move is action system foundation before education.
