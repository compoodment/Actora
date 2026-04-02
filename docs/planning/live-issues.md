---
title: Live Issues
role: bug-and-revisit-tracker
stability: low
layer: planning
relates_to: [working-ideas-register]
tags: [bugs, issues, revisit, planning]
---

Live Issues / Revisit Tracker
Date: 2026-03-31
Purpose: repo-local parking lot for current bugs, regressions, and revisit items so they do not get lost between patches.


=== NEEDS PLAYER TEST (cannot verify headlessly) ===

- Left panel scroll in main Life View
  Status: needs player test
  Note: scroll logic rewritten in v0.43.0. Needs real content overflow (relationships, jobs, etc.) to verify scrolling works correctly as panel grows.


=== CURRENTLY OPEN ===

- Shell / navigation redesign follow-through
  Status: open design pressure
  Scope:
  - implement the chosen balanced shell direction without reintroducing hidden keybind chaos
  - settle Menu / Options / Skip Time popup structure
  - finalize top-vs-footer responsibility split per surface
  Design follow-through still needed:
  - Death screen should show only important/marked records, not random events
  - "New Life: X" message in feed needs better phrasing or removal

- sibling/family birth tuning still needs later balancing
  Status: open revisit
  Note: the age/spacing/family-size fertility heuristic is intentionally simple first-pass logic and may need probability tuning once more long-run play data exists.

- Life View content cutoff / scrollability need
  Status: partially resolved in v0.36.7
  Note: simple left-pane vertical scrolling exists now; fancier tabs/section systems remain later if still justified.

- traits partially wired — only 2 events per trait
  Status: open revisit
  Note: v0.39.1 wired traits into events with required_traits field and 20 trait-gated events (2 per trait). More trait events should follow naturally as content expands. Traits still don't affect simulation outcomes beyond event eligibility.

- name pools are generic/surface-level per culture
  Status: open revisit
  Note: current culture name pools are top-20 common names per country with no regional variation within countries, no ethnic/religious diversity, no era awareness, and no family naming conventions (patronymic, compound surnames, etc). Fine for first pass but should deepen with IDEA-091 (identity generation realism) later.


=== DEFERRED ===

- gradual sexuality signal events (3-5 small events building toward suggestion)
  Status: deferred
  Note: planned but deferred past Slice 3 minimum. First pass uses a single choice prompt.

- culture/location-driven identity context for gender/sexuality prompts
  Status: deferred
  Note: eventually gender/sexuality emergence should be shaped by culture/location context. Requires place/context maturity.

- gender/sexuality changeable through Profile triggering life event
  Status: deferred
  Note: changing gender or sexuality through Profile should trigger a "came out as..." life event.

- "Other" sexuality integration with future romance events
  Status: deferred
  Note: "Other" sexuality is complicated when events need to know attraction patterns. Park until romance events exist.


=== RESOLVED (recent) ===

- v0.44.1: stat number padding removed (was causing double-space next to arrows)
- v0.44.0: all ←→ adjustable fields render ← value →; popup Enter fully blocked (Space-only)
- v0.43.0: wizard polish — first name error timing, appearance arrows, custom prompt, questionnaire weight, history breathing, continuation text
- v0.42.0: sex field unselectable, trait leak (questionnaire→manual), questionnaire separator, footer labels, continuation crash, None date TypeError, ESC/Enter handling
- v0.41.0: banners removed, selection behavior enforced, quit confirmation added
- v0.36.0–v0.40.1: see Working Ideas Register completed milestones

- v0.45.0 playtest round 2 findings
  Status: partially resolved — B1/B2/B3 fixed in repo; B4 closed as non-bug.
  Resolved:
  - B1: former relationships showing as continuation candidates (social/former leaking)
  - B2: gender/sexuality popups firing for already-adult continuation actors
  - B3: "A/Enter advances one month." leaking as last_message in Life View
  - Browser tab shell polish: bottom divider added under Relationships/History tabs; "Former" renamed to "Past"
  Closed:
  - B4: Age displaying with apostrophe ('79 instead of 79) — this was correct formatting, not a bug
  Design decisions logged (not bugs, implement later):
  - Death screen should show only important/marked records, not random events
  - Closeness decay too aggressive — tune down, add proximity-based passive maintenance
  - Batch social action: "Spend time with friends/family" covering a group at once
  - "New Life: X" message in feed needs better phrasing or removal
  - NPC identity auto-resolve: gender/sexuality must silently resolve for non-played actors at age threshold
