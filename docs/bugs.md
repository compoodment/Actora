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

- **Questionnaire framing screen ignores Backspace** — pressing Backspace on the framing screen does nothing. Should navigate back to mode selection (step 3) so the player can choose manual mode instead. *(found 2026-04-05)*

- **Reveal screen Backspace routing** — pressing Backspace on the reveal screen lands on Confirm with reveal content still showing, then requires another Enter to dismiss. Should go back to Q24 cleanly. *(found 2026-04-05)*

- **Skip Time: custom `0` advances 1 month** — entering `0` as custom months and pressing Enter silently advances 1 month instead of rejecting the input or falling back to the preset. Expected: reject 0 or do nothing.



- **Left panel scroll untested under real overflow** — scroll logic rewritten in v0.43.0 but needs real content overflow (relationships, jobs, etc.) to verify scrolling works correctly as panel grows.

## ⚪ Minor

- **Action feedback messages not visible on Actions screen** — `last_message` (e.g. "Already queued", "Not enough free time") only renders in the Life View left panel header, not on the Actions screen where the action happened. Player has to return to Life View to see the message. Fix: render last_message somewhere on the Actions screen (footer area or details column). *(noted 2026-04-05)*

- **Trait-gated events use old trait names** — events.py still has events gated on old trait names (Curious, Calm, Restless, Alert, Bold, Stubborn, Cheerful, Gentle, Shy). New 12-trait pool is in code but event eligibility still references old labels. Needs update as part of questionnaire/event redesign pass. *(noted 2026-04-05)*
