"""Lightweight isolated CaseProcess entry, released exactly once by its owner."""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from .codec import DocumentError, mathematical_hex, read_json, utc_now
from .error_serialization import error_wire
from .documents import file_ref, load_answer_history, load_config_document, load_execution_profile, load_oracle, load_problem, resolve_ref
from .processes import process_identity
from .project import load_project_context
from .schema import validate
from .storage import RunStore, empty_counts, publish_json


def timings(*, case_elapsed=None, api_elapsed=None, partial=None, recorder=None, answer_wait=None, observer=None, complete=False):
    keys = ("state_analysis_wall_seconds", "planning_wall_seconds", "persistence_in_call_wall_seconds",
            "worker_startup_wall_seconds", "worker_shutdown_wall_seconds", "unattributed_wall_seconds", "worker_cpu_seconds")
    return {**{key: None for key in keys}, "case_elapsed_seconds": case_elapsed, "api_call_wall_seconds": api_elapsed,
        "partial_api_elapsed_seconds": partial, "recorder_wall_seconds": recorder, "answer_wait_wall_seconds": answer_wait,
        "observer_wall_seconds": observer,
        "scope_version": 1, "complete_api_measurement": complete}


def bootstrap_result(payload, started, case_start, *, error=None, interruption=None, finalized_by="case_process"):
    return {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"], "problem_id": payload["problem_id"],
        "configuration_id": payload["configuration_id"], "execution_status": "interrupted" if interruption else "failed", "execution_stage": "bootstrap",
        "finalized_by": finalized_by, "started_at_utc": started, "finished_at_utc": utc_now(), "query_counts": empty_counts(),
        "timings": timings(case_elapsed=time.perf_counter() - case_start if case_start is not None else None), "solver_result": None,
        "quality": {"status": "not_selected", "audit_status": "not_available", "true_winner_ids": [], "regret_fraction": None, "findings": []},
        "error": error, "interruption": interruption, "telemetry_errors": [], "journal": None, "numeric_hex": {}}


def _provider(kind, problem, oracle, replay):
    from otqa.answers import ReplayAnswers, SimulatedAnswers
    from .serialization import history_answers
    if kind == "simulated":
        return SimulatedAnswers(tuple(float(value) for value in oracle["target_weights"]))
    if kind == "replay":
        return ReplayAnswers(history_answers(replay))

    def interactive(query):
        objectives = problem["objective_ids"]
        prompt = f"weight[{objectives[query.goal_index_a]}] ? {query.value!r} * weight[{objectives[query.goal_index_b]}] (<, =, >): "
        while True:
            print(prompt, file=sys.stderr, end="", flush=True)
            text = sys.stdin.readline()
            if text == "":
                raise KeyboardInterrupt("Interactive input ended")
            answer = text.strip()
            if answer in ("<", "=", ">"):
                return answer
            print("Enter exactly <, = or >.", file=sys.stderr, flush=True)
    return interactive


