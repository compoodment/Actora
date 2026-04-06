---
title: Guide
tags: [core, workflow, reference]
updated: 2026-04-06
---

# Actora Guide

The one doc. Navigation, workflows, reading order, routing.

---

## After context loss (compaction / reset / new session)

**This is not optional. Read ALL of these before doing ANY work:**

1. `memory/YYYY-MM-DD.md` (today + yesterday)
2. `MEMORY.md` (workspace, durable rules)
3. This file — doc map, workflows, routing
4. `rules.md` — constraints to not break things
5. `backlog.md` → Now section — what we're actively doing
6. `design.md` — current system designs, mechanical depth, interconnections
7. `identity.md` — project identity, architecture principles

The compaction summary is NOT a substitute for reading these docs. The docs are the truth. Skip this and you will forget the scale, the design decisions, and the constraints — it has happened every time.

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

**Before EVERY step, re-read this list. Not from memory — scroll back to this section.**

1. Check `rules.md` constraints
2. **Design gate:** Does this task touch a system with mechanical depth? If yes, check `design.md` — is there a completed interview/anchor for this system? If not, STOP. Flag as design-pending, do not implement.
3. Read relevant docs from the doc map above
4. **Scope scan:** If renaming/replacing anything, `grep -rn` across all source files first. List every affected file. This is mandatory before dispatching a worker.
5. Choose execution path: direct edit (tiny, 1-5 lines) / coding worker (medium+). See `TOOLS.md` (workspace) for which worker to use and when — do not make model decisions here.
6. Spec before apply for anything non-trivial
7. Verify: `python3 -c "import main"` + tmux playtest if TUI
8. **Review worker output:** read the actual diff line-by-line. Run the worker review checklist in rules.md. Compile is one gate, not the only gate.
9. `git add -A && git commit && git push`
10. **Doc sync (mandatory, never skip):** Update changelog, backlog, codebase. Cascade check — does this change make other docs stale? Do this BEFORE asking "what's next?"
11. Update daily memory log

**After step 11, post a completion block:**
```
✅ Implementation complete:
- [ ] rules.md checked
- [ ] design gate passed
- [ ] relevant docs read: [list]
- [ ] scope scan done (if rename/replace)
- [ ] spec written (if non-trivial)
- [ ] compiled clean
- [ ] playtested (if TUI)
- [ ] diff reviewed line-by-line
- [ ] review checklist passed
- [ ] committed + pushed
- [ ] changelog updated
- [ ] backlog updated
- [ ] codebase.md updated
- [ ] cascade check done
- [ ] daily memory updated
```
If any box is unchecked, go back and do it. Do not proceed.

### Version milestone workflow
1. All of implementation workflow above
2. Decide version bump level (see versioning rules in `rules.md`)
3. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`
4. Check `codebase.md` is current through this version
5. Update `backlog.md` — move completed items out
6. Promote durable insights to `MEMORY.md` if needed
7. Every ~3 version tags: run cross-doc health check (see `rules.md`)

### Worker context loading
When dispatching a coding worker, include:
- **UI/shell work** → `controls.md` + `screens.md` + `codebase.md` (relevant sections) + `ui.py` if touching layout primitives
- **System implementation** → `design.md` (relevant system) + `codebase.md` + `rules.md`
- **Mechanics/action work** → `codebase.md` + `mechanics.py` + `rules.md`
- **Wizard/creation work** → `codebase.md` + `wizard.py` relevant sections + `rules.md`
- **Bug fix** → `bugs.md` + `codebase.md` (relevant section)

### Coding worker rules
- **Tiny fix** (1-5 lines): direct edit, no worker needed
- **Medium+ changes**: minimal grounding → dispatch worker → review → verify → commit
- **Current worker:** Codex CLI (`codex exec --full-auto`). Claude Code CLI auth is broken as of 2026-04-05 — see `TOOLS.md` (workspace) for current status and fix instructions.
- Always verify `python3 -c "import main"` after Python changes; also verify `python3 -c "import ui; import mechanics; import wizard"` after touching extracted modules
- Always review worker output — compilation is one gate, not the throne of truth
- **Model selection:** See `TOOLS.md` (workspace) for the full routing table. Do not duplicate model decisions here.

### Kestrel review protocol
- **Kestrel** is a separate reviewer agent running on computment's laptop. He communicates with OpenComp via AgentMail (`kestrel-ai@agentmail.to` ↔ `opencomp@agentmail.to`).
- **When to use Kestrel:** For architecture proposals, design direction changes, module extractions, or any decision that benefits from a second opinion. Not needed for tiny fixes or routine bug patches.
- **How to request a review:** OpenComp emails Kestrel with a summary of the proposal and specific review questions. Kestrel replies by email with critique. OpenComp reads the review and incorporates feedback before implementing.
- **Kestrel does NOT:** implement code, push commits, or edit Actora files. He reviews only.
- **Trust model:** Kestrel's reviews are advisory. computment has final say on all decisions.

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
