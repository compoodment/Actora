---
title: Operator Guide
role: workflow-and-execution-discipline
stability: high
tags: [workflow, process, rules]
---

Actora Operator Guide v9

Purpose

This document defines the working method, workflow roles, patch discipline, review rules, verification expectations, and tool-selection rules for Actora.

It is the workflow anchor for the project.
It does not define the main project identity or milestone sequencing by itself.
Those belong to the [[master-context|Master Context]] and [[actora-roadmap|Actora Roadmap]].

It also does not replace repo-local implementation history.
Repo docs and [[changelog]] track what was actually changed in code.

This document should be used whenever work is being proposed, reviewed, patched, applied, verified, committed, tagged, or documented.

⸻

1. Core workflow

Actora work should follow this order:

source alignment -> spec -> execution-path selection -> draft/build/show when appropriate -> review -> approve -> apply -> VPS verification -> documentation update -> commit/tag if appropriate

This order exists to protect the project from scope drift, silent regressions, false completion claims, and tool-driven confusion.

1.1 Workflow roles

The assistant operating through OpenClaw is the planning, specification, synthesis, review, and source-alignment partner. It holds project context through the source documents loaded in the Actora project space and drives milestone shaping, guardrails, rewrite-risk spotting, patch review, workflow choice, and source-doc alignment.

Codex CLI is the current heavy implementation worker for Actora when the task is a real coding task rather than a tiny surgical fix, but only as a temporary worker while the user's ChatGPT-linked Codex access remains active. It is appropriate for multi-file feature work, refactors, larger implementation passes, and repository exploration that would otherwise waste chat tokens on repetitive patch labor.

Claude Code CLI is the intended successor heavy implementation worker for Actora once Codex access ends. It should be treated as the main replacement path for multi-file feature work, refactors, larger implementation passes, repo understanding, and planning-oriented coding work.

OpenClaw remains a valid implementation worker for repo work when its workflow is the better fit for the task, especially for controlled patch/show cycles, repo-document work, or cases where the operator intentionally chooses it.

Direct manual edits remain appropriate for tiny, low-risk, clearly bounded fixes where spawning an automated coding worker would add more friction than value.

The user remains the final decision-maker and middleman. The user reviews outputs, chooses what gets applied, committed, tagged, deferred, or discarded, and relays material between tools when needed.

The VPS is the final reality check for:
	•	on-disk file truth
	•	compile truth
	•	runtime truth
	•	git truth
	•	actual tool-auth / environment truth

1.2 Standard implementation paths

Actora has four normal implementation paths:

A. Direct edit path
scoped tiny fix -> edit -> verify -> docs update if needed -> commit if appropriate

B. Codex path
scoped Codex task -> Codex implementation pass -> review -> explicit approval if needed -> verify on VPS -> docs update -> commit/tag if appropriate

C. Claude Code path
scoped Claude Code task -> Claude implementation pass -> review -> explicit approval if needed -> verify on VPS -> docs update -> commit/tag if appropriate

D. OpenClaw path
scoped OpenClaw task -> build/show or patch output -> review -> explicit approval -> apply -> verify on VPS -> docs update -> commit/tag if appropriate

Important rule:
not every issue mentioned in the moment should be treated as an immediate fix request.

A discussed issue may be:
	•	immediate work
	•	deferred work
	•	roadmap pressure
	•	[[working-ideas-register|Working Ideas Register]] material
	•	simply a note

1.3 Execution-path selection rule

Use the lightest path that still fits the job.

Default selection rule for Actora:
	•	tiny surgical fix -> direct edit is allowed
	•	medium coding task -> do a minimal grounding pass, then default to the current primary coding worker (Codex CLI while available, Claude Code CLI after Codex access ends)
	•	real feature, refactor, or multi-file coding task -> do a minimal grounding pass, then default to the current primary coding worker (Codex CLI while available, Claude Code CLI after Codex access ends)
	•	planning-oriented repo work or repo understanding where Claude is the better fit -> Claude Code is allowed even before the Codex cutoff
	•	repo-doc workflow, controlled patch/show flow, or explicitly chosen OpenClaw task -> use OpenClaw
	•	GitHub-native review/meta tasks may use Copilot CLI selectively, but Copilot CLI is not the default heavy implementation worker

