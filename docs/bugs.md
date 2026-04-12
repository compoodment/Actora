---
title: Bugs
tags: [planning, tracking, wip]
updated: 2026-04-10
---

# Actora Bugs

Actual bugs only. Not design follow-through, not deferred features.
Done = delete from here + mention in changelog.

---

## 🟡 Annoying

- **Profile doc drift:** `docs/design.md` still says Profile is "Not started implementation" and "Read-only, no interaction," but `main.py` already implements interactive category rows and drill-down popups.
- **Profile Relationships behavior mismatch:** `docs/design.md` says pressing Enter on Relationships should open the Relationships Browser directly, but current `main.py` behavior opens a popup placeholder instead.

