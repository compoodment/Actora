# Actora


## What this repo contains

- terminal prototype code for Actora's curses-based character creation wizard and ordinary-play TUI
- stable source documents for project identity, workflow, and sequencing
- planning documents for active pressure and near-term direction
- repo-local implementation docs and changelog

## Repo structure

- `main.py` — character creation wizard, curses TUI ordinary-play shell, and current interface orchestration
- `world.py` — shared simulation state and simulation-step boundary
- `human.py` — current human actor model (11 stats, appearance, traits, sexuality)
- `events.py` — current human monthly event layer (120 events including trait-gated and family-aware)
- `identity.py` — current startup identity generation helpers
- `docs/` — source docs, planning docs, workflow docs, and repo-local documentation

## Where to start reading

1. `docs/core_architecture/master-context.txt` — durable project identity
2. `docs/workflow/operator-guide.txt` — workflow and patch discipline
3. `docs/core_architecture/actora-roadmap.txt` — dependency order and sequencing
4. `docs/core_architecture/source-index.txt` — source-system navigation and precedence
5. `docs/planning/working-ideas-register.txt` — active idea pressure
6. `docs/planning/actionable-summary.txt` — near-term planning snapshot
7. `docs/architecture.md` / `docs/changelog.md` — current repo truth and implementation history

## Doc roles (quick reference)

- **Master Context** — what Actora is (durable identity/architecture)
- **Operator Guide** — how work is done (workflow/patch discipline)
- **Roadmap** — what comes before what (dependency order)
- **Source Index** — how the doc system is organized
- **Working Ideas Register** — where active ideas live (flexible)
- **Actionable Summary** — near-term planning snapshot (flexible)
- **architecture.md** — current repo structure and behavior
- **changelog.md** — implementation history
- **live-issues.txt** — current bugs and revisit items

## Current implementation reality

The prototype is terminal-first with a curses TUI. It currently has:
- a curses character creation wizard with Identity, Location, Appearance, Creation Mode, then either Questionnaire → Confirm or Stats → Traits → Confirm
- an actor-first curses TUI with Life View, Profile, Lineage Browser, History Browser, and Skip Time screens
- 11 actor stats (3 primary + 8 secondary), appearance traits, personality traits, and sexuality emergence
- 120 human monthly events including trait-gated and family-aware events with cooldown
- an event-choice popup framework for interactive decisions during play (gender identity at puberty, sexuality in late teens)
- a world-owned simulation-step boundary with structured records, links, and place hierarchy
- focused-actor tracking with structural death, ordinary old-age mortality, and continuation handoff
- family continuity substrate with sibling generation, direct sibling links, and family-aware events
- death inspectability with life summary, two-step continuation inspection, and clean relationship labels
- consistent TUI control language (Space=select, Enter=proceed, B=back, ↑↓=navigate)

This repo is the live working Actora codebase on the VPS. Historical naming may still exist in old changelog entries or older git history where preserving history is the correct move.
