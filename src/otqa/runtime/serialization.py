"""Explicit domain-to-wire projection with original document ID mapping."""
from __future__ import annotations

import multiprocessing

from .codec import DocumentError, canonical_digest, float_projection
from .documents import typed_projection


def domain_inputs(problem_doc: dict, config_doc: dict, history_doc: dict | None):
    from otqa.config import AlgorithmPolicy, QueryBudget, SingleCandidateStop, SolverExecution, VolumeConfidenceStop
    from otqa.models.core import Problem
    algorithm = dict(config_doc["algorithm"])
    stopping = algorithm.pop("stopping")
    stop = SingleCandidateStop() if stopping["rule"] == "single_candidate" else VolumeConfidenceStop(float(stopping["threshold"]))
    problem = Problem(tuple(tuple(float(value) for value in row) for row in problem_doc["alternatives"]))
    policy = AlgorithmPolicy(**algorithm, stopping=stop)
    budget = QueryBudget(**config_doc["budget"])
    execution = SolverExecution(workers=config_doc["execution"]["workers"],
        multiprocessing_context=multiprocessing.get_context(config_doc["execution"]["start_method"]),
        cache_policy_id=config_doc["execution"]["cache_policy_id"])
    initial = history_answers(history_doc)
    return problem, policy, budget, execution, initial


def history_answers(document: dict | None):
    from otqa.models.core import AnsweredQuery, Query
    if document is None:
        return ()
    return tuple(AnsweredQuery(Query(item["goal_index_a"], item["goal_index_b"], float(item["value"])), item["answer"]) for item in document["answers"])


def query_wire(query) -> dict:
    return {"goal_index_a": query.goal_index_a, "goal_index_b": query.goal_index_b, "value": query.value}


def answered_wire(answer) -> dict:
    return {**query_wire(answer.query), "answer": answer.answer}


def score_wire(score) -> dict:
    from otqa.models.planning import EfficiencyScore, FixedScore
    common = {"expected_terminal_candidates": score.expected_terminal_candidates, "expected_terminal_loss": score.expected_terminal_loss}
    if isinstance(score, FixedScore):
        result = {"kind": "fixed", **common, "lexicographic_expected_values": list(score.lexicographic_profile)}
        if score.expected_queries is not None:
            result["expected_queries"] = score.expected_queries
        return result
    if isinstance(score, EfficiencyScore):
        return {"kind": "reduction_per_query", **common, "expected_queries": score.expected_queries, "gain": score.gain, "rate": score.rate}
    raise DocumentError("Unknown domain planning score")


def plan_summary(decision) -> dict:
    return {"horizon": decision.horizon, "query": query_wire(decision.query), "score": score_wire(decision.score),
            "answer_probabilities": dict(decision.answer_probabilities)}


def planning_wire(decision, *, stop_aware: bool, trace_level: str, candidate_count: int | None = None) -> dict:
    horizons = []
    for horizon in decision.horizons:
        selected_plan = getattr(horizon, "selected_plan", None)
        if horizon.selected_query is None:
            horizons.append({"horizon": horizon.horizon, "status": "no_query", "plan": None})
        elif selected_plan is not None:
            horizons.append({"horizon": horizon.horizon, "status": "available", "plan": plan_summary(selected_plan)})
        elif horizon.horizon == decision.horizon and horizon.selected_query == decision.query:
            horizons.append({"horizon": horizon.horizon, "status": "available", "plan": plan_summary(decision)})
        else:
            selected_score = getattr(horizon, "selected_score", None)
            selected_probabilities = getattr(horizon, "selected_answer_probabilities", None)
            if selected_score is None or selected_probabilities is None:
                raise DocumentError("Planner omitted an evaluated horizon's selected score/probabilities")
            horizons.append({"horizon": horizon.horizon, "status": "available", "plan": {"horizon": horizon.horizon,
                "query": query_wire(horizon.selected_query), "score": score_wire(selected_score), "answer_probabilities": dict(selected_probabilities)}})
    if not horizons:
        horizons = [{"horizon": decision.horizon, "status": "available", "plan": plan_summary(decision)}]
    # A selected tree is available only when actually exposed by the planner.
    # No recomputation is done merely to satisfy trace_level='full'.
    tree = _existing_plan_tree(decision, candidate_count, stop_aware) if trace_level == "full" else None
    return {"selected": plan_summary(decision), "horizons": horizons,
            "planning_stop_aware": stop_aware, "plan_tree": tree}


