---
title: Guide
tags: [core, workflow, reference]
updated: 2026-04-04
---

# Actora Guide

The one doc. Navigation, workflows, reading order, routing.

---

## After context loss (compaction / reset / new session)

1. `memory/YYYY-MM-DD.md` (today + yesterday)
2. `MEMORY.md` (workspace, durable rules)
3. This file — doc map, workflows, routing
4. `rules.md` — constraints to not break things
5. `backlog.md` → Now section — what we're actively doing

That gets you oriented. Only read other docs when the task requires them.

---

## Doc map

| Doc | What it is | When to read |
|-----|-----------|--------------|
| `guide.md` | This file. Navigation, workflows, routing | Every session start |
| `identity.md` | What Actora is. Project identity anchor | Architecture questions, grounding |
| `roadmap.md` | Dependency order. What before what | Sequencing, "should we build X now?" |
| `design.md` | Creative intent per system | Before designing or implementing a system |
| `screens.md` | Screen map, navigation hierarchy | UI structure, "where does X live?" |
| `controls.md` | Hotkeys, interaction rules, control contract | Before any TUI/shell work |
| `codebase.md` | Current repo implementation truth | Before coding, dispatching workers |
| `changelog.md` | Version history | "What changed?" |
| `backlog.md` | Now / Next / Later | "What are we working on?" |
| `bugs.md` | Actual bugs only | Before playtesting, during fixes |
| `decisions.md` | Major structural decisions log (immutable) | "Why did we decide X?" |
| `rules.md` | All project constraints | Before any work that touches code, docs, or design |

**Bug severity:** 🔴 Blocking (can't playtest) · 🟡 Annoying (noticeable but playable) · ⚪ Minor (cosmetic/edge)

---

## Where does this go?

| What happened | Put it in |
|---------------|-----------|
| Bug found | `bugs.md` |
| Bug fixed | Delete from `bugs.md`, mention in `changelog.md` |
| New idea / future feature | `backlog.md` → Later |
| Idea becomes active work | `backlog.md` → Now |
| Active work finished | Delete from `backlog.md`, add to `changelog.md` |
| Major structural decision made | `decisions.md` |
| Interview produced design intent (systems, stats, traits, skills, mechanics) | `design.md` |
| Interview produced screen/layout truth | `screens.md` |
| Interview produced hotkey/control truth | `controls.md` — update immediately, it is the only canonical home for hotkey decisions |
| New project rule / constraint | `rules.md` |
| Workflow changed | `guide.md` |
| Code structure changed meaningfully | `codebase.md` |
| Version milestone tagged | `changelog.md` |
| Durable project identity changed | `identity.md` |
| Dependency order changed | `roadmap.md` |

---

## Don't

- Don't leave finished work in `backlog.md`
- Don't put bugs in `backlog.md`
- Don't put design decisions in `bugs.md`
- Don't put workflow rules in `rules.md` (rules = constraints, guide = process)
- Don't put process in `rules.md` (guide = process, rules = constraints)
- Don't duplicate content across docs — every fact has ONE canonical home
- Don't create new docs without adding them to this guide

---

## Workflows

### Interview workflow
1. Send questions in one deliberate batch
2. For UI/shell/TUI work: show mockups or drafts before applying
3. If mockups aren't clear enough: use a throwaway branch/worktree, test the real surface
4. Capture results in the correct doc (design, screens, controls, or backlog)
5. Don't leave conclusions trapped in chat only

### Implementation workflow
1. Check `rules.md` constraints
2. Read relevant docs from the doc map above
3. Choose execution path: direct edit (tiny) / Codex / Claude Code (medium+)
4. Spec before apply for anything non-trivial
5. Verify: `python3 -c "import main"` + tmux playtest if TUI
6. `git add -A && git commit && git push`
7. Update affected docs (codebase, changelog, backlog) — check if the change makes other docs stale too
8. Update daily memory log

### Version milestone workflow
1. All of implementation workflow above
2. Decide version bump level (see versioning rules in `rules.md`)
3. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
4. Check `codebase.md` is current through this version
5. Update `backlog.md` — move completed items out
6. Promote durable insights to `MEMORY.md` if needed
7. Every ~3 version tags: run cross-doc health check (see `rules.md`)

### Worker context loading
When dispatching Codex or Claude Code, include:
- **UI work** → `controls.md` + `screens.md` + `codebase.md` (relevant sections)
- **System implementation** → `design.md` (relevant system) + `codebase.md` + `rules.md`
- **Bug fix** → `bugs.md` + `codebase.md` (relevant section)

### Coding worker rules
- **Tiny fix** (1-5 lines): direct edit, no worker needed
- **Medium+ changes**: minimal grounding → dispatch worker → review → verify → commit
- **Codex CLI**: primary worker until ~2026-04-22, then Claude Code takes over
- **Claude Code**: `claude --print` for read-only; `claude --permission-mode bypassPermissions --print` for edits
- Always verify `python3 -c "import main"` after Python changes
- Always review worker output — compilation is one gate, not the throne of truth

---

## Tag taxonomy (Obsidian)

Fixed set. Don't invent new tags without adding them here.

**Layer:** `core`, `planning`, `implementation`, `workflow`
**Domain:** `tui`, `controls`, `actions`, `relationships`, `identity`, `events`, `shell`
**Status:** `wip`, `stable`, `stale`
**Type:** `reference`, `decisions`, `tracking`

Each doc gets 2-4 tags from this taxonomy.

---

## Repo info

- Path: `/home/compadmin/openclaw_automated/actora`
- GitHub: `git@github.com:compoodment/Actora.git`
- Language: Python / curses TUI
- Playtesting: always use tmux (`tmux new-session -d -s actora-test -x 220 -y 50`)
