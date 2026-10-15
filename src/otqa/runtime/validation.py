"""Shared strict result-envelope validation, without process orchestration."""
from pathlib import Path

from .codec import DocumentError, digest, mathematical_hex, read_json
from .documents import file_ref, load_document, resolve_ref
from .schema import validate
from .storage import empty_counts


def journal_policy(manifest: dict, root: Path, manifest_path: Path) -> dict:
    """Resolve the stored actual policy inputs for every shared prefix reader."""
    problem = load_document("problem", resolve_ref(root, manifest["inputs"]["problem"]), reference_root=root)
    history = manifest["inputs"]["initial_answers"]
    initial = len(load_document("answer_history", resolve_ref(root, history), reference_root=root)["answers"]) if history else 0
    return {"manifest_sha256": file_ref(manifest_path, root)["sha256"], "initial_answers": initial, "algorithm": manifest["effective_algorithm"],
            "budget": manifest["effective_budget"], "alternative_ids": problem["alternative_ids"]}


def verify_result(path: Path, root: Path, payload: dict) -> dict:
    result = validate("result", read_json(path))
    for key in ("run_id", "attempt_id", "problem_id", "configuration_id"):
        if result[key] != payload[key]:
            raise DocumentError("Result identity differs from its reserved attempt")
    time = result["timings"]
    if time["complete_api_measurement"] != (time["api_call_wall_seconds"] is not None):
        raise DocumentError("Complete API measurement and its time disagree")
    if time["case_elapsed_seconds"] is not None and time["api_call_wall_seconds"] is not None and time["case_elapsed_seconds"] < time["api_call_wall_seconds"]:
        raise DocumentError("Case elapsed time is shorter than its included API call")
    if result["execution_status"] == "failed" and (result["error"] is None or result["interruption"] is not None or result["solver_result"] is not None):
        raise DocumentError("Failed result has inconsistent terminal payloads")
    if result["execution_status"] == "interrupted" and (result["interruption"] is None or result["error"] is not None or result["solver_result"] is not None or time["complete_api_measurement"]):
        raise DocumentError("Interrupted result claims a complete solver return")
    if result["execution_stage"] == "bootstrap":
        if result["execution_status"] == "completed" or result["solver_result"] is not None or result["journal"] is not None or result["query_counts"] != empty_counts() or result["timings"]["complete_api_measurement"]:
            raise DocumentError("Bootstrap result claims solver work")
        if any(value is not None for key, value in time.items() if key not in ("case_elapsed_seconds", "scope_version", "complete_api_measurement")):
            raise DocumentError("Bootstrap result claims SDK phase measurements")
    else:
        manifest_path = path.parent / "manifest.json"
        manifest = validate("manifest", read_json(manifest_path))
        for key in ("run_id", "attempt_id", "problem_id", "configuration_id"):
            if manifest[key] != result[key]:
                raise DocumentError("Manifest and result attempt identity differ")
        if "source" in payload and payload["source"] != manifest["source"]:
            raise DocumentError("Manifest source differs from the actually loaded immutable build stamp")
        if "project_binding" in payload and manifest["project_binding"] != payload["project_binding"]:
            raise DocumentError("Manifest project binding differs from its enclosing run or series")
        problem = load_document("problem", resolve_ref(root, manifest["inputs"]["problem"]), reference_root=root)
        configuration = load_document("config", resolve_ref(root, manifest["inputs"]["configuration"]), reference_root=root)
        if problem["problem_id"] != result["problem_id"] or configuration["configuration_id"] != result["configuration_id"]:
            raise DocumentError("Manifest input IDs differ from the result")
        for key, config_key in (("effective_algorithm", "algorithm"), ("effective_budget", "budget"), ("effective_execution", "execution"), ("effective_recording", "recording")):
            if manifest[key] != configuration[config_key]:
                raise DocumentError("Manifest effective configuration differs from its input document")
        history_ref = manifest["inputs"]["initial_answers"]
        initial_count = len(read_json(resolve_ref(root, history_ref))["answers"]) if history_ref else 0
        journal = result["journal"]
        if journal is None:
            raise DocumentError("Solver result has no confirmed journal proof")
        data = resolve_ref(root, {"path": journal["path"], "sha256": journal["sha256"]}).read_bytes()
        if len(data) != journal["bytes"] or digest(data[:journal["valid_prefix_bytes"]]) != journal["valid_prefix_sha256"]:
            raise DocumentError("Result journal byte/prefix proof differs")
        if journal["uncommitted_suffix_bytes"] != len(data) - journal["valid_prefix_bytes"] or journal["trailing_partial_line"] != bool(data and not data.endswith(b"\n")):
            raise DocumentError("Journal suffix metadata differs from actual raw bytes")
        from .journal import mathematically_equal, verify_prefix
        prefix = verify_prefix(data, journal["valid_prefix_bytes"], journal["valid_prefix_sha256"], journal["last_good_sequence"],
            initial_answers=initial_count, algorithm=manifest["effective_algorithm"], budget=manifest["effective_budget"], alternative_ids=problem["alternative_ids"])
        if prefix["events"][0]["payload"]["manifest_sha256"] != file_ref(manifest_path, root)["sha256"]:
            raise DocumentError("Journal start does not bind this manifest")
        if prefix["query_counts"] != result["query_counts"]:
            raise DocumentError("Result counts differ from its accepted journal prefix")
        alternative_ids = set(problem["alternative_ids"])
        objective_count = len(problem["objective_ids"])
        algorithm = manifest["effective_algorithm"]
        for event in prefix["events"]:
            if event["event_type"] == "state_analyzed" and not set(event["payload"]["candidate_ids"]).issubset(alternative_ids):
                raise DocumentError("State contains an alternative outside its problem")
            if event["event_type"] in ("query_dispatched", "answer_received", "query_completed"):
                query = event["payload"]["query"]
                if max(query["goal_index_a"], query["goal_index_b"]) >= objective_count:
                    raise DocumentError("Journal query exceeds its problem objective dimension")
            if event["event_type"] == "query_planned":
                planning = event["payload"]["planning"]
                if planning["planning_stop_aware"] != (algorithm["planning_evaluation"] == "stop_aware"):
                    raise DocumentError("Recorded planning path differs from its effective policy")
                if planning["selected"]["score"]["kind"] != algorithm["query_strategy"]:
                    raise DocumentError("Recorded score kind differs from its effective strategy")
                expected_horizons = {algorithm["depth"]} if algorithm["query_strategy"] == "fixed" else set(range(1, algorithm["depth"] + 1))
                if {item["horizon"] for item in planning["horizons"]} != expected_horizons:
                    raise DocumentError("Recorded horizon coverage differs from the effective policy")
        if result["execution_status"] == "completed":
            solver = result["solver_result"]
            if solver is None or not result["timings"]["complete_api_measurement"] or result["timings"]["api_call_wall_seconds"] is None or result["finalized_by"] != "case_process":
                raise DocumentError("Completed result is not a complete native API return")
            if prefix["last_event_type"] != "run_finished":
                raise DocumentError("Completed result lacks a committed terminal journal event")
            if result["error"] is not None or result["interruption"] is not None:
                raise DocumentError("Completed result contains an execution failure")
            if journal["uncommitted_suffix_bytes"] != 0:
                raise DocumentError("Regular completion has an uncommitted journal suffix")
            if len(solver["query_records"]) != result["query_counts"]["answered_new"] or len(solver["answered_queries"]) != result["query_counts"]["answered_total"]:
                raise DocumentError("Solver answer records differ from durable query counts")
            reason = solver["termination_reason"]
            terminal = prefix["events"][-1]["payload"]
            if reason != terminal["termination_reason"] or solver["solved"] != terminal["solved"]:
                raise DocumentError("Native result differs from its terminal journal decision")
            if not mathematically_equal(solver["final_state"], prefix["last_state"]):
                raise DocumentError("Native final state differs from the durable actual state")
            records = [event["payload"] for event in prefix["events"] if event["event_type"] == "query_completed"]
            if not mathematically_equal(solver["query_records"], records):
                raise DocumentError("Native query records differ from durable query completions")
            initial = read_json(resolve_ref(root, history_ref))["answers"] if history_ref else []
            new_answers = [{**event["payload"]["query"], "answer": event["payload"]["answer"]} for event in prefix["events"] if event["event_type"] == "answer_received"]
            if not mathematically_equal(solver["answered_queries"], initial + new_answers):
                raise DocumentError("Native answered history differs from durable answers")
            if solver["final_state"]["state_index"] != result["query_counts"]["answered_total"]:
                raise DocumentError("Final state index differs from accepted answers")
            selected = solver["selected_candidate_id"]
            if selected is not None and (selected not in alternative_ids or selected not in solver["final_state"]["candidate_ids"]):
                raise DocumentError("Selected candidate is not in the actual final candidate set")
            from .journal import actual_stop
            _, policy_selection = actual_stop(solver["final_state"], algorithm, manifest["effective_budget"], problem["alternative_ids"])
            if selected != policy_selection:
                raise DocumentError("Selected candidate differs from actual maximum-share/original-index stopping selection")
            if reason == "exact_single_candidate" and (not solver["solved"] or not solver["exactly_solved"] or len(solver["final_state"]["candidate_ids"]) != 1):
                raise DocumentError("Singleton result is inconsistent")
            if reason == "volume_confidence" and (not solver["solved"] or solver["exactly_solved"] or len(solver["final_state"]["candidate_ids"]) < 2):
                raise DocumentError("Confidence result is inconsistent")
            if reason in ("no_query", "max_questions") and (solver["solved"] or solver["selected_candidate_id"] is not None):
                raise DocumentError("Unsolved result claims an accepted selection")
            if reason == "volume_confidence":
                stopping = algorithm["stopping"]
                shares = solver["final_state"]["candidate_volume_shares"]
                if stopping["rule"] != "volume_confidence" or shares is None or shares.get(selected, -1.) < stopping["threshold"]:
                    raise DocumentError("Confidence selection does not meet its active stopping threshold")
            if reason == "max_questions" and (manifest["effective_budget"]["max_queries"] is None or result["query_counts"]["answered_total"] < manifest["effective_budget"]["max_queries"]):
                raise DocumentError("Query-cap return has not reached its configured budget")
            for result_key, state_key in (("selected_candidate_volume", "candidate_volumes"), ("selected_candidate_volume_share", "candidate_volume_shares")):
                mapping = solver["final_state"][state_key]
                expected = mapping.get(selected) if mapping is not None and selected is not None else None
                if not mathematically_equal(solver[result_key], expected):
                    raise DocumentError("Selected candidate volume/share differs from the final state")
    if result["numeric_hex"] != mathematical_hex(result["solver_result"], "/solver_result"):
        raise DocumentError("Result mathematical binary64 evidence differs")
    return result


