---
title: Changelog
tags: [implementation, reference, stable]
updated: 2026-04-04
---

# Actora Changelog

## Version 0.48.3 (Patch) - 2026-04-05
- **Stat redesign implemented (DEC-021):**
    - Creativity renamed Imagination in Human.stats, human.py, world.py, events.py, main.py
    - Memory (40-70 starting range) and Stress (5-20 starting range) added to Human stats
    - Profile screen now displays Imagination, Memory, Stress
    - human.py missed by Codex — fixed manually
    - codebase.md synced, bugs.md updated with trait-gated event stale note

## Version 0.48.2 (Patch) - 2026-04-05
- **Trait pool redesigned (DEC-022):**
    - New 12-trait pool: Driven, Chill, Curious, Social, Disciplined, Impulsive, Empathetic, Resilient, Introverted, Extraverted, Restless, Ambitious
    - Creation changed from pick-3 to pick-4
    - Wizard traits step updated (footer, validation, counter)
    - Questionnaire still outputs old pool — update pending (backlog Now)
- **Documentation overhaul:**
    - Full character system design interview captured in design.md
    - Stats redesign (13 stats, DEC-021), Traits redesign (DEC-022), Skills/Talents (DEC-023), Needs/Drives (DEC-024), Mood (DEC-025), Skip time limit (DEC-026), Reputation direction (DEC-027)
    - New system anchors in design.md: Skills & Talents, Needs & Drives, Mood, Profile Dashboard, Physical Conditions
    - Identity glossary expanded, roadmap updated, rules expanded

## Version 0.48.1 (Patch) - 2026-04-04
- **Logo panel header:**
    - ASCII logo centered in header with left and right info panels flanking it via `║` dividers
    - Left panel (right-aligned): date top, actor name, screen name
    - Right panel: location top, health, money
    - Placeholder logo: "actora" in script-style ASCII font (to be replaced with proper logo design)
    - Tab bar overlap fixed (moved to correct row after header)
- **Bugs fixed in shell v2:** browser tab bar row collision resolved

## Version 0.48.0 (Minor) - 2026-04-04
- **Shell v2 — new balanced header/footer structure:**
    - Row 0: `══ Actora ══` title (full terminal width)
    - Row 1: `Screen  │  Actor  │  Date` subtitle (content width)
    - Row 2: separator (full width)
    - Row 3: state line — city, country left; Health + money right
    - Row 4: separator (full width)
    - Body rows
    - Row N-2: separator (full width)
    - Row N-1: primary commands footer (centered)
- **Esc opens Options on all non-Life View screens:** Browser, Actions, Profile, Skip Time, Death, Continuation, Continuation Detail
- **Browser tab bar** moved to rows 5/6 to clear the new header rows (was overlapping separator)
- **City footer** now correctly says `[Enter] Select City` instead of `[Enter] Continue`
- **Continuation no-candidates:** removed redundant `"No one is available to continue."` body text and `[Bsp] Back to death summary` hint
- **Actions screen queued section:** Queued actions now displayed in lower half of Actions column, below available actions, with divider separator. Shows `(nothing queued)` when empty.
- **Bug logged:** Skip Time custom `0` advances 1 month — see bugs.md

## Version 0.47.2 (Patch) - 2026-04-04
- **Bug fix:** `gender_choice_offered` was missing from `ActoraTUI.__init__` — caused crash on first gender popup during play
- **Polish:** continuation no-candidates screen removed stale "Press B / Q to quit" text — now shows `[Bsp] Back to death summary`
- **Doc sync:** full pass across all 12 docs — codebase, decisions, design, screens, rules, backlog, guide updated to match v0.47.x reality

## Version 0.47.1 (Patch) - 2026-04-04
- **Wizard polish:**
    - Last name is now required for humans (was previously optional)
    - Error message: "First and last name are required."
    - Identity step: Esc triggers quit confirmation (Backspace is text-input only)
    - Identity step footer: `[Esc] Quit` replacing `[Bsp] Quit`
    - Traits step: removed "exactly" from trait count wording
    - Location footer: separate hints for country and city sub-states
    - Questionnaire footer: `[Enter] Continue` replacing `[Space] Select`
- **Popup polish:**
    - Options popup box widened; hint now fits properly
    - Menu popup box widened; hint now has correct `[ ]` brackets
    - Both popup hints: `[↑↓]`, `[Enter]`, `[Bsp]`, `[Esc]` brackets consistent
    - Pending choice popup hint: `[Enter] Select` replacing `[Space] Select`
    - Quit confirmation hint: `[Bsp] Back` replacing `[Bsp] Cancel`
    - Backspace on quit confirmation (when opened from Options) returns to Options
- **Life View footer:**
    - Added second `|` divider: `[1] Menu  |  [Esc] Options`
- **Actions footer:**
    - Removed `D/A` from focus hint — arrows only shown
- **controls.md synced:**
    - Wizard Esc exception documented (identity step only)
    - Quit confirmation Backspace semantics documented

## Version 0.47.0 (Minor) - 2026-04-03
- **Actions screen redesigned — three-column layout:**
    - Categories column (left): lists action categories; focus starts here on open; W/S navigates, D/→ moves to Actions
    - Actions column (middle): shows actions for selected category; W/S navigates, A/← returns to Categories, Enter activates
    - Details column (right): shows action description and context; updates live as Actions selection changes
    - For Hang Out: Details shows "who you can hang out with" — name and relationship tier
    - Enter on Hang Out opens friend selection popup (existing pending-choice system)
    - D/→ blocked if category has no actions — no navigating into empty columns
    - Screen resets focus to Categories on every open
    - Footer updated: `[↑↓] Move   [←→/D/A] Focus   [Enter] Select   [Bsp] Back   [Q] Advance`
    - Categories data structure: hardcoded list per actor state, easy to extend with new categories

## Version 0.46.2 (Patch) - 2026-04-03
- **Wizard quit path (option B):**
    - Backspace on empty first-name field triggers quit confirmation
    - Backspace on sex select field returns to name field (or quit if already at top)
    - Quit confirmation: Enter confirms quit, Backspace cancels back to wizard
- **Options popup implemented:**
    - Esc now opens a real centered Options popup instead of jumping straight to quit confirmation
    - Popup contains Quit Game, Help / Controls, and Settings
    - W/S or ↑↓ navigate, Enter selects, Esc closes
    - Help / Controls and Settings are currently display-only and dimmed
    - Quit Game routes into the existing quit confirmation
- **Space/Enter contract cleanup:**
    - Removed Space-as-confirm from wizard location selection
    - Removed Space-as-confirm from questionnaire choice selection
    - Pending choice popup now confirms with Enter instead of Space
    - Removed Space as adjustable field alias in wizard appearance step
- **Hidden hotkey cleanup:**
    - Removed undocumented G alias for year-jump in History (/ only, per contract)
- **Polish:**
    - Added [Bsp] Quit hint to wizard identity step footer

## Version 0.46.1 (Patch) - 2026-04-03
- **Menu popup complete:**
    - [1] opens a centered Menu popup with Browser / Actions / Profile items
    - W/S or ↑↓ navigate items; 1/2/3 fast-select; Enter opens; Backspace closes
    - Hint line added showing controls inside popup
- **Legacy letter keys removed:**
    - L/H/T/P removed from Life View (now accessed via [1] Menu)
    - L (living filter) and T (hang out) shortcuts removed from their respective screens
    - Hang Out is display-only in Actions until Actions gets full selection state
- **Polish:**
    - `[T]` label removed from Hang Out in Actions screen


- **Control Contract v2:**
    - Q = advance month (all non-input screens; blocked in: text input, search, popups, wizard, continuation, death screen)
    - E = skip time (same blocks as Q)
    - Backspace = universal Back (replaces B everywhere in navigation)
    - Esc = Options popup stub (opens quit confirmation until Options popup exists; Esc toggles it closed)
    - [1] = Menu stub (opens Browser until Menu popup exists)
    - WASD = full movement aliases for arrow keys (W/A/S/D = ↑/←/↓/→; WASD type characters in text input)
    - Enter-as-advance removed — Enter is now proceed/confirm only
    - Q-as-quit removed from all game screens (wizard has no quit path per contract)
    - B-as-back removed from all game screens (Backspace only)
    - Q blocked in popup/death/continuation/wizard handlers
    - All `[B] Back` footer labels → `[Bsp] Back`
    - All `[Q] Quit` footer labels removed from game screens
    - Esc toggles Options popup correctly (was not closing on second press)
    - Q blocked while popup/choice overlay is active
- **Polish:**
    - `Name:` indentation fix on wizard confirm screen (`.strip()` was stripping leading spaces)
    - Redundant body controls hint removed from continuation detail screen