Minimal grounding pass means:
	•	check the actual repo state relevant to the task
	•	read the specific docs/code needed to avoid fake assumptions
	•	return a short grounded proposal with the recommended move, patch boundary, and key things being kept out

Do not wait for the user to repeatedly say “re-read the docs” or “think properly” before doing non-trivial Actora work.
That grounding step is part of the normal workflow, not a special extra ritual.

Do not spawn Codex just to change one obvious string, one tiny conditional, one import, or one comment block.
Do not keep hand-editing a messy multi-file task just because the first file looked small.
Use judgment, not ritual.

Selection should consider:
	•	number of files likely touched
	•	need for repo exploration
	•	risk of drift or hidden coupling
	•	how much reviewable output is needed before apply
	•	whether token savings matter enough to justify agent orchestration
	•	whether the task is code-heavy or doc-heavy
	•	whether Codex is the better token split even for medium work

1.4 OpenClaw workflow rules

When opening an OpenClaw task for code or repo-doc work:
	•	keep the prompt grounded in actual repo truth and exact target behavior
	•	specify exact files, constraints, preserved behavior, and patch boundaries
	•	state the intended current date explicitly if repo docs are being edited
	•	prefer build/show, diff, or explicit patch output before apply when appropriate
	•	do not mix unrelated cleanup into one task

Do not ask OpenClaw to infer source-level architecture context from chat drift.
Give it what it needs to execute the patch correctly and no more.

Keep the old safety rule:
	•	build/show first when appropriate
	•	review the output
	•	only then apply if approved

If OpenClaw applies meaningful code changes without a separate review step, treat the result as unverified until it is properly checked.

1.5 Codex CLI workflow rules

When using Codex CLI for Actora:
	•	run it inside the actual repo or a deliberate scratch/worktree location
	•	keep the prompt repo-grounded and scope-bounded
	•	say what must change, what must stay unchanged, and how success will be verified
	•	prefer one coherent task over a rambling prompt with mixed goals
	•	make Codex do the implementation labor, not the decision-making about project truth
	•	prefer Codex for implementation-heavy work while access remains available, not for fluff or repetitive low-value repo summarization

Codex is the temporary default worker for medium-and-up coding work in Actora while the user's ChatGPT-linked access remains active.
A bad prompt still makes bad code. The robot is not a priest.

Codex output must still be reviewed for:
	•	scope control
	•	preserved behavior
	•	structural fit with stable docs
	•	verification completeness
	•	weird opportunistic rewrites
	•	confident nonsense
	•	what may have been missed
	•	whether a tighter or clearly better within-scope revision exists

Do not silently accept Codex changes just because they compile.
Compilation is one gate, not the throne of truth.

The review step is not only a correctness check.
It should also ask:
	•	Did the worker miss something important?
	•	Is there a cleaner, tighter, or more honest version still within the approved scope?
	•	Did the worker follow the letter of the task while missing the better interpretation?
	•	Should one additional within-scope improvement or revision be made before acceptance?

When Codex is used in the background or on a longer task:
	•	report that it was started
	•	report again only when a milestone, blocker, question, failure, or completion happens
	•	avoid dead silent tool labor if the user is waiting on live work

1.5.1 Claude Code workflow rules

When using Claude Code for Actora:
	•	run it inside the actual repo or a deliberate scratch/worktree location
	•	keep the prompt repo-grounded and scope-bounded
	•	say what must change, what must stay unchanged, and how success will be verified
	•	prefer Claude for repo understanding, planning-oriented coding work, and as the primary replacement path for multi-file implementation work after Codex access ends
	•	for read-only or analysis tasks, non-interactive `claude --print` is acceptable
	•	for edit tasks from OpenClaw runtime, use `claude --permission-mode bypassPermissions --print` as the reliable non-interactive path
	•	do not rely on `--permission-mode dontAsk --print` for edit tasks; it still stops for permission in this environment
	•	do not rely on `--permission-mode plan --print` until that combination is proven reliable on the current installed version

