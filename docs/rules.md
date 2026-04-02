---
title: Rules
tags: [core, reference, stable]
updated: 2026-04-02
---

# Actora Rules

All project constraints in one place. If it says "don't" or "must", it lives here.

---

## Code rules

1. Simulation core stays UI-agnostic — only `main.py` knows about curses
2. State mutation flows through controlled world-owned methods, not direct field pokes
3. Don't hard-bake human-only assumptions into architecture that should be species-general later
4. Preserve validated behavior unless the patch explicitly replaces it
5. Don't silently weaken input validation, output ordering, error handling, or structured result contracts
6. Don't bypass the link layer with random actor-owned relationship fields

## Design rules

1. Player-facing text must read like a game, not like a dev tool or database
2. No internal jargon in rendered UI: no "actor", "entity", "structural_status", "bootstrap", "continuation target"
3. No hidden keybinds outside scoped text-input/search contexts
4. Foundation-first: current work should not hard-bake assumptions that contradict the approved baseline
5. Actor-anchored, continuous universe, zoomable scope — this is the project identity
6. Fix small UI inconsistencies early before they become accepted invisible bugs
7. Event depth should come from real systems, not disconnected flavor-text accumulation

## Doc rules

1. Every piece of information has exactly ONE canonical home — no copies across docs
2. Done stuff leaves active docs immediately → changelog or delete
3. No new docs without adding them to `guide.md`
4. Every doc has a `updated:` date in frontmatter — if it's wrong, the doc is suspect
5. `guide.md` hard cap: 150 lines of content (excluding frontmatter)
6. Decisions in `decisions.md` are immutable-append — never edit, only supersede
7. Backlog staleness: Now items untouched for 7 days get flagged; Later items older than 30 days without reference get reviewed for deletion
8. `codebase.md` sync required on every version tag — if version doesn't match latest tag, it's stale
9. Cross-doc health check every ~3 version tags: currency, contradictions, duplication, backlog cleanliness
10. Tags follow the fixed taxonomy in `guide.md` — no inventing new tags without updating the taxonomy

## Patch rules

1. Spec before apply for anything non-trivial
2. Verify on VPS — `python3 -c "import main"` minimum, tmux playtest for TUI changes
3. Don't silently broaden scope — a patch does the approved job and no more
4. Review before acceptance — worker output must be checked, not blindly trusted
5. If a good idea appears mid-patch that doesn't belong in the current scope, route it to `backlog.md`

## Naming rules

1. Don't let temporary implementation naming harden into permanent architecture truth
2. `Location` is the right player-facing abstraction, not city-specific wording
3. Use "you" or the character's name in player text, never "actor" or "focused actor"
4. Use "family" not "connected actors" or "linked actors"

## Anti-drift rules

1. After every meaningful change: sync docs + memory immediately — don't batch it to later
2. Before starting any task: targeted memory_search + read only the relevant files
3. After compaction: re-read memory/daily + MEMORY.md + guide.md only; don't bulk-read source files unless needed
4. Before any config edit: create a backup first
5. For meaningful repo/file edits: create a local pre-edit backup in `.backups/`