- **Major documentation system rework:**
    - Flat `docs/` directory — killed all subfolders (`core_architecture/`, `planning/`, `workflow/`).
    - Renamed docs to clear names: master-context→identity, actora-roadmap→roadmap, vision-and-systems→design, ui-architecture→screens, tui-standards→controls, architecture→codebase, hotkey-control-workbook→hotkey-workbook.
    - New docs: `guide.md` (single navigation/workflow doc), `rules.md` (all project constraints), `backlog.md` (Now/Next/Later), `bugs.md` (actual bugs only), `decisions.md` (ADR-style immutable decision log, 11 entries).
    - Killed: source-index (472 lines), operator-guide (628 lines), working-ideas-register, actionable-summary, live-issues, README.md.
    - Trimmed: identity.md (516→143), roadmap.md (536→123), design.md (224→200).
    - Added: glossary in identity.md, routing table in guide.md, review checklist in rules.md, versioning rules, cascade check rule, heartbeat system.
    - Net result: 13 docs, ~2200 lines of bloat removed, no contradictions, no duplicate content.
    - All wikilinks updated to new doc names. Tags added to all docs for Obsidian.

## Version 0.45.0 (Minor) - 2026-04-01
- **Non-family Relationships + Action Foundation:**
    - Added acquaintance/friend/close_friend link types with numeric closeness score (0–100).
    - Player-initiated meeting events — popup choice to introduce yourself or keep to yourself.
    - NPCs generated at meeting with culture-aware names, plausible age/stats/traits.
    - Closeness decay per month with history-based resistance (long friendships decay slower).
    - Drift events fire when closeness hits 0; link archived with `status: former`.
    - Friend deaths affect player happiness scaled to closeness.
    - Social links folded into existing Relationships section in Life View left panel (name · tier).
    - `[T]` opens a dedicated Actions screen — pending actions + available social actions.
    - "Spend time with friend" action queues and resolves on next advance.
    - Relationship Browser replaces Lineage Browser — now a tabbed Browser screen.
    - `[L]` opens Browser on Relationships tab; `[H]` opens Browser on History tab.
    - Browser Relationships tab: persistent filter sidebar (All/Family/Friends/Past/Living/Dead), search restored.
    - Browser shell now renders a bottom divider under the Relationships/History tab row so the tabs read as browser chrome rather than body content.
    - Continuation candidates now exclude former social links, so drifted relationships no longer leak into handoff options.
    - Adult continuation handoffs silently auto-resolve identity state without firing gender/sexuality popups, while ordinary played-life popup behavior remains intact.
    - Life View idle status text no longer reuses the footer control hint, fixing the `A/Enter advances one month.` leak.
    - NPC last-name collision fix — generated friends no longer share player surname.
    - Main footer updated: `[A] Advance Month   [S] Skip Time  |  [L] Browser   [T] Actions   [P] Profile   [Q] Quit`.
    - tui-standards.md updated with new navigation map.

## Version 0.44.0 (Minor) - 2026-03-31
- **Arrow standard + popup fix:**
    - Stats screen active field now renders `← value →` — consistent with identity and appearance fields.
    - All adjustable value fields (`←→`) now visually show `← value →` when active. This is the enforced standard across all screens.
    - Popup choices (gender/sexuality emergence) now only respond to Space — Enter is fully blocked while a popup is active. Fixes held-Enter during month advancement eating popups silently.
    - Removed now-dead `pending_choice_input_guard` flag (replaced by hard Enter block).
    - Updated TUI Standards: `←→` applies to all adjustable fields (not stats-only), popup Enter block rule documented, `← value →` rendering requirement documented.

## Version 0.43.0 (Minor) - 2026-03-31
- **Playtest Polish Round 2:**
    - Appearance select fields now show `← value →` on the active row, consistent with identity fields.
    - "First name is required." only appears after a failed continue attempt; hidden otherwise.
    - Removed redundant "Use ←→ to change listed values." hint from appearance screen.
    - Custom appearance field (Other) now shows inline prompt e.g. `Type custom skin tone:` instead of generic warning.
    - Questionnaire question text rendered in uppercase with extra blank line for visual weight.
    - Popup input guard added: first Enter/Space after a gender/sexuality popup is created is consumed to prevent held-Enter eating the popup.
    - History browser year dividers now have a blank line before and after for breathing room.
    - Continuation screen: "No one is available to continue as." → "No one is available to continue." and "quit this run" → "quit the game."
    - Left panel in main Life View now scrollable in preparation for relationship/job/education growth.

## Version 0.42.0 (Minor) - 2026-03-31
- **Playtest Bug Fixes & Audit Fixes:**
    - Fixed sex field not visually indicating it's adjustable — now renders `← Male →` when active.
    - Fixed trait leak bug: completing the questionnaire then switching to manual mode no longer pre-populates the manual traits screen with questionnaire-derived traits.
    - Added visual separator between question text and answer options in the questionnaire screen.
    - Updated main TUI footer: `[A] Advance Month   [S] Skip Time  |  [P] Profile   [L] Lineage   [H] History   [Q] Quit`.
    - Fixed crash in `render_continuation_detail` when actor data is missing — now renders a safe fallback instead of crashing.
    - Fixed `TypeError` in `build_record_summary_lines` when year or month is `None` — now falls back to `0`.
    - ESC now works as back in the questionnaire (mirrors B/backspace behavior).
    - Enter now advances the questionnaire (previously only Space worked).
    - Enter now confirms in-game pending choice popups (previously only Space worked).

## Version 0.41.0 (Minor) - 2026-03-31
- **TUI Polish and Cleanup:**
    - Unified TUI control language and footer labels across wizard and in-game screens.
    - Clarified and enforced a stronger selection rule: single-choice lists use live highlight selection, `[x]` markers are reserved for true multi-select/toggle screens, and single-choice value fields now use direct `←→` cycling instead of nested option choosers.
    - Added quit confirmation prompt on `Q` to prevent accidental exits.
    - Fixed a custom-appearance input regression so `Backspace` erases typed text instead of unexpectedly leaving the appearance step, aligned the identity sex row with the direct-adjust value-field pattern, and cleaned up continuation wording/doc flow descriptions to match current behavior.
    - Questionnaire now allows backtracking with `B`; on question 1, `B` returns to mode selection.
    - Flattened the appearance selection flow to use direct `←→` row adjustment instead of nested option submodes.
    - Removed `banners.py` and all banner rendering: startup ASCII art title and post-exit quit banner are gone; `start_game()` now goes straight to the creation wizard with no pre-curses output.

## Version 0.40.1 (Minor) - 2026-03-30
- **Questionnaire-Based Character Creation Mode:**
    - Added `QUESTIONNAIRE_QUESTIONS` in `main.py` with 16 one-at-a-time personality prompts, per-answer stat deltas, and optional trait suggestions for a new alternative startup flow.
    - Inserted a creation-mode selection step into the curses `CreationWizard` after appearance so players can choose questionnaire-based generation or the existing manual setup path.
    - Added a questionnaire-only startup branch in `main.py` that runs without backtracking, starts all creation stats at `50`, applies cumulative answer effects with final `0-100` clamping, and derives the top three traits from suggested-trait frequency with random tie breaks/fill.
    - Kept the confirm screen and output payload shape unchanged so the generated questionnaire result still hands the same `appearance`, `traits`, and `stats` data into ordinary world setup without simulation-core changes.

## Version 0.40.0 (Minor) - 2026-03-30
- **Real Location Content + Culture-Aware Name Generation:**
    - Replaced the placeholder startup geography in `main.py` with module-level `WORLD_GEOGRAPHY`, adding `Earth`, 12 real countries, and their configured real cities to the world place registry at startup.
    - Inserted a new `Location` step into the curses `CreationWizard` between Identity and Appearance, storing `country_id` and `city_id` in the startup character payload and shifting the remaining step indexes accordingly.
    - Updated `setup_initial_world_from_character(...)` to place the player, parents, and startup siblings in the selected real city/country while preserving the existing compatibility wrapper `setup_initial_world(...)`.
    - Added `CULTURE_NAME_POOLS` in `identity.py` with culture-specific mother names, father names, and surnames for the configured country culture groups, and threaded `culture_group` through the parent identity context helpers with fallback to the older global pools.
    - Verified the existing profile/location display path continues to resolve real place names through the world place registry without new simulation systems.

## Version 0.39.1 (Minor) - 2026-03-30
- **Traits Wired Into Monthly Events:**
    - Added `required_traits` support to human monthly event definitions in `events.py`, preserving the existing event contract while allowing trait-gated eligibility.
    - Extended human monthly event selection to accept actor traits and exclude trait-gated events unless the focused actor has at least one required trait.
    - Passed the focused actor's `traits` from `World.simulate_advance_turn(...)` into monthly event selection so personality now affects which events can surface.
    - Added 20 new trait-gated monthly events across life stages, covering Curious, Calm, Fussy, Bold, Shy, Cheerful, Stubborn, Gentle, Restless, and Alert.

## Version 0.39.0 (Minor) - 2026-03-30
- **Event-Choice Framework + Gender/Sexuality Identity Emergence:**
    - Added a general-purpose pending-choice popup overlay to the curses TUI in `main.py`, with centered boxed rendering, selection movement, skip support, and full input capture while a choice is active.
    - Routed time advancement in `ActoraTUI.advance_time(...)` through TUI-owned month-by-month stepping so long skips now pause immediately when a major choice appears, preserving the existing world simulation boundary.
    - Added adolescence identity-emergence events for the focused actor: a gender identity choice in the teen years and a sexuality choice in the later teen years, both surfaced during ordinary play and written into the live event log/history.
    - Extended `Human` in `human.py` with a `sexuality` field, randomized sexuality for non-player generated humans, and exposed sexuality through the snapshot identity payload.
    - Updated the `Profile` screen in `main.py` to show sexuality alongside sex and gender, with a `"Not yet known"` fallback before the player-facing emergence event has happened.
    - Reset TUI-owned identity-choice offer flags on continuation handoff so the next focused life can surface its own adolescence identity moments when applicable.