def run_attempt(payload: dict, *, case_start: float, started_at: str, identity: dict) -> int:
    """The only runtime function that invokes the public solver API."""
    context = load_project_context(Path(payload["project_root"]))
    root, attempt = Path(payload["reference_root"]), Path(payload["attempt_dir"])
    store = recorder = None
    start_attempted = False
    try:
        from .source import loaded_source
        from .profiles import environment_snapshot
        source, _, _ = loaded_source()
        if source != payload["source"]:
            raise DocumentError("Loaded immutable build stamp changed between preparation and CaseProcess")
        problem = load_problem(resolve_ref(root, payload["inputs"]["problem"]), reference_root=root)
        config = load_config_document(resolve_ref(root, payload["inputs"]["configuration"]), reference_root=root)
        profile = load_execution_profile(resolve_ref(root, payload["execution_profile"]), reference_root=root)
        oracle = load_oracle(resolve_ref(root, payload["inputs"]["oracle"]), problem, reference_root=root) if payload["inputs"]["oracle"] else None
        history = load_answer_history(resolve_ref(root, payload["inputs"]["initial_answers"]), problem, reference_root=root) if payload["inputs"]["initial_answers"] else None
        replay = load_answer_history(resolve_ref(root, payload["inputs"]["replay_answers"]), problem, reference_root=root) if payload["inputs"]["replay_answers"] else None
        # Numerical imports are permitted only after the externally granted pulse.
        from otqa.numerics.profile import actual_backend_capabilities, resolved_cache_policy, resolved_numerical_profile
        capabilities = actual_backend_capabilities()
        if capabilities != profile["backend_capabilities"]:
            raise DocumentError("Actual backend capabilities differ from the qualified execution profile")
        from .serialization import domain_inputs, mathematical_input_digest, result_wire
        domain_problem, policy, budget, execution, initial = domain_inputs(problem, config, history)
        manifest = {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"],
            "series_id": payload["series_id"], "job_id": payload["job_id"], "problem_id": problem["problem_id"], "configuration_id": config["configuration_id"],
            "execution_kind": "continuation" if history is not None else "replay" if payload["answer_source"] == "replay" else "fresh",
            "answer_source": payload["answer_source"], "created_at_utc": utc_now(), "source": source, "source_inventory": payload["source_inventory"],
            "project_binding": context.binding(root), "run_purpose": payload["run_purpose"], "materialization_receipt": payload["materialization_receipt"],
            "launch_intent": file_ref(attempt / "launch_intent.json", root), "inputs": payload["inputs"],
            "mathematical_input_sha256": mathematical_input_digest(problem, config, payload["answer_source"], history, oracle, replay),
            "effective_algorithm": config["algorithm"], "effective_budget": config["budget"], "effective_execution": config["execution"],
            "effective_recording": config["recording"], "execution_profile": payload["execution_profile"], "numerical_profile": resolved_numerical_profile(),
            "resolved_cache_policy": resolved_cache_policy(), "environment": environment_snapshot(profile["packages"], capabilities), "process": identity}
        publish_json(context, attempt / "manifest.json", manifest, kind="manifest")
        store = RunStore(context, attempt, root, payload["run_id"], payload["attempt_id"], identity, len(initial))
        from .recorder import WireRecorder
        recorder = WireRecorder(store, problem["alternative_ids"], stop_aware=config["algorithm"]["planning_evaluation"] == "stop_aware", trace_level=config["recording"]["trace_level"])
        start_attempted = True
        recorder.event("run_started", {"manifest_sha256": file_ref(attempt / "manifest.json", root)["sha256"]}, commit=True)
    except BaseException as exc:
        if store is not None:
            store.close()
        if start_attempted:
            # A failed start cursor is intrinsically uncertain. Preserve raw bytes;
            # neither this child nor recovery invents an accepted start/Stage.
            publish_json(context, attempt / "start-error.json", {"error": error_wire(exc), "confirmed_start": False})
            return 1
        result = bootstrap_result(payload, started_at, case_start, error=error_wire(exc))
        publish_json(context, attempt / "result.json", result, kind="result")
        return 1

    provider = _provider(payload["answer_source"], problem, oracle, replay)
    provider_elapsed = 0.0
    def measured_provider(query):
        nonlocal provider_elapsed
        before = time.perf_counter()
        try:
            return provider(query)
        finally:
            provider_elapsed += time.perf_counter() - before

    from .telemetry import TelemetryObserver, terminal_display
    sink = terminal_display(sys.stderr)
    observer = TelemetryObserver(context, attempt, config["recording"]["telemetry_failure_policy"], sink) if sink is not None else None
    profiler = None
    if config["recording"]["profile"]:
        from .profiling import ParentCallProfiler
        profiler = ParentCallProfiler()
    api_start = time.perf_counter()
    recorder.api_started = api_start
    prior_recording = recorder.elapsed
    result = None
    error = interruption = None
    complete = False
    api_elapsed = partial = None
    exit_code = 0
    try:
        if profiler is not None:
            profiler.start()
        from otqa import solve
        result = solve(domain_problem, policy, measured_provider, budget=budget, execution=execution,
                       initial_answers=initial, recorder=recorder, observer=observer)
        api_elapsed = time.perf_counter() - api_start
        complete = True
    except KeyboardInterrupt as exc:
        partial = time.perf_counter() - api_start
        interruption = {"reason": "user_cancel", "message": str(exc) or "User cancelled"}
        exit_code = 130
    except BaseException as exc:
        api_elapsed = time.perf_counter() - api_start
        complete = True
        error = error_wire(exc)
        exit_code = 1
    finally:
        if profiler is not None:
            profiler.stop()
    recording_in_call = recorder.elapsed - prior_recording
    observer_elapsed = observer.elapsed if observer is not None else 0.0
    confirmed = store.cursor["query_counts"]
    status = "completed" if result is not None else "interrupted" if interruption else "failed"
    solver_result = result_wire(result, problem["alternative_ids"], stop_aware=config["algorithm"]["planning_evaluation"] == "stop_aware", trace_level=config["recording"]["trace_level"]) if result else None
    from otqa.analysis.quality import evaluate_quality
    from .journal import verify_cursor
    from .validation import journal_policy
    confirmed_prefix = verify_cursor((attempt / "events.jsonl").read_bytes(), store.cursor, **journal_policy(manifest, root, attempt / "manifest.json"))
    accepted_answers = list(history["answers"]) if history else []
    accepted_answers += [{**event["payload"]["query"], "answer": event["payload"]["answer"]} for event in confirmed_prefix["events"] if event["event_type"] == "answer_received"]
    quality = evaluate_quality(problem, oracle, solver_result["selected_candidate_id"] if solver_result else None,
        accepted_answers)
    try:
        if profiler is not None:
            metrics = [{"metric_id": "api_call", "scope": "wall", "aggregation": "inclusive", "value": api_elapsed or partial or 0.0, "unit": "seconds"},
                {"metric_id": "recorder_in_call", "scope": "wall", "aggregation": "inclusive", "value": recording_in_call, "unit": "seconds"},
                {"metric_id": "observer_in_call", "scope": "wall", "aggregation": "inclusive", "value": observer_elapsed, "unit": "seconds"}]
            # Publish the requested diagnostics before the terminal event. A
            # failed publication cannot leave a successful terminal decision.
            profiler.publish(context, attempt, root, payload["run_id"], payload["attempt_id"], metrics)
        if not store.failed:
            if result is not None:
                recorder.event("run_finished", {"termination_reason": result.termination_reason, "solved": result.solved, "query_counts": dict(confirmed)}, commit=True)
            elif interruption:
                recorder.event("run_interrupted", {"interruption": interruption, "query_counts": dict(confirmed)}, commit=True)
            else:
                recorder.event("run_failed", {"error": error, "query_counts": dict(confirmed)}, commit=True)
    except BaseException as exc:
        error = error_wire(exc, "persistence")
        interruption, solver_result, status, exit_code = None, None, "failed", 1
        quality = evaluate_quality(problem, oracle, None, accepted_answers)
    journal = store.journal_proof()
    if payload["answer_source"] == "replay":
        consumed = provider.consumed
        declared = len(replay["answers"])
        publish_json(context, attempt / "replay-status.json", {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"],
            "script": payload["inputs"]["replay_answers"], "declared_answers": declared, "consumed_answers": consumed,
            "remaining_answers": declared - consumed, "complete_replay": consumed == declared})
    envelope = {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"], "problem_id": problem["problem_id"],
        "configuration_id": config["configuration_id"], "execution_status": status, "execution_stage": "solver", "finalized_by": "case_process",
        "started_at_utc": started_at, "finished_at_utc": utc_now(), "query_counts": dict(store.cursor["query_counts"]),
        "timings": timings(case_elapsed=time.perf_counter() - case_start, api_elapsed=api_elapsed, partial=partial,
                           recorder=recording_in_call, answer_wait=provider_elapsed, observer=observer_elapsed, complete=complete),
        "solver_result": solver_result, "quality": quality, "error": error, "interruption": interruption,
        "telemetry_errors": observer.errors if observer is not None else [],
        "journal": journal, "numeric_hex": mathematical_hex(solver_result, "/solver_result") if solver_result else {}}
    publish_json(context, attempt / "result.json", envelope, kind="result")
    return exit_code


