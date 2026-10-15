"""Small explicit state trees exercise planning decisions without LP noise."""

from collections import OrderedDict
from dataclasses import dataclass
import sys
from types import ModuleType, SimpleNamespace

import pytest
import otqa.state  # noqa: F401 — bind the real package before replacing its narrow leaf seam.

from otqa.config import AlgorithmPolicy, SingleCandidateStop, SolverExecution, VolumeConfidenceStop
from otqa.models.core import Query
from otqa.models.planning import EfficiencyScore, NoQuery, QueryEvaluation
from otqa.planning.session import PlannerSession, _Evaluated


@dataclass(frozen=True)
class Node:
    name: str
    candidates: tuple
    history: tuple = ()
    shares: tuple = ()
    is_feasible: bool = True

    @property
    def analysis(self):
        return SimpleNamespace(candidates=self.candidates,
            candidate_volume_shares=dict(self.shares) if self.shares else None)

    @property
    def weight_space(self):
        return self.name


class Engine:
    def __init__(self, transitions):
        self.transitions = transitions

    def bind(self, state):
        return state

    def check(self, state):
        pass

    def ensure_analysis(self, state, **kwargs):
        return state

    def advance(self, state, answered, **kwargs):
        return self.transitions[state.name, answered.query.value, answered.answer]


def session(policy=None, transitions=None):
    instance = PlannerSession.__new__(PlannerSession)
    instance.policy = policy or AlgorithmPolicy("fixed", 2, "both", 5, "candidate_count", SingleCandidateStop())
    instance.execution = SolverExecution(1)
    instance._closed = False
    instance._worker = False
    instance._capture = instance._capture_options = None
    instance._session_id = "analytic-session"
    instance._plan_index = instance._task_counter = instance._observation_ordinal = 0
    instance._plan_address = None
    instance._plan_cache = OrderedDict()
    instance.states = Engine(transitions or {})
    instance.geometry = SimpleNamespace(probabilities=lambda space, query: {"<": 1.0, "=": 0.0, ">": 0.0})
    return instance


def queries(monkeypatch, mapping):
    module = ModuleType("otqa.queries")
    module.canonical_key = lambda query: (query.goal_index_a, query.goal_index_b, query.value)
    module.generate_queries = lambda state, depth: SimpleNamespace(
        query_candidates=mapping.get((state.name, depth), ()), query_sources={})
    monkeypatch.setitem(sys.modules, "otqa.queries", module)


def terminal_counts(monkeypatch, mapping, visited):
    module = ModuleType("otqa.state.analysis")

    def count(state, query, answer, probability, **kwargs):
        visited.append((state.name, query.value))
        return mapping[state.name, query.value], True

    module.compute_terminal_candidate_count = count
    monkeypatch.setitem(sys.modules, "otqa.state.analysis", module)


def test_fixed_only_refines_exactly_tied_best_queries(monkeypatch):
    a, b, c = (Query(0, 1, value) for value in (1, 2, 3))
    root = Node("root", tuple(range(4)))
    planner = session(transitions={
        ("root", 1.0, "<"): Node("a", (0, 1)),
        ("root", 2.0, "<"): Node("b", (0, 1)),
        ("root", 3.0, "<"): Node("c", (0, 1, 2)),
    })
    queries(monkeypatch, {("root", 2): (a, b, c)})
    visited = []
    terminal_counts(monkeypatch, {("root", 1.0): 3, ("root", 2.0): 2}, visited)
    result = planner.plan(root)
    assert result.query == b
    assert result.score.lexicographic_profile == (2.0, 2.0)
    assert [item.lexicographic_profile for item in result.horizons[0].evaluations] == [(2, 3), (2, 2), (3,)]
    assert visited == [("root", 1.0), ("root", 2.0)]


def test_fixed_query_identity_breaks_exact_full_tie(monkeypatch):
    first, second = Query(0, 1, 1), Query(0, 1, 2)
    root = Node("root", (0, 1, 2))
    planner = session(AlgorithmPolicy("fixed", 1, "both", 5, "candidate_count", SingleCandidateStop()))
    queries(monkeypatch, {("root", 1): (second, first)})
    terminal_counts(monkeypatch, {("root", 1.0): 2, ("root", 2.0): 2}, [])
    assert planner.plan(root).query == first


def test_stop_aware_keeps_actual_candidates_separate_from_absorbed_loss(monkeypatch):
    query = Query(0, 1, 1)
    root = Node("root", (0, 1, 2, 3))
    child = Node("confident", (0, 1, 2), shares=((0, .99), (1, .005), (2, .005)))
    planner = session(AlgorithmPolicy("fixed", 2, "both", 5, "stop_aware", VolumeConfidenceStop(.99)),
                      {("root", 1.0, "<"): child})
    queries(monkeypatch, {("root", 2): (query,)})
    result = planner.plan(root)
    assert result.score.expected_terminal_candidates == 3
    assert result.score.expected_terminal_loss == 1
    assert result.score.expected_queries == 1
    assert result.score.lexicographic_profile == (3,)
    branch = result.evaluation.branches[0]
    assert branch.stop_reason == "volume_confidence"
    assert branch.expected_followup_queries == 0