## Version 0.38.1 (Minor) - 2026-03-30
- **Character Creation Wizard + Appearance + Traits:**
    - Replaced the old plain-text startup `create_character()` flow in `main.py` with a curses-based `CreationWizard` that now runs inside the same overall TUI visual system before ordinary play begins.
    - Added step-by-step startup creation for identity, appearance, traits, stat allocation, and confirmation, including `Other` appearance text entry, exact-three trait selection, and stat randomization from the existing newborn ranges.
    - Added stored `appearance` and `traits` fields to `Human` in `human.py`, randomized them for non-player generated humans, and exposed both through `get_snapshot_data(...)`.
    - Updated the `Profile` screen in `main.py` to show appearance and trait sections between identity and stats.
    - Added `setup_initial_world_from_character(...)` in `main.py` so startup world creation can accept a fully prepared character payload while preserving the old `setup_initial_world(...)` wrapper for compatibility callers and tests.
    - Verified existing startup-family randomization still routes parent and sibling creation through `Human.randomize_starting_statistics()`, so generated relatives continue to receive both primary and secondary randomized stats.

## Version 0.38.0 (Minor) - 2026-03-30
- **Actor Stats Deepening + Profile Screen:**
    - Expanded `Human.stats` in `human.py` beyond the existing primary stats to include `strength`, `charisma`, `creativity`, `wisdom`, `discipline`, `willpower`, `looks`, and `fertility`, all with newborn-oriented randomized starting ranges.
    - Extended `Human.get_snapshot_data(...)` so the existing `statistics` block stays Life View-focused while a new `secondary_statistics` block exposes the deeper actor card data for richer shell surfaces.
    - Added a new `Profile` screen to the curses TUI in `main.py`, opened from Life View with `P`, showing identity, primary stats, secondary stats, location, and living-family relationships in one scrollable actor detail view.
    - Updated screen chrome and main footer hints in `main.py` to include the new `Profile` surface and shortened the main skip label to `[S] Skip`.
    - Deepened a small set of existing monthly event outcomes in `events.py` so ordinary life events now also produce small secondary-stat effects without changing event selection logic or the structured event contract.

## Version 0.37.7 (Patch) - 2026-03-30
- **Continuation + Event Log Cleanup:**
    - Updated three duplicate monthly event texts in `events.py` to keep the full 100-event pool while removing repeated player-facing copy.
    - Fixed `ActoraTUI.choose_continuation()` in `main.py` so successful continuation handoff now also updates `self.player_id` to the new focused actor instead of leaving the shell pointed at the dead original actor ID.
    - Added a shell-owned `life_separator` event-log entry after continuation handoff, rendered in both the live feed and full history view so multi-life runs read as distinct chapters.
    - Reset `last_logged_year` on continuation so year headers begin cleanly for the new focused life without changing simulation-core behavior or handoff order.

## Version 0.37.6 (Patch) - 2026-03-30
- **Playtest Follow-Up Fixes:**
    - Increased the main-screen advance-key hold throttle in `main.py` from 100ms to 200ms so held `A` / `Enter` advances less aggressively during ordinary play.
    - Added a shell-owned year-jump mode to the `History` browser in `main.py`, opened with `/` or `G`, with digit input, `Backspace`, `Enter`, and `Esc`, clamped to `1..current simulation year`, and falling back to the nearest available logged year header when the exact year is absent.
    - Updated `main.py` History footer hints so normal browsing now advertises `[ / ] Jump to Year`, while active year-jump mode shows the dedicated input hint strip.
    - Made the continuation footer in `main.py` dynamic so it only shows `[Enter] Inspect` when continuation candidates actually exist, and collapses to `[Q] Quit` when none do.

## Version 0.37.5 (Patch) - 2026-03-30
- **Playtest Bug Fixes:**
    - Updated all family-aware monthly event text in `events.py` to refer to relatives by role (`Your mother`, `your brother`, etc.) instead of rendering full names, and normalized `{family_role}` substitution to lowercase during event text rendering.
    - Fixed `main.py` history-browser footer rendering so the scroll indicator now reserves its own line and no longer overlaps the last visible history entry.
    - Changed shell event-log population in `main.py` to merge focused-actor monthly events with newly written `birth` and `death` records by simulation date before appending, preserving chronological order and year-header placement; structural live-feed entries now also show their actual year as `[Year N]`.
    - Added a 100ms `time.monotonic()` throttle to the main-screen advance action in `main.py`, preventing held `A`/`Enter` input from immediately punching through the death acknowledgment screen or causing excessive redraw jitter while leaving other navigation input unchanged.

## Version 0.37.4 (Patch) - 2026-03-30
- **History + Lineage Polish:**
    - Added structural event markers in `main.py` so focused-actor `birth` and `death` records carried into the shell-owned event log now render as `★` and `✦` in both the full `History` browser and the live right-pane feed, while ordinary monthly events remain unmarked.
    - Verified the Life View `Relationships` section already handles the new list-based snapshot data correctly and continues to show `No living family.` whenever the structured relationships list is empty.
    - Verified skip-time back UX in `main.py`: both `[B]` and `Esc` return immediately to the main screen, and `open_skip_time()` still resets preset selection and custom typed months each time the screen is reopened.

## Version 0.37.3 (Patch) - 2026-03-30
- **UX Cleanup + Event Quality:**
    - Reset Life View status text back to the default idle prompt when backing out of history, lineage, or skip-time, while preserving the existing advance-time and continuation-handoff messages.
    - Kept the existing left-pane scroll hint behavior in `main.py`, which already shows a `More details:` indicator on first render whenever Life View content exceeds the visible area.
    - Added a simple per-turn monthly-event cooldown in `events.py` and `world.py`, excluding the last three triggered event IDs during one `simulate_advance_turn(...)` run but falling back to the full eligible pool if cooldown would empty it.
    - Expanded the human monthly event pool with more infant and teenager coverage plus additional family-aware, goofy, and slightly darker grounded events without changing the event-result contract.

## Version 0.37.2 (Minor) - 2026-03-30
- **Life View Relationships + Event-Pool Thickening:**
    - Changed `Human.get_snapshot_data(...)` so Life View relationships now derive from all current outgoing `family` links, dedupe linked actors, skip dead relatives, and emit a structured list of living family entries instead of fixed `mother_name` / `father_name` fields.
    - Updated `main.py` Life View rendering to iterate the new relationships list directly and show `No living family.` when no linked living relatives are present.
    - Expanded `events.py` from the original 32 human monthly events into a much thicker grounded pool across all life stages, keeping the original events while adding more mundane, mixed-tone, and occasionally goofy life texture with small varied outcomes and some zero-effect events.
    - Added optional event-definition support for `family_context` and `family_roles`, allowing some monthly events to require living family and render actual relative names into event text.
    - Updated `World.simulate_advance_turn(...)` to build current living sibling/parent event context and pass it into monthly event selection without changing mortality, continuation, lineage, history, or skip-time flow.

## Version 0.37.1 (Minor) - 2026-03-30
- **Scrollable Event History Log:**
    - Replaced the Life View right pane in `main.py` with a shell-owned accumulating live event feed that now persists meaningful events, skip markers, and year headers across the full run instead of only summarizing the latest turn.
    - Added a full-screen `History` browser opened from Life View with `[H]`, auto-positioned at the newest entries and scrollable with `↑↓` while preserving existing lineage, skip-time, death, and continuation flows.
    - Expanded shell-side event-log population so focused-actor structured events plus newly written relevant `birth` and `death` records from each advance are folded into the same history stream while filtering hidden scaffolding record types (`family_bootstrap`, `actor_entry`).
    - Updated screen chrome and footer hints to include the new history surface and the revised main hint strip (`[A] Advance   [S] Skip Time   [L] Lineage   [H] History   [Q] Quit`).

## Version 0.37.0 (Minor) - 2026-03-30
- **Death / Continuation Inspectability Follow-Through:**
    - Filtered implementation-scaffolding records (`family_bootstrap`, `actor_entry`) out of player-facing lineage detail and death/continuation inspect surfaces while preserving the records in world storage.
    - Simplified lineage, death interrupt, and continuation header subtitles so they now show only the focused actor name instead of leaking flow-spec phrasing into the chrome.
    - Reworked continuation list rows in `main.py` to a tighter one-line format of name, relationship, age, and place, and removed the extra continuation heading.
    - Added a brief life-summary retrospective to the death interrupt showing age at death, place at death, key end-of-life stats, and recent meaningful records.
    - Changed continuation selection to a two-step inspect-first flow with a dedicated candidate detail screen, explicit confirm/back actions, and recent meaningful records before handoff.
    - Tightened world-owned parent continuation labels so family parents now render as `Mother` / `Father` instead of generic `family/mother` / `family/father`.

