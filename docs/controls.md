---
title: Controls
tags: [implementation, controls, tui, stable]
updated: 2026-04-03
---

# Actora Controls

Canonical control contract for all TUI surfaces. If it's not here, it's not official.

---

## Global contract

| Key | Action | Notes |
|-----|--------|-------|
| Q | Advance month | Blocked: text input, search, popups, wizard, continuation, death screen |
| E | Skip time | Same blocks as Q |
| Backspace | Back / cancel | Navigation; overridden to delete-char in text input |
| Esc | Options popup | Outside text input/search; closes Options if already open |
| Enter | Proceed / confirm | Screen transitions, popup confirm, confirmation screens |
| [1] | Menu | Always visible; opens Browser / Actions / Profile |
| [2][3][4] | Reserved | Future domain systems |
| / | Open search | Any screen that supports it |
| W / ↑ | Move up / scroll up | Outside text input |
| S / ↓ | Move down / scroll down | Outside text input |
| A / ← | Move left / adjust value left | Outside text input |
| D / → | Move right / adjust value right | Outside text input |
| Tab | Switch Browser tabs | Browser only |
| Space | Toggle / select | Multi-select screens only |

**Text-input contexts (search, year jump, custom month input):**
- Backspace = delete character
- Esc = cancel / exit the input context (takes priority over Options in this context)
- Options popup (Esc) is blocked while text input is active

This means in Skip Time custom input, Esc exits the input (not Options). Same rule for Browser search, History year jump, and any future text-input fields.

**WASD are full movement aliases for arrow keys.** Same behavior, same context rules. In text input, WASD type characters (no movement).

**Adjustable value fields:** A/D (and ←→) adjust value when the row is active/focused, navigate when it's not. Active adjustable fields must visually render as `← value →`.

---

## Context override rules

| Context | What changes |
|---------|-------------|
| Text input field | Backspace = delete char, WASD = type characters, Esc = exit text mode |
| Search / year jump / custom input | Backspace = delete char, WASD = type characters, Esc = cancel/exit input (Options blocked) |
| Any popup open | Q/E blocked, [1] blocked |
| Character creation wizard | Q/E blocked, Esc blocked, [1] blocked |
| Continuation/death screen | Q/E blocked |

---

## Per-screen contracts

### Life View (anchor screen)

| Key | Action |
|-----|--------|
| Q | Advance month |
| E | Open Skip Time |
| [1] | Menu |
| Esc | Options |
| W/S or ↑↓ | Reserved for future panel interaction |

Left/right panel scrolling: mouse wheel when hovering over panel (future implementation).

---

### Browser

Two tabs: Relationships (with filter sidebar + actor list) and History (read-only log).

| Key | Action | Context |
|-----|--------|---------|
| Tab | Switch Relationships / History tab | |
| W/S or ↑↓ | Move within active focus zone | |
| D or → | Move focus: filters → actor list | Relationships tab |
| A or ← | Move focus: actor list → filters | Relationships tab |
| Backspace | Actor list → filters | In actor list |
| Backspace | Close Browser | In filters |
| Enter | Inspect selected actor | Actor list |
| / | Open search | Either tab |

History tab: W/S scroll log, `/` opens year jump, Enter confirms year, Backspace cancels year input / closes Browser.

---

### Actions

Three columns: Categories / Actions / Details. Details is currently display-only.

| Key | Action | Context |
|-----|--------|---------|
| W/S or ↑↓ | Move within active column | |
| D or → | Move focus: categories → actions | |
| A or ← | Move focus: actions → categories | |
| Enter | Queue selected action | On an action |
| Backspace | Close Actions | |

Details column follows action selection automatically. Queued actions resolve on Q (next advance).

---

### Profile

Read-only for now. Future: commitments, health, property sections.

| Key | Action |
|-----|--------|
| W/S or ↑↓ | Scroll (when content grows) |
| Backspace | Close Profile |

---

### Skip Time