def main(argv=None):
    case_start, started_at = time.perf_counter(), utc_now()
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--release-fd", type=int, required=True)
    args = parser.parse_args(argv)
    payload = read_json(Path(args.request))
    context = load_project_context(Path(payload["project_root"]))
    attempt, root = Path(payload["attempt_dir"]), Path(payload["reference_root"])
    intent_path = attempt / "launch_intent.json"
    intent = validate("launch_intent", read_json(intent_path))
    identity = process_identity(intent["owner_token"])
    if identity["pid"] != identity["pgid"] or identity["pid"] != identity["sid"]:
        raise DocumentError("CaseProcess was not isolated into its own session/group")
    registration = {"schema_version": 1, "run_id": payload["run_id"], "attempt_id": payload["attempt_id"], "created_at_utc": utc_now(),
                    "intent": file_ref(intent_path, root), "nonce": intent["nonce"], "process": identity}
    publish_json(context, attempt / "child_registration.json", registration, kind="child_registration")
    try:
        pulse = os.read(args.release_fd, 1)
    finally:
        os.close(args.release_fd)
    if pulse != b"G":
        # EOF before release means no numerical import, worker or API call.
        return 1
    grant = validate("start_grant", read_json(attempt / "start_grant.json"))
    if grant["nonce"] != intent["nonce"] or grant["process"] != identity or grant["intent"] != registration["intent"] or grant["registration"] != file_ref(attempt / "child_registration.json", root):
        raise DocumentError("Start grant is not bound to this registered child")
    if any(name in sys.modules for name in ("numpy", "scipy")):
        raise DocumentError("Numerical module imported before case release")
    return run_attempt(payload, case_start=case_start, started_at=started_at, identity=identity)


if __name__ == "__main__":
    raise SystemExit(main())
