"""Public input semantics and ownership, using freshly constructed examples."""
from dataclasses import FrozenInstanceError

import pytest

from otqa import (
    AlgorithmPolicy, AnsweredQuery, Problem, Query, QueryBudget,
    SingleCandidateStop, SolverExecution, VolumeConfidenceStop,
)
from otqa.errors import InputValidationError, InvalidAnswerError


def test_problem_owns_nested_values_and_keeps_original_order():
    source = [[0.0, 1.0], [0.0, 1.0], [0.6, 0.2]]
    problem = Problem(source)
    source[0][0] = 0.8
    assert problem.alternatives == ((0.0, 1.0), (0.0, 1.0), (0.6, 0.2))
    assert (problem.alternative_count, problem.objective_count) == (3, 2)
    with pytest.raises(FrozenInstanceError):
        problem.alternatives = ((1.0,),)


@pytest.mark.parametrize('matrix', [[], [[]], [[0.0], [0.0, 1.0]], [[True]],
                                   [[float('nan')]], [[float('inf')]], [[-0.01]], [[1.01]], [['1']]])
def test_problem_rejects_invalid_matrix_without_normalizing(matrix):
    with pytest.raises(InputValidationError):
        Problem(matrix)


def test_query_preserves_negative_zero_and_original_orientation():
    query = Query(1, 0, -0.0)
    assert query.value.hex() == '-0x0.0p+0'
    query.validate_for(Problem(((0.1, 0.9),)))
    with pytest.raises(InputValidationError):
        query.validate_for(Problem(((0.1,),)))


@pytest.mark.parametrize('args', [(True, 1, 1), (0, 0, 1), (0, -1, 1), (0, 1, -1), (0, 1, True)])
def test_invalid_queries(args):
    with pytest.raises(InputValidationError):
        Query(*args)


@pytest.mark.parametrize('answer', [True, 1, ' >', 'greater', None])
def test_provider_answers_are_exact_literals(answer):
    with pytest.raises(InvalidAnswerError):
        AnsweredQuery(Query(0, 1, 1), answer)


def test_algorithm_policy_and_budget_are_independent():
    policy = AlgorithmPolicy('reduction_per_query', 3, 'both', 5, 'stop_aware', SingleCandidateStop())
    assert policy.depth == 3
    assert not hasattr(policy.stopping, 'threshold')
    assert QueryBudget(1).max_queries == 1
    assert SolverExecution().cache_policy_id == 'bounded_v1'
    assert VolumeConfidenceStop(1).threshold == 1.0


@pytest.mark.parametrize('value', [True, 0, -1, 1.0])
def test_integer_controls_do_not_accept_boolean_or_float(value):
    with pytest.raises(InputValidationError):
        SolverExecution(workers=value)
    with pytest.raises(InputValidationError):
        QueryBudget(value)
