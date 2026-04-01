---
title: Vision & Systems
role: creative-vision-and-system-intent
stability: moderate
layer: vision
relates_to: [master-context, ui-architecture]
---

# Actora Vision & Systems

Purpose: Persistent creative vision capture for Actora. Updated through interviews. Never thrown away — iterated.
This is the "what should this feel like and do" layer, distinct from architecture ([[master-context|Master Context]]), sequencing ([[actora-roadmap|Roadmap]]), and implementation (architecture.md/changelog).

Authority: Non-authoritative vs stable docs. When this conflicts with [[master-context|Master Context]] or [[actora-roadmap|Roadmap]], those win. When this conflicts with implementation truth, repo truth wins. But this is the primary source for creative intent per system and should be reflected in [[ui-architecture]].

---

## The Core Experience

Actora is a continuous universe simulator where you start as a person but the world never stops being real.

You are born. You live. You die. The universe continues.
Your great-great-grandchild might board a spacecraft in 2340 inside the same save.
Everything that happened before is still real, still recorded, still part of the same simulation.

It is not BitLife. It is not a detached god sim. It is not a spreadsheet with humans taped on.
It is actor-anchored, zoomable, continuous, and simulation-real.

The player primarily lives through their current actor, but that actor exists inside a larger world that doesn't pause for them.

---

## What Makes It Different

- **Continuity across lives** — one save, one universe, one advancing timeline. Your lineage matters. What your ancestors did is real history.
- **Scale** — from being born in Amsterdam in 2025 to commanding a warship in 2340 in the same save, same universe.
- **Consequences** — actions have real ripple effects. Go into crime and you attract a different kind of person. Become president and you can change the world or destroy it.
- **Systems that are real** — economy, politics, social perception, organizations — not flavor text, not fake numbers. Real interacting systems.
- **Era-awareness** — different eras have different rules, different technologies, different possibilities. Future eras have space travel. Past eras don't have smartphones. These are real constraints, not cosmetic.

---

## Systems — Vision Per System

### Character Creation & Identity

Character creation should feel like you are genuinely shaping who this person is — not filling out a form.

- **Ethnicity** — player picks their ethnicity (single or mixed). This informs parent ethnicity: parents could be mixed themselves, or they could be the source of the mix. Ethnicity affects name generation, cultural context, and appearance seeding.
- **Trait and stat inheritance** — the traits and stats the player picks (or the questionnaire derives) should feel like a believable blend of both parents' characteristics. Not purely random — a reflection of where you came from.
- **Sibling similarity** — siblings share family resemblance in traits and appearance but with natural variation. Sometimes very similar, sometimes noticeably different. Both are realistic.
- **Parents feel real** — parents should have their own consistent appearance, traits, and personality that the player can recognise and see reflected in their character.
- Later: parent backstory depth, grandparent lineage, family history context.
- Depends on: IDEA-091 (identity generation realism), culture-aware name generation (v0.40.0 foundation).

### Social Relationships- Closeness is numeric (0–100), tiered as acquaintance / friend / close friend
- All introduced NPCs are real full actors in the world
- Relationships form through player-initiated events — you choose who to engage with
- Closeness grows through shared time/events, decays when neglected
- Long-standing relationships decay slower — 10 years of friendship survives a quiet year
- **Proximity provides passive closeness maintenance** — living in the same city as a friend slows or offsets decay naturally. Moving away accelerates it. This reflects real life.
- Decay tuning: current implementation is too aggressive (forces hang out every ~3 months). Should feel sustainable without constant micro-management.
- Friend deaths affect you — stat impact scaled to closeness
- Social actions (hang out, call, etc.) are player-initiated and resolve on advance
- Later: invite friends to activities, friends can decline based on context
- Later: rivals, negative relationship types, romance
- Later: NPC-initiated relationship events (someone reaches out to you)
- **NPC identity rule:** Gender and sexuality for non-played actors must auto-resolve silently at the appropriate age — no popup. Popups are only for the currently focused/played actor. Any future popup system must follow this rule: player = popup, NPC = silent auto-resolve.

### Social Perception & Reputation
- Multi-axis, not a single karma score
- Different axes: trustworthiness, danger level, status, charisma, notoriety, etc.
- How people perceive you affects what opportunities appear, who approaches you, what's available
- Crime makes certain people avoid you and others seek you out
- Presidential power changes how the entire world perceives you
- Deferred until actor/link/context foundations are mature

### Actions
- Two types: instant (happens now, no queue) and monthly (queued, resolves on advance)
- Categorized: social, personal development, career, criminal, political, etc.
- **Action visibility:** Age/era/context gates → silently hidden. Resource/prerequisite gates (no money, missing item, etc.) → shown as unavailable with reason. Rule: if you can never do it right now regardless of effort, hide it. If you could do it but currently can't, show it greyed.
- **Action time budget:** Actions have a time cost. Free actions (texting a friend, quick errand) consume negligible time. Medium actions consume part of the month. Heavy commitments (job contract, military service, long voyage, expedition) consume most or all of the month's available time. The constraint on how many actions you can do in a month is emergent from time cost allocation, not an arbitrary cap.
- **Multi-month actions are era-agnostic** — a sailing voyage in 1600, a research expedition in 2010, a space mission in 2300. Same mechanic, different context. Time-based commitment applies to any era where the scenario warrants it.
- No forced constraints — player can queue freely, but time budget is real. Overcommitting means something gives.
- Dynamic — what's available depends on age, location, relationships, commitments, era
- Long commitments (education, job) live in Profile as "commitments", not in the action queue
- Urgent surprise opportunities are popups (1-month window). Open-ended opportunities have their own persistent section (TBD location)
- Social actions can optionally bring friends who may decline based on context
- Later: spiral side-quest chains — forced sequences of decisions with branching outcomes

