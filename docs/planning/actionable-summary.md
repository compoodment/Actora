---
title: Actionable Summary
role: near-term-planning-snapshot
stability: low
tags: [planning, snapshot, actionable]
---

Actionable Ideas Summary — Rev40
Date: 2026-03-31
Role: temporary near-term operational planning snapshot for Actora
Authority: non-authoritative; stable docs win, repo truth wins on implementation
Usage rule: keep this more distilled than the WIR and focused on the current working position, current planning question, and strongest near-term candidates


=== CURRENT WORKING POSITION ===

Verified repo truth is through v0.44.0 with source-stack sync through:
- [[master-context|Master Context]] v9, [[actora-roadmap|Actora Roadmap]] v10, [[operator-guide|Operator Guide]] v9 (+ section 18: player-facing text rule)

The project has a materially strong early backbone:
- World-owned actor registry, links, places (hierarchy), records, simulation step
- Structured snapshot/output contracts, centralized event outcome application
- Spatial identity separation (location/residence/jurisdiction/temporary occupancy)
- Structural death/continuity foundation with playable handoff
- Ordinary old-age mortality, family continuity substrate (siblings at startup + later births)
- Actor-first curses TUI with Life View, Profile, Lineage Browser, History Browser, Skip Time
- Character creation wizard (Identity → Location → Appearance → Mode → Stats/Questionnaire → Traits → Confirm)
- 120 events (100 general + 20 trait-gated) with family-aware dynamic text and cooldown
- 11 stats (3 primary + 8 secondary), appearance traits, personality traits
- Event-choice framework (popup overlay) with gender/sexuality identity emergence
- Death inspectability (life summary, two-step continuation inspection)
- Consistent TUI control language (Space=select, Enter=proceed, B=back, ↑↓=navigate, ←→=adjust)
- All adjustable value fields render ← value → when active; enforced standard across all screens
- Popup choices (gender/sexuality) blocked from Enter — Space-only confirm, Enter fully blocked during popup
- 12 real countries with 39 cities, culture-aware name generation (400+ names)
- Questionnaire-based character creation as alternative to manual (16 personality questions)
- Player-facing text lint tool and operator guide rule (section 18)
- tmux-based headless playtesting capability for TUI verification

Recent milestone sequence:
- v0.36.8 — ordinary mortality
- v0.36.9 — family continuity groundwork
- v0.37.0 — death/continuation inspectability
- v0.37.1 — scrollable event history
- v0.37.2 — relationships + event expansion + family-aware events
- v0.37.3–v0.37.7 — UX cleanup, event quality, playtest fixes
- v0.38.0 — actor stats deepening + profile screen
- v0.38.1 — character creation wizard + appearance + traits
- v0.39.0 — event-choice framework + gender/sexuality emergence
- v0.39.1 — traits wired into events
- v0.40.0 — real location content (12 countries, 39 cities, culture-aware names)
- v0.40.1 — questionnaire-based character creation mode
- v0.41.0 — TUI polish: banners removed, selection behavior enforced, footer labels, quit confirmation
- v0.42.0 — playtest bug fixes: sex field, trait leak, questionnaire separator, footer labels, crash fixes
- v0.43.0 — playtest polish: wizard UX, history breathing room, left panel scroll, continuation text
- v0.44.0 — arrow standard enforced on all adjustable fields, popup Enter blocked (Space-only)


=== CURRENT PLANNING QUESTION ===

"Given repo truth through v0.44.0 and a solid TUI polish pass, what is the next structural move?"

User direction: non-family relationships before education. Relationships before social space systems — dependency-minded sequencing confirmed and aligned with planning docs.


=== LEADING PLANNING CANDIDATES ===

1. Non-family relationships (leading next structural move)
- Friendships, acquaintances, rivals — the first non-family social layer
- Dependency: actor model (realized), event foundation (realized), place context (realized)
- Needed before social space systems and before education makes sense as a social context
- Would unlock real peer/friend event content and relationship-driven event eligibility

2. Education foundation (next after relationships)
- First mid-stage domain layer per roadmap
- Has location context to support it (different countries could mean different school systems later)
- Gives the actor something to DO during childhood/teenage years
- Depends on: actor model (realized), event foundation (realized), place context (realized), relationships (pending)

3. Current-layer polish (reactive, as found)
- More trait events (only 2 per trait currently)
- Name pool genericness (noted in [[live-issues|Live Issues]])
- These are reactive to playtest findings — address as discovered, not as a planned pass


=== DESIGN READ ===

Actora is a single continuous universe simulation where the player primarily lives as the current actor, but can zoom across scopes, continue through connected lives, and interact with real economic, political, spatial, and later social systems inside the same save.

Key design locks:
- Full custom sandbox setup by default
- Death is a structural transition, not a fail-state
- Economy and politics are pillars, not garnish
- Social perception should be multi-axis, not a single karma score
- Scope zoom: actor → city → country → world → star system → galaxy → universe
- Earliest practical era: modern + near future
- Traits: structured (pick at birth) + emergent (develop over time)
- Stats: 0-100, full sandbox customization
- Gender deferred to puberty, sexuality emerges through events
- Space=select/toggle, Enter=proceed, B=back across all TUI
- All ←→ adjustable fields render ← value → when active
- Enter must never confirm popup overlays — Space only


=== REAL TENSIONS ===

1. Scope remains huge — execution risk is "feature landfill" if sequencing discipline slips
2. Traits are wired into events but don't yet affect simulation outcomes beyond event eligibility
3. Identity depth (sexuality signals, culture-driven emergence) is stored but inert waiting for context systems
4. Archive/lineage depth is still intentionally narrow
5. Relationships currently only family — non-family social layer is the next dependency unlock


=== ONE-LINE SUMMARY ===

Actora has a materially strong TUI-driven prototype through v0.44.0 with real actor depth, real geography, culture-aware identity, and a polished creation wizard — next move is non-family relationships as the first social layer before education.
