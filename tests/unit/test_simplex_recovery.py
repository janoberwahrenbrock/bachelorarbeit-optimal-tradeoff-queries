"""Independent exact geometry references and exception-only recovery boundaries."""
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from otqa.geometry import GeometrySession
from otqa.geometry import session as geometry
from otqa.geometry import simplex_recovery as recovery
from otqa.geometry.constraints import ConstraintSystem
from otqa.geometry.rational import RecoveryGeometryError, RecoveryNotApplicable
from otqa.models import Query


FIXTURES = Path(__file__).parents[1] / "fixtures" / "geometry"


def coordinate(n, index, value=1):
    return tuple(value if i == index else 0 for i in range(n))


def simplex_key(n, extra=()):
    normals = [coordinate(n, i, -1) for i in range(n)]
    rhs = [0] * n
    for a, b in extra:
        normals.append(tuple(a))
        rhs.append(b)
    return tuple(normals), tuple(rhs), ((1,) * n,), (1,)


def measure(n, constraints=(), *, limits=None):
    budget = recovery.Budget(limits or recovery.Limits())
    poly = recovery.simplex_polytope(n, constraints, budget=budget)
    value, proof = recovery.coordinate_volume(poly, budget)
    return poly, value, proof


def fixture(name):
    data = json.loads((FIXTURES / name).read_text())
    expected = {answer: Fraction(int(value["numerator"]), int(value["denominator"]))
                for answer, value in data["expected_probabilities"].items()}
    return data, expected


@pytest.mark.parametrize("n", range(2, 8))
def test_simplex_coordinate_measure_is_one_over_factorial(n):
    poly, value, proof = measure(n)
    assert value == Fraction(1, math.factorial(n - 1))
    assert len(poly.vertices) == n
    assert proof["vertices_are_complete_for_final_region"]


@pytest.mark.parametrize("n", [4, 7])
def test_coordinate_cut_has_analytic_simplex_cap_probability(n):
    d, threshold = n - 1, Fraction(1, 4)
    result = recovery.partition(n, (), (coordinate(n, 0), threshold))
    greater = (1 - threshold) ** d
    assert result["parent_volume"] == Fraction(1, math.factorial(d))
    assert result["children"]["<"]["probability"] == 1 - greater
    assert result["children"][">"]["probability"] == greater
    assert sum(c["volume"] for c in result["children"].values()) == result["parent_volume"]
    assert result["exact_child_sum_passed"]


@pytest.mark.parametrize("n", range(2, 8))
def test_ratio_cut_through_simplex_vertices_is_exactly_symmetric(n):
    cut = tuple(int(i == 0) - int(i == 1) for i in range(n))
    result = recovery.partition(n, (), (cut, 0))
    assert result["children"]["<"]["probability"] == Fraction(1, 2)
    assert result["children"][">"]["probability"] == Fraction(1, 2)
    assert result["equality_probability"] == 0


@pytest.mark.parametrize("n", [4, 7])
def test_cube_with_nonsimplicial_faces_has_exact_volume_and_cut(n):
    d, side = n - 1, Fraction(1, n)
    constraints = [(coordinate(n, i), side) for i in range(d)]
    result = recovery.partition(n, constraints, (coordinate(n, 0), side / 3))
    assert result["parent_vertices"] == 2 ** d
    assert result["parent_geometry"]["simplices"] == math.factorial(d)
    assert result["parent_volume"] == side ** d
    assert result["children"]["<"]["probability"] == Fraction(1, 3)
    assert result["children"][">"]["probability"] == Fraction(2, 3)


def test_nonsimple_octahedron_vertices_are_not_mistaken_for_extra_edges():
    center, radius = Fraction(1, 4), Fraction(1, 16)
    constraints = [(tuple(signs) + (0,), radius + center * sum(signs))
                   for signs in product((-1, 1), repeat=3)]
    result = recovery.partition(4, constraints, (coordinate(4, 0), center))
    assert result["parent_vertices"] == 6
    assert result["parent_volume"] == Fraction(2 ** 3, math.factorial(3)) * radius ** 3
    assert result["children"]["<"]["probability"] == Fraction(1, 2)