## Version 0.36.9 (Minor) - 2026-03-30
- **Family Continuity Groundwork:**
    - Expanded startup family generation so some runs now begin with one or more older siblings created as real actors before the player is born, while only-child starts still remain common.
    - Replaced the fixed startup parent ages in `main.py` with a narrow randomized parent-age range so sibling plausibility and later family births are not detached from parent age truth.
    - Extended `World.create_human_child_with_parents(...)` so it can serve both startup family bootstrap and ordinary family births without falling back to fake placeholder relatives.
    - Added direct sibling link creation in `world.py` based on shared parents, so siblings are first-class close family actors that show up in lineage truth and continuation truth through the same current actor/link depth as parents.
    - Added a narrow world-owned monthly family-event seam that checks current coparent pairs, applies explicit simple fertility heuristics with age/spacing/family-size factors, and can produce later younger sibling births in the background.
    - Surfaced later sibling births to the focused actor only when they are directly meaningful, while otherwise leaving them as quiet background family records.
    - Tightened lineage/continuation relationship labeling so siblings now render with simple direct labels (`Brother` / `Sister`) and continuation ordering now prefers siblings ahead of less-close family/other linked actors by default.

## Version 0.36.8 (Minor) - 2026-03-29
- **Ordinary Mortality / Old-Age Death Truth:**
    - Added world-owned monthly old-age mortality in `world.py` so living actors now face baseline later-life death risk during ordinary simulation instead of surviving indefinitely by default.
    - Resolved mortality across all living actors each simulated month, not only the focused actor, so family-lineage truth can accumulate ordinary deaths as world time advances.
    - Used the simple first-pass death reason `Old age` and preserved it through the existing structural death flow, continuity state, and death record metadata.
    - Stopped skip-time advancement honestly when the focused actor dies mid-jump, with `simulate_advance_turn(...)` now reporting actual `months_advanced` instead of pretending the full request completed.
    - Strengthened death/history truth by freezing dead lineage ages at death time and by writing cause text into death records when a cause is known.

## Version 0.36.7 (Patch) - 2026-03-29
- **Life View + Lineage Usability Cleanup:**
    - Reworked the main alive-state TUI in `main.py` into a lighter split `Life View`, keeping identity/location/stats/relationships on the left and recent activity on the right so events remain visible during ordinary play.
    - Added simple vertical scrolling for the left-side Life View info stack so lower-priority sections like relationships are no longer silently cut off under tighter terminal heights.
    - Slimmed lineage browser rows down to name, relationship, alive/dead status, and age for faster scanning and less truncation noise.
    - Clarified lineage identity formatting in the detail pane with explicit labeled lines for `Species`, `Sex`, and `Gender`.
    - Fixed lineage search-mode exit handling so `Esc` cancels search first instead of immediately behaving like a full lineage back action.
    - Reduced visible dependence on `Esc` for back navigation by promoting `[B] Back` in lineage and skip-time footer hints while keeping `Esc` as a compatibility path.
    - Added `docs/planning/live-issues.txt` as a repo-local place to track current bugs, regressions, and revisit items without losing them between patches.

## Version 0.36.6 (Patch) - 2026-03-29
- **TUI Visual-System Consistency Pass:**
    - Reworked the current curses shell in `main.py` around a stronger centered visual system with a centered `Actora` header rule, centered subtitle/date rhythm, and more deliberate content-column composition instead of dumping most screens against the left edge.
    - Switched footer hints to a bracketed action language (for example `[A] Advance   [S] Skip Time   [L] Lineage   [Q] Quit`) so major screens now share a clearer interaction grammar.
    - Renamed the main alive-state screen from `Ordinary Play` to `Life View` and tightened screen-specific layout rhythm across ordinary play, lineage browsing, skip-time, death interrupt, and continuation flow without moving startup into curses.
    - Removed the heavy box dependence introduced by the lineage browser foundation and replaced it with lighter centered layout composition plus a narrow vertical divider, preserving compact one-line lineage rows while making the browser/detail split easier to read.
    - Strengthened spacing rhythm in ordinary play, made continuation/death utility screens feel more staged, and preserved current functionality across startup, lineage filters/search, skip-time flow, death acknowledgment, and continuation selection.
    - Fixed visual-pass follow-up issues before release, including skip-time highlight indexing and a small helper-shape cleanup in the centered column splitter.

## Version 0.36.5 (Patch) - 2026-03-29
- **TUI-Aware Repo Cleanup / Shell-Era Drift Reduction:**
    - Removed the dead `TIME_ADVANCED_BANNER` constant from `banners.py` since ordinary advancement and skip-time now live inside the TUI and the old shell-era banner path is gone.
    - Clarified startup-vs-curses boundary wording in `main.py` so the transition from plain-text startup into the curses shell is no longer ambiguously documented.
    - Tightened repo-local comments and file-level documentation to reflect that Actora is now TUI-driven in ordinary play rather than typed-command-driven.
    - Preserved all current TUI behavior, lineage browsing, skip-time flow, death/continuation handling, and simulation-core ownership.

## Version 0.36.4 (Patch) - 2026-03-29
- **Lineage Row Truncation Hygiene:**
    - Tightened left-pane lineage browser rendering in `main.py` so lineage rows now stay single-line and truncate with an ellipsis instead of wrapping awkwardly across multiple lines.
    - Kept right-pane detail text wrapped normally, so the browser now distinguishes compact list scanning from fuller detail reading more cleanly.
    - Preserved the `v0.36.3` lineage browser behavior, filters, search flow, skip-time flow, and continuation/death handling while eliminating a small visibility bug before it could turn into normalized UI sludge.

## Version 0.36.3 (Patch) - 2026-03-29
- **Lineage Browser Foundation Strengthening:**
    - Reworked lineage browsing in `main.py` from a page-flip list/detail flow into a structured two-pane lineage browser so family-linked actors can be inspected inside one persistent archive surface.
    - Added real lineage browser modes in the TUI: `A` for all, `L` for living only, and `D` for dead only.
    - Added modest lineage name search in the TUI with `/` to start typing, `Enter` to confirm, and `Backspace` to clear, while keeping the browser shell-owned.
    - Added a small world-owned lineage browser seam through `World.get_lineage_browser_data_for(...)` plus filtered/searchable `get_lineage_entries_for(...)` access, so browser state is backed by current actor/link/record truth rather than fake TUI-only data.
    - Expanded lineage metadata and unified person-card language across lineage and continuation rendering, including status, age vs age-at-death, place, and a lightweight `family_branch_label` when current family-link roles support it honestly.
    - Kept branch/family-side interpretation intentionally narrow (`maternal`, `paternal`, `descendant`) and did not overclaim a true family-tree or archive-storage system.
    - Preserved skip-time flow, death reveal ordering, continuation handoff behavior, and the existing simulation-core ownership boundaries.

## Version 0.36.2 (Patch) - 2026-03-29
- **TUI Style / Time-Control Follow-Through:**
    - Kept the v0.36.1 curses shell foundation but restored some visual personality through a restrained styled header bar, clearer screen titling, date chrome, and small bracketed section framing instead of dumping large ASCII banners into ordinary play.
    - Restored multi-month time skipping in `main.py` through a dedicated shell-owned skip-time screen opened with `S`, while preserving `A` / `Enter` as the quick one-month path from the main actor view.
    - Added obvious preset jumps (`1`, `3`, `6`, `12`, `24`, `60` months) plus a small numeric custom-month input path so larger jumps can be chosen without typed shell commands.
    - Kept larger skips delegating to the existing world-owned `World.simulate_advance_turn(...)` seam, so advancement still processes month-by-month internally and no simulation-core rewrite was introduced.
    - Preserved current reveal-flow rules: alive-state still does not expose structural-state sludge, death still interrupts first, and continuation choices still appear only after acknowledgment.
    - Preserved lineage browsing, continuation handoff flow, and the v0.36.1 footer safety fix that avoids writing into the terminal’s last column.

## Version 0.36.1 (Patch) - 2026-03-29
- **Curses Footer Render Fix:**
    - Fixed a terminal-edge rendering bug in the new curses shell where drawing the footer to the full terminal width could raise `_curses.error: addnwstr() returned ERR` on startup in real terminals.
    - Tightened footer rendering in `main.py` to reserve the last column safely instead of writing to the full reported width.
    - Added a safe horizontal-line fallback so footer rendering does not rely on `curses.ACS_HLINE` always being present outside fully initialized curses contexts.
    - Preserved the `v0.36.0` actor-first TUI behavior, keybindings, lineage browsing, and continuity/death flow.

## Version 0.36.0 (Minor) - 2026-03-29
- **Actor-First TUI Foundation:**
    - Replaced the ordinary typed play loop in `main.py` with a narrow curses-based TUI shell for ordinary play.
    - Added a persistent actor-first main screen showing the current focused actor snapshot plus recent activity and a visible footer hint strip.
    - Moved ordinary advancement, lineage opening, lineage back-navigation, and quit flow onto keys so normal play no longer depends on typed `lineage`, `back`, or `quit` command words.
    - Added key-driven lineage browsing with highlighted selection, detail opening on `Enter`, and clean return via `Esc` / `Backspace` / `q`.
    - Preserved the important reveal flow so alive-state still does not expose the structural-state block, death still interrupts first, and continuation choices still appear only after acknowledgment.
    - Kept continuity validation, lineage/detail data access, and simulation-step ownership world-owned rather than pushing terminal concerns into `world.py` or `human.py`.
    - Did not introduce a full-screen window manager, archive-browser sprawl, new simulation systems, random mortality, or external dependencies.