def test_fixed_singleton_stop_aware_delegates_to_count_path(monkeypatch):
    query = Query(0, 1, 1)
    planner = session(AlgorithmPolicy("fixed", 1, "both", 5, "stop_aware", SingleCandidateStop()))
    queries(monkeypatch, {("root", 1): (query,)})
    terminal_counts(monkeypatch, {("root", 1.0): 2}, [])
    result = planner.plan(Node("root", (0, 1, 2)))
    assert result.score.expected_terminal_loss == 2
    assert result.score.expected_queries is None
    assert result.evaluation.expected_terminal_loss is None


def test_adaptive_depth_three_evaluates_all_horizons_and_uses_ratio_of_expectations(monkeypatch):
    q1, q2, q3 = (Query(0, 1, value) for value in (1, 2, 3))
    root = Node("root", tuple(range(5)))
    planner = session(AlgorithmPolicy("reduction_per_query", 3, "both", 5, "candidate_count", SingleCandidateStop()))
    queries(monkeypatch, {("root", 1): (q1,), ("root", 2): (q2,), ("root", 3): (q3,)})
    evaluated = []

    def evaluate(state, data, depth, mode, **kwargs):
        evaluated.append(depth)
        query, candidates, cost = {1: (q1, 3, 1), 2: (q2, 1, 2), 3: (q3, 1, 2.9)}[depth]
        return (_Evaluated(QueryEvaluation(query, candidates, ()), cost),)

    planner._evaluate_many = evaluate
    result = planner.plan(root)
    # H1 and H2 have rate two. Lower expected cost wins, not lower loss.
    assert evaluated == [1, 2, 3]
    assert result.horizon == 1
    assert result.query == q1
    assert isinstance(result.score, EfficiencyScore)
    assert result.score.rate == 2
    assert len(result.horizons) == 3


def test_h3_child_frontier_contains_only_complete_h2_options(monkeypatch):
    root = Node("child", (0, 1, 2))
    query = Query(0, 1, 2)
    planner = session(AlgorithmPolicy("reduction_per_query", 3, "both", 5, "candidate_count", SingleCandidateStop()))
    queries(monkeypatch, {("child", 2): (query,)})
    evaluation = QueryEvaluation(query, 2, ())
    seen = []

    def evaluate(state, data, depth, mode, **kwargs):
        seen.append((depth, mode, tuple(data.query_candidates)))
        return (_Evaluated(evaluation, 2),)

    planner._evaluate_many = evaluate
    frontier = planner._child_frontier(root)
    assert seen == [(2, "efficiency", (query,))]
    assert len(frontier) == 1
    assert frontier[0].expected_queries == 2
    assert frontier[0].evaluation.query == query
    assert not any(option.evaluation is None for option in frontier)


def test_no_query_horizons_remain_explicit(monkeypatch):
    planner = session(AlgorithmPolicy("reduction_per_query", 3, "both", 5, "candidate_count", SingleCandidateStop()))
    queries(monkeypatch, {})
    result = planner.plan(Node("root", (0, 1)))
    assert isinstance(result, NoQuery)
    assert [item.horizon for item in result.horizons] == [1, 2, 3]
    assert all(item.selected_query is None and item.evaluations == () for item in result.horizons)


def test_session_close_rejects_new_plan_before_touching_state():
    planner = session()
    planner._closed = True
    with pytest.raises(RuntimeError, match="closed"):
        planner.plan(None)


def test_broken_pool_is_an_execution_failure_and_keeps_original_cause():
    from concurrent.futures.process import BrokenProcessPool
    from otqa.errors import ExecutionContextError

    cause = BrokenProcessPool("analytical process failure")

    def failed_result():
        raise cause

    with pytest.raises(ExecutionContextError) as caught:
        PlannerSession._receive(failed_result, None)
    assert caught.value.__cause__ is cause


def test_pool_submission_failure_is_an_execution_failure():
    from otqa.errors import ExecutionContextError
    cause = OSError("analytical dispatch failure")

    class FailedPool:
        def submit(self, *args):
            raise cause

    with pytest.raises(ExecutionContextError) as caught:
        PlannerSession._submit(FailedPool(), object())
    assert caught.value.__cause__ is cause


def test_pickling_failure_is_an_execution_failure_but_math_error_is_preserved():
    import pickle
    from otqa.errors import ExecutionContextError, NumericalError

    for cause in [pickle.PicklingError("analytical transfer failure"), NumericalError("analytical geometry failure")]:
        def failed_result():
            raise cause

        if isinstance(cause, pickle.PicklingError):
            with pytest.raises(ExecutionContextError) as caught:
                PlannerSession._receive(failed_result, None)
            assert caught.value.__cause__ is cause
        else:
            with pytest.raises(NumericalError) as caught:
                PlannerSession._receive(failed_result, None)
            assert caught.value is cause
