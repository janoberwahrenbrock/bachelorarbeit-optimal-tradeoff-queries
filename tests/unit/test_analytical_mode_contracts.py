"""Small analytical mode contracts through real geometry and the public SDK.

For two objectives, the uniform simplex has w0 uniformly distributed on [0, 1].
The query w0/w1 > .91 leaves w0 > .91/1.91. Alternative 0 wins for w0 > .5,
so its posterior share is (1 + .91)/2 = .955: above 95%, below 99%.
"""
import pytest

from otqa import (
    AlgorithmPolicy, AnsweredQuery, Problem, Query, QueryBudget,
    SingleCandidateStop, SolverExecution, VolumeConfidenceStop, solve,
)
from otqa.answers import SimulatedAnswers
from otqa.errors import PlanningInvariantError
from otqa.planning import PlannerSession


TWO_ALTERNATIVES = Problem(((1., 0.), (0., 1.)))


def test_real_single_objective_sdk_publishes_empty_state_then_errors_before_provider():
    events = []
    policy = AlgorithmPolicy('fixed', 1, 'both', 5, 'candidate_count', SingleCandidateStop())
    with pytest.raises(PlanningInvariantError, match='feasible query state has no candidate alternatives') as raised:
        solve(Problem(((.8,), (.2,))), policy,
              lambda query: pytest.fail('One-objective error must precede provider dispatch'),
              execution=SolverExecution(1), recorder=events.append)
    assert [type(event).__name__ for event in events] == ['StateAnalyzed']
    assert events[0].state.feasible
    assert events[0].state.candidate_indices == ()
    assert raised.value.context.query_counts.dispatched_new == 0
    assert raised.value.context.query_counts.answered_new == 0


@pytest.mark.parametrize('weights,winner', [((.99, .01), 0), ((.01, .99), 1)])
def test_full_grid_only_and_both_depth_two_solve_the_analytical_winner(weights, winner):
    # These weights lie beyond a separating Grid5 value. Both permitted query
    # policies can therefore identify the correct winner with singleton stop.
    # Equal query trajectories are not an obligation of different query sets.
    for source in ('grid', 'both'):
        policy = AlgorithmPolicy('fixed', 2, source, 5, 'candidate_count', SingleCandidateStop())
        result = solve(TWO_ALTERNATIVES, policy, SimulatedAnswers(weights),
                       execution=SolverExecution(1), budget=QueryBudget(16))
        assert result.solved and result.exactly_solved
        assert result.selected_candidate_index == winner
        assert result.final_state.candidate_indices == (winner,)
        assert 0 < result.query_counts.answered_new <= 16
        if source == 'grid':
            assert all(record.planning.evaluation.query_source == 'grid' for record in result.queries)


@pytest.mark.parametrize('planning,threshold,absorbed', [
    ('candidate_count', .95, False), ('stop_aware', .95, True), ('stop_aware', .99, False),
])
def test_real_geometry_distinguishes_95_percent_planning_from_actual_candidate_expectation(
    planning, threshold, absorbed,
):
    policy = AlgorithmPolicy('reduction_per_query', 1, 'both', 5, planning, VolumeConfidenceStop(threshold))
    with PlannerSession(TWO_ALTERNATIVES, policy, SolverExecution(1)) as planner:
        root = planner.initial_state()
        result = planner._evaluate_one(root, Query(0, 1, .91), 1, 'ratio', 'efficiency')
    evaluation = result.evaluation
    probability_greater = 1. / 1.91
    expected_actual_candidates = 1. + probability_greater
    assert dict((branch.answer, branch.probability) for branch in evaluation.branches)['>'] == pytest.approx(probability_greater)
    assert evaluation.expected_terminal_candidates == pytest.approx(expected_actual_candidates)
    assert result.expected_queries == 1.
    if planning == 'candidate_count':
        assert evaluation.expected_terminal_loss is None
    else:
        assert evaluation.expected_terminal_loss == pytest.approx(1. if absorbed else expected_actual_candidates)
        greater = next(branch for branch in evaluation.branches if branch.answer == '>')
        assert greater.candidate_count == 2
        assert greater.maximum_volume_share == pytest.approx(.955)
        assert greater.stop_reason == ('volume_confidence' if absorbed else None)
        assert greater.expected_terminal_loss == (1. if absorbed else 2.)


@pytest.mark.parametrize('planning', ['candidate_count', 'stop_aware'])
def test_actual_95_percent_sdk_stop_precedes_provider_while_99_percent_continues(planning):
    history = (AnsweredQuery(Query(0, 1, .91), '>'),)
    policy95 = AlgorithmPolicy('reduction_per_query', 2, 'both', 5, planning, VolumeConfidenceStop(.95))
    result95 = solve(TWO_ALTERNATIVES, policy95,
                     lambda query: pytest.fail('95% already reached: provider must not run'),
                     initial_answers=history, execution=SolverExecution(1))
    assert result95.solved and not result95.exactly_solved
    assert result95.termination_reason == 'volume_confidence'
    assert result95.selected_candidate_index == 0
    assert result95.final_state.candidate_indices == (0, 1)
    assert result95.selected_candidate_volume_share == pytest.approx(.955)
    assert result95.query_counts.initial_answers == result95.query_counts.answered_total == 1
    assert result95.query_counts.dispatched_new == result95.query_counts.answered_new == 0

    provider_calls = []
    simulated = SimulatedAnswers((.6, .4))
    def provider(query):
        provider_calls.append(query)
        return simulated(query)
    policy99 = AlgorithmPolicy('reduction_per_query', 2, 'both', 5, planning, VolumeConfidenceStop(.99))
    result99 = solve(TWO_ALTERNATIVES, policy99, provider,
                     initial_answers=history, execution=SolverExecution(1), budget=QueryBudget(8))
    assert result99.solved and result99.selected_candidate_index == 0
    assert len(provider_calls) == result99.query_counts.answered_new > 0
    assert result99.query_counts.initial_answers == 1
