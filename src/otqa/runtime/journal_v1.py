"""Independent validation of immutable journal prefixes and live cursor proofs."""
from __future__ import annotations

import math

from otqa.runtime.codec import DocumentError, decode, digest, mathematical_hex
from otqa.runtime.schema import validate
from otqa.runtime.storage import empty_counts


def _query_identity(query):
    if query["goal_index_a"] == query["goal_index_b"]:
        raise DocumentError("Query compares an objective with itself")
    return query["goal_index_a"], query["goal_index_b"], float(query["value"]).hex()


def mathematically_equal(left, right):
    return left == right and mathematical_hex(left) == mathematical_hex(right)


def validate_planning(planning):
    selected = planning["selected"]
    _query_identity(selected["query"])
    horizons = planning["horizons"]
    if len({item["horizon"] for item in horizons}) != len(horizons):
        raise DocumentError("Repeated planning horizon")
    match = [item for item in horizons if item["horizon"] == selected["horizon"]]
    if len(match) != 1 or match[0]["status"] != "available" or not mathematically_equal(match[0]["plan"], selected):
        raise DocumentError("Selected horizon is missing or differs from its evaluated plan")
    for horizon in horizons:
        plan = horizon["plan"]
        if (horizon["status"] == "no_query") != (plan is None):
            raise DocumentError("Horizon availability and plan disagree")
        if plan is not None:
            _query_identity(plan["query"])
            if plan["horizon"] != horizon["horizon"] or not math.isclose(sum(plan["answer_probabilities"].values()), 1., rel_tol=0., abs_tol=1e-9):
                raise DocumentError("Plan horizon or response probability mass is invalid")


def actual_stop(state, algorithm, budget, alternative_ids):
    """Evaluate only stored actual state data, with the public stop precedence."""
    candidates = state["candidate_ids"]
    order = {candidate: index for index, candidate in enumerate(alternative_ids)}
    if not candidates or not set(candidates).issubset(order):
        raise DocumentError("Actual state contains no candidates or unknown alternatives")
    if len(candidates) == 1:
        return "exact_single_candidate", candidates[0]
    stopping = algorithm["stopping"]
    if stopping["rule"] == "volume_confidence":
        shares = state["candidate_volume_shares"]
        if shares is None or set(shares) != set(candidates):
            raise DocumentError("Actual confidence state lacks complete volume shares")
        selected = min(candidates, key=lambda candidate: (-shares[candidate], order[candidate]))
        if shares[selected] >= stopping["threshold"]:
            return "volume_confidence", selected
    maximum = budget["max_queries"]
    if maximum is not None and state["state_index"] >= maximum:
        return "max_questions", None
    return None, None


def verify_planning_policy(planning, algorithm, answered_total):
    """Check the recorded horizon against the phase bound by accepted history."""
    if planning["planning_stop_aware"] != (algorithm["planning_evaluation"] == "stop_aware"):
        raise DocumentError("Recorded planning path differs from its effective policy")
    if planning["selected"]["score"]["kind"] != algorithm["query_strategy"]:
        raise DocumentError("Recorded score kind differs from its effective strategy")
    depth = algorithm["depth"]
    if algorithm["query_strategy"] == "fixed":
        if algorithm.get("horizon_execution", "receding") == "countdown":
            depth -= answered_total % depth
        horizons = {depth}
    else:
        horizons = set(range(1, depth + 1))
    if {item["horizon"] for item in planning["horizons"]} != horizons:
        raise DocumentError("Recorded horizon coverage differs from the effective policy")
    if planning["selected"]["horizon"] not in horizons:
        raise DocumentError("Selected planning horizon differs from the effective policy phase")