## Version 0.35.4 (Patch) - 2026-03-28
- **Family Lineage / Archive Foundation v1:**
    - Added world-owned lineage access through `get_lineage_entries_for(...)` and `get_lineage_detail_for(...)`, backed by the current actor/link/record stores without introducing separate physical archive storage.
    - Added a `lineage` command to the ordinary terminal loop in `main.py` so the current focused actor context can inspect family-linked alive/dead actors through a numbered list.
    - Added a lineage detail view showing summary information plus the latest few records for the selected actor.
    - Kept alive lineage rows unmarked by default while dead rows show lifespan-style date context plus cause of death and place.
    - Preserved current death/continuity flow, current record truth, current family-link semantics, and current world-owned continuation validation.
    - Did not introduce full family-tree rendering, archive-browser overbuild, search/filter/paging systems, inheritance/funeral systems, accomplishment summarization, or random mortality.

## Version 0.35.3 (Patch) - 2026-03-28
- **Continuation Choice Inspectability Improvement:**
    - Expanded structured continuity-candidate data in `world.py` to include `age`, `life_stage`, and `current_place_name` for each living continuation target.
    - Updated dead-focus continuation rendering in `main.py` so each candidate now shows relationship label, age, life stage, and current place instead of only name plus relationship label.
    - Preserved current deterministic candidate ordering, dead-focus acknowledgment flow, and world-owned continuation validation/handoff.
    - Did not introduce archive browsing, full actor preview UI, pagination, succession weighting, or broader continuity-system redesign.

## Version 0.35.2 (Patch) - 2026-03-28
- **Character Creation Sex / Gender Expansion:**
    - Expanded human biological sex selection in `main.py` from `Male/Female` to `Male/Female/Intersex`.
    - Expanded gender selection from `Male/Female/Non-binary` to `Male/Female/Non-binary/Agender/Genderfluid/Other`.
    - Added a free-text character-creation path so selecting `Other` prompts for a custom gender identity instead of forcing a fixed label.
    - Preserved current startup flow, actor construction shape, snapshot rendering, and the absence of deeper sex/gender gameplay systems.

## Version 0.35.1 (Patch) - 2026-03-28
- **Time Presentation Cleanup:**
    - Moved `Age` and `Life Stage` out of the terminal snapshot `Time` section and into `Identity` so actor-derived lifecycle facts are no longer visually mixed with shared simulation clock data.
    - Tightened the terminal `Time` section to one explicit `Sim Date` line (`Year`, `Month`) in `main.py`.
    - Updated `Human.get_snapshot_data(...)` so the structured snapshot contract now exposes `age` and `life_stage` under `identity`, while `time` now contains only simulation date fields.
    - Updated repo-local architecture documentation to match the new snapshot contract and terminal rendering truth.
    - Preserved current simulation behavior, continuity/death handling, spatial output, statistics, family display, and the absence of broader UI redesign.

## Version 0.35.0 (Minor) - 2026-03-28
- **Dead-Focus Transition Flow Tightening:**
    - Reworked shell-level dead-focus handling in `main.py` so death now appears as a dedicated interrupt instead of a flat continuity block.
    - The shell now leads with `You are dead.`, shows the dead focused actor plus death year/month/reason when available, and explicitly states that the universe continues.
    - Added a deliberate acknowledgment step before any continuation choices are rendered.
    - Kept continuation candidate ordering, validation, and focus handoff world-owned through the existing `World.build_continuity_state_for(...)` and `World.handoff_focus_to_continuation(...)` seams.
    - Preserved ordinary alive-play snapshot output without reintroducing the structural-state block.
    - Kept no-candidate dead-focus handling clean without introducing archive browsing, paged continuation UI, persistence changes, or broader death-system expansion.

## Version 0.34.0 (Minor) - 2026-03-28
- **Controlled Spatial Identity Mutation Boundary:**
    - Added `World.update_actor_spatial_identity(...)` as the narrow world-owned mutation seam for actor `current_place_id`, `residence_place_id`, `jurisdiction_place_id`, and `temporary_occupancy_place_id`.
    - Implemented explicit validation so unknown actor IDs fail, and any provided non-`None` place ID must already exist in the world place registry.
    - Kept unspecified spatial fields unchanged through an internal sentinel-based boundary while still allowing explicit `None`, including the current `temporary_occupancy_place_id = None` case.
    - Returned a small structured result describing which spatial fields actually changed.
    - Routed `World.create_human_actor(...)` through the new seam so startup actor spatial identity setup stays world-owned without adding a broader mutation engine.
    - Preserved current startup spatial truth (`earth_city_01` current/residence, `earth_country_01` jurisdiction, temporary occupancy unset), current snapshot output, structural death/continuity behavior, and the absence of travel, migration, property, politics, or auto-coupled spatial rules.

## Version 0.33.1 (Patch) - 2026-03-28
- **Alive-Play Snapshot Structural-State Removal:**
    - Removed the ordinary-play `Structural State` section from terminal snapshot rendering in `main.py` so alive-state is no longer redundantly exposed as front UI.
    - Preserved backend structural actor state, structural death data, and continuity/death handling logic.
    - Preserved current snapshot identity/time/location/statistics/family output and current continuity rendering paths.
    - Did not introduce the fuller death-transition UI, archive browser, richer continuation paging, or time-layout redesign.

## Version 0.33.0 (Minor) - 2026-03-27
- **Spatial Identity Separation Strengthening:**
    - Added explicit actor-level `jurisdiction_place_id` and `temporary_occupancy_place_id` storage alongside the existing `current_place_id` and `residence_place_id`.
    - Extended `World.create_human_actor(...)` and `World.create_human_child_with_parents(...)` so jurisdiction and temporary occupancy can be set at creation time without changing the broader place architecture.
    - Updated startup world setup so startup mother, startup father, and startup player still live in `"earth_city_01"` while now also explicitly carrying `jurisdiction_place_id = "earth_country_01"` and leaving temporary occupancy unset.
    - Extended `Human.get_spatial_state(...)` to return separate structured current-place, residence-place, jurisdiction-place, temporary-occupancy, and ancestry-resolved current-world-body values.
    - Updated snapshot data/rendering so the shell still shows `World Body` and `Current Place`, and now also shows one clean `Jurisdiction` line.
    - Preserved current startup flow, place hierarchy, link foundation, continuity handoff behavior, and the absence of travel, property, and politics simulation systems.

## Version 0.32.0 (Minor) - 2026-03-27
- **Structured Place / Place-Hierarchy Strengthening:**
    - Added a small world-owned place query seam in `world.py` with `get_child_places(...)`, `get_place_lineage(...)`, and `get_nearest_place_of_kind(...)`.
    - Updated startup world setup in `main.py` to create a minimal honest place hierarchy: one `world_body`, one `country`, and one `city`, wired through `parent_place_id`.
    - Reassigned startup mother, father, and player `current_place_id` / `residence_place_id` values to the startup city rather than the world body.
    - Updated `Human.get_spatial_state(...)` and `Human.get_snapshot_data(...)` so snapshot `World Body` display resolves through place ancestry when the current place is lower-level, and added one explicit `Current Place` display line in the shell snapshot.
    - Preserved startup flow, continuity handoff flow, existing link behavior, and the current shell loop.
    - Did not introduce travel, movement simulation, property/household systems, country-depth simulation, politics/jurisdiction systems, spatial-identity expansion, or map UI.

## Version 0.31.0 (Minor) - 2026-03-27
- **Link Foundation Strengthening:**
    - Added `_build_link_record(...)` in `world.py` so world-owned links are normalized at creation time and always store `metadata` as a dictionary.
    - Updated `add_link(...)` to delegate through the normalized link builder and kept `add_link_pair(...)` on the same path through `add_link(...)`.
    - Added the small general world-owned link query helper `get_links(...)` with optional filtering by source, target, entity plus direction, link type, role, and roles.
    - Refactored existing link lookup helpers into thin wrappers where sensible on top of `get_links(...)`, and routed continuity candidate gathering through the stronger generic query seam.
    - Updated `main.py` startup setup to add a direct parent-to-parent `association/coparent` link pair alongside the existing family links.
    - Preserved existing startup family links, current parent snapshot rendering, `get_parent_ids_for(...)`, and current continuity handoff behavior.
    - Did not introduce marriage, romance, org/property systems, lineage browsing, or broader social-graph expansion.

## Version 0.30.0 (Minor) - 2026-03-27
- **Continuation Handoff Flow / Continuity Link Refinement:**
    - Tightened continuity candidate data in `world.py` so candidates now carry deterministic display-ready fields including `relationship_label`, `structural_status`, and `is_alive`.
    - Made continuity candidate ordering deterministic instead of relying on incidental link iteration order.
    - Added world-owned continuation handoff validation through `World.handoff_focus_to_continuation(...)`, which only accepts living existing actors that are valid current continuity candidates for the dead focused actor.
    - Hardened `World.simulate_advance_turn(...)` so ordinary advancement no longer proceeds as if nothing happened when the focused actor is already dead; it now returns a blocked turn result with continuity state instead of advancing time or faking normal play.
    - Updated `main.py` to render dead-focus continuity state clearly, show deterministic numbered continuation options, allow successor selection, switch focus cleanly inside the same world state, and end the run cleanly when no valid continuation candidates exist.
    - Preserved startup flow, character creation flow, living focused-actor month advancement behavior, current event generation flow, current event record-writing flow, world-owned stores, and the absence of automatic mortality, archive, inheritance, or lineage systems.

