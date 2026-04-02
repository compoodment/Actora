---
title: TUI Standards
role: interaction-design-rules
stability: high
layer: implementation
relates_to: [ui-architecture, architecture]
---

# TUI Standards

Consistent controls, navigation, and interaction patterns for all Actora TUI surfaces.


## Controls

### Universal keys (available on every screen)
- `[Q]` — Quit (with confirmation prompt)
- `[B]` — Go back to previous screen (where applicable)

Rule:
- Do **not** add hidden convenience aliases for navigation outside clearly scoped text-input/search contexts. `Backspace` may edit text while typing, but ordinary surface navigation should use explicit documented keys like `[B]`.

### Navigation
- `[↑↓]` — Move selection or scroll content
- `[←→]` — Adjust values on any adjustable field (stats, appearance, identity value fields)

### Actions
- `[Space]` — Select or toggle an option when the screen supports explicit selection; also the **only** confirm key for popup choices (Enter must never confirm popups)
- `[Enter]` — Continue, proceed, or confirm screen transition

### Selection behavior
- **Single-choice lists:** moving the highlight changes the current choice immediately. Do not also require a separate commit state.
- **Single-choice value fields:** when a row owns one value from a fixed set, `←→` cycles the value directly on the row instead of opening a second nested chooser. The active field **must** visually render as `← value →` to signal it is adjustable.
- **Multi-select lists:** highlight shows focus; `[x]` shows toggled selections.
- **Single-choice lists should not show `[x]` markers** unless there is a true separate committed state the player can change independently of focus.
- **Enter must never be a confirm key for popup/choice overlays.** Popup overlays use Space only — Enter is reserved for month advancement and screen transitions and must be fully blocked while a popup is active.

### Specialist keys (context-specific)
- `[R]` — Randomize (stats screen only)
- `[/]` — Search or year-jump (Browser: Relationships/History tabs)
- `[0-9]` — Custom numeric input (skip time / history year jump)
- `[Tab]` — Switch Browser tabs when no tab-specific search input is active
- `[→]` — In Browser Relationships tab, move focus from filters to actor list
- `[←]` — In Browser Relationships tab, move focus from actor list back to filters
- `[A]` — Advance one month (Life View only; Enter also advances on Life View)
- `[S]` — Open Skip Time screen (Life View only)
- `[P]` — Open Profile (Life View only)
- `[L]` — Open Browser on Relationships tab (Life View only)
- `[H]` — Open Browser on History tab (Life View only)
- `[T]` — Open Actions screen (Life View only)


## Main screen navigation map

| Key | Destination |
|-----|------------|
| A / Enter | Advance 1 month |
| S | Skip Time screen |
| L | Browser → Relationships tab |
| H | Browser → History tab |
| T | Actions screen |
| P | Profile screen |
| Q | Quit confirmation |

**Notes:**
- `[H]` is a shortcut into the Browser at the History tab, not a separate standalone screen.
- The Browser is one shell with two tabs (`Relationships`, `History`), not two unrelated screens.


## Shell header + footer direction

Current shell direction for major in-game screens:
- Keep a compact top shell identity stack rather than collapsing everything into one command bar.
- Preferred current layout direction:
  1. centered Actora title
  2. actor + simulation turn line
  3. centered screen-name line
  4. compact state/info line (location/date on the left; health/money on the right)
- Primary commands should be centered and menu-like.
- Local controls should also be centered, but only shown when relevant to the current surface/mode.
- Use a single full-width divider unless the body is truly split into distinct panes.
- Do not repeat a screen title inside the body if the shell header already names the screen.

## Footer format

When a footer hint row is needed, follow this pattern:
```
[navigation] [actions] [specialist] [back] [quit]
```

Example: `[↑↓] Move   [Space] Select   [Enter] Continue   [B] Back   [Q] Quit`

Browser-specific rule:
- The Browser tab row is shell chrome, not body content.
- Visually separate the tab row from the active pane content with a bottom divider/rule.


## Naming rules

| Key | Always call it |
|-----|---------------|
| ↑↓ with selection list | Move |
| ↑↓ with scrollable content | Scroll |
| Space | Select |
| Enter | Continue (or "Start Game" on final confirmation only) |
| B | Back |
| Q | Quit |

Relationship wording rule:
- Use player-facing social-state labels that read naturally in the UI.
- Current label choice for archived/former social ties is `Past`.


## Quit confirmation

Pressing Q on any screen shows a centered confirmation prompt:
```
Are you sure you want to quit?

  [Enter] Quit   [B] Cancel
```

This prevents accidental quits. The game only exits when Enter is pressed on the confirmation.


## Browser behavior rules

- Browser Relationships tab has two focus zones: `filters` and `actors`.
- `↑↓` moves within the active focus zone.
- `[→]` or `[Tab]` moves from filters to actors.
- `[←]` or `[B]` moves from actors back to filters.
- `[B]` from filters exits the Browser back to Life View.
- `[/]` opens search on the active Browser tab.
- Search mode temporarily owns text input; tab switching should not fire while search is active.

## Adding new screens

When adding a new TUI screen:
1. Include `[Q] Quit` in the footer
2. Include `[B] Back` if the screen has a parent to return to
3. For single-choice lists, make the highlighted row the live selection
4. Use `[x]` markers only for true multi-select/toggle screens
5. Use `[Space] Select` for picking/toggling where explicit selection is needed; do not make Enter the primary list-selection key
6. Use `[Enter] Continue` for proceeding to the next step
7. Use `Move` for selection lists, `Scroll` for content browsing
8. Follow the footer format order: navigation → actions → specialist → back → quit
9. For shell-style multi-tab surfaces, visually separate shell chrome from body content
10. If layout clarity is still ambiguous after mockups, prefer a temporary worktree/branch experiment and playtest the real UI before finalizing the shape
11. Reference this document in the implementation prompt
