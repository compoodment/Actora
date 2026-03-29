# Planning

Flexible working layer for Actora.

This folder is not the stable source stack.
It is the working planning/intake layer that sits beneath:
- Master Context
- Roadmap
- Operator Guide
- verified repo truth

Use this folder for:
- active idea intake
- interview-derived design retention
- parked architecture pressure
- near-term planning snapshots
- bug/revisit tracking
- staging notes before anything gets promoted into stable docs

Files and intended roles:
- `working-ideas-register.txt`
  - the broad working idea/intake/staging layer
  - holds brainstorming, interview-derived game concepts, longer-lived design pressure, and realized-idea guardrails
  - should preserve substantial idea material instead of flattening everything into short-term task language
- `actionable-summary.txt`
  - the shorter operational snapshot
  - answers: where the repo is, what the current planning read is, and what the strongest near-term question appears to be right now
  - should stay more distilled than the WIR, but still grounded in the same source stack
- `live-issues.txt`
  - the current bug/revisit tracker so active problems do not get lost between patches

Interpretation rule:
- stable source docs win on durable architecture/workflow truth
- verified repo truth wins on what is already implemented
- planning docs help retain pressure, ideas, and active next-step framing without pretending every idea is approved or shipped

Anti-confusion rule:
- do not treat `working-ideas-register.txt` and `actionable-summary.txt` as duplicates
- WIR is the richer intake/staging/pressure layer
- Actionable Summary is the narrower operational read
- if they drift into saying contradictory things, fix the contradiction instead of flattening both docs into generic mush
