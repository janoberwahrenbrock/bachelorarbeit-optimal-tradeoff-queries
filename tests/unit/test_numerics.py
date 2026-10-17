from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from otqa.geometry import ConstraintSystem
from otqa.numerics.lp import LinearProgramBackend
from otqa.numerics.rational_lp import recover_minimum
from otqa.numerics.profile import resolved_numerical_profile, resolved_cache_policy


def test_native_cold_solve_matches_public_lp():
    native, public = LinearProgramBackend(), LinearProgramBackend(native=False)
    for objective in ([1.0, 2.0], [-2.0, 0.4], [0.0, 0.0], [1.0, 2.0]):
        arguments = dict(c=objective, A_ub=np.array([[-1., 0.], [0., -1.]]),
                         b_ub=np.zeros(2), A_eq=np.array([[1., 1.]]),
                         b_eq=np.array([1.]), bounds=[(None, None)] * 2)
        left, right = native.solve(**arguments), public.solve(**arguments)
        assert left.status == right.status
        assert float(left.fun).hex() == float(right.fun).hex()
        assert np.array_equal(left.x, right.x)
    native.close()
    public.close()


@pytest.mark.parametrize("native", [False, True])
def test_backend_classifies_infeasible_and_unbounded(native):
    backend = LinearProgramBackend(native=native)
    assert backend.solve(c=[1.], A_ub=np.array([[1.], [-1.]]),
                         b_ub=np.array([0., -1.]), bounds=[(None, None)]).status == 2
    assert backend.solve(c=[-1.], bounds=[(0., None)]).status == 3
    backend.close()


def test_invalid_input_is_not_silently_accepted_by_native_adapter():
    backend = LinearProgramBackend()
    with pytest.raises(ValueError):
        backend.solve(c=[float("nan")], bounds=[(None, None)])
    backend.close()


def test_exact_active_sets_certify_point_and_recession():
    bounded = ConstraintSystem([[-1., 0.], [0., -1.]], [0., 0.], [[1., 1.]], [1.])
    optimum = recover_minimum(bounded, [-1., 0.])
    assert optimum.status == "optimal"
    assert optimum.optimal_value == -1.0
    unbounded = ConstraintSystem([[-1., 0.], [0., -1.]], [0., 0.])
    assert recover_minimum(unbounded, [-1., 0.]).status == "unbounded"
    no_nonnegativity = ConstraintSystem([[1., 0.]], [1.])
    assert recover_minimum(no_nonnegativity, [-1., 0.]) is None


def test_session_backends_are_independent_across_threads():
    def solve(value):
        with_backend = LinearProgramBackend()
        result = with_backend.solve(c=[value], bounds=[(0., 1.)])
        with_backend.close()
        return result.fun
    with ThreadPoolExecutor(2) as executor:
        assert tuple(executor.map(solve, [1., -1.])) == (0., -1.)


def test_profile_contains_only_active_constants_and_separate_cache_policy():
    profile = resolved_numerical_profile()
    from dataclasses import asdict
    from otqa.geometry.simplex_recovery import Limits

    assert profile["profile_id"] == "otqa-exact-v2"
    assert sum(map(len, profile["values"].values())) == 52
    assert profile["values"]["simplex_partition_recovery"] == asdict(Limits())
    assert profile["values"]["query_generation"]["answer_order"] == ["<", "=", ">"]
    assert profile["numeric_hex"]["/values/geometry/tolerance"] == (1e-10).hex()
    profile["values"]["geometry"]["tolerance"] = 123
    assert resolved_numerical_profile()["values"]["geometry"]["tolerance"] == 1e-10
    assert resolved_cache_policy()["state_entries"] == 16


@pytest.mark.parametrize("invalid", ["bound", "slack", "equality", "nan"])
def test_continuous_checker_retains_every_primal_validation(invalid):
    from scipy.optimize._linprog_util import _check_result
    from otqa.numerics.validation import continuous_check
    x, fun, slack, con = np.array([.5]), .5, np.array([.5]), np.array([0.])
    bounds = np.array([[0., 1.]])
    if invalid == "bound":
        x[0] = 2.
    elif invalid == "slack":
        slack[0] = -1.
    elif invalid == "equality":
        con[0] = .5
    else:
        x[0] = float("nan")
    expected = _check_result(x, fun, 0, slack, con, bounds, 1e-9, "original", None)
    actual = continuous_check(_check_result, x, fun, 0, slack, con, bounds, 1e-9, "original")
    assert actual == expected
    assert actual[0] == 4
