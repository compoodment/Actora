"""Death and continuation flow screen controller/renderers."""

import curses

from ui import center_text, draw_text_block, get_content_bounds
from views.browser import build_record_summary_lines
from views.shell import build_death_lines


class DeathContinuationScreen:
    """Owns death acknowledgement and continuation-selection screens."""

    def __init__(self, back_keys):
        self.back_keys = back_keys

    def handle_death_ack_key(self, app, key):
        if key == 27:
            app.options_popup_active = True
            app.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            return
        if key in (curses.KEY_ENTER, 10, 13):
            app.acknowledge_death()

    def handle_continuation_key(self, app, key):
        if key == 27:
            app.options_popup_active = True
            app.options_selection = 0
            return
        continuity_state = app.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        if key in (ord("q"), ord("Q")):
            return
        if key in self.back_keys:
            app.screen_name = "death_ack"
            app.last_message = "Returned to death summary."
            return
        if not candidates:
            return
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            app.continuation_selection = max(0, app.continuation_selection - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            app.continuation_selection = min(
                len(candidates) - 1,
                app.continuation_selection + 1,
            )
        elif key in (curses.KEY_ENTER, 10, 13):
            app.open_continuation_detail()

    def handle_continuation_detail_key(self, app, key):
        if key == 27:
            app.options_popup_active = True
            app.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            return
        if key in self.back_keys:
            app.screen_name = "continuation"
            app.last_message = "Returned to available lives."
        elif key in (curses.KEY_ENTER, 10, 13):
            app.choose_continuation()

    def render_death_ack(self, app, stdscr, height, width):
        continuity_state = app.get_continuity_state()
        content_left, content_width = get_content_bounds(width, max_width=74)
        death_detail = app.build_actor_inspect_detail(
            app.get_focused_actor_id(),
            relationship_label="Self",
        )
        lines = [
            "",
            center_text("DEATH", content_width),
            "",
        ]
        lines.extend(build_death_lines(continuity_state))
        if death_detail is not None:
            lines.extend(
                [
                    "",
                    "Life Summary",
                    f"Age at death: {death_detail['age']}",
                    f"Place at death: {death_detail['current_place_name']}",
                    (
                        "At death: "
                        f"Health {death_detail['health']}   Happiness {death_detail['happiness']}   "
                        f"Intelligence {death_detail['intelligence']}   Money ${death_detail['money']}"
                    ),
                    "",
                    "Recent Records",
                ]
            )
            lines.extend(build_record_summary_lines(death_detail["records"]))
        lines.extend(
            [
                "",
                center_text("Press Enter to continue.", content_width),
            ]
        )
        draw_text_block(
            stdscr,
            5,
            content_left,
            content_width,
            height - 7,
            lines,
        )

    def render_continuation(self, app, stdscr, height, width):
        continuity_state = app.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        content_left, content_width = get_content_bounds(width, max_width=96)
        lines = [""]
        highlight_index = None

        if not candidates:
            lines.append("No living family members were found.")
        else:
            app.continuation_selection = max(
                0,
                min(app.continuation_selection, len(candidates) - 1),
            )
            for index, candidate in enumerate(candidates):
                line = (
                    f"{candidate['full_name']} · {candidate['relationship_label']} · "
                    f"Age {candidate['age']} · {candidate.get('current_place_name') or 'Unknown'}"
                )
                if index == app.continuation_selection:
                    highlight_index = len(lines)
                lines.append(line)

        draw_text_block(
            stdscr,
            app.HEADER_ROWS,
            content_left,
            content_width,
            height - app.HEADER_ROWS - app.FOOTER_ROWS,
            lines,
            highlight_index=highlight_index,
        )

    def render_continuation_detail(self, app, stdscr, height, width):
        continuity_state = app.get_continuity_state()
        candidates = continuity_state["continuity_candidates"]
        selected_candidate = next(
            (
                candidate
                for candidate in candidates
                if candidate["actor_id"] == app.selected_continuation_actor_id
            ),
            None,
        )
        if selected_candidate is None:
            app.screen_name = "continuation"
            app.last_message = "This person is no longer available."
            self.render_continuation(app, stdscr, height, width)
            return

        detail = app.build_actor_inspect_detail(
            selected_candidate["actor_id"],
            relationship_label=selected_candidate["relationship_label"],
        )
        if detail is None:
            content_left, content_width = get_content_bounds(width, max_width=86)
            draw_text_block(stdscr, app.HEADER_ROWS, content_left, content_width, height - app.HEADER_ROWS - app.FOOTER_ROWS, ["Actor data unavailable."])
            return
        content_left, content_width = get_content_bounds(width, max_width=86)
        lines = [
            center_text("CONTINUATION DETAIL", content_width),
            "",
            detail["full_name"],
            (
                f"{detail['relationship_label']}   Age {detail['age']}   "
                f"Location: {detail['current_place_name']}"
            ),
            (
                f"Health {detail['health']}   Happiness {detail['happiness']}   "
                f"Intelligence {detail['intelligence']}   Money ${detail['money']}"
            ),
            "",
            "Recent Records",
        ]
        lines.extend(build_record_summary_lines(detail["records"]))
        draw_text_block(
            stdscr,
            app.HEADER_ROWS,
            content_left,
            content_width,
            height - app.HEADER_ROWS - app.FOOTER_ROWS,
            lines,
        )
