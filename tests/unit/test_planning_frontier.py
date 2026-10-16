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


def test_child_pruning_capture_reports_actual_ties_and_existing_witnesses(monkeypatch):
    import otqa.planning.frontier as module

    a, b, same, worse = option(1, 3, 1), option(2, 2, 2), option(3, 2, 2), option(4, 3, 3)
    nearer = option(5, math.nextafter(2, 0), 3)
    inputs = [worse, same, nearer, b, a]
    original_identity = module.option_identity
    identities = []

    def identity(item):
        identities.append(item)
        return original_identity(item)

    monkeypatch.setattr(module, "option_identity", identity)
    expected = pareto_options(inputs)
    ordinary_calls = tuple(identities)
    identities.clear()
    events = []
    actual = pareto_options(inputs, lambda kind, value: events.append((kind, value)))
    assert actual == expected == (a, b, nearer)
    assert tuple(identities) == ordinary_calls
    assert all(kind == "frontier_projection" for kind, _ in events)
    decisions = [value for _, value in events]
    assert [item[3] for item in decisions] == [a, b, same, nearer, worse]
    assert [item[4:6] for item in decisions] == [
        (True, "certified_nondominated"), (True, "certified_nondominated"),
        (False, "certified_dominance"), (True, "certified_nondominated"),
        (False, "certified_dominance"),
    ]
    assert all(item[:3] == ("pruning_decision", "child_options", None) for item in decisions)
    assert decisions[2][3] is same and decisions[2][6] is b
    # The nearer loss cannot witness identity four: its identity is five.
    assert decisions[4][3] is worse and decisions[4][6] is b
    assert all(item[6] is None for item in decisions if item[4])


def test_weighted_pruning_capture_adds_no_identity_or_sum_calculations(monkeypatch):
    import otqa.planning.frontier as module

    a, b, same, worse = option(1, 3, 1), option(2, 2, 2), option(3, 2, 2), option(4, 3, 3)
    other = option(5, 1, 1)
    inputs = ((worse, same, b, a), (other,))
    original_identity, original_sum = module.option_identity, module.math.fsum
    identities, summands = [], []

    def identity(item):
        identities.append(item)
        return original_identity(item)

    def fsum(values):
        values = tuple(values)
        summands.append(values)
        return original_sum(values)

    monkeypatch.setattr(module, "option_identity", identity)
    monkeypatch.setattr(module.math, "fsum", fsum)
    expected = combine_frontiers(5, (.5, .5), inputs)
    ordinary_calls = (tuple(identities), tuple(summands))
    identities.clear()
    summands.clear()
    events = []
    actual = combine_frontiers(5, (.5, .5), inputs,
                               lambda kind, value: events.append((kind, value)))
    assert actual == expected
    assert (tuple(identities), tuple(summands)) == ordinary_calls
    decisions = [value for kind, value in events
                 if kind == "frontier_projection" and value[:2] == ("pruning_decision", "weighted_combinations")]
    assert all(item[:2] == ("pruning_decision", "weighted_combinations") for item in decisions)
    # Child projection already removes the two certified dominated options;
    # the final branch is scored directly rather than projected once more.
    assert [item[2] for item in decisions] == [0, 0]
    assert [item[3] for item in decisions] == [(a,), (b,)]
    assert all(item[6] is None for item in decisions if item[4])
    assert any(kind == "combination_choice" for kind, _ in events)
