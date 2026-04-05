---
title: Bugs
tags: [planning, tracking, wip]
updated: 2026-04-05
---

# Actora Bugs

Actual bugs only. Not design follow-through, not deferred features.
Done = delete from here + mention in changelog.

---

## 🟡 Annoying

- **Intersex sex option not preserved through wizard** — selecting "Intersex" on the identity step results in the character being saved as Male. The intersex value appears not to carry through to the final character payload. *(found 2026-04-05, RT playtest)* — **not reproduced in v0.51.3 testing; may be pre-existing fix. Keep until confirmed clean.**

- **Left panel scroll untested under real overflow** — scroll logic rewritten in v0.43.0 but needs real content overflow (relationships, jobs, etc.) to verify scrolling works correctly as panel grows.

