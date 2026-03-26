# CompLife Docs

This `docs/` directory now separates **source truth**, **planning**, and **repo truth** so the project does not turn into one giant markdown landfill.

## Structure

### `core_architecture/`
Stable source documents.
Use these first when the question is about durable project truth.

Files:
- `master-context.txt` — what CompLife is
- `comp_life-roadmap.txt` — dependency order and what should come before what
- `source-index.txt` — how the document system works

### `workflow/`
Workflow and execution discipline.

Files:
- `operator-guide.txt` — how CompLife work should be done

### `planning/`
Flexible working layer.
Use this for active pressures, parked ideas, and near-term planning snapshots.

Files:
- `working-ideas-register.txt`
- `actionable-summary.txt`

### repo-local docs in this folder
These are implementation-facing and should not be confused with the source stack.

Files:
- `architecture.md`
- `changelog.md`
- `lifecycle-system.md`

## Quick usage rules

- **Master Context** = durable identity / architecture truth
- **Operator Guide** = workflow rules
- **Roadmap** = sequencing and dependency order
- **Working Ideas Register** = active ideas and parked pressures
- **Actionable Summary** = temporary planning snapshot
- **Source Index** = source-system navigation and precedence
- **Repo docs / changelog** = what was actually implemented

## Practical loading guide

- Architecture question -> `master-context.txt`
- Workflow / review / patch-discipline question -> `operator-guide.txt`
- "What should come next?" -> `comp_life-roadmap.txt` + planning docs
- "Where does this idea belong?" -> `source-index.txt`
- "What changed in code?" -> repo docs + codebase + git

## Important rule

Do not treat the planning docs as durable truth.
Do not treat repo history as if it automatically updates the source stack.
Do not let random chat drift outrank the source documents.
