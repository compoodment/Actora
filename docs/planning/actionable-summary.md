---
title: Actionable Summary
role: near-term-planning-snapshot
stability: low
layer: planning
relates_to: [working-ideas-register, actora-roadmap]
---

Actionable Ideas Summary — Rev41
Date: 2026-04-01
Role: temporary near-term operational planning snapshot for Actora
Authority: non-authoritative; stable docs win, repo truth wins on implementation
Usage rule: keep this more distilled than the WIR and focused on the current working position, current planning question, and strongest near-term candidates


=== CURRENT WORKING POSITION ===

Verified repo truth is through v0.45.0 (partial — polish pass pending) with source-stack sync through:
- Master Context v9, [[actora-roadmap|Actora Roadmap]] v10, Operator Guide v9 (+ section 18: player-facing text rule)
- New docs added: [[vision-and-systems]] (creative intent per system), [[ui-architecture]] (screen map and navigation blueprint)

The project has a materially strong early backbone:
- World-owned actor registry, links, places (hierarchy), records, simulation step
- Structured snapshot/output contracts, centralized event outcome application
- Spatial identity separation (location/residence/jurisdiction/temporary occupancy)
- Structural death/continuity foundation with playable handoff
- Ordinary old-age mortality, family continuity substrate (siblings at startup + later births)
- Actor-first curses TUI with Life View, Profile, Relationship Browser (replaces Lineage), History, Skip Time, Actions panel
- Character creation wizard (Identity → Location → Appearance → Mode → Stats/Questionnaire → Traits → Confirm)
- 120 events (100 general + 20 trait-gated) with family-aware dynamic text and cooldown
- 11 stats (3 primary + 8 secondary), appearance traits, personality traits
- Event-choice framework (popup overlay) with gender/sexuality identity emergence
- Death inspectability (life summary, two-step continuation inspection)
- Consistent TUI control language — enforced standard, all ←→ adjustable fields render ← value →, popup Enter blocked (Space-only)
- 12 real countries with 39 cities, culture-aware name generation (400+ names)
- Questionnaire-based character creation as alternative to manual (16 personality questions)
- Non-family relationships: acquaintance/friend/close_friend with numeric closeness (0-100), player-initiated meeting popups, closeness decay, drift events, former link status, friend death impact
- Action foundation: "Spend time with friend" action queues and resolves on advance
- Player-facing text lint tool and operator guide rule (section 18)
- tmux-based headless playtesting capability for TUI verification

Recent milestone sequence:
- v0.40.0 — real location content (12 countries, 39 cities, culture-aware names)
- v0.40.1 — questionnaire-based character creation mode
- v0.41.0 — TUI polish: banners removed, selection behavior enforced, quit confirmation
- v0.42.0 — playtest bug fixes: sex field, trait leak, crash fixes, ESC/Enter handling
- v0.43.0 — playtest polish: wizard UX, history breathing room, left panel scroll, continuation text
- v0.44.0 — arrow standard enforced, popup Enter blocked (Space-only)
- v0.44.1 — stat number padding fix, docs restructured for Obsidian (wikilinks, YAML frontmatter)
- v0.45.0 — non-family relationships + action foundation (polish pass pending)


=== CURRENT PLANNING QUESTION ===

"v0.45.0 shipped but needs a polish pass. After that, what's next?"

Direction: Polish v0.45.0 first (UI restructure, bugs fixed, tui-standards updated). Then: action system foundation as the next structural move, then education.


=== LEADING PLANNING CANDIDATES ===

1. v0.45.0 polish pass (immediate)
- Remove Friends and Actions sections from Life View left panel — fold social links into Relationships section
- Give Actions its own screen ([T])
- Fix [L] → Relationship Browser routing, search, name collision bug, "no one to hang out" message
- Update tui-standards.md with new hotkeys and navigation
- See live-issues.md for full bug list

2. Action system foundation (next structural move)
- Two action types: instant and monthly
- Time budget per month (emergent constraint, not arbitrary cap)
- Categorized actions (social, personal, career, etc.)
- Dynamic availability based on age/location/relationships/era
- Visibility: age/era gates silently hidden; resource gates shown as unavailable
- Requires: relationship foundation (realized), place context (realized)

3. Education foundation (after action system)
- First mid-stage domain layer per roadmap
- Depends on: relationships (realized), action system (pending)


=== DESIGN READ ===

See [[vision-and-systems]] for full creative intent per system.
See [[ui-architecture]] for screen map and navigation rules.

Key locks:
- Death is a structural transition, not a fail-state
- Economy and politics are real future pillars
- Social perception: multi-axis, not a single karma score
- Scope zoom: actor → city → country → world → star system → galaxy → universe
- All ←→ adjustable fields render ← value → when active
- Enter must never confirm popup overlays — Space only
- `former` is a link status field, not a type — universal across all link types


=== REAL TENSIONS ===

1. v0.45.0 shipped but UI is not yet restructured — polish pass required before it's clean
2. Action system design is specced but not implemented — it's the missing agency layer
3. Traits affect event eligibility but not simulation outcomes
4. UI architecture doc exists but tui-standards.md hasn't been updated to match new navigation
5. Scope is huge — discipline required to avoid feature landfill


=== ONE-LINE SUMMARY ===

Actora has a strong TUI-driven prototype through v0.45.0 with real actor depth, geography, identity, relationships, and an action seed — next immediate move is the v0.45.0 polish pass, then action system foundation.
