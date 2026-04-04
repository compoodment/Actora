---
title: Bugs
tags: [planning, tracking, wip]
updated: 2026-04-04
---

# Actora Bugs

Actual bugs only. Not design follow-through, not deferred features.
Done = delete from here + mention in changelog.

---

## 🟡 Annoying

- **Skip Time: custom `0` advances 1 month** — entering `0` as custom months and pressing Enter silently advances 1 month instead of rejecting the input or falling back to the preset. Expected: reject 0 or do nothing.



- **Left panel scroll untested under real overflow** — scroll logic rewritten in v0.43.0 but needs real content overflow (relationships, jobs, etc.) to verify scrolling works correctly as panel grows.

## ⚪ Minor

- **Traits only affect event eligibility** — 20 trait-gated events exist (2 per trait) but traits don't affect simulation outcomes beyond event eligibility yet. More trait events should follow as content expands.