Claude Code should become the default worker for medium-and-up coding work in Actora after Codex access ends, and it is already a valid early choice when its workflow shape is better for the task.

Claude output must still be reviewed for:
	•	scope control
	•	preserved behavior
	•	structural fit with stable docs
	•	verification completeness
	•	weird opportunistic rewrites
	•	confident nonsense
	•	what may have been missed
	•	whether a tighter or clearly better within-scope revision exists

1.5.2 Copilot CLI workflow rules

Copilot CLI is available for selective GitHub-native or review/meta work, but it is not the default heavy implementation worker for Actora.

Use Copilot CLI selectively for:
	•	GitHub-aware review or repository meta tasks
	•	roadmap digestion or ranked next-step suggestions when that extra context is worth the spend
	•	PR/review-style critique where its workflow is the better fit

Do not default to Copilot CLI for ordinary implementation work unless there is a specific reason to spend premium usage there.

1.6 Source document revision workflow

When a source document needs revision, the workflow is:
	1.	Changes are proposed and discussed.
	2.	The user decides which changes are approved.
	3.	The current version of the document plus the approved changes go to whoever is producing the revision.
	4.	A complete revised file is produced — not fragile line-by-line fragments unless the change is intentionally tiny.
	5.	The user reviews the revised file against the prior version.
	6.	If approved, the user swaps the new file into the project source stack.
	7.	Future sessions then pick up the new version naturally.

This workflow avoids silent drift and error-prone piecemeal edits.

⸻

2. Source-first working method

Actora should be worked on through the source system rather than through drifting chat assumptions.

Use source documents in this priority order:
	1.	[[master-context|Master Context]]
	2.	[[operator-guide|Operator Guide]]
	3.	[[actora-roadmap|Actora Roadmap]]
	4.	[[source-index|Source Index]]
	5.	[[working-ideas-register|Working Ideas Register]]
	6.	[[actionable-summary|Actionable Summary]], if one is actively maintained

Use repo-local documents separately for implemented history and repo-local architecture notes.
Those are not the same thing as the source stack.

Interpretation rule:
	•	[[master-context|Master Context]] defines durable project identity and architecture truth
	•	[[operator-guide|Operator Guide]] defines workflow and patch discipline
	•	[[actora-roadmap|Actora Roadmap]] defines sequencing and dependency order
	•	[[source-index|Source Index]] explains source roles and precedence
	•	[[working-ideas-register|Working Ideas Register]] is flexible staging, not automatic truth
	•	[[actionable-summary|Actionable Summary]] is a temporary planning aid, not durable authority
	•	Repo [[changelog]] records actual implemented history
	•	Repo architecture notes describe codebase-facing structure and implementation-facing clarification

If a new idea conflicts with stable sources, do not silently follow the idea.
Route it through the [[working-ideas-register|Working Ideas Register]] or revise the stable docs deliberately if the baseline truly changed.

⸻

3. Truth classification

Always distinguish between these categories:

A. Verified on-disk / implemented truth

What is actually built, present in the repo, and preferably verified on the VPS.

B. Durable architecture / workflow truth

What the stable source documents define as current project truth.

C. Repo-local implementation history / code-facing documentation truth

What repo docs say was implemented, changed, or clarified for the codebase.

D. Proposed / not yet applied

Ideas, patch plans, rewrites, future systems, or speculative changes that are not yet implemented.

Do not blur these categories.
Do not present proposals as current implementation truth.
Do not present source-level architecture direction as already implemented if it is not.
Do not assume repo docs automatically update source docs or vice versa.

⸻

4. Patch approval rules

