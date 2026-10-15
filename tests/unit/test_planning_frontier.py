"""Analytical loss/cost examples, independently enumerated by the test."""

from itertools import product
import math

from otqa.models.core import Query
from otqa.models.planning import PolicyOption, QueryEvaluation, option_identity
from otqa.planning.frontier import combine_frontiers, pareto_options


def option(value, loss, cost):
    evaluation = QueryEvaluation(Query(0, 1, value), loss, ())
    return PolicyOption(evaluation, loss, loss, cost)


def test_frontier_uses_exact_dominance_and_deterministic_identity():
    a = option(1, 3, 1)
    b = option(2, 2, 2)
    c = option(3, 2, 3)
    d = option(4, math.nextafter(2, 0), 3)
    same = option(5, 3, 1)
    assert pareto_options([c, d, b, same, a]) == (a, b, d)


def test_global_ratio_matches_exhaustive_complete_policy_product():
    frontiers = (
        (option(1, 3, 1), option(2, 1, 2.9)),
        (option(3, 3, 1), option(4, 1, 2.0)),
        (option(5, 2, 1), option(6, 1, 2.4)),
    )
    probabilities = (0.25, 0.5, 0.25)

    def key(chosen):
        loss = math.fsum(p * child.expected_terminal_loss for p, child in zip(probabilities, chosen))
        cost = 1 + math.fsum(p * child.expected_queries for p, child in zip(probabilities, chosen))
        return (-(5 - loss) / cost, cost, tuple(option_identity(item) for item in chosen))

    expected = min(product(*frontiers), key=key)
    assert combine_frontiers(5, probabilities, frontiers) == expected


def test_global_choice_can_differ_from_locally_best_child_rates():
    # The root overhead and other branches change the best tradeoff in child 0.
    frontiers = ((option(1, 3, 0.2), option(2, 1, 2)), (option(3, 5, 0),))
    chosen = combine_frontiers(5, (0.1, 0.9), frontiers)
    local = max(frontiers[0], key=lambda item: (5 - item.expected_terminal_loss) / item.expected_queries)
    assert chosen[0] is frontiers[0][1]
    assert local is frontiers[0][0]


def test_no_voluntary_stopping_option_is_added_by_combination():
    only = option(1, 4, 2)
    assert combine_frontiers(5, (1.0,), ((only,),)) == (only,)


def test_empty_positive_child_frontier_is_an_error():
    import pytest
    with pytest.raises(RuntimeError, match="missing positive-probability"):
        combine_frontiers(3, (1.0,), ((),))
