---
title: Design
tags: [core, reference, stable]
updated: 2026-04-02
---

# Actora Design

Creative intent per system. Updated through interviews. Never thrown away — iterated.

For project identity, see `identity.md`. For sequencing, see `roadmap.md`. For implementation truth, see `codebase.md`.

---

## Systems — Vision Per System

Each system uses this format:
- **Status:** not started / in progress / implemented / evolving
- **Current truth:** what actually exists in code right now
- **Intent:** what it should feel like and do
- **Open questions:** unresolved design decisions

---

### Character Creation & Identity
**Status:** Implemented (evolving)
**Current truth:** Identity, Location, Appearance, Mode, Stats/Questionnaire, Traits, Confirm steps. Manual stat sliders or 16-question questionnaire. Culture-aware names. No ethnicity field yet.
**Intent:** Should feel like genuinely shaping who this person is — not filling out a form. The result should feel like a believable blend of both parents' characteristics, not random.
- Ethnicity — player picks (single or mixed). Informs parent ethnicity, name generation, cultural context, appearance seeding.
- Trait and stat inheritance — the questionnaire/manual choices should reflect where you came from.
- Siblings share family resemblance with natural variation.
- Parents feel real — consistent appearance, traits, personality visible in your character.
- Later: parent backstory depth, grandparent lineage, family history context.
**Open questions:** None currently blocking.

---

### Social Relationships
**Status:** Implemented (evolving)
**Current truth:** Acquaintance/friend/close_friend with numeric closeness (0–100). Player-initiated meeting via popup. Closeness decay per month with history-based resistance. Drift events + former link status (`Past`). Friend death stat impact. Relationship Browser with filter sidebar. "Spend time with friend" action queues and resolves on advance. Social links shown in Life View left panel.
**Intent:**
- Relationships should not feel purely manual — some baseline upkeep should happen through system logic without constant micromanagement.
- Decay tuning: current implementation is too aggressive. Should feel sustainable.
- Proximity provides passive closeness maintenance — living in the same city slows decay.
- Active social actions matter for stronger gains, targeted attention, batch upkeep, and social-focused playstyles.
- All introduced NPCs are real full actors in the world.
- Friend deaths affect you — scaled to closeness.
- Later: invite friends to activities, friends can decline based on context, rivals, negative relationship types, romance, NPC-initiated relationship events.
- **NPC identity rule:** gender and sexuality for non-played actors must auto-resolve silently — no popup. Player = popup, NPC = silent.
**Open questions:** Passive upkeep threshold/proximity mechanic not yet designed in detail.

---

### Social Perception & Reputation
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- Multi-axis, not a single karma score.
- Axes: trustworthiness, danger level, status, charisma, notoriety, etc.
- How people perceive you affects opportunities, who approaches you, what's available.
- Crime makes some people avoid you and others seek you out.
- Presidential power changes how the world perceives you.
**Open questions:** Full design deferred until actor/link/context foundations are mature.

---

### Actions
**Status:** In progress (foundation only)
**Current truth:** Actions screen exists with "Spend time with friend" social action. Categories/Actions/Details three-column layout in worktree experiment. Action queues and resolves on Q (next advance). No categories, no self-improvement actions yet.
**Intent:**
- Two time-shape types: immediate/negligible and month-consuming. Long-running states (education, job, travel) are commitments, not queue items.
- Categorized: social, personal development, career, criminal, political, etc.
- Actor skills are a likely later seam — learned capabilities distinct from stats/traits.
- The Actions surface is the main actor-action hub but not the only forever entry point.
- Action visibility: broadly visible by default, hidden only if fundamentally inapplicable (life stage, era, location).
- Time budget: flexible. Ordinary life functions at baseline without micromanagement; explicit actions provide focus, leverage, stronger effects.
- Multi-month actions are era-agnostic — sailing voyage 1600, research expedition 2010, space mission 2300.
- Urgent opportunities are popups (1-month window). Open-ended opportunities have a persistent section (TBD).
- Later: spiral side-quest chains.
**Open questions:** Where do persistent open-ended opportunities live? Detail pane interaction if it becomes interactive?

---

### Stats — Contract & Intent
**Status:** Partially implemented
**Current truth:** 11 stats displayed (3 primary + 8 secondary). Happiness wired to friend death. Everything else is decoration for now.
**Intent:** Stats should affect real simulation outcomes. Every stat should have at least one real effect before being considered complete. When building a new system, check this table and wire into relevant stats deliberately.

| Stat | Currently affects | Intended to affect |
|------|------------------|--------------------|
| Health | Nothing (displayed only) | Mortality risk, energy for actions, illness chance |
| Happiness | Friend death (-8/-18) | Event eligibility, action effectiveness, mental health events |
| Intelligence | Nothing | Education performance, questionnaire outcomes, job eligibility |
| Strength | Nothing | Physical actions, certain job eligibility |
| Charisma | Nothing | Social actions effectiveness, relationship formation speed |
| Creativity | Nothing | Certain career paths, event outcomes |
| Wisdom | Nothing | Decision quality events, elder life outcomes |
| Discipline | Nothing | Education performance, work consistency |
| Willpower | Nothing | Overcoming negative events, addiction resistance |
| Looks | Nothing | Social first impressions, certain relationship events |
| Fertility | Nothing | Chance of having children |