def verify_actual_policy(events, algorithm, budget, alternative_ids):
    """Check actual stop/budget order without evaluating any hypothetical plan."""
    state = None
    for event in events:
        kind, payload = event["event_type"], event["payload"]
        if kind == "state_analyzed":
            state = payload
            actual_stop(state, algorithm, budget, alternative_ids)
        elif kind == "query_planned":
            if state is None or actual_stop(state, algorithm, budget, alternative_ids)[0] is not None:
                raise DocumentError("Query planning continued after the actual stop or query budget")
            verify_planning_policy(payload["planning"], algorithm, state["state_index"])
        elif kind == "run_finished":
            if state is None:
                raise DocumentError("Normal completion has no actual state")
            expected, _ = actual_stop(state, algorithm, budget, alternative_ids)
            if payload["termination_reason"] != (expected or "no_query"):
                raise DocumentError("Terminal reason violates actual stopping and budget precedence")


def verify_prefix(data: bytes, byte_count: int, sha256: str, last_sequence: int, *, initial_answers: int = 0,
                  algorithm=None, budget=None, alternative_ids=None) -> dict:
    if type(byte_count) is not int or byte_count < 0 or byte_count > len(data):
        raise DocumentError("Cursor extends beyond available journal bytes")
    prefix = data[:byte_count]
    if digest(prefix) != sha256 or not prefix.endswith(b"\n"):
        raise DocumentError("Journal prefix digest or complete-line boundary differs")
    counts = empty_counts(initial_answers)
    active = answer = planning = None
    dispatched = terminal = False
    state_index = None
    last_answer_query_id = None
    last_state = None
    phase = "started"
    seen_states = set()
    seen_queries = set()
    last_monotonic = None
    run_id = attempt_id = started = None
    events = []
    for sequence, line in enumerate(prefix.splitlines(), 1):
        event = validate("event", decode(line))
        if event["sequence"] != sequence:
            raise DocumentError("Non-consecutive journal sequence")
        if last_monotonic is not None and event["monotonic_ns"] < last_monotonic:
            raise DocumentError("Journal monotonic timestamp regressed")
        last_monotonic = event["monotonic_ns"]
        if event["numeric_hex"] != mathematical_hex(event["payload"], "/payload"):
            raise DocumentError("Incomplete or incorrect event binary64 evidence")
        if sequence == 1:
            run_id, attempt_id, started = event["run_id"], event["attempt_id"], event["occurred_at_utc"]
            if event["event_type"] != "run_started" or event["query_id"] is not None:
                raise DocumentError("Journal must begin with run_started")
        elif event["run_id"] != run_id or event["attempt_id"] != attempt_id or event["event_type"] == "run_started":
            raise DocumentError("Journal identity changed or start repeated")
        if terminal:
            raise DocumentError("Event follows a terminal event")
        kind, payload, query_id = event["event_type"], event["payload"], event["query_id"]
        if kind == "state_analyzed":
            phase = "analyzing"
            if payload["state_index"] != counts["answered_total"] or payload["state_index"] in seen_states:
                raise DocumentError("State index differs from accepted answer count")
            if payload["last_answer_query_id"] != last_answer_query_id or query_id != last_answer_query_id:
                raise DocumentError("State is not bound to the latest accepted answer")
            if not payload["candidate_ids"]:
                raise DocumentError("An analyzed feasible state has no candidates")
            for key in ("candidate_volumes", "candidate_volume_shares"):
                if payload[key] is not None and set(payload[key]) != set(payload["candidate_ids"]):
                    raise DocumentError("State volume maps do not cover exactly its candidates")
            state_index = payload["state_index"]
            last_state = payload
            seen_states.add(state_index)
        elif kind == "query_planned":
            phase = "planning"
            if active is not None or query_id is None or query_id in seen_queries or state_index != counts["answered_total"] or payload["state_before_index"] != state_index:
                raise DocumentError("Planning does not follow the current actual state")
            active, planning, dispatched, answer = query_id, payload["planning"], False, None
            seen_queries.add(query_id)
            validate_planning(planning)
        elif kind == "query_dispatched":
            phase = "awaiting_answer"
            if query_id != active or active is None or dispatched or _query_identity(payload["query"]) != _query_identity(planning["selected"]["query"]):
                raise DocumentError("Dispatch is not bound to one selected query")
            counts["dispatched_new"] += 1
            if payload["dispatched_new"] != counts["dispatched_new"]:
                raise DocumentError("Dispatch count differs")
            dispatched = True
        elif kind == "answer_received":
            phase = "answer_committed"
            if query_id != active or not dispatched or answer is not None or _query_identity(payload["query"]) != _query_identity(planning["selected"]["query"]):
                raise DocumentError("Answer is not bound to an open dispatched query")
            answer = payload["answer"]
            last_answer_query_id = query_id
            counts["answered_new"] += 1
            counts["answered_total"] += 1
            if payload["answered_new"] != counts["answered_new"] or payload["answered_total"] != counts["answered_total"]:
                raise DocumentError("Answer counts differ")
        elif kind == "query_completed":
            if query_id != active or payload["query_id"] != active or answer is None or payload["answer"] != answer or state_index != counts["answered_total"]:
                raise DocumentError("Completion lacks its committed answer and actual successor state")
            if payload["state_before_index"] != counts["answered_total"] - 1 or payload["state_after_index"] != counts["answered_total"] or not mathematically_equal(payload["planning"], planning) or _query_identity(payload["query"]) != _query_identity(planning["selected"]["query"]):
                raise DocumentError("Completion state/planning binding differs")
            active = planning = answer = None
        elif kind in ("run_finished", "run_failed", "run_interrupted"):
            if payload["query_counts"] != counts or query_id is not None:
                raise DocumentError("Terminal journal counts differ")
            if kind == "run_finished" and active is not None:
                raise DocumentError("Normal finish retains an incomplete query")
            if kind == "run_finished":
                reason = payload["termination_reason"]
                if last_state is None or payload["solved"] != (reason in ("exact_single_candidate", "volume_confidence")):
                    raise DocumentError("Terminal reason and solved flag disagree")
                singleton = len(last_state["candidate_ids"]) == 1
                if singleton != (reason == "exact_single_candidate"):
                    raise DocumentError("Terminal reason disagrees with actual singleton state")
            terminal = True
            phase = {"run_finished": "completed", "run_failed": "failed", "run_interrupted": "interrupted"}[kind]
            active = None
        events.append(event)
    if not events or len(events) != last_sequence:
        raise DocumentError("Cursor last sequence differs from verified prefix")
    if any(value is not None for value in (algorithm, budget, alternative_ids)):
        if any(value is None for value in (algorithm, budget, alternative_ids)):
            raise DocumentError("Actual policy verification requires policy, budget and alternative IDs together")
        verify_actual_policy(events, algorithm, budget, alternative_ids)
    return {"run_id": run_id, "attempt_id": attempt_id, "query_counts": counts, "events": events,
            "last_event_type": events[-1]["event_type"], "started_at_utc": started, "active_query_id": active, "query_phase": phase, "last_state": last_state}


def verify_cursor(data: bytes, cursor: dict, *, initial_answers=0, algorithm=None, budget=None, alternative_ids=None,
                  manifest_sha256=None):
    """Shared reader for live ProgressDoc and immutable PartialSnapshotDoc."""
    prefix = verify_prefix(data, cursor["valid_prefix_bytes"], cursor["valid_prefix_sha256"], cursor["last_good_sequence"],
        initial_answers=initial_answers, algorithm=algorithm, budget=budget, alternative_ids=alternative_ids)
    for key in ("run_id", "attempt_id", "query_counts", "query_phase", "active_query_id"):
        if cursor[key] != prefix[key]:
            raise DocumentError(f"Cursor {key} differs from its verified journal prefix")
    if manifest_sha256 is not None and prefix["events"][0]["payload"]["manifest_sha256"] != manifest_sha256:
        raise DocumentError("Cursor prefix start does not bind its actual manifest")
    return prefix
