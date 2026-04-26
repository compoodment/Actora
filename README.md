# Actora

A life simulation where the world doesn't stop when you die.

You're born in Amsterdam in 1987. You grow up, make friends, maybe go to school, get a job. You die in 2051. Then you continue as your daughter, who was born in 2012 and is now 39. She builds a company. Her son emigrates to Tokyo. His granddaughter boards a spacecraft in 2280.

Same save. Same universe. The history is real.

It's not BitLife. It's not a god sim. It's somewhere in between — you live through one person at a time, but the world around you is actually running.

Currently a terminal prototype. Python, curses TUI. Work in progress.

---

## What exists right now

- Character creation with questionnaire or manual stat setup
- Life sim with events, relationships, family, death, and continuation
- Friends — meet people, grow close, drift apart, lose them
- Relationship browser and history log
- 12 countries, 39 cities, culture-aware names
- 120 events including family-aware and personality-specific ones

## Running it

```bash
python3 main.py
```

Requires Python 3 and a terminal that supports curses.

## Docs

Start with [`docs/guide.md`](docs/guide.md) — it maps everything.

| | |
|---|---|
| [`identity.md`](docs/identity.md) | What Actora is trying to be |
| [`roadmap.md`](docs/roadmap.md) | What gets built and in what order |
| [`design.md`](docs/design.md) | How each system should feel |
| [`codebase.md`](docs/codebase.md) | What's actually implemented |
| [`changelog.md`](docs/changelog.md) | Version history |
| [`controls.md`](docs/controls.md) | Keybinds and controls |
| [`screens.md`](docs/screens.md) | UI screens and layouts |

### Internal

| | |
|---|---|
| [`rules.md`](docs/internal/rules.md) | Internal logic rules |
| [`decisions.md`](docs/internal/decisions.md) | Architecture decisions |
| [`bugs.md`](docs/internal/bugs.md) | Known bugs |
| [`backlog.md`](docs/internal/backlog.md) | Internal backlog |