## Version 0.28.0 (Minor) - 2026-03-27
- **Death / Continuity Structural Transition Foundation:**
    - Added narrow structural actor-state storage in `human.py` through `structural_status`, `death_year`, `death_month`, and `death_reason`.
    - Added `Human.is_alive()` and `Human.get_structural_state()` so living/dead state is derived cleanly from one stored structural status instead of duplicated truth.
    - Added world-owned focused actor tracking through `focused_actor_id`, `set_focused_actor(...)`, `get_focused_actor_id()`, and `get_focused_actor()`.
    - Added a controlled world-owned death transition path through `World.mark_actor_dead(...)`.
    - Added structured continuity candidate resolution from living linked actors through `get_continuity_candidates_for(...)` and `build_continuity_state_for(...)`.
    - Extended the turn result contract with `focused_actor_id`, `focused_actor_alive`, `structural_transition`, and `continuity_state`.
    - Added narrow structural-state snapshot rendering and continuity-aware terminal rendering seams in `main.py`.
    - Added preserved `death` records with structural-transition metadata including reason, focus state, and continuity candidate IDs.
    - Preserved current startup flow, month advancement, event flow, and terminal-first shell behavior.
    - Did not introduce automatic mortality, archive behavior, inheritance, lineage UI, continuation chooser UI, or broader actor/entity refactors.

## Version 0.27.1 (Patch) - 2026-03-26
- **Post-v0.27.0 Docs / Planning Sync:**
    - Synced repo-local architecture and planning docs to the already-landed v0.27.0 startup actor ID cleanup.
    - Updated architecture notes to reflect the narrow `generate_startup_actor_id(...)` helper and the removal of fixed startup singleton IDs.
    - Updated planning docs so singleton startup actor IDs are no longer treated as pending work and the next-step read is based on v0.27.0 repo truth.
    - Did not change runtime behavior beyond the already-implemented v0.27.0 code state.

## Version 0.27.0 (Patch) - 2026-03-26
- **Singleton Startup Actor ID Cleanup:**
    - Replaced the hardcoded singleton startup actor IDs (`"mother"`, `"father"`, `"player"`) with a narrow startup-only ID generation helper in `main.py`.
    - Preserved current one-family startup behavior, startup family link wiring, parent/player visible behavior, snapshot behavior, event flow, and terminal flow.
    - Did not introduce broader family bootstrap redesign, sibling support, persistence work, or a generic global ID framework.

## Version 0.26.0 (Patch) - 2026-03-26
- **CLI Input Boundary Hardening:**
    - Added a narrow shared input boundary helper in `main.py` so interactive CLI input exits cleanly on `EOFError` and `KeyboardInterrupt` instead of crashing with a traceback.
    - Covered character creation prompts and the main loop advance/quit prompt through the same clean-exit path.
    - Preserved current prompt wording, validation behavior, typed `quit` behavior, startup flow, snapshot rendering, simulation flow, and event rendering.
    - Did not introduce broader CLI redesign, identity changes, lifecycle changes, or unrelated architecture work.

## Version 0.25.0 (Patch) - 2026-03-25
- **Unknown-Stat Mutation Hardening:**
    - Hardened `Human.modify_stat(...)` so unsupported stat names now fail explicitly instead of being silently ignored.
    - Preserved current supported stat mutation behavior for `health`, `happiness`, `intelligence`, and `money`.
    - Preserved current startup flow, snapshot flow, event flow, and terminal behavior.
    - Did not introduce new stats, a broader stat framework, or unrelated runtime/input changes.

## Version 0.24.0 (Minor) - 2026-03-24
- **Simulation Step Ownership / Boundary Foundation:**
    - Moved the authoritative simulation-step boundary into the world layer so time advancement, structured event collection, centralized outcome application, record writing, and structured turn-result assembly are owned together.
    - Preserved the current turn result contract (`months_advanced`, `events`, `had_any_events`) and current event result shapes.
    - Preserved current startup flow, snapshot flow, event flow, terminal behavior, and current grounded human-only event coverage.
    - Did not introduce Universe implementation, multi-system orchestration, or a broad simulation-engine rewrite.

## Version 0.23.0 (Minor) - 2026-03-23
- **Identity Generation Context Prep:**
    - Added a structured context-prep seam to the current identity-generation layer so startup identity generation no longer depends only on loose placeholder-style inputs.
    - Routed current startup identity generation through the cleaner seam while preserving current visible behavior and fallback pool usage.
    - Kept the current identity layer honest about its present limitations; this patch does not implement place-aware, culture-aware, era-aware, or world-aware identity generation.
    - Did not redesign broader actor creation, startup flow, or non-human identity generation.

## Version 0.22.0 (Minor) - 2026-03-23
- **Event Boundary Honesty Foundation:**
    - Hardened the current monthly event seam so the implementation boundary is more honest about the event layer’s current human-only scope.
    - Reduced unnecessary direct coupling in the event path where practical without redesigning the wider simulation flow.
    - Preserved the current structured event contract, including `outcome.stat_changes` as the sole mutation payload location.
    - Preserved current grounded human event content and later-life coverage.
    - Did not introduce species-general event architecture, non-human event content, or broader actor/entity framework work.

## Version 0.21.0 (Minor) - 2026-03-20
- **Origin / Care Semantics Foundation:**
    - Added explicit metadata to current startup parent/child family links so origin meaning, caregiving meaning, and startup bootstrap provenance are no longer implied only by bare family roles.
    - Added narrow world helper access for cleaner origin/caregiver retrieval on top of the existing `World.links` store.
    - Preserved current startup family behavior, snapshot behavior, and terminal behavior.
    - Did not introduce adoption systems, household systems, broader relationship redesign, or entity-layer rewrites.

## Version 0.20.0 (Minor) - 2026-03-20
- **Later-Life Human Event Coverage:**
    - Expanded the human event pool beyond Infant and Child so ordinary play no longer goes quiet simply because the event content ends after the Child stage.
    - Added grounded later-life human events for the post-Child portion of the currently implemented lifecycle system.
    - Preserved the current structured event contract, including `outcome.stat_changes` as the sole mutation payload location.
    - Did not introduce species-general event architecture, broader lifecycle redesign, or unrelated simulation-framework work.

## Version 0.19.0 (Patch) - 2026-03-20
- **Event Result Contract Cleanup:**
    - Removed the redundant top-level `stat_changes` field from structured event results returned by `get_monthly_event(...)`.
    - Kept `outcome.stat_changes` as the single authoritative mutation payload consumed by the simulation step.
    - Preserved event generation behavior, event rendering behavior, startup flow, and terminal behavior.
    - Did not introduce event-content expansion, broader mutation-framework work, or species-general event support.

## Version 0.18.0 (Minor) - 2026-03-20
- **Snapshot Output Contract Foundation:**
    - Added `Human.get_snapshot_data(...)` as a structured current-state snapshot helper.
    - Removed direct snapshot terminal printing from `Human`.
    - Updated `main.py` to render snapshots from structured snapshot data instead of printing from the model layer.
    - Preserved current visible snapshot content, startup flow, event flow, and terminal behavior.
    - Did not introduce a broader UI framework or presentation system.

## Version 0.17.0 (Minor) - 2026-03-20
- **Human Actor Construction Naming Honesty:**
    - Renamed the current world-owned constructor seam from `create_actor(...)` to `create_human_actor(...)`.
    - Updated startup actor creation and current human child bootstrap to delegate through `create_human_actor(...)`.
    - Updated actor-entry record metadata so the recorded entry method matches the renamed constructor seam.
    - Preserved actor-safe registry naming, record/query layers, startup behavior, event flow, and terminal behavior.
    - Did not introduce a generic actor constructor, species framework, or broader origin system.

## Version 0.16.1 (Patch) - 2026-03-19
- **Docs Formatting Repair:**
    - Repaired repository-local changelog formatting only.
    - Did not change runtime behavior or implemented simulation structure.

## Version 0.16.0 (Patch) - 2026-03-18
- **Record Structure Stabilization:**
    - Added an internal `_build_record(...)` helper to normalize the world-owned record shape before storage.
    - Updated `add_record(...)` to delegate record construction through the normalization helper.
    - Preserved the existing record store, query helpers, and record-writing behavior introduced in v0.14.0 and v0.15.0.
    - Did not introduce record IDs, indexing, persistence, archive systems, memory systems, or history UI.

## Version 0.15.0 (Patch) - 2026-03-18
- **Record Access / Query Foundation:**
    - Added narrow world-owned record query helpers on top of `World.records`.
    - Added `get_actor_records(...)`, `get_latest_record(...)`, and `get_records_by_tag(...)` for cleaner record access without ad hoc filtering across future systems.
    - Preserved the existing record store and record-writing behavior introduced in v0.14.0.
    - Included small low-risk cleanup of closely related residue where applicable.
    - Did not introduce archive systems, memory systems, history UI, or record indexing complexity.

