# Actora

A continuous universe life simulation. Actor-anchored, zoomable, foundation-first.

## What is Actora?

You are born. You live. You die. The universe continues. Your great-great-grandchild might board a spacecraft in 2340 — in the same save.

Actora is not BitLife. It's not a detached god sim. It's one continuous simulation where you live through an actor inside a larger world that doesn't stop being real just because you're focused on one life.

## Current state

Terminal prototype with a curses TUI. Currently has:
- Character creation (identity, location, appearance, traits, stats — manual or questionnaire)
- Life View with identity/stats/relationships and accumulating event feed
- Non-family relationships (acquaintance/friend/close friend) with closeness, decay, and drift
- Tabbed Browser (Relationships + History)
- Actions screen with social actions
- 120 lifecycle events including trait-gated and family-aware
- Death, continuation through connected actors, and lineage
- 12 countries, 39 cities, culture-aware name generation (400+ names)

## Repo structure

```
main.py          — TUI, creation wizard, shell, rendering (3857 lines)
world.py         — simulation state, links, places, records, social, mortality (2090 lines)
human.py         — actor model, lifecycle, spatial, snapshot (289 lines)
events.py        — monthly events, meeting events (388 lines)
identity.py      — name pools, culture-aware identity generation (299 lines)
docs/            — project documentation (flat, 13 docs)
```

## Documentation

All docs live flat in `docs/`. Start with `docs/guide.md` — it tells you where everything else is.

| Doc | What it is |
|-----|-----------|
| `guide.md` | Navigation, workflows, routing — the one doc |
| `identity.md` | What Actora is |
| `roadmap.md` | Dependency order |
| `design.md` | Creative intent per system |
| `screens.md` | Screen map, navigation |
| `controls.md` | Hotkeys, interaction rules |
| `codebase.md` | Current implementation truth |
| `changelog.md` | Version history |
| `backlog.md` | What we're working on |
| `bugs.md` | Known bugs |
| `decisions.md` | Major structural decisions |
| `rules.md` | Project constraints |