**Stat application rule:** stat changes must flow through `world.apply_outcome`, not scattered direct mutation.
**Open questions:** None blocking — stats wire in as each domain system is built.

---

### Education
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- First mid-stage domain layer after relationships.
- School as a real place with real NPC teachers and peers.
- Different countries = different school systems.
- Gives the actor something to DO during childhood/teen years.
- Unlocks real peer/friend event content.
- Long commitment — lives in Profile, not action queue.
- Later: grades, performance, subject specialization, dropout mechanic.
**Open questions:** Depends on action system foundation.

---

### Work & Career
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- Jobs as real role-based commitments. Income, career progression.
- Boss/coworker NPCs are real actors.
- Domain actions via Profile.
- Later: starting companies, hiring, company trade in relevant fields. When you own a company you can trade with others. When you're a professor you can apply to schools.
**Open questions:** Requires education foundation and actor-state stability.

---

### Economy
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- Real future pillar — not fake spreadsheet theater.
- Firms, organizations, markets, investment structures.
- Economy affects what jobs exist, what opportunities appear, what things cost.
- Macro conditions are real — recession, boom, war economy.
**Open questions:** Requires work/role, links, records, place, state-mutation foundations.

---

### Politics & Power
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- Becoming president/leader is a real possibility.
- Presidential actions: wage war, make peace, change economies, issue policy.
- Elections, coups, political parties as real structures.
- Power has real consequences — world events, NPC reactions, history records.
**Open questions:** Requires country/political layer, economy, social perception.

---

### Crime & Consequence
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- Criminal actions are a real category in the action system.
- Crime changes your social perception — some people avoid you, others seek you.
- Law enforcement, legal status as real systems.
- Criminal networks as real organizations with real actor NPCs.
- Consequences persist — your criminal history is real history.
**Open questions:** Depends on social perception and action system.

---

### News & Information
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- Local and global newspapers (and era-appropriate equivalents).
- Content: wars, coups, disasters, presidential actions, company moves.
- Makes the world feel alive and larger than your actor's immediate life.
**Open questions:** Requires political layer, economic layer, event system maturity.

---

### Health & Conditions
**Status:** Not started (Health stat exists but is decoration)
**Current truth:** Health stat displayed but affects nothing yet.
**Intent:**
- Health as a real system — illness, injury, recovery as structured events.
- Affects what actions are available, what opportunities exist.
**Open questions:** Requires lifecycle/event/link/state foundations.

---

### Property & Household
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- Owned places separate from where you live, which is separate from where you are.
- Household depth: who lives with you, dependencies, costs.
- Inventory and item ownership as real structures.
**Open questions:** Requires structured place, spatial identity separation.

---

### Travel & Movement
**Status:** Not started
**Current truth:** Location exists in actor model (city/country) but is static — no movement system.
**Intent:**
- Moving between cities, countries, world bodies.
- Not assumed terrestrial long-term.
- Travel affects relationship decay, opportunity availability, cultural context.
**Open questions:** Requires structured places, spatial identity separation.

---

### Space & Galactic Layers
**Status:** Not started
**Current truth:** Nothing implemented.
**Intent:**
- Future eras have space travel as a real available system.
- Vessels, stations as non-fixed place types.
- Star systems, solar systems as real place hierarchy layers.
- Galaxy-level play as the eventual ceiling.
**Open questions:** Requires all lower spatial layers proven first.

---

### Eras & Timeline
**Status:** Not started
**Current truth:** Modern era only. No era awareness in events or systems.
**Intent:**
- Different eras have different rules, technologies, possibilities.
- Modern era first. Near-future follows. Futuristic eras beyond that.
- Era affects: what actions exist, what species exist, what places exist, what news looks like.
- Characters are era-restricted — a medieval peasant can't use a smartphone.
- Compverse = one save = one continuous universe with one advancing timeline.

---

## UI Vision (TUI Phase)
See [[screens]] for the full screen map, navigation hierarchy, and rules for adding new systems.

Current priority: get the TUI working well before thinking about visual UI.

The terminal is a temporary shell — the simulation core must remain UI-agnostic. Future presentation forms (panel UI, map views, mixed micro-to-macro) should be possible without core rewrites.

Current TUI shell direction:
- favor a compact stacked shell header for major in-game screens rather than a single overloaded command bar
- keep shell identity visible (Actora, actor, screen, simulation progression)
- keep compact actor/world state visible near the top (location/date context, health, money)
- use centered, menu-like primary commands and show lower control hints only when relevant to the current surface
- prefer visible mockups/drafts before implementing meaningful shell/layout changes so visual flaws are caught before patching the real UI

---

## Open Design Questions (to resolve through future interviews)

- Where does the "persistent opportunities" section live? (open-ended opportunities that last longer than 1 month)
- How does scope-shifting work in the TUI? (actor → city → country view — when and how?)
- What does the Profile screen look like when commitments are added?
- How does the news/newspaper surface in the TUI?
- When the left panel splits (if it does), what goes where?
