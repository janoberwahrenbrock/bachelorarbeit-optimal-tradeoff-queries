"""History-bound countdown phases across JSON, SDK adapters and durable readers."""
from copy import deepcopy
from uuid import uuid4

import pytest

from otqa.runtime.codec import DocumentError, digest, encode, mathematical_hex
from otqa.runtime.journal import verify_actual_policy, verify_prefix
from otqa.runtime.schema import validate
from otqa.runtime.serialization import domain_inputs


def configuration():
    return {"schema_version": 1, "configuration_id": "countdown-control",
        "algorithm": {"query_strategy": "fixed", "depth": 2, "higher_depth_query_source": "both", "grid_size": 5,
                      "planning_evaluation": "candidate_count", "stopping": {"rule": "single_candidate"}},
        "budget": {"max_queries": None},
        "execution": {"workers": 1, "start_method": "forkserver", "native_threads": 1, "case_timeout_seconds": None, "cache_policy_id": "bounded_v1"},
        "recording": {"durability": "per_answer", "trace_level": "standard", "profile": False, "telemetry_failure_policy": "continue"}}


def planning(horizon):
    plan = {"horizon": horizon, "query": {"goal_index_a": 0, "goal_index_b": 1, "value": 1.},
        "score": {"kind": "fixed", "expected_terminal_candidates": 1.5, "expected_terminal_loss": 1.5,
                  "lexicographic_expected_values": [1.5]},
        "answer_probabilities": {"<": .5, "=": 0., ">": .5}}
    return {"selected": plan, "horizons": [{"horizon": horizon, "status": "available", "plan": deepcopy(plan)}],
            "planning_stop_aware": False, "plan_tree": None}


def state(index, query_id=None):
    return {"state_index": index, "last_answer_query_id": query_id, "candidate_ids": ["a", "b"],
            "candidate_volumes": None, "candidate_volume_shares": None}


def test_legacy_configuration_defaults_without_mutating_stored_document():
    document = configuration()
    snapshot = deepcopy(document)
    assert validate("config", document) is document
    problem = {"alternatives": [[1., 0.], [0., 1.]]}
    _, policy, *_ = domain_inputs(problem, document, None)
    assert policy.horizon_execution == "receding"
    assert document == snapshot and "horizon_execution" not in document["algorithm"]


@pytest.mark.parametrize("depth", [1, 2, 3])
def test_countdown_configuration_and_sdk_adapter_preserve_explicit_mode(depth):
    document = configuration()
    document["algorithm"].update(depth=depth, horizon_execution="countdown")
    validate("config", document)
    _, policy, *_ = domain_inputs({"alternatives": [[1., 0.], [0., 1.]]}, document, None)
    assert policy.depth == depth and policy.horizon_execution == "countdown"


@pytest.mark.parametrize("mode", ["reset", "", None, True, 2])
def test_schema_rejects_unknown_or_untyped_execution_mode(mode):
    document = configuration()
    document["algorithm"]["horizon_execution"] = mode
    with pytest.raises(DocumentError):
        validate("config", document)


def test_schema_rejects_adaptive_countdown_but_accepts_legacy_and_explicit_receding():
    document = configuration()
    document["algorithm"]["query_strategy"] = "reduction_per_query"
    validate("config", document)
    document["algorithm"]["horizon_execution"] = "receding"
    validate("config", document)
    document["algorithm"]["horizon_execution"] = "countdown"
    with pytest.raises(DocumentError):
        validate("config", document)


@pytest.mark.parametrize("depth,horizons", [(1, [1, 1, 1]), (2, [2, 1, 2, 1, 2]), (3, [3, 2, 1, 3, 2, 1, 3])])
def test_policy_reader_accepts_only_actual_countdown_phase(depth, horizons):
    algorithm = {**configuration()["algorithm"], "depth": depth, "horizon_execution": "countdown"}
    for answered_total, expected in enumerate(horizons):
        events = [{"event_type": "state_analyzed", "payload": state(answered_total)},
                  {"event_type": "query_planned", "payload": {"planning": planning(expected)}}]
        verify_actual_policy(events, algorithm, {"max_queries": None}, ["a", "b"])
        if expected != depth:
            events[1]["payload"]["planning"] = planning(depth)
            with pytest.raises(DocumentError, match="horizon coverage"):
                verify_actual_policy(events, algorithm, {"max_queries": None}, ["a", "b"])


