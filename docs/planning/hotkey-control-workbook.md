---
title: Hotkey & Control Workbook
role: fill-in-control-contract-workbook
stability: low
layer: planning
relates_to: [tui-standards, ui-architecture, actionable-summary]
---

# Hotkey & Control Workbook

Purpose: fill-in workbook for locking Actora's control contract more explicitly before more shell/UI redesign work.

Status: provisional working document. This is **not** the canonical hotkey contract yet.
Use it to capture current desired truth + future direction, then promote the reviewed result into `tui-standards.md` / `ui-architecture.md`.

Notes:
- Prefilled values below are my best read of current repo truth + recent interview signals.
- Change anything you dislike.
- Replace `PROVISIONAL` / `UNSURE` / `TBD` freely.

---

# Template 1 — Current-State Hotkey Contract

## 1. GLOBAL RULES
- Quit key: `Q`
- Back key: `B`
- Popup confirm key: `Space`
- Popup cancel key: `B` only when popup is explicitly skippable
- Continue/proceed key: `Enter`
- Search key: `/`
- Are hidden aliases ever allowed outside text input/search?: **No**
- Are Backspace/Esc allowed as navigation outside text input/search?: **Probably no**, except where current code still has legacy behavior that should be cleaned up

## 2. MAIN / LIFE VIEW
- Advance one month: `A` and `Enter`
- Skip time: `S`
- Open browser (default tab): `L`
- Open browser directly to history: `H`
- Open actions: `T`
- Open profile: `P`
- Open menu: `PROVISIONAL: maybe [3] later, not canonical yet`
- Open options: `PROVISIONAL: maybe [4] later, not canonical yet`
- Left panel scroll up: `↑`
- Left panel scroll down: `↓`
- Anything else on main: numbered top-level shell commands are desired direction, but not canonical truth yet

## 3. BROWSER — GLOBAL
- Switch browser tabs: `Tab`
- Back from browser: `B`
- Search in browser: `/`
- Should browser have direct tab hotkeys too?: `UNSURE`
- If yes, which ones?: `TBD`

## 4. BROWSER — RELATIONSHIPS TAB
- Move in filters: `↑↓`
- Move into actor list: `→` or `Tab`
- Move back to filters: `←` or `B`
- Move in actor list: `↑↓`
- Inspect selected actor: `Enter`
- Clear search: `TBD (currently code uses Backspace in some places; likely should be tighter)`
- Any filter shortcut keys: `Probably none for now`
- If yes, which ones?: `N/A`

## 5. BROWSER — HISTORY TAB
- Scroll history up: `↑`
- Scroll history down: `↓`
- Open year jump/search: `/`
- Confirm typed year: `Enter`
- Cancel typed year: `Esc`
- Clear typed year: `Backspace while typing`
- Any direct history shortcuts: `Probably none for now`

## 6. ACTIONS SCREEN
- Back from Actions: `B`
- Open/activate selected action: `Enter` (PROVISIONAL)
- Move categories: `↑↓` if categories are a vertical list, or `←→` if categories are horizontal
- Move actions: `↑↓`
- Move details pane (if any): `Probably not directly; details follow selection`
- Any direct action shortcut that should exist now: `T is currently legacy for Hang Out, but likely not a good final pattern`
- Should Actions have primary shell number keys visible now?: `Not until they are fully canonical + implemented honestly`
- If yes, what should they do?:
  - `[1]` Advance
  - `[2]` Skip Time
  - `[3]` Menu or Back-to-main equivalent
  - `[4]` Options or Quit depending on final shell decision

## 7. PROFILE
- Back from Profile: `B`
- Scroll up: `↑`
- Scroll down: `↓`
- Any profile-specific keys now: `None strongly established`

## 8. SKIP TIME
- Move preset selection: `↑↓`
- Confirm preset/custom: `Enter`
- Custom numeric input: `0-9`
- Clear numeric input: `Backspace while typing`
- Cancel/back: `B`
- Should Skip Time remain a screen for now?: `Probably yes for now, even if popup direction is likely later`

## 9. CONTINUATION / DEATH
- Continue after death summary: `Enter`
- Back from continuation: `B`
- Move continuation candidates: `↑↓`
- Inspect/select continuation: `Enter`
- Back from continuation detail: `B`
- Confirm continuation choice: `Enter`