Do not apply changes until they are explicitly approved, unless the chosen workflow is intentionally using a pre-approved low-risk direct edit path.

4.1 Required patch spec fields

Every meaningful patch spec should include the following before apply is considered:
	•	Target description: what the patch is trying to accomplish
	•	Execution path: direct edit, Codex task, OpenClaw task, or other approved path
	•	Files touched: which files will be created, modified, moved, or renamed
	•	Behavior changed: what will be different after the patch
	•	Behavior preserved: what must remain exactly the same
	•	Regression risks: what could break
	•	Verification plan: how the result will be checked
	•	Unresolved conflicts or uncertainties: anything not yet settled

If any of these fields cannot be filled in clearly, the spec is not ready.

4.2 General patch rules

If touching validated code, explicitly separate:
	•	changed behavior
	•	preserved behavior

If the requested change risks regression, stop and report the conflict instead of partially forcing the patch through.

⸻

5. Scope discipline

Actora should remain foundation-first.

Do not:
	•	broaden a patch just because related ideas are tempting
	•	smuggle future systems into a narrow milestone
	•	rewrite validated code just because another structure seems cleaner
	•	treat large conceptual shifts as excuses for uncontrolled implementation churn
	•	treat every identified issue as an automatic same-session fix request

Patch rule:
A patch should do the approved job and no more.

If a good idea appears but does not belong in the current patch:
	•	keep it out of the patch
	•	route it to the [[working-ideas-register|Working Ideas Register]] if needed
	•	preserve sequencing discipline

⸻

6. Preservation rules

Preserve previously validated behavior unless the approved spec explicitly replaces it.

When revising or extending validated code:
	•	identify what must stay the same
	•	identify what may change
	•	verify that control flow, ordering, and validation remain intact unless intentionally changed
	•	avoid silent formatting or behavior drift

Do not silently weaken:
	•	input validation
	•	output ordering
	•	error handling
	•	state separation
	•	structured result contracts
	•	current simulation rules

If formatting itself is behaviorally important, preserve it exactly.

⸻

7. Review order and gates

7.1 General review order
	1.	source alignment
	2.	spec clarity
	3.	execution-path choice
	4.	worker/task framing
	5.	draft review / diff review / resulting change review
	6.	preservation review
	7.	gap / missed-something review
	8.	within-scope revision opportunity review
	9.	approval to apply when the workflow requires it
	10.	VPS verification after apply
	11.	verification against the approved spec
	12.	documentation update
	13.	commit/tag if appropriate

This order matters.
Do not treat broad “looks complete” claims as primary truth.
Do not skip the review step just because a tool sounds confident.
Do not treat review as only “did it technically work.”
Review should also check whether something important was missed, whether a better within-scope revision exists, and whether the result is merely acceptable versus actually the best clean version of the approved patch.

7.2 Automated-worker pre-acceptance gate

Before accepting an OpenClaw-produced or Codex-produced meaningful code patch, confirm all of the following:
	1.	Does the patch spec exist? (yes/no)
	2.	Does it list files touched? (yes/no)
	3.	Does it list behavior changed? (yes/no)
	4.	Does it list behavior preserved? (yes/no)
	5.	Has the output, diff, or changed result been reviewed? (yes/no)
	6.	Have regression risks been identified? (yes/no)
	7.	If a build/show-first path was intended, was that respected? (yes/no)
	8.	Has the result been approved before final apply when approval was required? (yes/no)
	9.	Is the VPS verification plan clear? (yes/no)
	10.	Are there any obvious efficiency, scaling, or architecture-fit issues in the changed code? (yes/no — if yes, flag and evaluate before acceptance)

If any answer is no, stop and resolve before treating the patch as accepted.

⸻

8. VPS verification expectations

Manual verification matters, and the VPS is the final reality check.