def test_redundant_scaled_and_permuted_halfspaces_preserve_all_measures():
    constraints = [(coordinate(4, 0), Fraction(1, 4)),
                   (coordinate(4, 1), Fraction(1, 3))]
    cut = ((1, -1, 0, 0), 0)
    reference = recovery.partition(4, constraints, cut)
    redundant = list(reversed(constraints)) + constraints + [
        (tuple(3 * x for x in a), 3 * b) for a, b in constraints]
    actual = recovery.partition(4, redundant, cut)
    assert actual["parent_volume"] == reference["parent_volume"]
    for answer in ("<", ">"):
        assert actual["children"][answer]["volume"] == reference["children"][answer]["volume"]
        assert actual["children"][answer]["probability"] == reference["children"][answer]["probability"]


def test_supporting_cut_is_zero_ambient_measure_without_claiming_empty():
    poly, value, proof = measure(4, [(coordinate(4, 0), 0)])
    assert value == 0
    assert poly.status == "lower_dimensional_zero"
    assert len(poly.vertices) == 3
    assert proof["dimension_upper_bound"] == 2
    with pytest.raises(recovery.ZeroParentVolume):
        recovery.partition(4, [(coordinate(4, 0), 0)], ((0, 1, -1, 0), 0))


def test_empty_region_and_later_constraints_on_zero_measure_are_distinguished():
    poly, value, _ = measure(4, [(coordinate(4, 0), Fraction(-1, 8))])
    assert value == 0 and poly.status == "empty"
    poly, value, proof = measure(4, [(coordinate(4, 0), 0), (coordinate(4, 1), -1)])
    assert value == 0 and poly.status == "lower_dimensional_zero"
    assert proof["unprocessed_constraints"] == 1
    assert not proof["vertices_are_complete_for_final_region"]


def test_binary64_coefficients_are_not_rationalized_as_decimal_strings():
    threshold = 0.1
    result = recovery.partition(2, (), ((1, 0), threshold))
    assert result["children"]["<"]["probability"] == Fraction.from_float(threshold)
    assert result["children"]["<"]["probability"] != Fraction(1, 10)


def test_tiny_positive_mass_stays_exact_and_float_underflow_is_typed():
    # A small six-dimensional simplex has volume t**6/6!, even below binary64.
    threshold = Fraction(1, 2 ** 200)
    cut = ((1, 1, 1, 1, 1, 1, 0), threshold)
    _, volume, _ = measure(7, [cut])
    probability = volume * math.factorial(6)
    assert probability == Fraction(1, 2 ** 1200)
    assert probability > 0
    with pytest.raises(recovery.ProbabilityUnderflow):
        recovery.positive_probability_float(probability)
    with pytest.raises(recovery.ProbabilityUnderflow):
        recovery.partition(7, (), cut)


@pytest.mark.parametrize("limits", [
    recovery.Limits(max_vertices=2), recovery.Limits(max_operations=1),
    recovery.Limits(max_constraints=3), recovery.Limits(max_rank_calls=1),
    recovery.Limits(max_faces=1), recovery.Limits(max_simplices=1),
])
def test_resource_caps_raise_instead_of_returning_partial_volume(limits):
    with pytest.raises(recovery.WorkLimitExceeded):
        recovery.partition(4, (), ((1, 1, -1, -1), 0), limits=limits)


def test_child_regions_share_the_same_pair_check_budget():
    # Each child takes four crossing-pair checks; resetting per child would pass.
    with pytest.raises(recovery.WorkLimitExceeded) as raised:
        recovery.partition(4, (), ((1, 1, -1, -1), 0),
                           limits=recovery.Limits(max_pair_checks=7))
    assert raised.value.budget["counts"]["pair_checks"] == 8


def test_fraction_bit_and_wall_caps_fail_closed_without_waiting():
    with pytest.raises(recovery.WorkLimitExceeded):
        recovery.partition(4, (), (coordinate(4, 0), Fraction(1, 32)),
                           limits=recovery.Limits(max_bits=4))
    budget = recovery.Budget(recovery.Limits(max_wall_seconds=1), started=0)
    with patch.object(recovery.time, "perf_counter", return_value=2):
        with pytest.raises(recovery.WorkLimitExceeded):
            budget.tick()


