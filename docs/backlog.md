---
title: Backlog
tags: [planning, tracking, wip]
updated: 2026-04-05
through: v0.49.0
---

# Actora Backlog

Now / Next / Later. No archive. Done = deleted or changelog.

---

## Now

- **Profile dashboard redesign** — implement summary row per category (Stats/Traits/Skills/Needs/Mood), Enter→drill detail pattern. Reusable component for future category screens. Build incrementally as systems land.



## Next

- **Logo redesign** — replace placeholder "actora" script ASCII with a proper custom logo design. Layout already built and waiting for it.

- **main.py extraction** — identify first sane decomposition seam after shell settles (shell/browser/actions rendering is the likely first candidate). During this pass: flatten `secondary_statistics` into one `statistics` dict with all 13 stats — snapshot should not encode rendering decisions; let the renderer decide what to show where.

## Later

- **Education foundation** — first mid-stage domain layer per roadmap, depends on action system *(2026-03-31)*
- **Actor skills (Skills/Talents system)** — system architecture designed (DEC-023, design.md Skills & Talents). Implementation: TRAIT_DEFINITIONS skill_growth_modifiers wiring, skill discovery mechanics, Profile Talents section. Depends on action system. *(2026-04-01, updated 2026-04-04)*
- **Actor personalities (NPC behavior layer)** — NPC decision-making layer distinct from player-facing traits. Influences NPC action preference, response patterns, relationship behavior. Note: player Trait evolution (DEC-022) covers the player side; this is specifically for NPC simulation depth. *(2026-04-01)*
- **Ethnicity + trait inheritance + sibling similarity** — parked until identity generation is mature *(2026-03-31)*
- **Multi-axis social perception / reputation** — single reputation axis ships first (DEC-027), multi-axis expands as domain systems (crime, career, politics) land. Depends on stronger social foundations. *(2026-03-27, updated 2026-04-04)*
- **Professional doc structure upgrade** — remaining ADR patterns, review checklists beyond what's already done *(2026-04-02)*
- **Contabo Firewall** — optional second security layer on top of existing UFW host firewall *(2026-04-01)*
- **NPC identity auto-resolve** — gender/sexuality must silently resolve for non-played actors at age threshold *(2026-04-01)*
- **Closeness decay tuning** — current decay may be too aggressive; add proximity-based passive maintenance *(2026-04-01)*
- **Batch social action** — "Spend time with friends/family" covering a group at once *(2026-04-01)*
- **Death screen record filtering** — show only important/marked records, not random events *(2026-04-01)*
- **"New Life: X" feed phrasing** — needs better wording or removal *(2026-04-01)*
- **Gradual sexuality signal events** — 3-5 small events building toward suggestion instead of single choice *(2026-03-31)*
- **Culture/location-driven identity context** for gender/sexuality emergence *(2026-03-31)*
- **Gender/sexuality changeable through Profile** triggering life event *(2026-03-31)*
- **"Other" sexuality** integration with future romance events *(2026-03-31)*
- **Sibling/family birth probability tuning** — current heuristic is intentionally simple first-pass *(2026-03-31)*
- **Name pool deepening** — regional variation, ethnic/religious diversity, era awareness, family naming conventions *(2026-03-31)*
- **History tab filtering by actor** — currently shows full universe history across all actors. Should probably filter to records relevant to the currently focused actor, starting from when you took over. Needs a design interview — does the Browser become actor-scoped, or do we add a toggle? *(2026-04-02)*
- **Simulation depth per actor** — high-detail simulation for all tracked actors every turn is a performance concern at scale. Revisit when actor count grows. Connects to the layered simulation depth principle in identity.md. *(2026-04-02)*
- **Cancel / reorder queued actions** — Actions screen currently shows queued actions as display-only. Future: allow cancelling or reordering. *(2026-04-04)*
- **Heartbeat routing split** — optionally split Actora-specific heartbeat beats from general infra/memory hygiene beats. Could use a separate cron for infra checks. Low priority. *(2026-04-04)*
- **Skip time limit** — cap normal human skip at ~10 years. Contextual extension for passive commitments (jail, coma). Passive simulation still runs during skip. Currently unlimited for development. *(2026-04-04)*
- **Context-driven mood labels** — current design is fixed label set. Future: labels driven by context (why mood is low matters — "Grieving" vs "Burnout" at same numeric value). Add when event system is rich enough to supply context. *(2026-04-04)*
- **Physical Conditions system** — temporary states (Injured, Sick, Recovering, Exhausted) that modify action availability and effectiveness. Bridges Health stat and action system. *(2026-04-04)*
- **Event audit** — all existing passive events were auto-generated and never reviewed. Need pass to: verify stat effects, balance passive simulation outcomes for characters who never interact, ensure "ghost player" life quality is realistic. Do before action system is considered complete. *(2026-04-04)*
- **Inventory / objects** — not yet designed. Protected future concern per roadmap (Property/Household/Inventory layer). Needs a design interview when dependencies are ready. *(2026-04-02)*
