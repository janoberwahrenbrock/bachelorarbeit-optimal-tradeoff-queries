"""Independent complete products certify threshold and floating-point edges."""
from itertools import product
import math
import random

import pytest

from otqa.models.core import Query
from otqa.models.planning import PolicyOption, QueryEvaluation, option_identity
from otqa.planning.frontier import select_frontiers, pareto_options
from otqa.planning.dominance import binary_integer, certified_projection


def option(identity, loss, cost):
    return PolicyOption(QueryEvaluation(Query(0, 1, float(identity)), loss, ()), loss, loss, cost)


def exhaustive(count, probabilities, raw, threshold):
    rows = []
    for chosen in product(*raw):
        loss = math.fsum(p * item.expected_terminal_loss for p, item in zip(probabilities, chosen, strict=True))
        cost = 1 + math.fsum(p * item.expected_queries for p, item in zip(probabilities, chosen, strict=True))
        gain = float(count) - loss
        identity = tuple(option_identity(item) for item in chosen)
        rows.append((chosen, gain, (-gain / cost, cost, identity), (-gain, identity)))
    eligible = [row for row in rows if threshold is None or row[1] > threshold]
    return (min(eligible, key=lambda row: row[2])[0] if eligible else None,
            min(rows, key=lambda row: row[3])[0])


def test_h3_threshold_selects_another_complete_policy_of_the_same_root_query():
    a, b = option(1, 1.99900015, 1.99900015), option(2, 1.99899995, 2.)
    raw, probabilities = ((a, b), (a, b)), (.5, .5)
    assert select_frontiers(2, probabilities, raw).selected == (a, a)
    actual = select_frontiers(2, probabilities, raw, minimum=.001)
    assert actual.selected == actual.best_progress_witness == (b, b)
    assert (actual.selected, actual.best_progress_witness) == exhaustive(2, probabilities, raw, .001)


def test_native_rounding_of_partial_sums_does_not_discard_the_full_winner():
    a = option(2, 1.5, math.nextafter(1.5, math.inf))
    b = option(1, math.nextafter(1.5, math.inf), 1.5)
    c, d = option(3, 1., 1.), option(4, math.nextafter(1., math.inf), 2.)
    probabilities, raw = (.5, .25, .25), ((a, b), (c,), (d,))
    assert math.fsum((.5 * a.expected_terminal_loss, .25)) == math.fsum((.5 * b.expected_terminal_loss, .25))
    actual = select_frontiers(2, probabilities, raw, minimum=.001)
    assert actual.selected == (a, c, d)
    assert actual.selected == exhaustive(2, probabilities, raw, .001)[0]


def test_global_key_identity_is_preserved_when_weighting_erases_a_child_advantage():
    low_identity = option(1, math.nextafter(2., math.inf), 1.)
    lower_loss = option(2, 2., 1.)
    # Both must remain: later multiplication can erase the real loss advantage.
    assert set(pareto_options((lower_loss, low_identity))) == {low_identity, lower_loss}
    probabilities = (2.**-60, 1. - 2.**-60)
    raw = ((low_identity, lower_loss), (option(3, 1., 1.),))
    actual = select_frontiers(3, probabilities, raw)
    assert actual.selected == exhaustive(3, probabilities, raw, None)[0]


def test_all_negative_native_gains_use_unpruned_raw_children(monkeypatch):
    import otqa.planning.frontier as module
    cheap, expensive = option(1, math.nextafter(2., math.inf), 1.), option(2, math.nextafter(2., math.inf), 2.)
    monkeypatch.setattr(module, 'pareto_options', lambda *a, **k: pytest.fail('negative gain cannot use cost dominance'))
    actual = select_frontiers(2, (1.,), ((cheap, expensive),))
    assert actual.selected == (expensive,)
    assert actual.best_progress_witness == (cheap,)


def test_strict_progress_comparison_uses_subtraction_not_rounded_loss_cutoff():
    value = option(1, 1.999, 1.)
    gain = 2. - value.expected_terminal_loss
    thresholds = (math.nextafter(gain, -math.inf), gain, math.nextafter(gain, math.inf))
    assert value.expected_terminal_loss == 2. - thresholds[0]
    for threshold, accepted in zip(thresholds, (True, False, False), strict=True):
        result = select_frontiers(2, (1.,), ((value,),), minimum=threshold)
        assert (result.selected is not None) is accepted
        assert result.best_progress_witness == (value,)


@pytest.mark.parametrize('branches', (1, 2, 3))
@pytest.mark.parametrize('threshold', (None, 0., .001, .75, 10.))
def test_certified_projection_matches_exhaustive_products_near_binary_neighbors(branches, threshold):
    rng = random.Random(4600 + branches)
    probabilities = {1: (1.,), 2: (.25, .75), 3: (.125, .375, .5)}[branches]
    losses = (1., math.nextafter(1., math.inf), 1.999, 2., math.nextafter(2., math.inf), 2.5)
    costs = (0., 1., math.nextafter(1., math.inf), 1.5, 2.)
    for _ in range(40):
        raw = tuple(tuple(option(index * 10 + j, rng.choice(losses), rng.choice(costs))
                          for j in range(4)) for index in range(branches))
        actual = select_frontiers(3, probabilities, raw, minimum=threshold)
        assert (actual.selected, actual.best_progress_witness) == exhaustive(3, probabilities, raw, threshold)


def test_exact_dominance_uses_the_identity_prefix_and_supplies_a_real_witness():
    points = [(1, 3, (3,), 'identity3'), (1, 4, (1,), 'identity1'), (2, 4, (2,), 'dominated')]
    decisions = []
    retained = certified_projection(points, lambda *args: decisions.append(args))
    assert [record[3] for record in retained] == ['identity3', 'identity1']
    record, keep, witness = decisions[-1]
    assert not keep and witness[3] == 'identity1'
    assert all(witness[i] <= record[i] for i in range(3))
    assert binary_integer(math.nextafter(1., math.inf)) > binary_integer(1.)
    assert binary_integer(5e-324) == 1
