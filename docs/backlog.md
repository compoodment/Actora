---
title: Backlog
tags: [planning, tracking, wip]
updated: 2026-04-02
through: v0.45.0+
---

# Actora Backlog

Now / Next / Later. No archive. Done = deleted or changelog.

---

## Now

- **Shell experiment** — resume now that control contract is locked. Implement new contract (Q/E/WASD/Backspace/Esc) in worktree first, then merge. See controls.md for full spec.
- **Space/Enter overlap fix** — known violation in current code, fix in next UI pass
- **BACK_KEYS aliases cleanup** — `handle_actions_key` still uses legacy aliases, fix in UI pass
- **Remove legacy letter keys (L/H/T/P/A/S)** — these are deprecated. L/H open Browser, T opens Actions, P opens Profile, A/S were advance/skip. All replaced by Q/E/[1] Menu. Remove once Menu popup exists and is confirmed working.

## Next

- **Resume shell experiment** — implement chosen balanced shell direction against the locked control contract
- **main.py extraction** — identify first sane decomposition seam after shell settles (shell/browser/actions rendering is the likely first candidate)
- **Stable doc sync** — verify all docs match current implementation after shell work lands
- **Action system implementation** — narrow first-wave: social + self-improvement categories

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
- **Inventory / objects** — not yet designed. Protected future concern per roadmap (Property/Household/Inventory layer). Needs a design interview when dependencies are ready. *(2026-04-02)*