### Stats — Contract & Intent

Stats are 0–100 values. They should affect real simulation outcomes — not just be numbers on a profile screen. This table tracks what each stat currently does vs what it's intended to do. Update this when a new system wires into a stat.

**Rule:** every stat should have at least one real effect before being considered complete. When building a new system, check this table and wire into relevant stats deliberately.

| Stat | Currently affects | Intended to affect |
|------|------------------|--------------------|
| Health | Nothing yet (displayed only) | Mortality risk, energy for actions, illness chance |
| Happiness | Friend death impact (-8/-18) | Event eligibility, action effectiveness, mental health events |
| Intelligence | Nothing yet | Education performance, questionnaire outcomes, job eligibility |
| Strength | Nothing yet | Physical actions, certain job eligibility |
| Charisma | Nothing yet | Social actions effectiveness, relationship formation speed |
| Creativity | Nothing yet | Certain career paths, event outcomes |
| Wisdom | Nothing yet | Decision quality events, elder life outcomes |
| Discipline | Nothing yet | Education performance, work consistency |
| Willpower | Nothing yet | Overcoming negative events, addiction resistance |
| Looks | Nothing yet | Social first impressions, certain relationship events |
| Fertility | Nothing yet | Chance of having children |

**Current reality:** Most stats are decoration. That's acceptable while the systems that consume them don't exist. But as each domain system is built, the relevant stats must be wired in — not left inert.

**Stat application rule:** stat changes should flow through the controlled mutation boundary (world.apply_outcome) not be scattered across files. This is already the architectural direction (master-context section 18).

### Education
- First mid-stage domain layer after relationships
- School as a real place with real NPC teachers and peers
- Different countries = different school systems
- Gives the actor something to DO during childhood/teen years
- Unlocks real peer/friend event content
- Long commitment — lives in Profile, not action queue
- Later: grades, performance, subject specialization, dropout mechanic

### Work & Career
- Jobs as real role-based commitments
- Income, work-state, career progression
- Domain actions via Profile: view current job, take job actions from there
- Boss/coworker NPCs are real actors (more thoroughly simulated despite potentially low closeness — context threshold)
- Later: starting companies, hiring, company trade with other companies in the right field
- When you own a company you can trade with others in the relevant field
- When you're a professor you can apply to schools
- Requires: education foundation, actor-state stability

### Economy
- Real future pillar — not fake spreadsheet theater
- Firms, organizations, markets, investment structures
- Company ownership enables trade relationships with other companies
- Economy affects what jobs exist, what opportunities appear, what things cost
- Macro conditions are real — countries can be in recession, boom, war economy
- Requires: work/role foundation, links, records, place, state-mutation foundations

### Politics & Power
- Real future pillar
- Becoming president / leader is a real possibility
- Presidential actions: wage war, make peace, change economies, issue policy
- Elections, coups, political parties as real structures
- Power has real consequences — world events, NPC reactions, history records
- Requires: country/political layer, economy, social perception

### Crime & Consequence
- Criminal actions are a real category in the action system
- Crime changes your social perception — some people avoid you, others seek you
- Law enforcement, legal status as real systems
- Criminal networks as real organizations with real actor NPCs
- Consequences persist — your criminal history is real history

### News & Information
- Local newspapers and global newspapers (and future equivalents in futuristic eras)
- Content: country went to war, coup happened, tsunami killed 4000 people, presidential actions, company moves
- Makes the world feel alive and larger than your actor's immediate life
- Future equivalents in futuristic eras have different names/forms
- Requires: political layer, economic layer, event system maturity

### Health & Conditions
- Health as a real system, not just a stat
- Illness, injury, recovery as structured events
- Affects what actions are available, what opportunities exist
- Requires: lifecycle/event/link/state foundations

### Property & Household
- Owned places separate from where you live, which is separate from where you are
- Household depth: who lives with you, dependencies, costs
- Inventory and item ownership as real structures
- Requires: structured place, spatial identity separation

### Travel & Movement
- Moving between cities, countries, world bodies
- Not assumed to be terrestrial or local long-term
- Future eras: space travel, interplanetary movement
- Travel affects relationship decay, opportunity availability, cultural context
- Requires: structured places, spatial identity separation

### Space & Galactic Layers
- Future eras have space travel as a real available system
- Vessels, stations as non-fixed place types
- Star systems, solar systems as real place hierarchy layers
- Galaxy-level play as the eventual ceiling
- Your sister's fantasy planet: a real world body in a pre-BC era within the same universe save
- Requires: all lower spatial layers proven first

### Eras & Timeline
- Different eras have different rules, technologies, possibilities
- Modern era is the first. Near-future follows. Futuristic eras beyond that.
- Era affects: what actions exist, what species exist, what places exist, what news looks like
- Characters are era-restricted — a medieval peasant can't use a smartphone
- Compverse = the concept of universe saves; one save = one continuous universe with one advancing timeline

---

## UI Vision (TUI Phase)
See [[ui-architecture]] for the full screen map, navigation hierarchy, and rules for adding new systems.

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