When a patch changes visible behavior, simulation flow, prompts, output order, data structures, file layout, naming, tool wiring, or user-facing logic:
	•	check git truth
	•	run compile checks if the language/runtime supports them
	•	test the changed path directly
	•	test key preserved behaviors too
	•	confirm exact important outputs when formatting matters
	•	confirm worker/auth/environment assumptions when the patch depends on them

Do not rely only on tool-generated success claims.
Do not assume claimed completion means real completion.

A change should not be treated as fully verified until VPS truth matches the claimed result, when VPS access is relevant to the patch.

⸻

9. Documentation discipline

Actora uses separate documentation layers.
Do not collapse them into one blob.

Stable source docs should remain durable and relatively compact.
Flexible source docs should absorb active idea pressure.
Repo docs should carry implementation-facing truth and change history.

Use documents like this:
	•	[[master-context|Master Context]] for durable identity and architecture truth
	•	[[operator-guide|Operator Guide]] for workflow rules
	•	[[actora-roadmap|Actora Roadmap]] for sequencing and dependency order, not patch-by-patch progress tracking
	•	[[source-index|Source Index]] for source navigation and precedence
	•	[[working-ideas-register|Working Ideas Register]] for active idea intake and staging
	•	[[actionable-summary|Actionable Summary]] for temporary planning snapshots when useful
	•	Repo [[changelog]] for implemented history
	•	Repo architecture notes for code-facing structural clarification

Do not:
	•	stuff every brainstorm into stable docs
	•	use the [[working-ideas-register|Working Ideas Register]] as implementation truth
	•	use the [[actionable-summary|Actionable Summary]] as durable authority
	•	use the [[changelog|Changelog]] for speculative planning
	•	make the [[actora-roadmap|Actora Roadmap]] depend on current patch numbers if dependency order is all that matters
	•	assume source docs and repo docs automatically stay in sync without deliberate updates

If a patch lands and only implementation history changed, update repo docs as needed and leave the stable source stack alone.

When baseline truth changes meaningfully:
	•	revise the relevant stable doc deliberately
	•	do not leave contradictions hanging

⸻

10. Stable-doc revision rule

Revise stable docs when:
	•	project identity changes meaningfully
	•	architecture baseline changes meaningfully
	•	workflow rules change meaningfully
	•	roadmap dependency order changes meaningfully
	•	source-role definitions change meaningfully
	•	stable docs no longer match the approved baseline

Do not revise stable docs just because:
	•	a new idea sounds cool
	•	wording can be polished forever
	•	a flexible working doc got larger
	•	a temporary discussion happened
	•	a patch landed that only changed implementation history

Actora should periodically check whether stable docs still match the evolving approved baseline before major rewrites or milestone planning.

⸻

11. Versioning rule

Versioning should reflect real change, not ceremony.

General interpretation:
	•	major = large phase shift
	•	minor = meaningful foundation piece or meaningful stable-doc revision
	•	patch = cleanup, polish, correction, smaller improvement, or flexible-doc refresh

For code:
	•	commits happen after apply and verification
	•	tags may be used for known-good milestone restore points
	•	meaningful milestones should prefer plain version tags rather than descriptive sentence tags

For docs:
	•	stable docs should be versioned when their durable content changes meaningfully
	•	flexible docs may be updated more often and should not create needless maintenance burden
	•	repo docs may change whenever implementation history or repo-facing clarification requires it

11.1 Patch lifecycle rule

Use this default lifecycle for automated patch work:

open patch -> define spec -> choose execution path -> run worker or direct edit -> review -> approve when required -> verify on VPS -> update docs if needed -> commit -> tag if appropriate

Do not tag unverified work.
Do not treat “tool said done” as a release condition.

⸻

12. Naming and architecture caution

Actora should not let temporary implementation naming harden into permanent architecture truth.

Current implementation may sometimes remain narrower than the long-term baseline, but review work should check for:
	•	misleading human-only assumptions
	•	false universality in class or concept names
	•	location flattening
	•	ownership/residence/current-location conflation
	•	actor/playability conflation
	•	actor overload
	•	metrics being treated like entities
	•	UI-driven architecture shortcuts
	•	bypassing the link layer with random actor-owned relationship fields

