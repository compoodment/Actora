---
title: Screens
tags: [implementation, tui, reference]
updated: 2026-05-11
---

# Actora Screens

Screen map, navigation hierarchy, and rules for adding new systems to the UI.
Separate from controls (interaction rules) and design (creative intent).

Note: Current implementation is TUI-first. This doc describes the intended TUI structure and should remain compatible with future non-TUI presentation.

---

## Web Shell Track (`/lab/actora`)

DEC-035 starts a web shell implementation as a parallel presentation track. This section maps existing screen responsibilities to the first web surface so the web version does not drift into a separate game design.

Route:
- Public game surface: `/lab/actora`
- `Projects` may continue linking the repo/showcase until explicitly removed; this decision does not delete it.

Entry flow:
- Title / Start / Save-lite screen first
- New game enters web character creation
- Continue/load resumes an existing local test save when present

Screen responsibility mapping:
- **Life View → Main play screen:** still the anchor/home surface. Shows current actor, current date/month, primary stats, location, relationships summary, and accumulating event feed.
- **Actions → Action cards/queue:** button/card interaction, time budget visible, queued actions clear, sub-type choices explicit.
- **Profile → Card dashboard:** follow the card dashboard direction from `design.md`; web should use this before continuing TUI row-dashboard polish.
- **Browser → Relationships + History surfaces:** relationships remain structural link browsing; history remains record/event browsing with year separation and markers.
- **Skip Time → Time controls:** month advance remains primary. Larger skips can be exposed as explicit controls, but still resolve month-by-month through simulation truth.
- **Death / Continuation → Staged interrupt flow:** death appears first, then acknowledgment, then continuation candidate browsing/detail, then handoff.

Web interaction direction:
- Use buttons/cards as the primary interaction model.
- Preserve keyboard accessibility where practical, but do not make command input the core web interaction.
- Visual weirdness is allowed only when readability stays strong; Actora-specific strangeness should come from premise, continuity, records, and scope, not confusing controls.

Do not add new top-level web systems that the roadmap says are not ready. If a future screen candidate appears visually useful, keep it as a placeholder or disabled affordance unless its underlying system exists.

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
**Purpose:** Full-picture character sheet. Who you are right now. Dashboard of summary rows, each drillable.

**Current truth (pre-redesign):** Flat read-only list — Identity, Appearance, Traits, Primary Stats, Secondary Stats, Location, Relationships.

**Dashboard design (interview 2026-04-07):**

Category rows in order:
1. Identity — name, age, gender (replaces sex once chosen), sexuality, life stage
2. Appearance — eye/hair/skin
3. Stats — Health, Happiness, Intelligence, Money (primary)
4. Attributes — Strength, Charisma, Imagination, Memory, Wisdom, Discipline, Willpower, Stress, Looks, Fertility (secondary)
5. Traits — the player's 4 traits
6. Mood — placeholder (grayed, `—`) until system ships
7. Needs — placeholder until system ships
8. Skills / Talents — placeholder until system ships
9. Location — planet, city, country
10. Relationships — summary counts only (e.g. `2 family · 3 friends`, sorted by closeness)

Each row: summary value inline. Enter → popup overlay with full detail. Backspace closes popup. Relationships Enter → opens Relationships tab in Browser.

Backspace from Profile summary: returns to origin screen (Life View / wherever player came from), not back into Menu. Navigation stack required — sub-task.

Placeholder rows visible by default; settings toggle to hide them (in Options popup).

**What does NOT live here:**
- Event history (→ Browser / History tab)
- Full relationship list (→ Browser / Relationships tab, opened via Relationships row drill)
- Pending actions (→ Actions screen)

**Future:**
- Commitments section (education, jobs)
- Physical Conditions row when that system ships
- Domain sections as systems mature

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
