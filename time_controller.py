"""Time advancement orchestration controller."""


class TimeController:
    """Owns shell orchestration around world turn advancement."""

    def advance_time(self, app, months_to_advance, *, is_resume=False):
        """Advances time using the existing world-owned simulation seam."""
        aggregated_turn_result = {
            "months_advanced": 0,
            "events": [],
            "focused_actor_alive": True,
            "continuity_state": None,
        }
        new_records = []
        focused_actor_id = app.get_focused_actor_id()

        spend_time_actions = [a for a in app.active_actions if a["action_type"] == "spend_time"]
        personal_actions_queued = [a for a in app.active_actions if a["action_type"] == "personal"]
        shared_actor_ids = {a["target_actor_id"] for a in spend_time_actions}

        first_month = True
        for _ in range(months_to_advance):
            prior_record_count = len(app.world.records)
            month_turn_result = app.world.simulate_advance_turn(app.player_id, 1)
            new_records_this_month = app.world.records[prior_record_count:]
            new_records.extend(new_records_this_month)
            aggregated_turn_result["months_advanced"] += month_turn_result["months_advanced"]
            aggregated_turn_result["events"].extend(month_turn_result["events"])
            aggregated_turn_result["focused_actor_alive"] = month_turn_result["focused_actor_alive"]
            aggregated_turn_result["continuity_state"] = month_turn_result["continuity_state"]

            if first_month:
                if month_turn_result.get("focused_actor_alive", True):
                    for action in spend_time_actions:
                        event = app.world.spend_time_with_actor(
                            focused_actor_id,
                            action["target_actor_id"],
                        )
                        if event is not None:
                            aggregated_turn_result["events"].append(event)

                    for action in personal_actions_queued:
                        event = app.world.resolve_personal_action(focused_actor_id, action)
                        if event is not None:
                            aggregated_turn_result["events"].append(event)

                app.active_actions = [
                    a for a in app.active_actions if a["action_type"] not in ("spend_time", "personal")
                ]

            for record in new_records_this_month:
                if record.get("record_type") != "death":
                    continue
                for dead_actor_id in record.get("actor_ids", []):
                    if dead_actor_id == focused_actor_id:
                        continue
                    event = app.world.resolve_social_death_impact(focused_actor_id, dead_actor_id)
                    if event is not None:
                        aggregated_turn_result["events"].append(event)

            if month_turn_result.get("focused_actor_alive", True):
                month_shared = shared_actor_ids if first_month else set()
                drift_events = app.world.apply_social_link_decay(focused_actor_id, month_shared)
                for drift in drift_events:
                    app.append_event_log_entry(
                        "event",
                        drift["text"],
                        year=drift["year"],
                        month=drift["month"],
                    )

            first_month = False

            if month_turn_result["months_advanced"] <= 0 or not month_turn_result["focused_actor_alive"]:
                break
            if app.maybe_offer_identity_choice():
                remaining = months_to_advance - aggregated_turn_result["months_advanced"]
                if remaining > 0:
                    app.remaining_skip_months = remaining
                break
            if app.maybe_offer_meeting_event():
                remaining = months_to_advance - aggregated_turn_result["months_advanced"]
                if remaining > 0:
                    app.remaining_skip_months = remaining
                break

        app.append_event_log_turn(aggregated_turn_result, months_to_advance, new_records, suppress_skip_marker=is_resume)
        actual_months_advanced = aggregated_turn_result["months_advanced"]
        if actual_months_advanced == 1:
            app.last_message = "Advanced 1 month."
        elif actual_months_advanced != months_to_advance:
            if app.pending_choice is not None:
                app.last_message = "A personal choice needs your attention."
            else:
                app.last_message = f"Advanced {actual_months_advanced} of {months_to_advance} months before death."
        else:
            app.last_message = f"Advanced {actual_months_advanced} months."
        if aggregated_turn_result["continuity_state"] is not None and not aggregated_turn_result["focused_actor_alive"]:
            app.screen_name = "death_ack"

    def advance_one_month(self, app):
        self.advance_time(app, 1)
