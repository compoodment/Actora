---
title: Actora Docs Index
role: navigation
stability: high
tags: [index, navigation]
---

# Actora Docs

This `docs/` directory separates stable source truth, flexible planning, workflow rules, and repo-local implementation truth so the project does not collapse into one giant markdown swamp.

## Structure

### `core_architecture/`
Stable source documents.
Use these first when the question is about durable project truth.

Files:
- `[[master-context]]` — what Actora is
- `[[actora-roadmap]]` — dependency order and what should come before what
- `[[source-index]]` — how the document system works

### `workflow/`
Workflow and execution discipline.

Files:
- `[[operator-guide]]` — how Actora work should be done

### `planning/`
Flexible working layer.
Use this for active pressures, parked ideas, and near-term planning snapshots.

Files:
- `[[working-ideas-register]]`
- `[[actionable-summary]]`

### repo-local docs in this folder
These are implementation-facing and should not be confused with the source stack.

Files:
- `[[architecture]]`
- `[[changelog]]`
- `[[architecture#Lifecycle System|lifecycle-system]]`

## Quick usage rules

- **[[master-context|Master Context]]** = durable identity / architecture truth
- **[[operator-guide|Operator Guide]]** = workflow rules
- **[[actora-roadmap|Actora Roadmap]]** = sequencing and dependency order
- **[[working-ideas-register|Working Ideas Register]]** = active ideas and parked pressures
- **[[actionable-summary|Actionable Summary]]** = temporary planning snapshot
- **[[source-index|Source Index]]** = source-system navigation and precedence
- **Repo docs / [[changelog]]** = what was actually implemented

## Practical loading guide

- Architecture question -> `[[master-context]]`
- Workflow / review / patch-discipline question -> `[[operator-guide]]`
- "What should come next?" -> `[[actora-roadmap]]` + planning docs
- "Where does this idea belong?" -> `[[source-index]]`
- "What changed in code?" -> repo docs + codebase + git

## Important rule

Do not treat the planning docs as durable truth.
Do not treat repo history as if it automatically updates the source stack.
Do not let random chat drift outrank the source documents.
