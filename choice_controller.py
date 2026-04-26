"""Pending-choice modal input controller."""

import curses

from mechanics import HANG_OUT_TIME_COST, get_monthly_free_hours


class ChoiceController:
    """Owns input handling for pending modal choices."""

    def __init__(self, back_keys, sexuality_option_labels):
        self.back_keys = back_keys
        self.sexuality_option_labels = sexuality_option_labels

    def handle_key(self, app, key):
        if key in (ord("q"), ord("Q"), ord("e"), ord("E")):
            return

        if app.pending_choice is None:
            return

        options = app.pending_choice["options"]
        selected_index = app.pending_choice["selected_index"]
        if key in (curses.KEY_UP, ord("w"), ord("W")):
            app.pending_choice["selected_index"] = max(0, selected_index - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            app.pending_choice["selected_index"] = min(len(options) - 1, selected_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            selected_option = options[app.pending_choice["selected_index"]]
            if app.pending_choice["choice_id"] == "sexuality":
                selected_value = dict(self.sexuality_option_labels)[selected_option]
            else:
                selected_value = selected_option
            self.resolve_choice(app, app.pending_choice["choice_id"], selected_value)
        elif app.pending_choice.get("skippable") and key in self.back_keys:
            self.resolve_choice(
                app,
                app.pending_choice["choice_id"],
                app.pending_choice.get("default_value"),
            )

    def resolve_choice(self, app, choice_id, selected_value):
        actor = app.get_focused_actor()
        if actor is None:
            app.pending_choice = None
            return

        if choice_id == "gender_identity":
            old_gender = actor.gender
            actor.gender = selected_value
            if selected_value != old_gender:
                app.append_event_log_entry(
                    "event",
                    f"You now identify as {selected_value}.",
                    year=app.world.current_year,
                    month=app.world.current_month,
                )
            else:
                app.append_event_log_entry(
                    "event",
                    "You reflected on your identity.",
                    year=app.world.current_year,
                    month=app.world.current_month,
                )
        elif choice_id == "sexuality":
            if selected_value is not None:
                actor.sexuality = selected_value
                app.append_event_log_entry(
                    "event",
                    f"You identify as {selected_value}.",
                    year=app.world.current_year,
                    month=app.world.current_month,
                )
            else:
                app.append_event_log_entry(
                    "event",
                    "You are still figuring things out.",
                    year=app.world.current_year,
                    month=app.world.current_month,
                )
        elif choice_id == "meeting_npc":
            if selected_value == "Introduce yourself":
                focused_actor_id = app.get_focused_actor_id()
                npc_actor_id, npc = app.world.generate_meeting_npc(focused_actor_id)
                app.world.create_social_link_pair(
                    focused_actor_id,
                    npc_actor_id,
                    closeness=15,
                    status="active",
                    closeness_history_months=0,
                )
                app.append_event_log_entry(
                    "event",
                    f"You introduced yourself to {npc.get_full_name()}.",
                    year=app.world.current_year,
                    month=app.world.current_month,
                )
                app.last_message = f"You met {npc.get_full_name()}."
            else:
                app.append_event_log_entry(
                    "event",
                    "You decided to keep to yourself.",
                    year=app.world.current_year,
                    month=app.world.current_month,
                )
                app.last_message = "You kept to yourself."

        elif choice_id == "select_hang_out_target":
            if selected_value is not None:
                options_list = (app.pending_choice or {}).get("options", [])
                try:
                    selected_idx = options_list.index(selected_value)
                    target_actor_id = app.hang_out_actor_ids[selected_idx]
                except (ValueError, IndexError):
                    app.pending_choice = None
                    return
                already_queued = any(
                    a["action_type"] == "spend_time" and a["target_actor_id"] == target_actor_id
                    for a in app.active_actions
                )
                if not already_queued:
                    focused_actor = app.world.get_focused_actor()
                    free_hours = get_monthly_free_hours(focused_actor)
                    used_hours = sum(a.get("time_cost", 0) for a in app.active_actions)
                    action_cost = HANG_OUT_TIME_COST
                    if used_hours + action_cost > free_hours:
                        app.last_message = "Not enough free time. (" + str(int(free_hours - used_hours)) + "h left)"
                        app.pending_choice = None
                        return
                    target_actor = app.world.get_actor(target_actor_id)
                    target_name = target_actor.get_full_name() if target_actor else "Someone"
                    app.active_actions.append({
                        "action_type": "spend_time",
                        "target_actor_id": target_actor_id,
                        "label": f"Spend time with {target_name}",
                        "time_cost": HANG_OUT_TIME_COST,
                    })
                    app.last_message = f"Queued: Spend time with {target_name}."
                else:
                    app.last_message = "Already queued to hang out with them."
            else:
                app.last_message = "Cancelled."
            app.pending_choice = None
            return
        elif choice_id in ("select_exercise_subtype", "select_read_subtype", "select_rest_subtype"):
            if selected_value is not None:
                options_list = (app.pending_choice or {}).get("options", [])
                try:
                    selected_idx = options_list.index(selected_value)
                    subtype = app.personal_subtype_options[selected_idx]
                except (ValueError, IndexError):
                    app.pending_choice = None
                    app.personal_subtype_options = []
                    return
                focused_actor = app.world.get_focused_actor()
                free_hours = get_monthly_free_hours(focused_actor)
                used_hours = sum(a.get("time_cost", 0) for a in app.active_actions)
                if used_hours + subtype["time_cost"] > free_hours:
                    app.last_message = "Not enough free time. (" + str(int(free_hours - used_hours)) + "h left)"
                    app.pending_choice = None
                    app.personal_subtype_options = []
                    return
                app.active_actions.append({
                    "action_type": "personal",
                    "subtype_id": subtype["id"],
                    "label": subtype["label"],
                    "time_cost": subtype["time_cost"],
                    "stat_changes": subtype["stat_changes"],
                })
                app.last_message = f"Queued: {subtype['label']}."
            else:
                app.last_message = "Cancelled."
            app.pending_choice = None
            app.personal_subtype_options = []
            return

        app.pending_choice = None
        remaining = app.remaining_skip_months
        app.remaining_skip_months = 0
        if remaining > 0:
            app.advance_time(remaining, is_resume=True)