## Version 0.14.0 (Minor) - 2026-03-17
- **Records / History Foundation:**
    - Added world-owned structured record storage via `World.records`.
    - Added `add_record(...)` and `get_records(...)` helpers for preserved simulation history.
    - Actor entry through `create_actor(...)` now writes an `actor_entry` record.
    - Current human startup family bootstrap through `create_human_child_with_parents(...)` now writes a `family_bootstrap` record.
    - Triggered monthly events are now also preserved as structured `event` records in addition to current terminal rendering.
    - Preserved current visible startup, snapshot, advancement, event output, and quit behavior.
    - Did not introduce archive systems, memory systems, save/load, or broad history UI.

## Version 0.13.0 (Minor) - 2026-03-17
- **Actor Entry / Origin Foundation:**
    - Added `World.create_actor(...)` as the canonical world-owned actor entry helper.
    - Added `World.create_human_child_with_parents(...)` as a narrow human-startup helper layered on top of `create_actor(...)`.
    - Refactored startup world setup to use world-owned actor entry instead of direct inline Human construction and repeated setup glue.
    - Preserved current visible startup behavior, parent generation behavior, place assignment behavior, link outcome, event flow, and snapshot behavior.
    - Did not introduce a full origin system, species framework, or broader entity architecture.

## Version 0.12.0 (Patch) - 2026-03-17
- **Human-Lock Cleanup Foundation:**
    - Renamed world actor registry and access API from person-shaped naming to actor-safe naming (`World.actors`, `add_actor(...)`, `get_actor(...)`).
    - Added generic world-core link target retrieval helper `get_link_target_ids(...)` so relationship/origin-style retrieval is no longer expressed only through mother/father-specific access.
    - Kept `get_parent_ids_for(...)` as a narrow human-specific wrapper over the generic helper to preserve current `Mother`/`Father` snapshot display behavior.
    - Updated architecture documentation to reflect actor-safe registry naming and the generic relationship retrieval seam beneath human interpretation.
    - Corrected stale fallback surname pool naming in docs to `FALLBACK_LAST_NAME_POOL`.
    - Removed stale old-path header residue from `human.py`.

## Version 0.11.0 (Minor) - 2026-03-16
- **Identity Generation Foundation:**
    - Extracted parent identity generation into new `identity.py`.
    - Moved approved mother/father first-name pools and fallback surname pool logic out of `main.py`.
    - Added narrow structured helpers: `resolve_family_last_name(player_last_name)` and `generate_parent_identity(role, family_last_name)`.
    - Updated startup world setup to consume structured parent identity data while keeping `Human` construction in `main.py`.
    - Preserved current visible startup behavior, including prompts/input flow, parent sex/gender assignment, parent birth-month randomization, fallback surname behavior, place assignment, and family link creation.
    - Did not introduce place-aware, culture-aware, or era-aware naming logic.

## Version 0.10.0 (Minor) - 2026-03-16
- **Controlled State Mutation Foundation:**
    - Updated `events.py` so `get_monthly_event(...)` returns structured outcomes instead of directly mutating actor state.
    - Added `World.apply_outcome(...)` in `world.py` as a small centralized mutation path for current event stat changes.
    - Updated `simulate_advance_turn(...)` to apply event outcomes during the simulation step while still collecting structured event results for rendering.
    - Preserved visible gameplay behavior, snapshot structure, and terminal event output format.
    - Did not introduce a large generic mutation framework.

## Version 0.9.2 (Patch) - 2026-03-16
- **Spatial Access Boundary & Changelog Consistency Cleanup:**
    - Added `Human.get_spatial_state(world)` as a formal spatial access/query helper.
    - Added `World.get_place_kind(place_id)` for consistent place-kind lookup.
    - Updated snapshot rendering to read current location through the spatial-state helper without changing visible output.
    - Cleaned recent changelog entry consistency/formatting.

## Version 0.9.1 (Patch) - 2026-03-16
- **Architecture/Changelog Consistency Cleanup:**
    - Cleaned up repository architecture/changelog wording after v0.9.0.
    - Clarified spatial identity separation wording without changing implemented behavior.
    - Preserved current behavior where residence remains internal and snapshots still show only current world-body location.
    - No gameplay behavior changed.

## Version 0.9.0 (Minor) - 2026-03-16
- **Spatial Identity Separation Foundation**:
    - Kept `Human.residence_place_id` as a stored internal actor field.
    - Snapshot continues to display only current world-body location at this stage.
    - Preserved startup assignment behavior where mother, father, and player receive both `current_place_id` and `residence_place_id`.

## Version 0.8.1 (Patch) - 2026-03-16
- **Snapshot Place-Name Lookup Cleanup:**
    - Snapshot location rendering now reuses `World.get_place_name(...)` in `Human.display_snapshot(...)`.
    - Unknown location fallback behavior is preserved (`"Unknown"` when no place name resolves).
    - Architecture docs now explicitly describe starter place creation (`"earth"`) and `current_place_id` assignment during initial setup for mother, father, and player.
    - No gameplay behavior changed.

## Version 0.8.0 (Minor) - 2026-03-16
- **Structured Place Foundation:**
    - Added world-owned place registry via `World.places` in `world.py`.
    - Added place helpers: `add_place(...)`, `get_place(...)`, and `get_place_name(...)`.
    - Removed loose `World.location` storage.
    - Added `Human.current_place_id` for actor-level current place references.
    - Updated initial world setup to create starter place `"earth"` and assign it to mother, father, and player.
    - Updated snapshot location rendering to resolve world body display through the place registry.
    - Preserved existing gameplay flow without expanding into travel, residence, ownership, or politics systems.

## Version 0.7.0 (Minor) - 2026-03-16
- **Link Foundation Expansion:**
    - Added world-owned link storage via `World.links` in `world.py`.
    - Added world link helpers: `add_link(...)`, `add_link_pair(...)`, `get_outgoing_links(...)`, `get_incoming_links(...)`, `get_related_links(...)`, `get_linked_ids(...)`, and `get_parent_ids_for(...)`.
    - Moved relationship truth out of `Human` and into `World`.
    - Removed `mother_id`/`father_id` constructor inputs and relationship storage/helpers from `Human`.
    - Updated `Human.display_snapshot(...)` to resolve parent IDs through `world.get_parent_ids_for(human_id)`.
    - Updated initial world setup to create explicit forward and reverse family links (`player -> mother`, `mother -> player`, `player -> father`, `father -> player`).
    - Preserved existing gameplay flow and snapshot layout while enabling structurally general non-family link categories.

## Version 0.6.4 (Patch) - 2026-03-17
- **Initialization Name-Pool Correction:**
    - Replaced temporary parent first-name pools with approved mother/father pools.
    - Replaced single fallback surname behavior with randomized fallback from `LAST_NAME_POOL` when player last name is blank.
    - Preserved player-entered first and last names exactly as entered.
    - Preserved startup flow, snapshot structure, parent birth-month randomization, simulation loop, event behavior, and advancement behavior.

## Version 0.6.3 (Patch) - 2026-03-17
- **Character / World Initialization Polish:**
    - Replaced hardcoded parent placeholder names with randomized first names from small fixed internal pools.
    - Parent last names now inherit the player surname when one is provided during character creation.
    - Added a clean fallback parent surname (`Smith`) when the player leaves last name blank.
    - Parent birth months are now randomized (1-12) instead of always defaulting to January.
    - Preserved startup flow, relationship model, snapshot structure/order, advancement behavior, quit flow, and player starting-stat randomization.

## Version 0.6.2 (Patch) - 2026-03-16
- **Terminal Event Presentation Cleanup:**
    - Improved post-advancement event rendering in `main.py` for long skips that trigger many events.
    - Small event counts still render as full dated event lines.
    - Large event counts now render in compact form with:
        - a total events summary line,
        - a limited recent subset of dated events,
        - and a clear older-events-omitted line.
    - Preserved simulation behavior exactly: event generation, eligibility, effects, time advancement, input handling, quit flow, snapshot content, and high-level output order.

## Version 0.6.1 (Patch) - 2026-03-15
- **Human Model Structural Cleanup:**
    - Replaced direct `Human` stat fields with a consolidated `self.stats` dictionary containing `health`, `happiness`, and `intelligence`.
    - Kept `money` as a separate top-level field and preserved unbounded money mutation behavior in `modify_stat(...)`.
    - Preserved silent-ignore behavior for unknown stat names in `modify_stat(...)`.
    - Replaced nested family relationship storage with a list of structured relationship records containing `type`, `role`, and `target_id`.
    - Added relationship helpers on `Human`: `add_relationship(...)`, `get_relationships(...)`, and `get_parent_ids()`.
    - Updated snapshot rendering to read stats from `self.stats` and resolve parent display through `get_parent_ids()` while preserving existing output format and behavior.
    - Preserved current gameplay behavior, including event effects/text, input handling, quit flow, and output ordering.

