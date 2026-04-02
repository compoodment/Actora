---
title: Decisions
tags: [core, decisions, stable]
updated: 2026-04-02
---

# Actora Decisions

Major structural decisions. Immutable — never edit an entry. If a decision changes, add a new one that supersedes the old.

## Template

```
### DEC-XXX: [Title]
**Date:** YYYY-MM-DD
**Context:** [Why this decision was needed]
**Decision:** [What was decided]
**Alternatives rejected:** [What else was considered]
**Supersedes:** DEC-YYY (only if replacing an earlier decision)
```

---

### DEC-001: Actor-anchored continuous universe
**Date:** 2026-03-27
**Context:** Needed to lock project identity so design doesn't drift toward BitLife clone, detached god sim, or vague universe handwaving.
**Decision:** Actora is one continuous universe simulation per save. Player lives as the current actor. Same-save scope zoom from actor → city → country → world → star system → galaxy → universe. Death is structural transition, not fail state. Continuity through connected actors.
**Alternatives rejected:** Pure BitLife loop, separate game modes, hard fail on death.

### DEC-002: Simulation core stays UI-agnostic
**Date:** 2026-03-30
**Context:** Needed clean separation so simulation logic can work independently of rendering.
**Decision:** Only `main.py` knows about curses. World, Human, events, identity are pure simulation.
**Alternatives rejected:** Curses calls scattered through simulation code.

### DEC-003: Options popup replaces standalone Quit key
**Date:** 2026-04-01
**Context:** Shell redesign interview — Quit as a top-level key wastes a primary command slot.
**Decision:** `[4]` = Options popup containing quit game + misc/system actions. Not a standalone quit key.
**Alternatives rejected:** `Q` as permanent top-level quit, separate Options screen.

### DEC-004: Menu as primary navigation hub
**Date:** 2026-04-01
**Context:** Shell interview — too many letter keys for navigation creates mnemonic clutter.
**Decision:** `[3]` = Menu containing Browser / Actions / Profile. Old letter keys (`L`, `H`, `T`, `P`) become legacy once Menu is real.
**Alternatives rejected:** Keep all letter keys permanently, pure number navigation.

### DEC-005: No hidden keybind aliases
**Date:** 2026-04-01
**Context:** Backspace/Esc/LEFT were quietly acting as Back on many screens without being documented.
**Decision:** No hidden convenience aliases outside scoped text-input/search contexts. `B` is Back. Period.
**Alternatives rejected:** Allow Backspace as universal back, allow multiple back aliases.

### DEC-006: Action time-shape over abstract buckets
**Date:** 2026-04-01
**Context:** Interview tried to force instant/monthly/commitment as rigid categories. User corrected.
**Decision:** Action classification should come from what the action touches and how much time it costs, not from predeclared abstract bucket types. Real seam is: (1) no time / negligible, (2) month-consuming but bounded, (3) ongoing commitment / stateful.
**Alternatives rejected:** Rigid instant/monthly/commitment taxonomy.

### DEC-007: Passive-vs-active life maintenance
**Date:** 2026-04-01
**Context:** Game shouldn't force tedious micromanagement for ordinary functional life.
**Decision:** Ordinary relationship/life upkeep should happen through thresholds/system logic. Active actions provide stronger gains, targeted attention, and playstyle expression. Applies beyond relationships to jobs and other systems.
**Alternatives rejected:** Fully manual maintenance, fully automatic with no player agency.

### DEC-008: Balanced shell header direction
**Date:** 2026-04-01
**Context:** Shell redesign interview — needed a chosen visual direction.
**Decision:** Option 2 (Balanced): centered Actora title, actor + turn line, screen-name line, compact state line (location/date left, health/money right), centered numbered primary commands, local controls only when relevant.
**Alternatives rejected:** Minimal header, heavy three-band header, pure game-y yolo header.

### DEC-009: Show-before-apply for TUI work
**Date:** 2026-04-01
**Context:** ASCII mockups in chat kept being ambiguous. Real UI experiments needed.
**Decision:** For UI/shell/TUI layout work: show mockups/drafts first. If mockups aren't clear enough, use a throwaway worktree and test the real surface. Don't patch blind.
**Alternatives rejected:** Keep guessing from prose descriptions, apply and hope.

### DEC-010: Lock control contract before shell redesign
**Date:** 2026-04-02
**Context:** Shell experiments kept drifting because hotkey truth was fragmented across code, tui-standards, and ui-architecture.
**Decision:** Stop redesigning shell/UI surfaces while hotkey/control truth is fragmented. First lock the control contract, then resume shell experimentation.
**Alternatives rejected:** Keep patching and hope it converges.

### DEC-011: Flat doc structure with clear names
**Date:** 2026-04-02
**Context:** Docs had vague names (WIR, live issues), mixed purposes, subfolders adding no value, and overlapping content across 14 files.
**Decision:** Flat `docs/` directory, 13 docs with names that say what they are. No subfolders. Every doc has one clear purpose. Routing table in guide.md.
**Alternatives rejected:** Keep existing layered system, add more docs to cover gaps.
