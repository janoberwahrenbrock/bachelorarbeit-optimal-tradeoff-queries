"""Analytical interior-grid contracts, without LP or geometry reconstruction."""
import math
from types import SimpleNamespace

import numpy as np
import pytest

from otqa.config import AlgorithmPolicy, SingleCandidateStop
from otqa.models import AnsweredQuery, Query
from otqa.models.numerical import LinearResult
from otqa.numerics.profile import GRID_MAXIMUM, GRID_MINIMUM, resolved_numerical_profile
from otqa.queries import candidates
from otqa.state.types import GoalPairRatioIntervals, RatioInterval


def interval(lower=0.0, upper=None):
    return RatioInterval(LinearResult("optimal", "min", lower),
                         LinearResult("unbounded", "max") if upper is None else
                         LinearResult("optimal", "max", upper))


def test_default_five_points_match_documented_values():
    assert candidates.grid_values(interval(), 5) == pytest.approx(
        [.1357208808, .3684031499, 1.0, 2.7144176166, 7.3680629973], abs=5e-11, rel=0)


@pytest.mark.parametrize("lower,upper", [(.05, 20.0), (.2, 8.0), (2.0, 3.0)])
@pytest.mark.parametrize("grid_size", [1, 3, 5, 10, 20])
def test_equal_log_gaps_include_both_outer_gaps(lower, upper, grid_size):
    values = candidates.grid_values(interval(lower, upper), grid_size)
    assert len(values) == grid_size
    assert all(lower < value < upper for value in values)
    assert values == sorted(values)
    expected = (math.log(upper) - math.log(lower)) / (grid_size + 1)
    np.testing.assert_allclose(np.diff(np.log([lower, *values, upper])), expected,
                               rtol=2e-13, atol=1e-14)
    if grid_size == 1:
        assert values[0] == pytest.approx(math.sqrt(lower * upper), rel=2e-15)


@pytest.mark.parametrize("lower,upper,clipped", [
    (0.0, None, (.05, 20.0)), (.2, None, (.2, 20.0)),
    (0.0, 8.0, (.05, 8.0)), (.2, 8.0, (.2, 8.0)),
])
def test_bounds_are_state_dependent_and_unbounded_upper_is_capped(lower, upper, clipped):
    values = candidates.grid_values(interval(lower, upper), 5)
    start, stop = clipped
    expected = [start * (stop / start) ** (rank / 6) for rank in range(1, 6)]
    assert values == pytest.approx(expected, rel=2e-15)


def test_keyword_bounds_remain_available():
    assert candidates.grid_values(interval(), 1, minimum=.25, maximum=4.) == [1.0]


@pytest.mark.parametrize("lower,upper", [
    (0.0, .01), (21.0, None), (4.0, 3.0), (1.0, 1.0),
    (1.0, 1.0 + 5e-13), (.05, .05), (20.0, 20.0),
])
def test_empty_exact_and_tolerance_collapsed_intervals_have_no_points(lower, upper):
    assert candidates.grid_values(interval(lower, upper), 5) == []


@pytest.mark.parametrize("lower,upper", [
    (LinearResult("infeasible", "min"), LinearResult("infeasible", "max")),
    (LinearResult("infeasible", "min"), LinearResult("optimal", "max", 2.)),
    (LinearResult("optimal", "min", 1.), LinearResult("infeasible", "max")),
])
def test_infeasible_intervals_are_empty(lower, upper):
    assert candidates.grid_values(RatioInterval(lower, upper), 5) == []


def test_unbounded_lower_keeps_visible_error():
    with pytest.raises(ValueError, match="lower ratio bound must not be unbounded"):
        candidates.grid_values(RatioInterval(LinearResult("unbounded", "min"),
                                            LinearResult("unbounded", "max")), 5)


@pytest.mark.parametrize("which", ["lower", "upper"])
@pytest.mark.parametrize("value", [None, math.nan, math.inf, -math.inf])
def test_malformed_optimal_bounds_are_errors_not_empty(which, value):
    lower = LinearResult("optimal", "min", value if which == "lower" else 1.)
    upper = LinearResult("optimal", "max", value if which == "upper" else 2.)
    with pytest.raises(RuntimeError, match="optimal ratio bound"):
        candidates.grid_values(RatioInterval(lower, upper), 5)


