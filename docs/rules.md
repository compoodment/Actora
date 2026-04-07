---
title: Rules
tags: [core, reference, stable]
updated: 2026-04-05
---

# Actora Rules

All project constraints in one place. If it says "don't" or "must", it lives here.

---

## Code rules

> **Note:** All popup types (Menu, Options, Profile) use `draw_box` from `ui.py` as the shared rendering primitive. Do not add new popup types with manual border construction — call `draw_box` instead.


1. Simulation core stays UI-agnostic — only `main.py` knows about curses
2. State mutation flows through controlled world-owned methods, not direct field pokes
3. Don't hard-bake human-only assumptions into architecture that should be species-general later
4. Preserve validated behavior unless the patch explicitly replaces it
5. Don't silently weaken input validation, output ordering, error handling, or structured result contracts
6. Don't bypass the link layer with random actor-owned relationship fields
7. **Import boundary (DEC-033):** `ui.py` and `mechanics.py` import standard lib only. `wizard.py` must never import from `main.py`. New files must declare their position in the import graph (see `codebase.md` §2) before any code is written. No circular imports.

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

1. Spec before apply for anything non-trivial — include: target, files touched, behavior changed, behavior preserved, regression risks, verification plan
2. Verify on VPS — `python3 -c "import main"` minimum, tmux playtest for TUI changes
3. Don't silently broaden scope — a patch does the approved job and no more
4. Review before acceptance — worker output must be checked, not blindly trusted
5. If a good idea appears mid-patch that doesn't belong in the current scope, route it to `backlog.md`
6. Not every mentioned issue is an immediate fix request — it may be backlog, later, or just a note
7. Don't mix unrelated cleanup into one task
8. Don't assume claimed completion means real completion — VPS truth is the final check
9. **When verifying a control/hotkey change: check that old keys are GONE, not just that new keys work. Both directions must be verified. Partial re-wiring is how broken state accumulates.**
10. **Playtest workflow: present findings first, apply only after explicit approval.** Do not apply fixes mid-playtest without reporting findings and getting a go-ahead first.
11. **TUI overlay verification: when checking if a popup is visible in tmux, grep for the popup box content — never the background screen header.** The Life View header is always visible under any overlay. Checking "Life View • ..." as evidence a popup closed is wrong.
12. **Full-codebase grep before renaming/removing anything:** Before dispatching a worker to rename, remove, or replace any symbol (stat, trait, function, key), run `grep -rn "term" *.py` across ALL source files first. List every file that contains it. Include ALL of them in the worker spec. Never assume a subset is complete.

## Worker output review checklist

Before accepting any worker-produced code change, confirm:
1. Does a patch spec exist?
2. Files touched listed?
3. **Did you grep the full codebase to find ALL files containing the changed symbol?**
4. Behavior changed listed?
5. Behavior preserved listed?
6. **Output/diff actually read line-by-line?** (not just "compile passed")
7. Regression risks identified?
8. Build/show-first respected if intended?
9. Result approved before final apply?
10. VPS verification plan clear?
11. Any architecture-fit or efficiency issues flagged?
12. Did the worker miss something important?
13. Is there a tighter/better version still within scope?
14. **Are hardcoded values extracted to constants?**
15. **Does the code follow code rule 2 (state mutation through world-owned methods)?**

If any answer is no, stop and resolve before accepting.

## Naming rules

1. Don't let temporary implementation naming harden into permanent architecture truth
2. `Location` is the right player-facing abstraction, not city-specific wording
3. Use "you" or the character's name in player text, never "actor" or "focused actor"
4. Use "family" not "connected actors" or "linked actors"
5. Internal code/comments/architecture docs may use full internal vocabulary — only rendered display text follows player-facing rules
6. When dispatching workers, include the player-facing text rule explicitly so they don't reintroduce jargon
7. Meaningful milestones should prefer plain version tags like `v0.28.0` — not descriptive sentence tags

## Versioning rules

Format: `vMAJOR.MINOR.PATCH` (e.g. `v0.45.0`, `v0.45.1`)

1. **Major (v1.0.0, v2.0.0)** — fundamental phase shift. We're still v0 because the game isn't feature-complete yet. v1.0.0 = first "this is a real playable game" milestone.
2. **Minor (v0.45.0 → v0.46.0)** — new system, meaningful feature, or structural foundation piece. Examples: non-family relationships (v0.45.0), questionnaire creation (v0.40.1), real location content (v0.40.0).
3. **Patch (v0.45.0 → v0.45.1)** — bug fix, polish, cleanup, doc-only changes, small corrections. Examples: stat padding fix (v0.44.1), playtest polish rounds.

Rules:
- Stay on v0.x.x until the game reaches a coherent first-playable milestone
- Don't bump minor for pure doc/cleanup work — that's a patch
- Don't bump major just because a lot of patches accumulated
- Tag format: `v0.45.0` not `v0.45` or `0.45.0` — always three numbers, always `v` prefix
- Use plain version tags only — no descriptive sentence tags like `v0.45.0-relationships-and-actions`

## Truth classification

Always distinguish:
1. **Verified truth** — actually built, in the repo, verified on VPS
2. **Architecture direction** — what stable docs define as current project truth
3. **Proposed** — ideas, plans, specs not yet implemented

Don't blur these. Don't present proposals as implemented. Don't assume docs auto-sync.

## Anti-drift rules


0. **Compare views actively during design:** When design decisions are non-trivial, present both sides and challenge each other's reasoning. Don't default to agreement — push back when there's a real counter-argument.
1. **Interview documentation standard:** After any design interview or decision session, write results to docs as full system anchors — not bullet summaries. Each anchor must include: current truth, intent, design rules, the "why" behind decisions, and open questions. The doc must survive without the session. A reader with no session context must understand what was decided, why, and what remains open.
2. After every meaningful change: sync docs + memory immediately — don't batch it to later
3. **Cascade check:** when updating any doc, check if other docs reference or depend on the same information and update them too. One doc change can make others stale.
4. **Forward-thinking check:** after any decision, interview, or new system lands, ask: "does this create a new ongoing obligation?" If yes, add the rule/workflow/routing entry NOW, not later. Don't wait for the user to notice it's missing.
5. Before starting any task: targeted memory_search + read only the relevant files
6. After compaction: re-read memory/daily + MEMORY.md + guide.md + rules.md + backlog.md (Now); don't bulk-read other docs unless the task needs them
7. Before any config edit: create a backup first
8. For meaningful repo/file edits: create a local pre-edit backup in `.backups/`
9. **Design before implementation:** If a task touches a system with mechanical depth (traits, stats, skills, questionnaire, needs, mood, actions), it requires a design interview first. Do not patch, hack, or "quick fix" systems that need real design. If there's no interview to reference, flag the task as design-pending and stop. Building on undesigned foundations is how we get things we have to tear out later.
10. **Check workflow during execution, not just at the start:** Reading guide.md once is not enough. Before each step of the implementation workflow (dispatch, review, commit, doc sync), re-verify you're following it. The failure mode is: read → understand → get momentum → cut corners. The workflow exists specifically to prevent this.
11. **Full doc re-read after compaction is mandatory:** After any compaction, /new, or /reset, read ALL docs in this order before doing ANY work: (1) memory/daily (today + yesterday), (2) MEMORY.md, (3) guide.md, (4) rules.md, (5) backlog.md Now, (6) design.md, (7) identity.md. Not skimming — reading. The summary from compaction is not a substitute for the docs. The docs are the truth. If you skip this, you WILL forget the scale of the project, the interconnections between systems, and the design decisions that constrain implementation. This has happened repeatedly.
