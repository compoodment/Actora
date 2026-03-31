# TUI Standards

Consistent controls, navigation, and interaction patterns for all Actora TUI surfaces.


## Controls

### Universal keys (available on every screen)
- `[Q]` — Quit (with confirmation prompt)
- `[B]` or `Backspace` — Go back to previous screen (where applicable)

### Navigation
- `[↑↓]` — Move selection or scroll content
- `[←→]` — Adjust values (stats only)

### Actions
- `[Space]` — Select, toggle, or pick an option
- `[Enter]` — Continue, proceed, or confirm

### Specialist keys (context-specific)
- `[R]` — Randomize (stats screen only)
- `[/]` — Search or jump to year (lineage, history)
- `[0-9]` — Custom numeric input (skip time)
- `[A] [L] [D]` — Filter shortcuts (lineage: All, Living, Dead)
- `[A]` — Advance one month (Life View only)
- `[S]` — Open skip time (Life View only)
- `[P]` — Open profile (Life View only)
- `[L]` — Open lineage (Life View only)
- `[H]` — Open history (Life View only)


## Footer format

Footers should follow this pattern:
```
[navigation] [actions] [specialist] [back] [quit]
```

Example: `[↑↓] Move   [Space] Select   [Enter] Continue   [B] Back   [Q] Quit`


## Naming rules

| Key | Always call it |
|-----|---------------|
| ↑↓ with selection list | Move |
| ↑↓ with scrollable content | Scroll |
| Space | Select |
| Enter | Continue (or "Start Game" on final confirmation only) |
| B | Back |
| Q | Quit |


## Quit confirmation

Pressing Q on any screen shows a centered confirmation prompt:
```
Are you sure you want to quit?

  [Enter] Quit   [B] Cancel
```

This prevents accidental quits. The game only exits when Enter is pressed on the confirmation.


## Adding new screens

When adding a new TUI screen:
1. Include `[Q] Quit` in the footer
2. Include `[B] Back` if the screen has a parent to return to
3. Use `[Space] Select` for picking options, not Enter
4. Use `[Enter] Continue` for proceeding to the next step
5. Use `Move` for selection lists, `Scroll` for content browsing
6. Follow the footer format order: navigation → actions → specialist → back → quit
7. Reference this document in the implementation prompt
