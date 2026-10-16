"""Actual-root progress admission, using independently specified state trees."""
from dataclasses import replace
import math

import pytest

from otqa.config import AlgorithmPolicy, SingleCandidateStop, VolumeConfidenceStop
from otqa.errors import InputValidationError
from otqa.models.core import Query
from otqa.models.planning import PolicyOption, QueryEvaluation
from otqa.planning.session import _Evaluated
from test_planning_selection import Node, session, queries, terminal_counts


def policy(strategy='fixed', depth=2, minimum=.001, stopping=None, evaluation='candidate_count'):
    return AlgorithmPolicy(strategy, depth, 'both', 5, evaluation,
        stopping or SingleCandidateStop(), min_expected_progress=minimum)


def test_policy_default_and_keyword_only_boundary_preserve_positional_fields():
    value = AlgorithmPolicy('fixed', 2, 'both', 5, 'candidate_count', SingleCandidateStop(), 'countdown')
    assert value.min_expected_progress == .001
    assert value.horizon_execution == 'countdown'
    with pytest.raises(TypeError):
        AlgorithmPolicy('fixed', 2, 'both', 5, 'candidate_count', SingleCandidateStop(), 'receding', .5)
    assert replace(value, min_expected_progress=None).min_expected_progress is None


@pytest.mark.parametrize('minimum', (-1, True, '0.001', math.nan, math.inf, -math.inf))
def test_policy_rejects_invalid_progress_before_planning(minimum):
    with pytest.raises(InputValidationError):
        policy(minimum=minimum)


@pytest.mark.parametrize('minimum,expected', ((.001, 'insufficient_expected_progress'), (0., 'insufficient_expected_progress'),
                                              (None, 'available')))
def test_fixed_zero_gain_is_an_explicit_rejection_not_an_empty_inventory(monkeypatch, minimum, expected):
    query = Query(0, 1, 1.)
    planner = session(policy(depth=1, minimum=minimum))
    queries(monkeypatch, {('root', 1): (query,)})
    terminal_counts(monkeypatch, {('root', 1.): 2}, [])
    attempt = planner.plan(Node('root', (0, 1)), requested_depth=1)
    assert attempt.outcome == expected
    horizon = attempt.horizon_evidence[0]
    assert horizon.generated_query_count == horizon.evaluated_query_count == 1
    assert horizon.best_progress.expected_progress == 0.
    assert attempt.best_progress_witness.query == query
    assert (attempt.selected_plan is not None) == (minimum is None)


def test_fixed_stop_aware_progress_uses_absorbed_loss_not_remaining_candidates(monkeypatch):
    query = Query(0, 1, 1.)
    root = Node('root', (0, 1, 2, 3))
    child = Node('child', (0, 1, 2, 3), shares=((0, .99), (1, .003), (2, .003), (3, .004)))
    planner = session(policy(stopping=VolumeConfidenceStop(.99), evaluation='stop_aware'),
                      {('root', 1., '<'): child})
    queries(monkeypatch, {('root', 2): (query,)})
    actual = planner.plan(root, requested_depth=2)
    assert actual.outcome == 'available'
    assert actual.selected_plan.score.expected_terminal_candidates == 4
    assert actual.selected_progress.basis == 'effective_loss'
    assert actual.selected_progress.expected_terminal_value == 1
    assert actual.selected_progress.expected_progress == 3


def test_adaptive_selects_a_sufficient_plan_before_ranking_rates(monkeypatch):
    planner = session(policy('reduction_per_query', 3))
    q1, q2 = Query(0, 1, 1.), Query(0, 1, 2.)
    queries(monkeypatch, {('root', 1): (q1,), ('root', 2): (q2,)})
    visited = []

    def evaluate(state, data, depth, mode, **kwargs):
        visited.append(depth)
        return tuple(_Evaluated(QueryEvaluation(query, 1.9992 if depth == 1 else 1.9989, ()), float(depth))
                     for query in data.query_candidates)

    planner._evaluate_many = evaluate
    actual = planner.plan(Node('root', (0, 1)), requested_depth=3)
    assert visited == [1, 2, 3]
    assert actual.selected_plan.query == q2
    assert [row.outcome for row in actual.horizon_evidence] == ['insufficient_expected_progress', 'available', 'no_query']
    assert actual.horizon_evidence[0].best_progress.expected_progress < .001