@pytest.mark.parametrize("n", [1, 8])
def test_dimensions_outside_the_declared_domain_are_unsupported(n):
    with pytest.raises(recovery.UnsupportedGeometry):
        recovery.simplex_polytope(n)


@pytest.mark.parametrize("equalities", [
    [((1, 0, 0, 0), Fraction(1, 2))], [((1, 1, 1, 1), 2)],
])
def test_independent_or_inconsistent_equalities_are_not_dropped(equalities):
    with pytest.raises(recovery.UnsupportedGeometry):
        recovery.simplex_polytope(4, equalities=equalities)


@pytest.mark.parametrize("cut", [((0, 0, 0, 0), 0), ((1, 1, 1, 1), 1)])
def test_affine_constant_queries_are_explicitly_unsupported(cut):
    with pytest.raises(recovery.UnsupportedGeometry):
        recovery.partition(4, (), cut)


@pytest.mark.parametrize("coefficient", [True, float("nan"), float("inf")])
def test_nonfinite_and_boolean_coefficients_are_not_accepted(coefficient):
    with pytest.raises(recovery.UnsupportedGeometry):
        recovery.partition(4, (), ((coefficient, 0, 0, 0), 0))


@pytest.mark.parametrize("missing", ["nonnegative", "simplex", "independent_equality"])
def test_source_key_must_explicitly_prove_the_supported_weight_domain(missing):
    a, b, e, f = simplex_key(4)
    if missing == "nonnegative":
        a, b = a[1:], b[1:]
    elif missing == "simplex":
        e, f = (), ()
    else:
        e, f = e + ((1, 0, 0, 0),), f + (Fraction(1, 2),)
    with pytest.raises(recovery.UnsupportedGeometry):
        recovery.constraint_key_arguments((a, b, e, f))
    with pytest.raises(RecoveryNotApplicable):
        recovery.recover_probabilities(SimpleNamespace(key=(a, b, e, f), variable_count=4), Query(0, 1, 1))


def test_product_recovery_marks_exact_partition_and_retains_bounded_work():
    result = recovery.recover_probabilities(
        SimpleNamespace(key=simplex_key(7), variable_count=7), Query(0, 1, 1))
    assert result == {"<": 0.5, "=": 0.0, ">": 0.5}
    assert result.recovered_exact_partition
    assert result.recovery_diagnostics["exact_child_sum_passed"]
    assert result.recovery_diagnostics["work"]["counts"]["operations"] > 0


def test_product_cap_failure_is_a_recovery_error_with_cause_and_work():
    budget = recovery.Budget(recovery.Limits(max_operations=1))
    with patch.object(recovery, "_profile_budget", return_value=budget):
        with pytest.raises(RecoveryGeometryError) as raised:
            recovery.recover_probabilities(
                SimpleNamespace(key=simplex_key(7), variable_count=7), Query(0, 1, 1))
    assert isinstance(raised.value.__cause__, recovery.WorkLimitExceeded)
    assert raised.value.reason == "work_limit_exceeded"
    assert raised.value.diagnostics["work"]["counts"]["operations"] == 2


@pytest.mark.parametrize("name", ["qhull_failure_492.json", "qhull_failure_528.json"])
def test_captured_failure_has_exact_reference_partition(name):
    data, expected = fixture(name)
    n, constraints, equalities = recovery.constraint_key_arguments(data["constraint_key"])
    result = recovery.partition(n, constraints, recovery.ratio_query(n, data["query"]), equalities=equalities)
    assert n == 7 and result["dimension"] == 6
    assert result["exact_child_sum_passed"]
    assert sum(child["volume"] for child in result["children"].values()) == result["parent_volume"]
    assert sum(expected.values()) == 1
    for answer in ("<", ">"):
        assert result["children"][answer]["probability"] == expected[answer]
        assert result["children"][answer]["probability_float"] == float(expected[answer])


