---
title: Decisions
tags: [core, decisions, stable]
updated: 2026-04-04
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

### DEC-003: Options popup replaces standalone Quit key *(superseded by DEC-015)*
**Date:** 2026-04-01
**Context:** Shell redesign interview — Quit as a top-level key wastes a primary command slot.
**Decision:** `[4]` = Options popup containing quit game + misc/system actions. Not a standalone quit key.
**Alternatives rejected:** `Q` as permanent top-level quit, separate Options screen.

### DEC-004: Menu as primary navigation hub *(superseded by DEC-016)*
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

### DEC-008: Balanced shell header direction *(implemented v0.48.0)*
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

### DEC-012: Q = advance month, E = skip time
**Date:** 2026-04-02
**Context:** Hotkey contract interview. Wanted advance/skip to be one-key actions reachable from anywhere, and freed Q from its old quit role.
**Decision:** Q = advance month. E = skip time. Both globally available except in: text input, search, popups, wizard, continuation, death screen.
**Alternatives rejected:** A/Enter for advance (kept as legacy but not canonical), S for skip.

### DEC-013: Backspace = universal Back
**Date:** 2026-04-02
**Context:** P was freed from Profile (Profile moved into Menu). Needed an intuitive global back key.
**Decision:** Backspace = Back globally outside text input. In text input/search, Backspace deletes characters. In search, Esc exits search mode.
**Alternatives rejected:** B = Back (old standard), P = Back.

### DEC-014: WASD as movement aliases
**Date:** 2026-04-02
**Context:** User is a gamer, fingers naturally on WASD. Wanted movement without leaving home position.
**Decision:** W/A/S/D are full aliases for ↑/←/↓/→. Same behavior, same context rules. In text input, WASD type characters.
**Alternatives rejected:** WASD only (no arrows), arrows only.

### DEC-015: Esc = Options popup (toggle)
**Date:** 2026-04-02
**Context:** Needed a dedicated key for the Options popup that's always accessible without being a number key.
**Decision:** Esc opens/closes Options popup. Outside text input: Esc = Options. In text input/search: Esc = exit text mode. Esc does NOT close other popups — only Options.
**Alternatives rejected:** [4] for Options (number key), dedicated key like O.

### DEC-016: Profile moves into Menu, P freed
**Date:** 2026-04-02
**Context:** Shell redesign — reduce top-level letter key clutter. Profile doesn't need its own dedicated hotkey if Menu is always one key away.
**Decision:** Profile accessible via [1] Menu → Profile. P key freed (not reassigned — Backspace became the universal Back key instead).
**Alternatives rejected:** Keep P = Profile as standalone hotkey, P = Back.

### DEC-018: Actions use a monthly time budget, not slot limits
**Date:** 2026-04-04
**Context:** Action quantity cap design. Slot-based limits (e.g. "2 actions per month") are arbitrary and don't model real life. Time is the real resource.
**Decision:** Each character has a monthly free-time pool in hours: total hours − sleep hours − obligatory maintenance (eating, hygiene). Each action and sub-action has a specific time cost in hours. Players can only queue what fits in their remaining free time.
Sleep hours vary by trait and later by condition/lifestyle. Example starting baseline: ~240hr/month sleep (8hr/night). Restless trait = less sleep = more free time. Later: sleep disorders, shift work, etc. affect this.
Sub-actions carry individual time costs — a specific book has its own read time (eventually sourced from real data), a specific exercise session has its own duration.
**Alternatives rejected:** Abstract slot system, discipline-gated slots.

### DEC-019: Action sub-selections — each action has a sub-type with individual properties
**Date:** 2026-04-04
**Context:** Exercise, Read, Rest are categories, not actions. Each sub-type (running, math book, nap) has distinct outcomes and time costs.
**Decision:** Actions with sub-types open a sub-selection UI on Enter. Each sub-type has: label, time cost in hours, stat outcome. Exercise sub-types affect physical stats (e.g. home workout ~1hr, gym session ~1.5hr). Read sub-types affect knowledge stats by subject (math → intelligence, history → wisdom, etc.). Rest sub-types affect recovery (nap ~1hr, music/stare-at-wall ~0.5hr).
Time costs are estimated initially but should eventually reflect real-world durations: books sourced from real page-count data, workouts from standard exercise guides.
Future: real books get actual read times from external data lookup.
**Alternatives rejected:** Single generic action with variable outcome, flat action list without sub-types.

### DEC-020: Trait pool redesign — traits must be meaningful and non-weird
**Date:** 2026-04-04
**Context:** Original trait pool ("Fussy", etc.) was AI-generated without care. Traits should feel like real personality descriptors a player would actually pick.
**Decision:** Replace the current trait pool with a clean redesigned set. Traits must: (1) be recognizable human personality words, (2) have actual gameplay effects (not just event eligibility flavor), (3) feel meaningful to pick. Fussy, Restless, Alert removed or renamed. New pool to be designed as a separate task before action system ships.
**Alternatives rejected:** Keep current pool, add more AI-generated traits.


