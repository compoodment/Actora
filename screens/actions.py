"""Actions screen controller and renderer."""

import curses
import time

from mechanics import get_monthly_free_hours
from ui import draw_text_block, draw_vertical_divider, get_content_bounds, truncate_for_width, wrap_text_line
from views.browser import get_social_tier_label
from wizard import format_stat_change_summary


class ActionsScreen:
    """Owns actions-screen input handling and rendering."""

    def __init__(self, back_keys, advance_throttle_seconds, main_idle_message):
        self.back_keys = back_keys
        self.advance_throttle_seconds = advance_throttle_seconds
        self.main_idle_message = main_idle_message

    def handle_key(self, app, key):
        if key == 27:
            app.options_popup_active = True
            app.options_selection = 0
            return
        if key in (ord("q"), ord("Q")):
            now = time.monotonic()
            if now - app.last_advance_time < self.advance_throttle_seconds:
                return
            app.last_advance_time = now
            app.advance_one_month()
        elif key in (ord("e"), ord("E")):
            app.open_skip_time()
        elif key in self.back_keys:
            if app.actions_focus == "actions":
                app.actions_focus = "categories"
                app.actions_action_index = 0
            else:
                app.screen_name = "main"
                app.last_message = self.main_idle_message
        elif key in (curses.KEY_UP, ord("w"), ord("W")):
            if app.actions_focus == "categories":
                categories = app.get_actions_categories()
                app.actions_category_index = max(0, app.actions_category_index - 1)
                app.actions_action_index = 0
            else:
                categories = app.get_actions_categories()
                cat = categories[app.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                app.actions_action_index = max(0, app.actions_action_index - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            if app.actions_focus == "categories":
                categories = app.get_actions_categories()
                app.actions_category_index = min(len(categories) - 1, app.actions_category_index + 1)
                app.actions_action_index = 0
            else:
                categories = app.get_actions_categories()
                cat = categories[app.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                app.actions_action_index = min(max(0, len(actions) - 1), app.actions_action_index + 1)
        elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
            if app.actions_focus == "categories":
                categories = app.get_actions_categories()
                cat = categories[app.actions_category_index] if categories else None
                if cat and cat["actions"]:
                    app.actions_focus = "actions"
                    app.actions_action_index = 0
        elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
            if app.actions_focus == "actions":
                app.actions_focus = "categories"
                app.actions_action_index = 0
        elif key in (curses.KEY_ENTER, 10, 13):
            if app.actions_focus == "actions":
                categories = app.get_actions_categories()
                cat = categories[app.actions_category_index] if categories else None
                actions = cat["actions"] if cat else []
                if actions and app.actions_action_index < len(actions):
                    action = actions[app.actions_action_index]
                    if action["id"] == "hang_out":
                        app.open_hang_out_select()
                    elif action["id"] in ("exercise", "read", "rest"):
                        subtypes = action["subtypes"]
                        app.personal_subtype_options = subtypes
                        app.pending_choice = {
                            "title": "Choose type",
                            "text": "",
                            "question": "",
                            "options": [f"{s['label']}  {s['time_cost']}h" for s in subtypes],
                            "selected_index": 0,
                            "skippable": True,
                            "choice_id": f"select_{action['id']}_subtype",
                            "default_value": None,
                        }
                        app.last_message = f"Choose how you want to {action['label'].lower()}."

    def render(self, app, stdscr, height, width):
        top = app.HEADER_ROWS
        body_height = height - app.HEADER_ROWS - app.FOOTER_ROWS
        content_left, content_width = get_content_bounds(width, max_width=120)
        col_w = content_width // 3
        cat_left = content_left
        act_left = content_left + col_w + 1
        det_left = content_left + col_w * 2 + 2
        det_width = content_width - col_w * 2 - 2

        categories = app.get_actions_categories()
        cat_idx = app.actions_category_index
        act_idx = app.actions_action_index
        current_cat = categories[cat_idx] if categories else None
        actions = current_cat["actions"] if current_cat else []
        current_action = actions[act_idx] if actions and act_idx < len(actions) else None

        for i, cat in enumerate(categories):
            label = f" {cat['label']}"
            attr = curses.A_REVERSE if (i == cat_idx and app.actions_focus == "categories") else curses.A_NORMAL
            if i == cat_idx and app.actions_focus != "categories":
                attr = curses.A_BOLD
            row = top + 1 + i
            if row < height:
                stdscr.addnstr(row, cat_left, label.ljust(col_w - 1), col_w - 1, attr)
        if not categories:
            stdscr.addnstr(top + 1, cat_left, " (none)", col_w - 1, curses.A_DIM)

        draw_vertical_divider(stdscr, top, act_left - 1, body_height)

        avail_rows = max(1, body_height // 2 - 2)
        if not actions:
            stdscr.addnstr(top + 1, act_left, " (none yet)", col_w - 1, curses.A_DIM)
        else:
            for i, action in enumerate(actions):
                if i >= avail_rows:
                    break
                label = f" {action['label']}"
                attr = curses.A_REVERSE if (i == act_idx and app.actions_focus == "actions") else curses.A_NORMAL
                row = top + 1 + i
                if row < height:
                    stdscr.addnstr(row, act_left, label.ljust(col_w - 1), col_w - 1, attr)

        queue_top = top + avail_rows + 2
        if queue_top < height - 2:
            try:
                stdscr.hline(queue_top - 1, act_left, getattr(curses, "ACS_HLINE", ord("-")), col_w - 1)
            except curses.error:
                pass
            stdscr.addnstr(queue_top, act_left, " Queued", col_w - 1, curses.A_BOLD)
            if app.active_actions:
                for i, queued in enumerate(app.active_actions):
                    row = queue_top + 1 + i
                    if row >= height - 1:
                        break
                    stdscr.addnstr(row, act_left, f"  {queued['label']}", col_w - 1)
            else:
                if queue_top + 1 < height - 1:
                    stdscr.addnstr(queue_top + 1, act_left, " (nothing queued)", col_w - 1, curses.A_DIM)

        draw_vertical_divider(stdscr, top, det_left - 1, body_height)

        focused_actor = app.world.get_focused_actor()
        free_hours = int(get_monthly_free_hours(focused_actor))
        queued_hours = int(sum(a.get("time_cost", 0) for a in app.active_actions))
        remaining_hours = free_hours - queued_hours
        if current_action:
            det_lines = [f" {current_action['label']}", ""]
            if current_action["id"] == "hang_out":
                links = current_action.get("links", [])
                if links:
                    det_lines.append(" Who you can hang out with:")
                    det_lines.append("")
                    for lnk in links:
                        target_id = lnk.get("target_id")
                        target_actor = app.world.get_actor(target_id)
                        if target_actor is None:
                            continue
                        meta = lnk.get("metadata", {})
                        closeness = meta.get("closeness", 0)
                        tier = get_social_tier_label(closeness)
                        det_lines.append(f"  {target_actor.get_full_name()} · {tier}")
                else:
                    det_lines.append(" No active social connections yet.")
            elif current_action["id"] in ("exercise", "read", "rest"):
                det_lines.append(" Ways to spend your time:")
                det_lines.append("")
                for subtype in current_action.get("subtypes", []):
                    effects_text = format_stat_change_summary(subtype.get("stat_changes", {}))
                    det_lines.append(f"  {subtype['label']} - {subtype['time_cost']}h - {effects_text}")
            next_y = draw_text_block(stdscr, top, det_left, det_width, body_height, det_lines)
            if next_y < top + body_height:
                next_y = draw_text_block(stdscr, next_y, det_left, det_width, body_height - (next_y - top), [""])
            y = next_y
        else:
            stdscr.addnstr(top + 1, det_left, " Select an action", det_width, curses.A_DIM)
            y = top + 3

        budget_lines = [
            (" Time Budget", curses.A_BOLD),
            (f"  {free_hours}h free", curses.A_DIM),
            (f"  {queued_hours}h queued", curses.A_DIM),
            (f"  {remaining_hours}h left", curses.A_DIM),
        ]
        for raw_line, attr in budget_lines:
            for wrapped_line in wrap_text_line(raw_line, det_width):
                if y >= top + body_height:
                    break
                stdscr.addnstr(y, det_left, wrapped_line, det_width, attr)
                y += 1

        if app.last_message:
            msg_row = top + body_height - 1
            if msg_row >= top:
                stdscr.addnstr(
                    msg_row,
                    det_left,
                    truncate_for_width(app.last_message, det_width),
                    det_width,
                    curses.A_DIM,
                )