@pytest.mark.parametrize("name", ["qhull_failure_492.json", "qhull_failure_528.json"])
def test_marked_native_failure_uses_captured_common_partition(name):
    data, expected = fixture(name)
    failure = RuntimeError("captured native halfspace failure")
    failure.native_geometry_volume_error = True
    with GeometrySession() as session:
        space = ConstraintSystem.from_key(data["constraint_key"], session.backend)
        with patch.object(session, "cached_support", return_value=(-1.0, 1.0)), patch.object(
                session, "_volume_by_key", side_effect=failure):
            actual = session.probabilities(space, Query(**data["query"]))
    assert actual == {"<": float(expected["<"]), "=": 0.0, ">": float(expected[">"])}
    assert actual.recovered_exact_partition


@pytest.mark.parametrize("name", ["qhull_failure_492.json", "qhull_failure_528.json"])
def test_actual_native_call_completes_or_recovers_captured_geometry(name):
    data, expected = fixture(name)
    with GeometrySession() as session:
        space = ConstraintSystem.from_key(data["constraint_key"], session.backend)
        actual = session.probabilities(space, Query(**data["query"]))
    # Qhull may succeed on another platform, so this unforced call does not
    # promise the exact recovery's accuracy for the ordinary native path.
    assert set(actual) == {"<", "=", ">"}
    assert all(math.isfinite(value) for value in actual.values())
    assert actual["="] == 0.0
    for answer in ("<", ">"):
        assert 0.0 < actual[answer] < 1.0
    assert abs(math.fsum(actual.values()) - 1.0) <= math.ulp(1.0)
    if getattr(actual, "recovered_exact_partition", False):
        assert actual == {"<": float(expected["<"]), "=": 0.0, ">": float(expected[">"])}


def test_unmarked_native_error_never_enters_the_new_fallback():
    original = RuntimeError("unmarked volume failure")
    with GeometrySession() as session:
        space = session.weight_space((), 7)
        with patch.object(session, "cached_support", return_value=(-1.0, 1.0)), patch.object(
                session, "_volume_by_key", side_effect=original), patch.object(
                geometry, "recover_simplex_probabilities", side_effect=AssertionError("unmarked error")):
            with pytest.raises(RuntimeError) as raised:
                session.probabilities(space, Query(0, 1, 1))
    assert raised.value is original


def test_exhausted_recovery_preserves_native_cause_geometry_and_sdk_partial_context():
    from otqa.errors import NumericalError
    from otqa.models.core import AnsweredQuery
    from otqa.models.execution import ExecutionCursor
    from otqa.models.results import PartialContext, QueryCounts
    from otqa.runtime.error_serialization import error_wire

    original = RuntimeError("native halfspace failure")
    original.native_geometry_volume_error = True
    budget = recovery.Budget(recovery.Limits(max_operations=1))
    with GeometrySession() as session:
        space = session.weight_space((), 7)
        with patch.object(session, "cached_support", return_value=(-1.0, 1.0)), patch.object(
                session, "_volume_by_key", side_effect=original), patch.object(
                recovery, "_profile_budget", return_value=budget):
            with pytest.raises(RuntimeError) as raised:
                session.probabilities(space, Query(0, 1, 1))
        assert raised.value is original
        assert isinstance(original.__cause__, RecoveryGeometryError)
        evidence = original.geometry_failure_context
        assert evidence["constraint_key"] == space.key
        assert evidence["query"] == {"goal_index_a": 0, "goal_index_b": 1, "value": 1.0}
        assert evidence["recovery"]["reason"] == "work_limit_exceeded"
        assert evidence["recovery"]["work"]["counts"]["operations"] == 2
    accepted = AnsweredQuery(Query(0, 1, 1), "<")
    partial = PartialContext(None, (accepted,), (), QueryCounts(0, 1, 1, 1), None,
                             ExecutionCursor(1, 2))
    public = NumericalError("native halfspace failure", context=partial)
    public.__cause__ = original
    wire = error_wire(public)
    assert public.partial_context is partial
    assert wire["code"] == "numerical_failure"
    assert wire["context"]["memory_answer_count"] == 1
    assert wire["context"]["memory_execution_cursor"] == {"answered_total": 1, "remaining_depth": 2}
    assert wire["context"]["geometry_failure"] == evidence