### DEC-021: Stat list redesign — 13 stats replacing 11
**Date:** 2026-04-04
**Context:** Original 11-stat list had Creativity (vague scope), no cognitive retention stat, no stress mechanism. Age curves not designed.
**Decision:** Replace 11 stats with 13: Health, Happiness, Intelligence, Memory, Stress, Strength, Charisma, Imagination, Wisdom, Discipline, Willpower, Looks, Fertility. Creativity renamed Imagination (character's intrinsic creative capacity; what the player does with it is their choice). Memory added (lifestyle-degradable cognitive retention, distinct from Intelligence). Stress added (pressure valve; high Stress degrades other stats). Fertility kept (player agency over family planning).
**Age curves:** Strength peaks 18-25; Health declines from ~40; Memory declines from ~50; Wisdom grows lifelong; Imagination peaks young; Looks peaks young adulthood. All curves are lifestyle-modifiable baselines, not deterministic paths.
**Stat cap:** Soft cap 100. Trait-extended ceiling possible (e.g. relevant trait lets a stat exceed 100).
**Alternatives rejected:** Cutting Fertility (would remove player agency), keeping Creativity as stat name (scope too broad), flat age curves.

### DEC-022: Trait pool redesign — 12 traits replacing 10
**Date:** 2026-04-04
**Context:** Original 10-trait pool (Fussy, Calm, Alert, etc.) was AI-generated without care. Traits had no real gameplay effects beyond event eligibility.
**Decision:** New pool of 12 traits (adjective form, pick 4 at creation): Driven, Chill, Curious, Social, Disciplined, Impulsive, Empathetic, Resilient, Introverted, Extraverted, Restless, Ambitious. Each trait defines: sleep modifier, stat ceiling/growth modifiers, skill growth modifiers, event tags, action effectiveness modifiers. Defined as a data dict — adding a new trait = one dict entry, no code hunting.
**Trait evolution:** Traits drift gradually through lifestyle (you become what you do). Major life events can accelerate drift. No dramatic pop-up — player notices over long runs.
**Species:** Trait system is Actor-level architecture. The pool is per-species content. Humans get this pool; other species get their own.
**Alternatives rejected:** 3 traits at creation (too few for meaningful expression), fixed traits (unrealistic, humans adapt).

### DEC-023: Skills & Talents architecture
**Date:** 2026-04-04
**Context:** Skills needed as a layer distinct from stats (practiced competency vs raw capacity) and traits (personality vs learned ability).
**Decision:** Skills are practiced competencies starting at 0, growing through actions/events/relationships. Player-facing label: Talents. Internal code: `skills`. Talents (passive/inherited) are a future sub-system with a `source` field to distinguish them from practiced skills. Trait gives both a starting bonus AND a faster growth rate for related skills. Stat determines the growth ceiling (high Imagination → higher ceiling for creative skills). Skills discoverable/unlockable through play, not a fixed starting list.
**Alternatives rejected:** Skills as a renamed stat (they're fundamentally different — practiced, not intrinsic), flat skill list with no discovery.

### DEC-024: Needs & Drives — sleep as time budget only, social as background pressure
**Date:** 2026-04-04
**Context:** Needed to decide: are needs micromanagement meters (Sims-style) or background simulation pressures?
**Decision:** Needs are background pressure — player notices consequences when ignored, never babysits a meter. Sleep is purely a time budget constraint: monthly free time = total hours − sleep hours − maintenance. No sleep action, no deprivation state (for now). Social need: ~6 months true isolation → Happiness drain begins. Threshold is realistic because time skip runs passive events month-by-month — isolation only accumulates if genuinely isolated. Ignoring social need long-term → depression risk → effectiveness reduction → health chain. Future needs (physical activity, creative outlet, purpose) added when supporting systems exist.
**Alternatives rejected:** Sims-style micromanagement meters (tedious, wrong for the game feel), ignoring needs entirely (removes meaningful simulation depth).

### DEC-025: Mood system — numeric + contextual label, both visible
**Date:** 2026-04-04
**Context:** Happiness covers long-term satisfaction. Short-term emotional state had no representation. Needed a mechanic that responds to immediate events.
**Decision:** Mood is short-term emotional state, distinct from Happiness. Internal: numeric -50 to +50 (0 = neutral). Player-visible: both the number AND a contextual descriptive label that carries mechanical signal. Example: "-20 · Grieving — social actions less effective." Labels are a fixed set first, context-driven later. Mood affects: action effectiveness, event eligibility, NPC reactions, skill growth. Sustained bad mood → Happiness drain. High Happiness buffers mood drops.
**Why both number and label:** Number = precise feedback. Label = human meaning + gameplay consequence signal. Neither alone sufficient.
**Alternatives rejected:** Label only (loses precision), number only (loses human meaning), merging Mood into Happiness (they operate on different timescales).

### DEC-017: Q/E available from any non-input screen
**Date:** 2026-04-02
**Context:** User doesn't want to navigate back to Life View just to advance time or skip. You should be able to advance/skip from Browser, Actions, Profile, future Education/Company views, etc.
**Decision:** Q and E work from any screen that isn't actively consuming input. The game should not require returning to Life View to perform time actions.
**Alternatives rejected:** Q/E only on Life View.
