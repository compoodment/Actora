# Actora


## What this repo contains

- terminal prototype code for Actora's current plain-text startup flow plus curses TUI ordinary-play surface
- stable source documents for project identity, workflow, and sequencing
- planning documents for active pressure and near-term direction
- repo-local implementation docs and changelog

## Repo structure

- `main.py` — plain-text startup flow, curses TUI ordinary-play shell, and current interface orchestration
- `world.py` — shared simulation state and simulation-step boundary
- `human.py` — current human actor model
- `events.py` — current human monthly event layer
- `identity.py` — current startup identity generation helpers
- `banners.py` — non-curses startup / exit banner text
- `docs/` — source docs, planning docs, workflow docs, and repo-local documentation

## Where to start reading

1. `docs/core_architecture/master-context.txt` — durable project identity
2. `docs/workflow/operator-guide.txt` — workflow and patch discipline
3. `docs/core_architecture/actora-roadmap.txt` — dependency order and sequencing
4. `docs/core_architecture/source-index.txt` — source-system navigation and precedence
5. `docs/planning/working-ideas-register.txt` — active idea pressure
6. `docs/planning/actionable-summary.txt` — near-term planning snapshot
7. `docs/architecture.md` / `docs/changelog.md` — current repo truth and implementation history

## Current implementation reality

The current prototype is still terminal-first and still structurally narrow, but the repo now splits interface responsibility more explicitly into plain-text startup plus a curses TUI for ordinary play, lineage browsing, skip-time flow, and continuity/death navigation. It currently has:
- a world-owned simulation-step boundary
- structured records, links, and places, plus a small startup place hierarchy
- focused-actor tracking and structural death / continuity foundation
- plain-text character creation followed by actor-first curses ordinary play
- structured lineage/archive browsing inside the TUI
- cleaner death/continuation reveal flow and clearer age-vs-simulation-date snapshot presentation
- expanded human character-creation options for sex and gender
- current human-only event content

This repo is the live working Actora codebase on the VPS. Historical naming may still exist in old changelog entries or older git history where preserving history is the correct move.