def _existing_plan_tree(decision, candidate_count, stop_aware):
    """Serialize retained chosen continuations; omitted lazy trees stay omitted."""
    if candidate_count is None:
        return None
    def continuation_node(item, node_id):
        loss = item.expected_terminal_loss
        if loss is None and not stop_aware:
            loss = item.expected_terminal_candidates
        if loss is None:
            return None
        evaluation = item.evaluation
        node = {"node_id": node_id, "candidate_count": item.candidate_count, "stop_reason": item.stop_reason,
            "maximum_volume_share": item.maximum_volume_share, "query": query_wire(evaluation.query) if evaluation else None,
            "expected_terminal_candidates": item.expected_terminal_candidates, "expected_terminal_loss": loss,
            "branches": [{"answer": child.answer, "probability": child.probability,
                "child": continuation_node(child, node_id + f"-b{index}") if child.probability > 0 else None}
                for index, child in enumerate(item.continuations)]}
        if item.expected_queries is not None:
            node["expected_queries"] = item.expected_queries
        return node
    branches = []
    if decision.continuations:
        branches = [{"answer": item.answer, "probability": item.probability,
            "child": continuation_node(item, f"root-b{index}") if item.probability > 0 else None}
            for index, item in enumerate(decision.continuations)]
    else:
        for index, branch in enumerate(decision.evaluation.branches):
            child = None
            loss = branch.expected_terminal_loss
            if loss is None and not stop_aware:
                loss = branch.expected_terminal_candidates
            if decision.horizon == 1 and branch.probability > 0 and branch.candidate_count is not None and loss is not None:
                child = {"node_id": f"root-b{index}", "candidate_count": branch.candidate_count, "stop_reason": branch.stop_reason,
                    "maximum_volume_share": branch.maximum_volume_share, "query": None, "expected_terminal_candidates": branch.expected_terminal_candidates,
                    "expected_terminal_loss": loss, "branches": []}
            branches.append({"answer": branch.answer, "probability": branch.probability, "child": child})
    tree = {"node_id": "root", "candidate_count": candidate_count, "stop_reason": None, "maximum_volume_share": None,
        "query": query_wire(decision.query), "expected_terminal_candidates": decision.score.expected_terminal_candidates,
        "expected_terminal_loss": decision.score.expected_terminal_loss, "branches": branches}
    if decision.score.expected_queries is not None:
        tree["expected_queries"] = decision.score.expected_queries
    return tree


def state_wire(state, alternatives: list[str], last_query_id: str | None) -> dict:
    return {"state_index": state.answered_total, "last_answer_query_id": last_query_id,
        "candidate_ids": [alternatives[index] for index in state.candidate_indices],
        "candidate_volumes": {alternatives[index]: value for index, value in state.candidate_volumes},
        "candidate_volume_shares": {alternatives[index]: value for index, value in state.candidate_volume_shares}}


def record_wire(record, query_id: str, *, stop_aware: bool, trace_level: str) -> dict:
    return {"query_id": query_id, "query": query_wire(record.query), "answer": record.answer,
        "planning": planning_wire(record.planning, stop_aware=stop_aware, trace_level=trace_level, candidate_count=record.before.candidate_count),
        "state_before_index": record.before.answered_total, "state_after_index": record.after.answered_total}


def result_wire(result, alternatives: list[str], *, stop_aware: bool, trace_level: str) -> dict:
    records = [record_wire(record, f"q{index + 1:06d}", stop_aware=stop_aware, trace_level=trace_level) for index, record in enumerate(result.queries)]
    last = records[-1]["query_id"] if records else None
    return {"solved": result.solved, "exactly_solved": result.exactly_solved, "termination_reason": result.termination_reason,
        "selected_candidate_id": None if result.selected_candidate_index is None else alternatives[result.selected_candidate_index],
        "selected_candidate_volume": result.selected_candidate_volume, "selected_candidate_volume_share": result.selected_candidate_volume_share,
        "final_state": state_wire(result.final_state, alternatives, last), "query_records": records,
        "answered_queries": [answered_wire(answer) for answer in result.answers]}


def mathematical_input_digest(problem: dict, config: dict, answer_source: str,
                              initial: dict | None, oracle: dict | None, replay: dict | None) -> str:
    effective_config = typed_projection("config", config)
    value = {"problem": typed_projection("problem", problem), "algorithm": effective_config["algorithm"], "budget": effective_config["budget"],
        "answer_source": answer_source, "initial_answers": [] if initial is None else typed_projection("answer_history", initial)["answers"],
        "oracle": None if oracle is None else typed_projection("oracle", oracle),
        "replay_answers": None if replay is None else typed_projection("answer_history", replay)["answers"]}
    return canonical_digest(float_projection(value))