Do not force immediate refactors without a clear spec.
Do not ignore conceptual misfits either.
Flag them, classify them, and place them correctly in the workflow.

⸻

13. Foundation-first implementation rule

The prototype should be the best foundation for the future product, not a narrow structure that later has to be escaped.

That does not mean implementing every future idea now.
It means current work should avoid hard-baking assumptions that contradict the approved baseline, including:
	•	human-first architecture
	•	one-detail-level-for-everything simulation
	•	flattened location/ownership/residence semantics
	•	terminal-only design assumptions
	•	throwaway history handling
	•	link structure ignored in favor of random fields
	•	actor state becoming a dumping ground for every new subsystem

Protect future-safe architecture now.
Implement future systems only when sequencing allows it.

⸻

14. Interaction with the roadmap

When evaluating a proposal, ask:
	•	does this fit the current layer or milestone?
	•	does it require later foundations first?
	•	is this real structural work or just exciting expansion?
	•	should this be implemented now, parked for later, or promoted into stable docs?

If roadmap order and a tempting idea conflict, the roadmap wins unless the stable baseline truly changed enough to justify a roadmap revision.

Do not use one exciting idea to bypass dependency order.

⸻

15. Working ideas rule

The [[working-ideas-register|Working Ideas Register]] is the intake / filter / staging layer.

Use it for:
	•	good ideas that do not fit the current milestone
	•	unresolved architectural tensions
	•	rewrite pressures
	•	future systems that should be remembered without being implemented now

Use the [[actionable-summary|Actionable Summary]], if maintained, as a temporary planning snapshot rather than durable truth.

Promotion rule:
Only move an idea into a stable source when it is durable enough to be relied on by default.

Do not mark anything:
	•	implemented unless it is actually built and verified
	•	incorporated into stable docs unless it is actually reflected in the stable source stack

⸻

16. Reporting expectations after apply

After an applied patch, report only what matters:
	•	files changed
	•	exact applied behavior change
	•	exact preserved behavior
	•	conflicts, uncertainties, or incomplete parts
	•	VPS verification status if relevant
	•	documentation updates performed or still needed
	•	readiness for commit, tag, or follow-up review if relevant
	•	which execution path was used if that matters for trust or review depth

Do not inflate reports with vague victory language.
Do not claim broad completion beyond the approved scope.

⸻

17. Final discipline rule

Actora should be worked on with:
	•	source alignment
	•	explicit scope control
	•	intentional execution-path choice
	•	preserved validated behavior
	•	real review before acceptance
	•	VPS-grounded verification
	•	deliberate documentation updates
	•	honest distinction between what exists, what is approved, and what is only being explored

That discipline is part of the project foundation, not administrative overhead.

⸻

18. Player-facing text rule

All text visible to the player should read like a game, not like a developer tool or database interface.

The current implementation is human-only. Player-facing text should assume a human life experience until other species actually exist in the game.

Forbidden in player-facing text:
	•	internal field names (actor, entity, structural_status, record_type, link_type, bootstrap)
	•	architecture jargon (continuation target, continuation candidate, connected actors, jurisdiction, world body, focused actor)
	•	dev-facing abbreviations or labels that leak implementation structure

Use instead:
	•	"you" or the character's name, not "actor" or "focused actor"
	•	"family" or "family members," not "connected actors" or "linked actors"
	•	"choose who to continue as," not "select continuation target"
	•	"country," not "jurisdiction" (on Earth)
	•	"planet," not "world body" (on Earth)
	•	human-natural phrasing that assumes the player is living a life, not inspecting a simulation

Internal code, comments, architecture docs, and variable names may still use the full internal vocabulary. Only the rendered display text must follow this rule.

When dispatching implementation work, include this rule in the prompt or reference it explicitly so automated workers do not reintroduce internal jargon into player-facing surfaces.
