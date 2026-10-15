import math

import pytest

from otqa.models.planning import EfficiencyScore, FixedScore, QueryEvaluation
from otqa.models.core import Query


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, True])
@pytest.mark.parametrize("field", ["expected_terminal_candidates", "expected_terminal_loss", "expected_queries", "gain", "rate"])
def test_efficiency_scores_reject_nonfinite_or_boolean_values(field, value):
    values = dict(expected_terminal_candidates=2.0, expected_terminal_loss=2.0,
                  expected_queries=1.5, gain=1.0, rate=2 / 3)
    values[field] = value
    with pytest.raises(ValueError):
        EfficiencyScore(**values)


@pytest.mark.parametrize("cost", [0, -1, math.nan])
def test_efficiency_costs_are_positive(cost):
    with pytest.raises(ValueError):
        EfficiencyScore(2, 2, cost, 1, 1)


def test_fixed_missing_lazy_values_are_absent_rather_than_zeros():
    values = [2.0]
    score = FixedScore(2, 2, values)
    values.append(0.0)
    assert score.lexicographic_profile == (2.0,)
    assert score.expected_queries is None


def test_query_evaluation_owns_sequence_containers():
    branches = []
    profile = [2.0]
    evaluation = QueryEvaluation(Query(0, 1, 1), 2, branches, lexicographic_profile=profile)
    branches.append("mutation")
    profile[0] = 0
    assert evaluation.branches == ()
    assert evaluation.lexicographic_profile == (2,)
