---
title: Bugs
tags: [planning, tracking, wip]
updated: 2026-04-02
---

# Actora Bugs

Actual bugs only. Not design follow-through, not deferred features.
Done = delete from here + mention in changelog.

---

## 🟡 Annoying

- **Left panel scroll untested under real overflow** — scroll logic rewritten in v0.43.0 but needs real content overflow (relationships, jobs, etc.) to verify scrolling works correctly as panel grows.

## ⚪ Minor

- **Traits only affect event eligibility** — 20 trait-gated events exist (2 per trait) but traits don't affect simulation outcomes beyond event eligibility yet. More trait events should follow as content expands.
