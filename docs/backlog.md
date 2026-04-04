---
title: Backlog
tags: [planning, tracking, wip]
updated: 2026-04-04
through: v0.48.1
---

# Actora Backlog

Now / Next / Later. No archive. Done = deleted or changelog.

---

## Now

- **Trait pool redesign** — current pool (Fussy, Restless, Alert, etc.) was AI-generated. Redesign with meaningful real personality words that have actual gameplay effects. Do before action system ships.
- **Action system first wave** — time-budget model (monthly free hours), sub-type selections per action (exercise type, book subject, rest type), individual time costs per sub-action. Social: Hang Out resolves with +5 closeness. Personal: Exercise, Read, Rest with sub-types. Do before Education.
- **Action time budget** — derive monthly free hours from sleep baseline (240hr/month) minus maintenance. Restless trait modifier. Wire to action queue so you can't queue more than fits.



## Next

- **Logo redesign** — replace placeholder "actora" script ASCII with a proper custom logo design. Layout already built and waiting for it.

- **main.py extraction** — identify first sane decomposition seam after shell settles (shell/browser/actions rendering is the likely first candidate)
- **Action system implementation** — narrow first-wave: social + self-improvement categories (foundation screen now exists)

## Later

- **Education foundation** — first mid-stage domain layer per roadmap, depends on action system *(2026-03-31)*
- **Actor skills** — learned capabilities / proficiencies distinct from stats/traits. Actions and later systems depend on this. *(2026-04-01)*
- **Actor personalities** — structural NPC behavior layer distinct from traits. Influences action preference, NPC response, relationship behavior, event choice weighting. *(2026-04-01)*
- **Ethnicity + trait inheritance + sibling similarity** — parked until identity generation is mature *(2026-03-31)*
- **Multi-axis social perception / reputation** — depends on stronger social foundations *(2026-03-27)*
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
- **Inventory / objects** — not yet designed. Protected future concern per roadmap (Property/Household/Inventory layer). Needs a design interview when dependencies are ready. *(2026-04-02)*