## Version 0.6.0 (Minor) - 2026-03-14
- **Event System Foundation:**
    - Moved event definitions from `get_monthly_event()` to a module-level data structure (`ALL_EVENTS`) in `events.py`.
    - Implemented a clear event generation pipeline in `get_monthly_event()` (lifecycle evaluation, filtering, chance roll, selection, stat application).
    - `get_monthly_event()` now returns complete structured event results (dict with `event_id`, raw `text`, `stat_changes`, `tags`, `year`, `month`) or `None`.
    - `simulate_advance_turn()` in `world.py` updated to collect these complete structured event results without mutating or decorating them.
    - `main.py` now renders terminal event lines by combining the structured `year`, `month`, and raw `text` fields from event results.
    - Preserved all validated gameplay behavior: input handling, advancement, snapshot output, monthly event chance, stat mutation, lifecycle filtering, and Infant/Child event content pool.

## Version 0.5.7 (Patch) - 2026-03-14
- **Docs Sync After Structural Cleanup:**
    - Updated `architecture` to reflect the current repository structure after v0.5.6:
        - `world.py` and `banners.py` now listed in file structure.
        - Module responsibilities updated to reflect `World` and `simulate_advance_turn(...)` in `world.py`.
        - `main.py` responsibilities updated to reflect decomposed shell functions.
        - `banners.py` responsibilities documented.
        - Turn flow updated to include startup, character creation, and world setup steps.
    - Added missing v0.5.6 changelog entry.

## Version 0.5.6 (Patch) - 2026-03-14
- **Structural Code Cleanup:**
    - Extracted `World` and `simulate_advance_turn(...)` from `main.py` into new `world.py`.
    - Extracted ASCII banner constants from `main.py` into new `banners.py`.
    - Decomposed `start_game()` into smaller shell-level functions in `main.py`:
        - `create_character()`
        - `setup_initial_world(...)`
        - `game_loop(...)`
    - Preserved all existing terminal behavior, prompts, output ordering, advancement flow, event display, and quit behavior exactly.

## Version 0.5.5 (Minor) - 2026-03-14
- **Person to Human Naming Correction:**
    - Renamed the concrete implemented model class from `Person` to `Human`.
    - Renamed the module `comp_life/person.py` to `comp_life/human.py`.
    - Updated all imports and code references across `main.py` and `events.py` to use the new `Human` class and `human` module.
    - Updated documentation (`architecture`) to reflect `Human` / `human.py` for the concrete model.
    - Preserved all existing character creation, lifecycle math, event filtering, and overall game behavior exactly.

## Version 0.5.4 (Minor) - 2026-03-14
- **Derived Lifecycle Cleanup:**
    - Introduced `Person.get_lifecycle_state(current_year, current_month)` as a formal access boundary for derived lifecycle state.
    - This method returns a structured dictionary containing `age_years`, `age_months`, `life_stage`, and `life_stage_model` ("human_default").
    - Refactored `Person.get_age()`, `Person.get_age_in_months()`, and `Person.get_human_life_stage()` to delegate to `get_lifecycle_state()`.
    - Updated `Person.display_snapshot()` to use `get_lifecycle_state()` for lifecycle-derived values.
    - Modified `events.py` to call `person.get_lifecycle_state()` once and use its result for event filtering, replacing separate direct lifecycle calls.
    - Preserved all existing age math, life-stage thresholds, snapshot values, and event eligibility behavior exactly.
    - Refreshed `architecture` to accurately reflect the current repository structure and responsibilities.

## Version 0.5.3 (Minor) - 2026-03-12
- **Structured Turn Result Contract:**
    - `simulate_advance_turn(...)` function now returns a stable, structured dictionary (`months_advanced`, `events`, `had_any_events`) instead of a raw list of event messages.
    - This enforces a cleaner separation between simulation logic and terminal rendering.
    - `start_game()` now consumes this structured result to render post-turn output.
    - Preserves all previously validated advancement, event, and output behavior exactly.

## Version 0.5.2 (Minor) - 2026-03-12
- **Simulation Boundary Extraction:**
    - Introduced `simulate_advance_turn(world, player_id, months_to_advance)` as a reusable simulation-step boundary in `main.py`.
    - This function encapsulates month-by-month advancement, event collection, and data return, while remaining completely free of terminal I/O.
    - Terminal input handling and output rendering remain in `start_game()`.
    - Cleaner separation of concerns: terminal layer is now a shell, simulation logic is isolated and testable.
    - All validated advancement behavior, event triggering, and display preserved exactly.

## Version 0.5.1 (Patch) - 2026-03-12
- **Terminal Presentation & Event Frequency Polish:**
    - Replaced ASCII title and time advanced banners with refined versions.
    - Added a new ASCII quit banner that displays when the player exits via "quit".
    - Updated the time advance prompt text to: "Press Enter for the next month, type a number to skip months, or type 'quit': "
    - Implemented a 50% chance for monthly event generation in `events.py`.
    - Ensured `events.py` returns an empty list when no event is triggered (by chance or due to lack of suitable events).
    - Modified `main.py` to only display triggered events (no silent filler messages for quiet months).
    - Added a single fallback line ("No notable events occurred during this period.") when no events occur during the entire advancement turn.

## Version 0.5.0 (Minor) - 2026-03-12
- **Customizable Month Advancement & Dated Events:**
    - Implemented customizable month advancement: Pressing Enter advances 1 month, typing a positive integer advances that many months, and typing 'quit' exits the game.
    - Added robust input validation to reject invalid inputs (0, negative numbers, floats, non-numeric strings).
    - Ensures internal processing remains month-by-month even for multi-month skips.
    - All displayed event messages now include the simulation date in `[Year X, Month Y]` format.
    - Updated prompt text to: "Press Enter for 1 month, type a number to advance multiple months, or type 'quit': ".
    - Improved post-advancement display sequence (banner, snapshot, then collected dated events).

## Version 0.4.1 (Patch) - 2026-03-12
- **Terminal Presentation Polish:**
    - Replaced plain startup title/welcome with ASCII art title banner.
    - Replaced plain `--- Time Advanced ---` heading with ASCII art banner.
    - Improved advance prompt text: "Life unfolds... Press Enter to advance one month, or type 'quit' to end your journey: ".
    - Removed "Month X:" prefix from event entries in the `--- Events ---` section for cleaner display.
    - Made character creation's first name input required.

## Version 0.4.0 (Minor) - 2026-03-11
- **Enhanced Human Character Creation:**
    - Integrated `species` as a core identity field in the `Person` class, fixed to `"Human"` for this patch.
    - `Person.name` attribute removed; full name is now derived via `Person.get_full_name()` from `first_name` and `last_name`.
    - `Person.display_snapshot` updated to show `Full Name`, `Species`, `Sex`, and `Gender` in the `--- Identity ---` section.
    - Character creation flow in `main.py` now uses menu-driven input with numbered choices and validation for `sex` (Male/Female) and `gender` (Male/Female/Non-binary).
    - First name and last name inputs are now optional (can be left empty).
    - Parent `Person` objects updated to align with new identity fields.
    - This establishes a more robust and future-expandable identity and creation system.

## Version 0.3.0 (Minor) - 2026-03-11
- **Enhanced Event System & Presentation:**
    - Event processing and presentation are now strictly separated: `get_monthly_event` processes events and applies effects, `main.py` displays event messages (as a list) under a new `--- Events ---` section *after* the updated life snapshot.
    - `get_monthly_event` now returns a *list* of event messages (even if only one), and `main.py` iterates through this list for display.
    - Removed `Person.event_log`; event messages are displayed immediately per turn without storing a per-person log.
    - Removed implementation-detail text (e.g., `(Health +1)`) from visible event messages.
- **UI & Stat Refinements:**
    - Renamed snapshot section from `Stats` to `Statistics`.
    - Player's starting `health`, `happiness`, and `intelligence` are now randomized via `Person.randomize_starting_statistics()` immediately after player creation in `main.py`. Tighter, human infant-appropriate ranges are used (Health: 85-100, Happiness: 80-100, Intelligence: 45-60). `money` remains 0.
- **Expanded Monthly Event Pool:**
    - Expanded event pool to 16 beginner-friendly events, exclusively focused on "Infant" (8 events) and "Child" (8 events) life stages.
    - Events are monthly-appropriate, include positive, neutral, and mild negative scenarios, and are filtered by `life_stages`, `min_age_months`, and `max_age_months` to ensure appropriateness.

## Version 0.1.0 (Minor) - 2026-03-11
- **Cleanup Patch:**
    - Improved stat handling: Added `Person.modify_stat()` helper method for centralized stat changes with clamping.
    - Event system cleaned up: Removed old prototype events; `events.py` now contains only a placeholder `process_random_event` function that returns a message string.
    - Corrected event message printing: `events.py` now only returns event messages, `main.py` is responsible for printing, preventing duplicate output.
    - Fixed `SyntaxError` in `main.py`'s `World` class `__init__` method regarding the `location` parameter.
    - Refined life snapshot display in `Person.display_snapshot` for clarity: Age and Year/Month on separate lines, `--- Stats ---` and `--- Family ---` headers.
    - Changed starting money in `Person.__init__` to $0.
    - Introduced `Person.get_human_life_stage` for derived life stage, displayed in snapshot.
    - Introduced `World.advance_months(1)` for 1-month progression, removed redundant `Year X, Month Y` from input prompt and simplified advancement heading.
    - Consolidated top-level World location display into the `Person.display_snapshot` method.
    - Introduced `Person.relationships` dictionary with `family` category for `mother_id` and `father_id`, explicitly displayed in snapshot.