@pytest.mark.parametrize("explicit", [False, True])
def test_receding_reader_keeps_full_horizon_after_any_accepted_history(explicit):
    algorithm = configuration()["algorithm"]
    if explicit:
        algorithm["horizon_execution"] = "receding"
    events = [{"event_type": "state_analyzed", "payload": state(7)},
              {"event_type": "query_planned", "payload": {"planning": planning(2)}}]
    verify_actual_policy(events, algorithm, {"max_queries": None}, ["a", "b"])
    events[1]["payload"]["planning"] = planning(1)
    with pytest.raises(DocumentError, match="horizon coverage"):
        verify_actual_policy(events, algorithm, {"max_queries": None}, ["a", "b"])


def journal_events(initial_answers, horizons):
    run_id = str(uuid4())
    events = []
    counts = {"initial_answers": initial_answers, "dispatched_new": 0, "answered_new": 0, "answered_total": initial_answers}

    def append(kind, payload, query_id=None):
        sequence = len(events) + 1
        events.append({"schema_version": 1, "run_id": run_id, "attempt_id": "attempt0001", "sequence": sequence,
            "occurred_at_utc": "2026-10-15T00:00:00Z", "monotonic_ns": sequence, "event_type": kind,
            "query_id": query_id, "payload": payload, "numeric_hex": mathematical_hex(payload, "/payload")})

    append("run_started", {"manifest_sha256": "0" * 64})
    append("state_analyzed", state(initial_answers))
    for offset, horizon in enumerate(horizons, 1):
        index = counts["answered_total"]
        query_id = f"q{offset:06d}"
        plan = planning(horizon)
        query = plan["selected"]["query"]
        append("query_planned", {"state_before_index": index, "planning": plan}, query_id)
        counts["dispatched_new"] += 1
        append("query_dispatched", {"query": query, "dispatched_new": counts["dispatched_new"]}, query_id)
        counts["answered_new"] += 1
        counts["answered_total"] += 1
        append("answer_received", {"query": query, "answer": "<", "answered_new": counts["answered_new"], "answered_total": counts["answered_total"]}, query_id)
        append("state_analyzed", state(index + 1, query_id), query_id)
        append("query_completed", {"query_id": query_id, "query": query, "answer": "<", "planning": plan,
            "state_before_index": index, "state_after_index": index + 1}, query_id)
    append("run_finished", {"termination_reason": "no_query", "solved": False, "query_counts": counts.copy()})
    return events


def verify_events(events, initial_answers=1):
    data = b"".join(encode(event) for event in events)
    return verify_prefix(data, len(data), digest(data), len(events), initial_answers=initial_answers,
        algorithm={**configuration()["algorithm"], "horizon_execution": "countdown"}, budget={"max_queries": None}, alternative_ids=["a", "b"])


def test_durable_journal_continues_phase_from_initial_answers():
    prefix = verify_events(journal_events(1, [1, 2, 1]))
    assert prefix["query_counts"] == {"initial_answers": 1, "dispatched_new": 3, "answered_new": 3, "answered_total": 4}
    assert prefix["query_phase"] == "completed"


def test_rehashed_journal_with_reset_phase_is_rejected_despite_consistent_internal_plan():
    events = journal_events(1, [2, 1])
    with pytest.raises(DocumentError, match="horizon coverage"):
        verify_events(events)


def test_selected_horizon_cannot_escape_coverage_in_policy_reader():
    plan = planning(1)
    plan["selected"]["horizon"] = 2
    events = [{"event_type": "state_analyzed", "payload": state(1)},
              {"event_type": "query_planned", "payload": {"planning": plan}}]
    with pytest.raises(DocumentError, match="Selected planning horizon"):
        verify_actual_policy(events, {**configuration()["algorithm"], "horizon_execution": "countdown"}, {"max_queries": None}, ["a", "b"])
