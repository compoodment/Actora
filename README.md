# Actora

**A continuous-history life simulation.**

You're born in Amsterdam in 1987. You grow up, make friends, get a job, and eventually die in 2051. But the world doesn't end. You continue as your daughter—born in 2012, now 39, building a company. Later, her son emigrates to Tokyo. His granddaughter boards a spacecraft in 2280.

Same save. Same universe. The history is real. 

It's not BitLife. It's not a god sim. It's a persistent world where you live through one person at a time, while the simulation runs for everyone else in the background.

---

## Current Status
**Pre-Alpha Prototype.** 
Built in Python using a `curses` terminal UI. It is highly experimental, actively being rewritten, and prone to breaking.

### What actually works right now:
- **Character Creation:** Questionnaire-based generation or manual stat allocation.
- **Life Engine:** Event processing, aging, relationships, family dynamics, death, and lineage continuation.
- **Social Graph:** Meet people, grow close, drift apart, or lose them entirely. Trackable via a relationship browser and history log.
- **World Data:** 12 countries, 39 cities, and culture-aware naming conventions.
- **Event System:** 120+ unique events, factoring in family context and personality traits.

---

## Running It

You'll need Python 3 and a terminal that supports `curses` (Linux/macOS default; WSL recommended for Windows).

```bash
git clone https://github.com/compoodment/Actora.git
cd Actora
python3 main.py
```

---

## Documentation

Start with [`docs/guide.md`](docs/guide.md) — it maps the current state of the game.

### Public Specs & Systems
| | |
|---|---|
| [`identity.md`](docs/identity.md) | The core vision: what Actora is trying to be |
| [`roadmap.md`](docs/roadmap.md) | What gets built and in what order |
| [`design.md`](docs/design.md) | How each system should feel and function |
| [`codebase.md`](docs/codebase.md) | What's actually implemented right now |
| [`changelog.md`](docs/changelog.md) | Version history |
| [`controls.md`](docs/controls.md) | Keybinds and UI navigation |
| [`screens.md`](docs/screens.md) | UI layout references |

### Internal Architecture
| | |
|---|---|
| [`rules.md`](docs/internal/rules.md) | Internal logic rules |
| [`decisions.md`](docs/internal/decisions.md) | Architecture and pivot log |
| [`bugs.md`](docs/internal/bugs.md) | Known issues and breaks |
| [`backlog.md`](docs/internal/backlog.md) | The immediate to-do list |