| Key | Action |
|-----|--------|
| W/S or ↑↓ | Move between presets |
| Enter | Confirm selected preset / confirm custom input |
| 0-9 | Type custom month count |
| Backspace | Delete typed digit; close screen if input empty |
| Q/E | Blocked |

---

### Character Creation Wizard

| Key | Action | Context |
|-----|--------|---------|
| W/S or ↑↓ | Move between fields | |
| A/D or ←→ | Cycle value / adjust | Adjustable fields |
| Enter | Proceed to next step | |
| Backspace | Go back one step | Navigation |
| Backspace | Delete character | Text input field |
| Space | Select / toggle | Choice fields |
| R | Randomize all stats | Stats step only |
| Q / E / Esc / [1] | Blocked | Entire wizard |

---

### Continuation / Death

Death summary → candidate list → candidate detail → confirm. Q/E fully blocked throughout.

| Key | Action | Context |
|-----|--------|---------|
| Enter | Acknowledge death / proceed | Death summary |
| W/S or ↑↓ | Move between candidates | Candidate list |
| Enter | Inspect selected candidate | Candidate list |
| Backspace | Back to candidate list | Candidate detail |
| Enter | Confirm continuation | Candidate detail |
| Backspace | No effect | Death summary (nowhere to go) |

---

### Menu popup ([1])

| Key | Action |
|-----|--------|
| W/S or ↑↓ | Move between items |
| 1 / 2 / 3 | Fast-select (Browser / Actions / Profile) |
| Enter | Open selected |
| Backspace | Close popup |

---

### Options popup (Esc)

| Key | Action |
|-----|--------|
| W/S or ↑↓ | Move between items |
| Enter | Select item |
| Esc | Close popup |

Current items: Quit Game → confirmation, Help/Controls (future), Settings (future).

---

### Quit confirmation

| Key | Action |
|-----|--------|
| Enter | Confirm quit |
| Backspace | Cancel |

---

## Popup close rules

| Popup | Close key |
|-------|-----------|
| Options popup | Esc (toggle) |
| Menu popup | Backspace |
| Quit confirmation | Backspace |
| Choice overlays | Backspace (if skippable) |

Esc only closes Options. It does not close other popups.

---

## Footer naming conventions

| Key | Display label |
|-----|--------------|
| ↑↓ with selection list | Move |
| ↑↓ with scrollable content | Scroll |
| Space | Select |
| Enter | Continue (or "Start" on final confirmation only) |
| Backspace | Back |
| Q | Quit (only in footer if Options is unavailable) |

Relationship wording: archived/former social ties use the player-facing label `Past`.

---

## Rules for adding new screens

1. Include `[1] Menu` and `Esc Options` in shell header
2. Include `[Backspace] Back` in footer if screen has a parent
3. Single-choice lists: highlighted row = live selection (no separate commit)
4. Adjustable fields: render `← value →` when active
5. Use `[Space] Select` only for true multi-select/toggle screens
6. Use `[Enter] Continue` for proceeding; never for popup confirm
7. Q/E must be blocked during any active input context
8. Follow footer order: navigation → actions → specialist → back
9. Visually separate shell chrome from body content (divider)
10. If layout is ambiguous after mockups, use a throwaway worktree to test real UI
11. Reference this doc in implementation prompts
12. After adding a screen, cascade-check: does screens.md need updating?

---

## Known issues (fix in next UI pass)

- Space/Enter overlap was fixed in wizard location, questionnaire, and pending choice popup. Remaining screens should still be audited for any leftovers.
- BACK_KEYS aliases (Backspace/127/8) in `handle_actions_key` — should be Backspace only
- Q/E not yet wired as advance/skip (currently A/S) — full wiring needed in next UI pass **[DONE in worktree v0.46.0]**
- WASD movement not yet implemented — current code uses arrows only **[DONE in worktree v0.46.0]**
- Skip Time: Backspace exits screen instead of deleting typed digit first — acceptable for now since Skip Time is destined to become a popup
- `[Bksp] Erase` label in Skip Time footer is inconsistent with `[Bsp] Back` elsewhere — fix when Skip Time becomes a popup
