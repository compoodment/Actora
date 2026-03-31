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
- `[Space]` — Select or toggle an option when the screen supports explicit selection
- `[Enter]` — Continue, proceed, or confirm

### Selection behavior
- **Single-choice lists:** moving the highlight changes the current choice immediately. Do not also require a separate commit state.
- **Multi-select lists:** highlight shows focus; `[x]` shows toggled selections.
- **Single-choice lists should not show `[x]` markers** unless there is a true separate committed state the player can change independently of focus.
- **Enter should never be the primary selection key on list screens.** It is for continuing/proceeding.

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
3. For single-choice lists, make the highlighted row the live selection
4. Use `[x]` markers only for true multi-select/toggle screens
5. Use `[Space] Select` for picking/toggling where explicit selection is needed; do not make Enter the primary list-selection key
6. Use `[Enter] Continue` for proceeding to the next step
7. Use `Move` for selection lists, `Scroll` for content browsing
8. Follow the footer format order: navigation → actions → specialist → back → quit
9. Reference this document in the implementation prompt
