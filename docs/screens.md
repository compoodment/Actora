---
title: Screens
tags: [implementation, tui, reference]
updated: 2026-04-04
---

# Actora Screens

Screen map, navigation hierarchy, and rules for adding new systems to the UI.
Separate from controls (interaction rules) and design (creative intent).

Note: Current implementation is TUI-first. This doc describes the intended TUI structure and should remain compatible with future non-TUI presentation.

---

## Navigation Hierarchy

```
Life View (anchor / home)
├── [1] Menu
│   ├── Browser
│   │   ├── Relationships tab
│   │   └── History tab
│   ├── Actions
│   └── Profile
├── [E] Skip Time
├── [Q] Advance month
└── [Esc] Options (quit, help, misc)
```

All screens are reachable from Life View. Nested screens return to their parent with [B].

---

## Screen Definitions

### Life View (anchor)
**Purpose:** The primary play surface. Where the player lives.
**What lives here:**
- Left panel: Identity, Location, primary Stats, Relationships (family + social links combined, name + type)
- Right panel: Accumulating event feed
- Header: Actor name, current date
- Footer: Primary hotkeys

**What does NOT live here:**
- Pending actions list (→ Actions screen)
- Friends as a separate section (→ folded into Relationships in left panel)
- History (→ Browser)
- Full actor detail (→ Profile)

**Scroll:** Left panel scrollable. Right panel scrollable.

**Left panel sections (in order):**
1. Identity (name, age, sex, gender, sexuality, location)
2. Stats (primary: health/happiness/intelligence)
3. Relationships (family roles + social links, all in one list, name + type label)

**Future left panel additions:**
- Commitments (education, job) — added when those systems ship
- Do NOT add more standalone sections without a structural review

---

### Profile (via Menu → Profile)
**Purpose:** Full actor detail. Who you are, what you've committed to. Being redesigned as a dashboard.
**What lives here (current):**
- Full stats (primary + secondary)
- Appearance
- Traits
- Sexuality, gender

**Dashboard design (in progress — DEC-2026-04-04):**
- Summary row per category: Stats, Traits, Skills/Talents, Needs, Mood
- Enter on any row → drill into category detail view
- Reusable pattern for any future category-based screen
- Implement incrementally as systems land

**Future:**
- Commitments section (education, jobs — long-term active states)
- Domain sections as systems mature (health conditions, property, etc.)

**What does NOT live here:**
- Event history (→ Browser / History tab)
- Relationship browser (→ Browser / Relationships tab)
- Pending actions (→ Actions screen)

---

### Browser (via Menu → Browser)
**Purpose:** Browsing and exploration of persistent simulation data.
**Tabs:**
- **Relationships** — all actors you have a link to, filterable by type/status/living
- **History** — your life event log with year separators and markers

**Relationships tab:**
- Persistent filter sidebar: All / Family / Friends / Former / Living / Dead
- Actor list: name, relationship type + closeness (for social), family role (for family), living/dead, age
- Detail pane: full actor detail on selection
- Search [/]

**History tab:**
- Chronological event log
- Year dividers with breathing room
- Year-jump [/]
- Scroll

**Future Browser tabs (as systems mature):**
- Archive / Lineage (family tree depth, deceased actor archive)
- Universe (broader world records — news, major events)

**What does NOT live here:**
- Actions or pending queue (→ Actions screen)
- Profile detail (→ Profile)

---

### Actions (via Menu → Actions)
**Purpose:** Player agency. What you can do. What you've queued.
**What lives here:**
- Pending actions (queued, awaiting next advance)
- Available actions by category (social, personal, career, etc.)
- Future: Active commitments display (education, job — long-duration states)
- Future: Open opportunities (persistent, non-urgent)

**What does NOT live here:**
- Life events (→ Life View feed / History)
- Profile commitments (Profile shows them as state; Actions is where you act on them)

**Filtering/navigation:**
- Category sidebar: Social, Personal (implemented). Career, etc. (future).
- Time Budget display in details column: total free hours, queued hours, remaining hours.
- Sub-type picker popup: Exercise, Read, Rest each open a picker showing sub-type options with time costs.
- **Age/context/era gating** — silently hidden (if you literally cannot do it right now regardless of effort, don't show it)
- **Resource/prerequisite gating** — shown as unavailable with reason (if you could do it but currently can't, e.g. no money, show it greyed with context)

**Future:**
- Cancel queued action
- Multi-month active actions with progress display
- Urgent opportunities (1-month window) surface as popups, not here

---

### Skip Time ([E] from Life View or any non-input screen)
**Purpose:** Advance simulation time in bulk.
**What lives here:**
- Preset jumps (1, 3, 6, 12, 24, 60 months)
- Custom numeric input
- Returns to Life View after skip

---

## Hotkey Map (current — v2 contract)

| Key | Action |
|-----|--------|
| Q | Advance month |
| E | Open Skip Time |
| [1] | Menu (Browser / Actions / Profile) |
| Esc | Options popup |
| Backspace | Back |

**Reserved context-only keys:**
- ↑↓ / W/S: navigate / scroll
- ←→ / A/D: adjust value fields (show ← value → when active)
- Space: toggle/select on multi-select screens
- Enter: proceed / confirm
- Tab: switch Browser tabs
- /: open search
- Enter: proceed / continue / confirm screen transition
- /: search or year-jump (Relationships, History)
- R: randomize (Stats creation screen only)
- 0-9: custom numeric input (Skip Time)
- Tab / →: switch focus between panels (Browser)

**Note:**
- [Q] advances month, [E] opens Skip Time — both available from any non-input screen.
- Browser, Actions, and Profile are accessed via [1] Menu. Legacy keys L/H/T/P have been removed.

---

## Rules for Adding New Systems

1. **Does it fit in an existing screen?**
   - New stat type → Profile stats section
   - New relationship type → Relationships tab in Browser
   - New action type → Actions screen category
   - New long-term commitment → Profile commitments section + Actions
   - New historical event type → History tab in Browser

2. **Is it a new top-level domain?**
   - Needs its own screen → assign a free hotkey, document it here, add to footer
   - Currently free: [N] (news future), [R] (reserved), L/H/T/P (freed after legacy cleanup)

3. **Never:**
   - Add standalone sections to Life View left panel without structural review
   - Add hotkeys without documenting them here
   - Overlap two screens' responsibilities
   - Use Enter to confirm popup choices (Enter = advance/proceed only)

---

## Future Screen Candidates

| Hotkey | Screen | Depends on |
|--------|--------|-----------|
| E | Education | Education system |
| W | Work / Career | Work system |
| N | News / World | News system |
| M | Map / World View | Travel + Place systems |
| ? | Universe / Scope View | Broader scope systems |

These are candidates, not commitments. Assign only when the system ships.

---

## Left Panel Growth Strategy

The left panel will grow as systems are added. Rules:

- **Current sections:** Identity, Stats, Relationships
- **Future additions in order:** Commitments (education/job status), then Health summary, then Property summary
- **Cap consideration:** At some point the left panel may need tabs or a collapsible section system. Do not implement until genuinely needed.
- **Never:** Add a section to the left panel if it has its own dedicated screen (actions, history, etc.)

---

## Right Panel (Event Feed)

- Accumulates events as they happen
- Scrollable
- Never used for navigation or status display — events only
- Year separators added automatically on year change

---

## Open Structural Questions

- When does the left panel need to split into tabs or collapse? (monitor as systems grow)
- Where exactly do "open opportunities" (persistent, non-urgent) live? (candidates: Actions screen, or a future dedicated section)
- How does scope-shifting (actor → city → country view) surface in the TUI? (deferred until scope systems exist)
