---
title: Design
tags: [core, reference, stable]
updated: 2026-04-05
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
**Open questions:** Trait pool redesign is in progress (see Traits section). Wizard currently shows wrong trait pool and wrong count (3 instead of 4) — fix is a Now backlog item.


---

### Questionnaire
**Status:** Implemented (v0.50.0)
**Current truth:** 24-question questionnaire. Framing screen → Q1-24 → reveal screen. Outputs 4 traits from new pool. Active trait blocking for hard-block pairs. Stress baseline 0. Pick-4.

**Design (interview 2026-04-05):**
- 24 questions (up from 16)
- Variable answer count: 3 or 4 per question depending on what fits naturally — uniformity forced is worse than the right number of options
- No negative stat changes — questionnaire should not penalise personality types. Gameplay handles downsides.
- Stat baseline: all stats start at 50, Stress starts at 0 (it's a signed stat per DEC-028, not a neutral-at-50 stat)
- Memory: not seeded by questionnaire. Starts at 0, drifts through gameplay only.
- Stat changes per answer: +4 to +7 per stat, typically 1-2 stats per answer. Over 24 questions, focused play on one stat produces 74-96 range. Neutral spread produces 55-65.
- Trait blocking: active tally competition (DEC-030). Introverted↔Extraverted and Disciplined↔Impulsive compete throughout — answer for one subtracts from the other.
- Each trait must be suggestable at least 3 times across 24 questions. No trait should be unreachable.
- Neutral answers allowed — not every option needs a trait_suggest. Some options are genuine personality neutrals that still seed stats.
- Question style: mix of second-person situational ("In a room full of people...") and first-person ("When I want something..."). Forced consistency either way is wrong.
- Childhood/formative questions use observable behaviour framing — what did you DO, not what did you THINK about it. Kids don't reflect analytically.
- Tone: psychological depth without being clinical. Real personality signals, not "which Hogwarts house are you" material.
- Framing screen and reveal screen text: locked in DEC-029.
- Ethnicity: not on questionnaire — belongs on identity screen (DEC-031).

**Trait coverage (24 questions, minimum 3 each):**
Energy/pace cluster (Driven, Chill, Restless) — ~6 questions, most mechanically active (time budget).
Social style cluster (Social, Introverted, Extraverted, Empathetic) — ~7 questions, core social systems.
Structure cluster (Disciplined, Impulsive) — ~5 questions, hard-block pair.
Depth/growth cluster (Curious, Ambitious) — ~4 questions.
Toughness cluster (Resilient) — ~3 questions.

**Open questions:**
- Future: progress bar during questionnaire (logged in backlog Later)
- Should the questionnaire be re-takeable after character creation, ever? (deferred)
- How does questionnaire output interact with future ethnicity/background systems?

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
**Status:** Not started (direction set 2026-04-04)
**Current truth:** Nothing implemented.
**Intent:**
- Start with one general reputation axis. Expand to multi-axis later (trustworthiness, danger level, status, notoriety, etc.).
- Reputation is how the *world* perceives you — distinct from individual relationship closeness. Affects: who approaches you, what opportunities appear, what doors open or close.
- Crime makes some people avoid you and others seek you out.
- Presidential power, public acts, social status all feed into reputation.
- First implementation: single numeric reputation score per actor. Multi-axis is a later layer.
**Why single axis first:** Building multi-axis reputation before the systems that feed it (crime, politics, career) exist is premature. One axis gives the scaffold; axes are added as each domain system ships.
**Open questions:** Full mechanical design deferred until link/record/context foundations are mature.

---

### Actions
**Status:** In progress (foundation)
**Current truth:** Actions screen with three-column layout. Two categories: Social (Hang Out — friend picker, +5 closeness, +3 happiness, -2 stress) and Personal (Exercise, Read, Rest — each with sub-type picker popup, individual time costs and stat effects). Time budget system: 360h/month baseline, trait sleep modifiers, queue enforces budget. Actions resolve on Q (first month of advance). Sub-type picker popups for Exercise (Home Workout/Gym/Run), Read (Fiction/Non-Fiction/History/Science), Rest (Nap/Music/Walk). All stat changes route through world.apply_outcome.
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

**Time budget design (DEC-018/019):**
- Monthly free time = total hours − sleep hours (~240/month baseline) − obligatory maintenance
- Traits affect sleep hours (Restless = less sleep = more time)
- Each action and sub-action has individual time cost
- Queue rejects additions that exceed remaining free time
- Future: real books get real read times from external data

---

### Stats — Contract & Intent
**Status:** Implemented (v0.48.3, range update v0.50.1)
**Current truth:** 13 stats in code (Health, Happiness, Intelligence, Memory, Stress, Strength, Charisma, Imagination, Wisdom, Discipline, Willpower, Looks, Fertility). Happiness wired to friend death and Hang Out action (+3). Stress reduced by Hang Out (-2) and Rest actions. Exercise affects Strength/Health. Read affects Intelligence/Wisdom/Imagination/Happiness. Most stats still display-only beyond these action effects.

**Redesigned stat list (13 stats, interview 2026-04-04):**

| Stat | Affects now | Intended to affect | Age curve |
|------|------------|-------------------|-----------|
| Health | Mortality baseline | Mortality risk, energy for actions, illness chance | Declines from ~40, sharper after 70 |
| Happiness | Friend death (-8/-18) | Event eligibility, action effectiveness, depression risk | No natural age curve — driven entirely by events and circumstances |
| Intelligence | Nothing | Education performance, questionnaire outcomes, job eligibility | Stable across life |
| Memory | Nothing | Skill learning speed, job performance, event recall | Stable until ~50, declines after (accelerated by substance abuse, sleep deprivation). **Range: -50 to +50. 0 = average baseline.** |
| Stress | Hang Out (-2), Rest actions | Degrades other stats when high, action effectiveness, illness risk | No natural age curve — driven entirely by events and circumstances. **Range: -50 to +50. 0 = baseline.** |
| Strength | Nothing | Physical actions, job eligibility, certain events | Peaks 18-25, slow decline from 30, sharper after 60 |
| Charisma | Nothing | Social action effectiveness, relationship formation speed | No natural age curve — modified by social experience and lifestyle |
| Imagination | Nothing | Quality ceiling for creative output, creative skill growth rate | Peaks young/young adult, maintainable with practice |
| Wisdom | Nothing | Decision quality events, elder life outcomes, mentoring | Grows lifelong, no peak |
| Discipline | Nothing | Education/work consistency, action reliability | Driven by lifestyle |
| Willpower | Nothing | Resistance to negative forces, addiction resistance | Driven by lifestyle |
| Looks | Nothing | Social first impressions, certain relationship events | Peaks young adulthood, natural decline from 40s. Note: Looks curve is more culturally/contextually variable than physical stats — grooming, style, and confidence modify where a character lands on the curve. |
| Fertility | Nothing | Chance of conception — player has agency over this via health/lifestyle | Age-dependent, peaks 20-35 |

**Why these stats:**
- Memory added: cognitive retention is distinct from Intelligence (raw processing). Degrades via lifestyle — meaningful player choice.
- Stress added: the pressure valve. Without it, there's no mechanism for overwork/relationship/sleep debt to cascade into other effects.
- Creativity renamed Imagination: Imagination is the character's intrinsic creative capacity. What the player *does* with it (inventing, painting, writing) is their choice. High Imagination raises the quality ceiling of creative output.
- Fertility kept: gives players agency over family planning; improves via health/lifestyle actions.

**Age curve design principle:** Curves are baseline tendencies for a sedentary lifestyle. Actions and lifestyle modify where a character actually lands on the curve. A highly active Elder has better Strength than a sedentary Young Adult. Implement basic curves for Strength and Health first; full lifestyle-interaction version is a later pass.

**Stat application rule:** all stat changes must flow through `world.apply_outcome`, never scattered direct mutation.
**Open questions:** None blocking — stats wire in as each domain system is built. Event audit needed when passive events are revised.
---

### Traits
**Status:** Implemented in code (v0.48.2, DEC-022)
**Current truth:** 12 traits in code (Driven, Chill, Curious, Social, Disciplined, Impulsive, Empathetic, Resilient, Introverted, Extraverted, Restless, Ambitious), pick 4 at manual creation. TRAIT_DEFINITIONS dict with sleep_modifier per trait. Trait-gated events remapped to new pool. Questionnaire still uses old trait names and picks 3 — design interview needed before fixing.

**New trait pool (12 traits, adjective form, pick 4 at creation — interview 2026-04-04):**

| Trait | Sleep modifier | Primary mechanical effect |
|-------|---------------|--------------------------|
| Driven | -0.5h/night | More free time; actions more effective across categories |
| Chill | +0.5h/night | Less free time; stress events less severe; recovery faster |
| Curious | neutral | Study/read actions more effective; Intelligence ceiling +; faster academic skill growth |
| Social | neutral | Social actions stronger; closeness gains higher; relationship events more frequent |
| Disciplined | -0.5h/night | More free time; work/study actions more consistent; less action failure variance |
| Impulsive | neutral | Event outcomes more volatile (higher risk and reward); some actions execute faster |
| Empathetic | neutral | Relationship events richer; NPC reactions warmer; social perception gains faster |
| Resilient | neutral | Negative stat hits reduced; recovery from conditions faster; mood stabilizes quicker |
| Introverted | +0.5h/night | Solo actions more effective; social actions less effective; skill growth faster when alone |
| Extraverted | -0.5h/night | Social actions more effective; Charisma ceiling +; relationship formation faster |
| Restless | -1h/night | Most free time; short-term focus bonus but sustained tasks less consistent |
| Ambitious | neutral | Career/reputation actions more effective; social actions with higher-status actors boosted; Stress accumulates when goals unmet |

**Why these traits:**
- Adjective form chosen: "you are Driven" reads more naturally than "you have Drive." Industry standard (Dwarf Fortress, RimWorld, Sims all use adjective traits).
- Each covers a distinct personality axis: effort/pace (Driven/Chill), curiosity, social energy (Social/Introverted/Extraverted/Empathetic), structure (Disciplined), impulse (Impulsive/Restless), toughness (Resilient), goal-seeking (Ambitious).
- Driven vs Ambitious: Driven = sustained energy and effort. Ambitious = goal-seeking and status-climbing. Distinct mechanics.
- Introverted AND Extraverted both present: they're a pair. Having one without the other is incomplete.
- Pool expandable — defined as a dict, adding a new trait = one entry.

**Trait data structure (each trait must define):**
- `label`: display name
- `sleep_modifier`: hours/night adjustment (positive = more sleep = less free time, negative = less sleep = more free time)
- `stat_modifiers`: which stats get ceiling extension or growth rate bonus (e.g. Curious: Intelligence ceiling +10)
- `skill_growth_modifiers`: which skill categories grow faster (e.g. Curious: study skills +20% growth)
- `event_tags`: events that this trait makes more/less likely
- `action_effectiveness`: action categories that perform better/worse

**Trait evolution:**
- Traits drift gradually through lifestyle, not dramatic milestone moments. A Driven character who rests constantly slowly drifts toward Chill. The player notices when checking their traits over a long run.
- Major life events (trauma, transformation) can accelerate drift — layered on top of lifestyle drift, not replacing it.
- Traits are species-specific: humans get the human pool. Other species get their own pool. The trait system is Actor-level architecture, the pool is per-species content.

**Open questions:** Should traits have a visible drift indicator in Profile? Can you actively resist drift through actions?


---

### Skills & Talents
**Status:** Not started (architecture designed 2026-04-04)
**Current truth:** Nothing implemented. Skills referenced in trait modifiers but no system exists.

**Design (interview 2026-04-04):**
- Skills are practiced competencies that grow through doing. They start at 0 (or low based on life stage/context) and grow via: actions, events, relationships, and passive time in environments.
- Player-facing label: **Talents** (feels more human than "Skills"). Internal code: `skills`. Note: "Talents" serves two meanings — (1) the UI label for the whole skills section in Profile, and (2) a future sub-concept for passively/genetically inherited abilities (distinct from practiced skills).
- **Talents (inherited, future):** things absorbed passively from context — household environment, genetics, early childhood. Not practiced, inherited or absorbed. Future system — tracked with a `source` field on the skill record to distinguish from practiced skills.
- Skills discovered/unlocked through: (1) actions (reading math → Mathematics skill appears), (2) events (witness crime → Criminal knowledge), (3) relationships (friend teaches you something). Future: passive environment exposure over time.
- Trait gives both: a starting bonus to related skills AND a faster growth rate when practising. Both, not either.
- Starting skill values: age-based baseline + trait modifier. A 16-year-old has basic cooking from household context. A child of wealthy neglectful parents may have low practical skills but high exposure to wealth behaviors.
- Skill growth interacts with relevant stat: high Imagination → faster growth ceiling for creative skills. High Intelligence → faster growth for academic skills. Stat = raw capacity, Skill = what you've done with it.

**Profile display:** Talents section in Profile dashboard. Summary row shows top skills. Enter → drill into detail.
**Open questions:** Skill degradation over time if not practised? Skill prerequisites for certain actions?

---

### Needs & Drives
**Status:** Not started (architecture designed 2026-04-04)
**Current truth:** Nothing implemented. Sleep handled as time budget only.

**Design (interview 2026-04-04):**
- Needs are background simulation pressures — not meters to micromanage. The player notices when ignored, but doesn't babysit them.
- **Sleep:** Time budget only. Monthly free time = total hours − sleep hours − obligatory maintenance. Sleep hours vary by trait modifier. No sleep action, no deprivation state (for now). Never a player-managed mechanic.
- **Social contact:** If a character goes ~6 months with truly zero social interaction, Happiness begins to drain. Threshold is realistic, not inflated, because time skip runs passive social events month-by-month — isolation only accumulates if the character is genuinely isolated by circumstance. Ignoring social needs long-term → depression risk → action effectiveness reduction → health impact chain.
- **Future needs (when supporting systems exist):** Physical activity (health/stress), creative outlet (imagination/mood), purpose/meaning (happiness/wisdom). Each added when the systems they connect to are built.
- Needs do not interrupt play. They produce consequences through the event and stat system, not through forced pop-ups.

**Open questions:** Should neglected needs surface as visible warnings in Profile, or remain purely in background stat changes?

---

### Mood
**Status:** Not started (architecture designed 2026-04-04)
**Current truth:** Nothing implemented. Happiness covers long-term satisfaction but short-term emotional state has no representation.

**Design (interview 2026-04-04):**
- Mood is short-term emotional state. Distinct from Happiness (long-term life satisfaction). They interact: sustained bad mood → Happiness drain; high Happiness buffers mood drops.
- **Internal representation:** Numeric -50 to +50. 0 = neutral. Driven by events, circumstances, needs fulfillment/neglect.
- **Player-visible:** Both the number AND a contextual descriptive label. Example: "-20 · Grieving — social actions less effective." Labels carry mechanical signal, not just feeling description.
- **Label design:** Fixed set first (shippable), context-driven labels later when event system is rich enough to know why mood is low. Each label specifies: mood range it applies to, context that activates it, mechanical effect it signals.
- **Mood affects:** action effectiveness, event eligibility, NPC reactions, skill growth rate.

**Why both number and label:** Number gives the player precise feedback. Label translates it into human meaning AND communicates the gameplay consequence. Neither alone is sufficient.
**Open questions:** How many distinct mood labels? How does Stress stat interact with Mood (are they the same axis or separate)?

---

### Profile — Dashboard Design
**Status:** Implementation shipped (v0.54.0, 2026-04-07).
**Current truth:** Profile is an interactive dashboard with 10 category rows. Each row shows a summary; Enter drills into a centered popup overlay. Backspace closes popup, second Backspace returns to origin screen. Mood, Needs, Skills rows are placeholders showing "Coming soon." in popup.

**Design (interview 2026-04-07):**

#### Purpose
Full-picture screen for who your character is right now. Should feel like a genuine character sheet, not a debug dump. Everything is visible at a glance via summary rows; any row can be drilled into for detail.

#### Category rows (in order)
1. **Identity** — name, age, gender (replaces sex once gender is chosen), sexuality, life stage
2. **Appearance** — eye colour, hair colour, skin tone
3. **Stats** — primary stats (Health, Happiness, Intelligence, Money)
4. **Attributes** — secondary stats (Strength, Charisma, Imagination, Memory, Wisdom, Discipline, Willpower, Stress, Looks, Fertility)
5. **Traits** — the player's 4 traits
6. **Mood** — placeholder until Mood system ships
7. **Needs** — placeholder until Needs system ships
8. **Skills / Talents** — placeholder until Skills system ships
9. **Location** — planet, city, country
10. **Relationships** — counts at summary level; Enter opens the Relationships tab in Browser

Stats and Attributes are intentionally split: Stats are the player-facing moment-to-moment concerns; Attributes are deeper character makeup. They serve different mental models.

#### Summary row format (one line per category)
- `Identity  ·  Test User  ·  Age 0  ·  Male`
- `Stats  ·  Health 99  ·  Happiness 83  ·  Intel 53  ·  $0`
- `Attributes  ·  Str 61  Cha 58  Img 43  Mem 5  Wis 21  Dsc 46  Wil 54  Str 8  Lks 50  Fer 86` (all 10, abbreviated labels — do not show only "most important", that creates invisible tiers within secondary stats)
- `Traits  ·  Driven, Chill, Curious, Social`
- `Mood  ·  —` (placeholder)
- `Needs  ·  —` (placeholder)
- `Relationships  ·  2 family  ·  3 friends` (sorted by closeness descending)

#### Placeholder rows
Rows for unimplemented systems (Mood, Needs, Skills) appear grayed with `—` value. This makes the dashboard feel like a real destination that will grow rather than a stub. A settings option controls whether placeholder rows are shown or hidden.

#### Drill-down (Enter on any row → popup overlay)
- **Identity** — full identity fields
- **Appearance** — full appearance fields
- **Stats** — all primary stats with values and future: bar/trend context
- **Attributes** — all secondary stats with values
- **Traits** — each trait name + mechanical description (what it actually does)
- **Mood / Needs / Skills** — "Coming soon" placeholder screen
- **Location** — full location fields
- **Relationships** — opens Relationships tab in Browser directly (not a popup)

Drill popups: overlay popup sized to fit content, expandable as systems deepen. Same popup system as the rest of the game.

#### Navigation
- Enter: open drill popup for highlighted row
- Backspace: close popup → back to Profile summary. From Profile summary, Backspace goes back to wherever the player navigated from (Life View, not back into the Menu). This requires the navigation stack to track origin — not trivial, flag as a sub-task.
- ↑↓: move between category rows on summary view

#### Design rules
- This is a reusable pattern. Any future category-based screen follows summary→detail with Enter→Bsp drill.
- Implement incrementally: ship Identity/Appearance/Stats/Attributes/Traits/Location/Relationships first. Mood/Needs/Skills rows are placeholders that fill in when those systems land.
- Do not rebuild Profile all at once. Build the scaffold, then populate.
- Placeholder rows with settings toggle keeps the screen honest about future direction without lying about current state.

#### NPC type question (flagged 2026-04-07)
During the Profile interview, it became clear that family NPCs (parents, siblings) and social NPCs (met during play) likely have different capabilities — family NPCs probably don't have closeness decay or hangout mechanics. This is an unresolved architectural question: should all NPCs eventually be the same class with the same capabilities, or are there genuinely different NPC tiers? This needs its own design decision before the relationship system deepens. Flagged as design-pending, not blocking Profile implementation.

**Open questions:**
- Navigation stack / origin tracking for Backspace — confirmed: this should be a shared primitive for all Menu-reached screens (Browser, Actions, Profile), not a Profile-specific hack. NavStack sub-task required before implementation.
- NPC tier architecture — confirmed: tiered design is correct. Family NPCs have structural permanence social NPCs lack. Should look for `RelationshipClass` or `Tier` field on actor link with `KinshipLink` vs `SocialLink` as distinct types. Different decay/action logic per type. Design decision required before deepening relationship system.
- Settings toggle placement (in Options popup)
- Relationship drill: does it deep-link into the Browser Relationships tab, or open a mini-list popup that then offers to open the full Browser?
- Attributes row: show all 10 with abbreviated labels if width allows. Do not abbreviate to "most important" — that creates an invisible tier within secondary stats.

---

### Physical Conditions
**Status:** Not started (concept defined 2026-04-04)
**Current truth:** Nothing implemented. Health stat exists but no condition states.

**Design:**
- Physical Conditions are temporary states that modify what actions are available and how effective they are.
- Examples: Injured (physical actions unavailable or penalized), Sick (all action effectiveness reduced, health drains), Recovering (some actions unavailable, health gradually restoring), Exhausted (time budget reduced).
- Conditions are not permanent — they resolve over time or through rest/treatment actions.
- Conditions are distinct from the Health stat: Health is a long-term numeric measure; Conditions are short-term structural states.
- A character can have multiple conditions simultaneously (e.g. Injured + Sick).
- Conditions affect Profile display and should be visible to the player.
- This system is the bridge between the Health stat and the action/time-budget system.

**Build dependency:** Requires basic Health system and action effectiveness modifiers to be meaningful.
**Open questions:** How long do conditions last? Are they event-triggered only, or can player actions cause them? Can conditions be ignored at a cost?

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

Current TUI shell structure (v2 implemented v0.48.0, logo panel layout in progress):
- Row 0: `═══` separator (full width)
- Rows 1-4: three-panel logo row — left panel (date/actor/screen, right-aligned), center (ASCII logo), right panel (location/health/money)
- Row 5: `═══` separator (full width)
- Body rows (screen content)
- Row N-2: `═══` separator (full width)
- Row N-1: primary commands footer (centered, screen-specific)
- Logo header implemented (v0.51.0) — custom crest with box-drawing corners and shading gradient
- Prefer visible mockups/drafts before implementing meaningful shell/layout changes

---

## Open Design Questions (to resolve through future interviews)

- Where does the "persistent opportunities" section live? (open-ended opportunities that last longer than 1 month)
- How does scope-shifting work in the TUI? (actor → city → country view — when and how?)
- What does the Profile screen look like when commitments are added?
- How does the news/newspaper surface in the TUI?
- When the left panel splits (if it does), what goes where?
