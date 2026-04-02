---
title: Actionable Summary
role: near-term-planning-snapshot
stability: low
layer: planning
relates_to: [working-ideas-register, actora-roadmap]
tags: [planning, snapshot, next-steps]
---

Actionable Ideas Summary — Rev42 | 2026-04-01 | Near-term snapshot; non-authoritative, stable docs and repo truth win.


=== CURRENT WORKING POSITION ===

Verified repo truth is through v0.45.0 plus post-release polish/follow-through, with source-stack sync through:
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
- v0.45.0 — non-family relationships + action foundation
- post-v0.45.0 follow-through — continuation/browser/Hang Out fixes and shell-direction decision


=== CURRENT PLANNING QUESTION ===

"The immediate polish wave mostly landed. What is the next real structural move, and what shell redesign pressure should stay in view while we get there?"

Direction: Treat the generic v0.45.0 polish pass as mostly complete. The remaining near-term design pressure is the shell/navigation redesign (chosen direction documented; implementation still pending). The next real structural move is action system foundation, then education.


=== LEADING PLANNING CANDIDATES ===

1. Shell / navigation redesign follow-through (immediate design pressure)
- Chosen direction: balanced stacked shell header, centered numbered primary commands, controls only when relevant, no hidden keybinds
- Still needs implementation scoping for Menu / Options / Skip Time popup structure and final top-vs-footer responsibility split
- Shell redesign decisions are now documented; implementation should follow the chosen direction rather than re-inventing the shell per patch

2. Action system foundation (next structural move)
- Core role now clearer: Actions is the actor-action hub, but not the only possible action entry point forever
- First meaningful implementation scope should stay narrow: social + self-improvement
- Long-running states like education/job/travel should be treated as commitments, not ordinary one-month action rows
- Visibility should be broad by default, with fundamentally inapplicable actions hidden and richer discovery/unlock logic deferred
- Passive-vs-active balance matters: ordinary life should still function without tedious micromanagement; explicit actions provide focus, leverage, stronger effects, and playstyle expression
- Still needs one focused follow-up pass on the unresolved seam: action time-shape / exact monthly queue shape vs instant actions vs commitments, plus whether the Actions surface benefits from a detail pane

3. Education foundation (after action system)
- First mid-stage domain layer per roadmap
- Depends on: relationships (realized), action system (pending)


=== DESIGN READ ===

See [[vision-and-systems]] for creative intent and [[ui-architecture]] for screen structure.


=== REAL TENSIONS ===

1. Shell redesign direction is now chosen, but implementation shape is still open enough to drift if not scoped carefully
2. Action system design is specced but not implemented — it's still the missing agency layer
3. Traits affect event eligibility but not simulation outcomes
4. Relationship maintenance / social decay still needs a better passive-vs-active balance
5. Scope is huge — discipline required to avoid feature landfill


=== ONE-LINE SUMMARY ===

Actora has a strong TUI-driven prototype through v0.45.0 plus follow-through polish; next immediate pressures are shell/navigation redesign follow-through and action system foundation.
