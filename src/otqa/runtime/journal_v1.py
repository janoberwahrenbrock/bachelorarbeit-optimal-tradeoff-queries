"""Independent validation of immutable journal prefixes and live cursor proofs."""
from __future__ import annotations

from otqa.runtime.codec import DocumentError, decode, digest, mathematical_hex
from otqa.runtime.schema import validate
from otqa.runtime.journal_structure import (
    _fold_validated_events,
    _query_identity as _query_identity,
    mathematically_equal as mathematically_equal,
    validate_planning as validate_planning,
)


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


def _validated_events(prefix):
    """Yield one historically validated event, without reading ahead."""
    last_monotonic = None
    for sequence, line in enumerate(prefix.splitlines(), 1):
        event = validate("event", decode(line))
        if event["sequence"] != sequence:
            raise DocumentError("Non-consecutive journal sequence")
        if last_monotonic is not None and event["monotonic_ns"] < last_monotonic:
            raise DocumentError("Journal monotonic timestamp regressed")
        last_monotonic = event["monotonic_ns"]
        if event["numeric_hex"] != mathematical_hex(event["payload"], "/payload"):
            raise DocumentError("Incomplete or incorrect event binary64 evidence")
        yield event


def verify_prefix(data: bytes, byte_count: int, sha256: str, last_sequence: int, *, initial_answers: int = 0,
                  algorithm=None, budget=None, alternative_ids=None) -> dict:
    if type(byte_count) is not int or byte_count < 0 or byte_count > len(data):
        raise DocumentError("Cursor extends beyond available journal bytes")
    prefix = data[:byte_count]
    if digest(prefix) != sha256 or not prefix.endswith(b"\n"):
        raise DocumentError("Journal prefix digest or complete-line boundary differs")
    result = _fold_validated_events(_validated_events(prefix), last_sequence,
        initial_answers=initial_answers)
    if any(value is not None for value in (algorithm, budget, alternative_ids)):
        if any(value is None for value in (algorithm, budget, alternative_ids)):
            raise DocumentError("Actual policy verification requires policy, budget and alternative IDs together")
        verify_actual_policy(result['events'], algorithm, budget, alternative_ids)
    return result


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