## 10. POPUPS / CHOICE OVERLAYS
- Move choice up/down: `↑↓`
- Confirm choice: `Space`
- Cancel/skip choice: `B` only when popup is skippable
- Should Enter ever confirm a popup?: `No`
- Should B ever cancel a non-skippable popup?: `No`

## 11. NUMBERED PRIMARY COMMANDS
- Should [1][2][3][4] exist NOW on main screens?: `Directionally yes, but only once canonical + honestly implemented`
- If yes, what should [1] do?: `Advance`
- If yes, what should [2] do?: `Skip Time`
- If yes, what should [3] do?: `Menu`
- If yes, what should [4] do?: `Options`
- On which screens should the numbered row appear right now?: `UNSURE — probably only major in-game screens, not every surface`
- On which screens should it NOT appear right now?: `wizard/setup screens, search/input submodes, popups, maybe continuation until shell is more stable`

## 12. CURRENT NON-NEGOTIABLE RULES
- Rule 1: No hidden convenience aliases outside text input/search contexts
- Rule 2: `B` is Back
- Rule 3: Popup confirm is `Space`, not `Enter`
- Rule 4: If a command is visibly rendered, it must actually work
- Rule 5: Player-facing UI language must read like a human game UI, not spec/dev sludge

---

# Template 2 — Future / Expansion Hotkey Roadmap

## 1. PRIMARY SHELL DIRECTION
- Long-term, should main shell navigation be mostly: `Mixed, leaning menu-like / numbered for top-level shell actions`
- Why: reduce mnemonic clutter, reduce conflicts, make shell more menu-like and easier to remember

## 2. MENU / OPTIONS
- Should Menu become a major shell entry point long-term?: `Yes, likely`
- What should Menu eventually contain?: `Browser, Actions, Profile, maybe other actor/navigation surfaces`
- What should Options eventually contain?: `Quit, controls/help, maybe later settings/system/meta items`
- Should Menu and Options use numbers, arrows, or both?: `Probably numbers to open, arrows within popup`

## 3. BROWSER FUTURE
- Should Relationships / History keep sharing one Browser shell long-term?: `Yes`
- Should browser tabs have explicit direct hotkeys later?: `Maybe, but not required yet`
- Should browser search/discovery get deeper controls later?: `Probably yes`
- Any future browser hotkey ideas: `TBD`

## 4. ACTIONS FUTURE
- Should Actions eventually have category shortcuts?: `Maybe, but only if it stays understandable`
- Should Actions eventually have separate hotkeys for commitments/opportunities/available actions?: `UNSURE`
- Should there be action-specific quick keys later, or avoid that?: `Avoid premature clutter`
- Any future action-control ideas: `Action time-shape may matter more than fancy control shortcuts`

## 5. LOCATION / DOMAIN SCREENS FUTURE
- If Education / Work / Company / Travel get their own surfaces, should they:
  - use the same global shell contract: `Yes`
  - have local extra keys: `Yes, when needed`
  - both: `Yes`
- Notes: domain screens should not break the global control language just because they are specialized

## 6. POPUP / OVERLAY FUTURE
- Should small modals become more common than full screens?: `For lightweight things, probably yes`
- Which things should likely become popups later?: `Skip Time, Options, maybe small selectors / opportunities`
- Which things should probably stay full screens?: `Life View, Browser, Profile, Actions, bigger domain surfaces`

## 7. NUMBERED COMMAND EVOLUTION
- If [1][2][3][4] becomes real, should it stay limited to top-level shell commands only?: `Probably yes at first`
- Should deeper screens also use numbered actions later?: `Only if the surface truly becomes menu-like and it stays readable`
- What should be avoided here?: `number spam, duplicate meanings, fake visible commands that do nothing`

## 8. HOTKEY DESIGN PRINCIPLES FOR THE FUTURE
- Principle 1: easy to remember beats clever
- Principle 2: one concept should not have five aliases
- Principle 3: shell commands and local controls should have different jobs
- Principle 4: if UI shows a key, the key must work
- Principle 5: future depth should not turn the TUI into hidden-key soup

## 9. THINGS YOU DEFINITELY DO NOT WANT
- Don’t want: hidden keybind chaos
- Don’t want: different screens inventing their own random control language
- Don’t want: UI text claiming hotkeys/features that are not actually implemented