def test_h3_same_query_retains_an_admissible_more_expensive_continuation(monkeypatch):
    planner = session(policy('reduction_per_query', 3))
    query = Query(0, 1, 1.)
    root, left, right = Node('root', (0, 1)), Node('left', (0, 1)), Node('right', (0, 1))
    planner.states.transitions = {('root', 1., '<'): left, ('root', 1., '>'): right}
    planner.geometry.probabilities = lambda *a: {'<': .5, '=': 0., '>': .5}
    queries(monkeypatch, {('root', 3): (query,)})
    a = PolicyOption(QueryEvaluation(Query(0, 1, 2.), 1.99900015, ()), 1.99900015, 1.99900015, 1.99900015)
    b = PolicyOption(QueryEvaluation(Query(0, 1, 3.), 1.99899995, ()), 1.99899995, 1.99899995, 2.)
    planner._child_frontier = lambda child: (a, b)
    actual = planner.plan(root, requested_depth=3)
    assert actual.outcome == 'available'
    assert actual.selected_plan.score.gain > .001
    assert actual.selected_plan.score.expected_queries == 3.
    assert tuple(child.evaluation.query for child in actual.selected_plan.continuations) == (b.evaluation.query,) * 2


def test_maximum_progress_witness_is_not_the_best_rate_and_no_horizon_is_skipped(monkeypatch):
    planner = session(policy('reduction_per_query', 3, minimum=10.))
    q = {d: Query(0, 1, float(d)) for d in (1, 2, 3)}
    queries(monkeypatch, {('root', d): (q[d],) for d in q})
    seen = []

    def evaluate(state, data, depth, mode, **kwargs):
        seen.append(depth)
        return (_Evaluated(QueryEvaluation(q[depth], float(4 - depth), ()), float(depth)),)

    planner._evaluate_many = evaluate
    actual = planner.plan(Node('root', tuple(range(5))), requested_depth=3)
    assert seen == [1, 2, 3]
    assert actual.outcome == 'insufficient_expected_progress'
    assert actual.selected_plan is None
    assert actual.best_progress_witness.horizon == 3
    assert [row.best_progress.expected_progress for row in actual.horizon_evidence] == [2., 3., 4.]


@pytest.mark.parametrize('depth', (None, True, 0, -1, 1., 4))
def test_requested_depth_is_explicit_and_validated(depth):
    planner = session(policy())
    with pytest.raises((InputValidationError, ValueError)):
        planner.plan(Node('root', (0, 1)), requested_depth=depth)


def test_cache_keys_the_explicit_request_not_answer_modulo(monkeypatch):
    planner = session(policy(depth=3))
    q1, q2 = Query(0, 1, 1.), Query(0, 1, 2.)
    queries(monkeypatch, {('root', 1): (q1,), ('root', 2): (q2,)})
    visited = []
    planner._evaluate_many = lambda state, data, depth, mode, **kwargs: (
        visited.append(depth) or _Evaluated(QueryEvaluation(data.query_candidates[0], 1., ())),)
    root = Node('root', (0, 1))
    first = planner.plan(root, requested_depth=1)
    second = planner.plan(root, requested_depth=2)
    assert planner.plan(root, requested_depth=1) is first
    assert planner.plan(root, requested_depth=2) is second
    assert first.selected_plan.horizon == 1 and second.selected_plan.horizon == 2
    assert visited == [1, 2]
    assert len(planner._plan_cache) == 2