@pytest.mark.parametrize("which", ["lower", "upper"])
def test_unknown_bound_failure_status_is_not_an_empty_interval(which):
    lower = LinearResult("numerical_error" if which == "lower" else "optimal", "min", 1.)
    upper = LinearResult("numerical_error" if which == "upper" else "optimal", "max", 2.)
    with pytest.raises(RuntimeError, match="unexpected ratio bound status"):
        candidates.grid_values(RatioInterval(lower, upper), 5)


def test_rounding_to_endpoints_never_emits_boundary_queries():
    lower, upper = 1.0, 1.0 + 2e-12
    raw = np.geomspace(lower, upper, 20_002)[1:-1]
    assert any(value == lower or value == upper for value in raw)
    values = candidates.grid_values(interval(lower, upper), 20_000)
    assert 0 < len(values) < 20_000
    assert all(lower < value < upper for value in values)


def test_grid_queries_keep_one_existing_bound_call_per_ordered_pair(monkeypatch):
    calls = []
    def bounds(system, a, b):
        calls.append((a, b))
        return interval(.2, 8.)
    monkeypatch.setattr(candidates, "ratio_bounds", bounds)
    queries = candidates.grid_queries(SimpleNamespace(variable_count=3), 3)
    assert calls == [(a, b) for a in range(3) for b in range(3) if a != b]
    assert queries == tuple(sorted(queries, key=candidates.query_key))


def state(source, history=()):
    pair = GoalPairRatioIntervals(0, 1, {0: interval(50., 100.)})
    return SimpleNamespace(policy=AlgorithmPolicy("fixed", 2, source, 5,
                                                  "candidate_count", SingleCandidateStop()),
                           weight_space=SimpleNamespace(variable_count=2),
                           history=history, analysis=SimpleNamespace(ratio_intervals=(pair,)))


def test_grid_component_identical_in_both_modes_and_ratios_remain_outside_grid(monkeypatch):
    monkeypatch.setattr(candidates, "ratio_bounds", lambda *args: interval())
    captures = {}
    for mode in ("grid", "both"):
        events = []
        data = candidates.generate_queries(state(mode), 2, capture_filter=lambda *event: events.append(event))
        captures[mode] = [query for reason, query, _ in events if reason == "source_grid"]
        assert list(data.query_candidates) == sorted(data.query_candidates, key=candidates.query_key)
        assert all(value != "unknown" for value in data.query_sources.values())
    assert captures["grid"] == captures["both"]
    pair = state("both").analysis.ratio_intervals
    assert candidates.ratio_queries(pair) == (Query(0, 1, 49.999), Query(0, 1, 100.001))
    both = candidates.generate_queries(state("both"), 2)
    for query in candidates.ratio_queries(pair):
        assert query in both.query_candidates
        assert both.query_sources[candidates.canonical_key(query)] == "ratio"


@pytest.mark.parametrize("mode", ["grid", "both"])
def test_final_level_stays_ratio_only_without_state_bound_calls(monkeypatch, mode):
    def forbidden(*args, **kwargs):
        raise AssertionError("Final level must not generate a grid or query state LP bounds")
    monkeypatch.setattr(candidates, "ratio_bounds", forbidden)
    data = candidates.generate_queries(state(mode), 1)
    assert data.query_candidates == candidates.ratio_queries(state(mode).analysis.ratio_intervals)
    assert set(data.query_sources.values()) == {"ratio"}


def test_answered_and_mirrored_grid_queries_remain_filtered(monkeypatch):
    monkeypatch.setattr(candidates, "ratio_bounds", lambda *args: interval())
    history = (AnsweredQuery(Query(0, 1, 1.), ">"),)
    data = candidates.generate_queries(state("both", history), 2)
    assert all(not candidates.already_answered(query, history) for query in data.query_candidates)
    keys = [candidates.canonical_key(query) for query in data.query_candidates]
    assert len(keys) == len(set(keys))


def test_grid_defaults_use_the_resolved_profile_constants():
    profile = resolved_numerical_profile()
    values = profile["values"]["query_generation"]
    assert profile["profile_id"] == "otqa-exact-v3"
    assert candidates.grid_values.__kwdefaults__ == {"minimum": GRID_MINIMUM, "maximum": GRID_MAXIMUM}
    assert values["min_grid_value"] == GRID_MINIMUM == .05
    assert values["max_grid_value"] == GRID_MAXIMUM == 20.
