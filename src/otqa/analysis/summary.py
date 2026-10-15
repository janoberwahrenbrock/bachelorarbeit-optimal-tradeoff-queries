"""Independent aggregates retaining planned denominators and all attempt costs."""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from pathlib import Path

from otqa.runtime.codec import DocumentError, read_json
from otqa.runtime.documents import load_document, resolve_ref
from otqa.runtime.validation import verify_result

from .journal import verify_prefix


def distribution(values):
    values = list(values)
    if not values:
        return {"n": 0, **{key: None for key in ("total", "mean", "median", "minimum", "maximum", "p90")}}
    ordered = sorted(values)
    position = 0.9 * (len(values) - 1)
    lo, hi = math.floor(position), math.ceil(position)
    p90 = ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)
    return {"n": len(values), "total": sum(values), "mean": statistics.mean(values), "median": statistics.median(values),
            "minimum": ordered[0], "maximum": ordered[-1], "p90": p90}


def build_summary(root: Path, audit: dict, audit_ref: dict) -> dict:
    if audit["status"] == "failed":
        raise DocumentError("A failed integrity audit cannot yield verified summary statistics")
    plan = load_document("series_plan", resolve_ref(root, audit["plan"]), reference_root=root)
    state = load_document("series_state", resolve_ref(root, audit["state"]), reference_root=root)
    if state["plan_sha256"] != audit["plan"]["sha256"]:
        raise DocumentError("Audit snapshot binds a different plan")
    state_jobs = {job["job_id"]: job for job in state["jobs"]}
    prefixes = {}
    for ref in audit["prefix_snapshots"]:
        snapshot = load_document("partial_snapshot", resolve_ref(root, ref), reference_root=root)
        data = (root / snapshot["journal_path"]).read_bytes()
        manifest = load_document("manifest", resolve_ref(root, snapshot["manifest"]), reference_root=root)
        initial_ref = manifest["inputs"]["initial_answers"]
        initial_count = len(read_json(resolve_ref(root, initial_ref))["answers"]) if initial_ref else 0
        verified = verify_prefix(data, snapshot["valid_prefix_bytes"], snapshot["valid_prefix_sha256"], snapshot["last_good_sequence"], initial_answers=initial_count)
        if verified["query_counts"] != snapshot["query_counts"]:
            raise DocumentError("Immutable partial snapshot counts differ")
        prefixes[(snapshot["run_id"], snapshot["attempt_id"])] = snapshot
    rows, group_members, attempt_results = [], defaultdict(list), {}
    for job in plan["jobs"]:
        job_state = state_jobs[job["job_id"]]
        problem = load_document("problem", resolve_ref(root, job["problem"]), reference_root=root)
        result_refs, results = [], []
        for attempt in job_state["attempts"]:
            if attempt["result"] is not None:
                document = verify_result(resolve_ref(root, attempt["result"]), root,
                    {"run_id": attempt["run_id"], "attempt_id": attempt["attempt_id"], "problem_id": job["problem_id"], "configuration_id": job["configuration_id"]})
                result_refs.append(attempt["result"])
                results.append((attempt, document))
        terminal = results[-1] if results and job_state["status"] in ("completed", "failed", "interrupted") else None
        accepted = terminal[1] if terminal else None
        solver = accepted["solver_result"] if accepted else None
        counts = accepted["query_counts"] if accepted else None
        if accepted is None and job_state["attempts"]:
            last = job_state["attempts"][-1]
            snapshot = prefixes.get((last["run_id"], last["attempt_id"]))
            counts = snapshot["query_counts"] if snapshot else None
        row = {"job_id": job["job_id"], "case_id": job["case_id"], "configuration_id": job["configuration_id"], "repetition_index": job["repetition_index"],
            "objective_count": len(problem["objective_ids"]), "alternative_count": len(problem["alternative_ids"]), "status": job_state["status"],
            "accepted_attempt_id": terminal[0]["attempt_id"] if terminal else None,
            "termination_reason": solver["termination_reason"] if solver else None, "solved": solver["solved"] if solver else None,
            "selected_candidate_id": solver["selected_candidate_id"] if solver else None, "quality_status": accepted["quality"]["status"] if accepted else "unknown",
            "query_counts": counts, "api_call_wall_seconds": accepted["timings"]["api_call_wall_seconds"] if accepted and accepted["timings"]["complete_api_measurement"] else None,
            "attempt_results": result_refs}
        rows.append(row)
        key = (row["configuration_id"], row["objective_count"], row["alternative_count"])
        group_members[key].append((row, job_state))
        attempt_results[job["job_id"]] = results
    groups = []
    for (configuration, dimensions, alternatives), members in group_members.items():
        group_rows = [row for row, _ in members]
        completed = [row for row in group_rows if row["status"] == "completed"]
        solved = [row for row in completed if row["solved"]]
        correct = [row for row in solved if row["quality_status"] == "correct"]
        def times(sample):
            return [row["api_call_wall_seconds"] for row in sample if row["api_call_wall_seconds"] is not None]
        def queries(sample):
            return [row["query_counts"]["answered_new"] for row in sample if row["query_counts"] is not None]
        all_attempts = [attempt for _, job_state in members for attempt in job_state["attempts"]]
        failed_times = [document["timings"]["api_call_wall_seconds"] for row in group_rows for _, document in attempt_results[row["job_id"]]
                        if document["execution_status"] == "failed" and document["timings"]["complete_api_measurement"] and document["timings"]["api_call_wall_seconds"] is not None]
        group = {"configuration_id": configuration, "objective_count": dimensions, "alternative_count": alternatives,
            "planned_jobs": len(group_rows), "unique_cases": len({row["case_id"] for row in group_rows}), "completed_native": len(completed), "solved": len(solved),
            "singleton_stops": sum(row["termination_reason"] == "exact_single_candidate" for row in completed),
            "confidence_stops": sum(row["termination_reason"] == "volume_confidence" for row in completed),
            "no_query": sum(row["termination_reason"] == "no_query" for row in completed), "query_cap": sum(row["termination_reason"] == "max_questions" for row in completed),
            "correct": len(correct), "incorrect": sum(row["quality_status"] == "incorrect" for row in solved), "unknown_quality": sum(row["quality_status"] == "unknown" for row in completed),
            **{status: sum(row["status"] == status for row in group_rows) for status in ("failed", "interrupted", "pending", "launching", "running")},
            "total_attempts": len(all_attempts), "unknown_controller_attempt_times": sum(item["controller_elapsed_seconds"] is None for item in all_attempts),
            "solution_time": distribution(times(solved)), "correct_solution_time": distribution(times(correct)), "completed_call_time": distribution(times(completed)),
            "controller_attempt_time": distribution(item["controller_elapsed_seconds"] for item in all_attempts if item["controller_elapsed_seconds"] is not None),
            "failed_api_call_time": distribution(failed_times), "answered_new_solved": distribution(queries(solved)), "answered_new_correct": distribution(queries(correct)),
            "answered_new_completed": distribution(queries(completed)), "solution_sample_job_ids": [row["job_id"] for row in solved],
            "correct_sample_job_ids": [row["job_id"] for row in correct], "completed_sample_job_ids": [row["job_id"] for row in completed]}
        groups.append(group)
    return {"schema_version": 1, "series_id": plan["series_id"], "generated_at_utc": audit["created_at_utc"],
        "scope": "partial" if audit["status"] == "partial" else "complete", "basis": "verified_raw_attempts",
        "plan": audit["plan"], "state": audit["state"], "audit": audit_ref, "prefix_snapshots": audit["prefix_snapshots"], "rows": rows, "groups": groups}
