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

- **Multiple "X Months Skipped" entries in event log** — when a skip is interrupted by a popup (identity choice, meeting event), each resumed segment generates a new skip marker. e.g. "9835 Months Skipped", then "9832 Months Skipped", then "9831 Months Skipped". Cosmetically messy. Not a crash. *(found 2026-04-05)*

- **Intersex sex option not preserved through wizard** — selecting "Intersex" on the identity step results in the character being saved as Male. The intersex value appears not to carry through to the final character payload. *(found 2026-04-05, RT playtest)*

- **"Other" appearance option may skip custom text input** — in some navigation paths, selecting "Other" for eye/hair color appears to default to the first real option (Brown) instead of opening the custom text input. Needs isolated test to confirm. *(found 2026-04-05, RT playtest)*

- **Questionnaire framing screen ignores Backspace** — pressing Backspace on the framing screen does nothing. Should navigate back to mode selection (step 3) so the player can choose manual mode instead. *(found 2026-04-05)*

- **Skip Time: custom `0` advances 1 month** — entering `0` as custom months and pressing Enter silently advances 1 month instead of rejecting the input or falling back to the preset. Expected: reject 0 or do nothing.



- **Left panel scroll untested under real overflow** — scroll logic rewritten in v0.43.0 but needs real content overflow (relationships, jobs, etc.) to verify scrolling works correctly as panel grows.

## ⚪ Minor

- **Action feedback messages not visible on Actions screen** — `last_message` (e.g. "Already queued", "Not enough free time") only renders in the Life View left panel header, not on the Actions screen where the action happened. Player has to return to Life View to see the message. Fix: render last_message somewhere on the Actions screen (footer area or details column). *(noted 2026-04-05)*

