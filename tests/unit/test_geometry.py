import math

import numpy as np
import pytest

from otqa.geometry import GeometrySession, ConstraintSystem
from otqa.geometry.rational import recover_probabilities, recover_volume, RecoveryNotApplicable
from otqa.models import Query, AnsweredQuery


@pytest.mark.parametrize("dimensions", [2, 3, 5, 7])
def test_simplex_intrinsic_volume(dimensions):
    with GeometrySession() as geometry:
        space = geometry.weight_space((), dimensions)
        expected = math.sqrt(dimensions) / math.factorial(dimensions - 1)
        assert geometry.volume(space) == pytest.approx(expected, rel=1e-12)
        vertices = geometry.vertices(space)
        assert vertices.status == "full_dimensional"
        assert len(vertices.vertices) == dimensions


@pytest.mark.parametrize("ratio", [0.01, 0.3, 1.0, 4.0, 100.0])
def test_uniform_simplex_ratio_distribution(ratio):
    with GeometrySession() as geometry:
        space = geometry.weight_space((), 3)
        result = geometry.probabilities(space, Query(0, 1, ratio))
        assert result["<"] == pytest.approx(ratio / (1 + ratio), abs=1e-12)
        assert result["="] == 0.0
        assert result[">"] == pytest.approx(1 / (1 + ratio), abs=1e-12)


def test_equality_reduces_affine_measure_and_forces_answer():
    query = Query(0, 1, 2.0)
    with GeometrySession() as geometry:
        space = geometry.weight_space((AnsweredQuery(query, "="),), 3)
        result = geometry.probabilities(space, query)
        assert result == {"<": 0.0, "=": 1.0, ">": 0.0}
        assert geometry.vertices(space).affine_dimension == 1
        assert geometry.volume(space) > 0


def test_inequality_degeneracy_has_zero_area_not_line_length():
    with GeometrySession() as geometry:
        space = geometry.weight_space((), 3)
        space.add_inequality([1.0, 0.0, 0.0], 0.0)
        assert geometry.volume(space) == 0.0
        assert recover_volume(space) == 0.0


def test_explicit_infeasible_point_retains_zero_volume_convention():
    with GeometrySession() as geometry:
        space = geometry.weight_space((), 2)
        space.add_equality([1.0, 0.0], 2.0)
        assert geometry.volume(space) == 0.0
        assert recover_volume(space) == 0.0


def test_small_explicit_region_rational_partition():
    with GeometrySession() as geometry:
        space = geometry.weight_space((), 3)
        space.add_inequality([1.0, 0.0, 0.0], 1e-11)
        exact = recover_probabilities(space, Query(1, 2, 1.0))
        assert exact == {"<": 0.5, "=": 0.0, ">": 0.5}
        assert exact.recovered_exact_partition
        assert recover_volume(space) > 0.0


def test_rational_recovery_declines_higher_affine_dimension():
    with GeometrySession() as geometry:
        space = geometry.weight_space((), 5)
        with pytest.raises(RecoveryNotApplicable):
            recover_volume(space)


def test_cache_ownership_closed_state_and_immutable_vertices():
    first, second = GeometrySession(), GeometrySession()
    space = first.weight_space((), 3)
    value = first.volume(space)
    assert first.volume(space) == value
    assert first.volume_cache.cache_info().hits == 1
    assert second.volume_cache.cache_info().currsize == 0
    cached = first.vertex_cache.get((space.key, 1e-10))
    with pytest.raises(ValueError):
        cached.vertices.setflags(write=True)
    first.close()
    assert second.volume(second.weight_space((), 3)) == value
    with pytest.raises(RuntimeError):
        first.volume(space)
    second.close()


def test_foreign_constraint_system_uses_owning_geometry_backend():
    first, second = GeometrySession(), GeometrySession()
    try:
        space = first.weight_space((), 3)
        before = first.backend.calls
        assert second.probabilities(space, Query(0, 1, 1.))["<"] == pytest.approx(.5)
        assert first.backend.calls == before
        assert second.backend.calls > 0
    finally:
        first.close()
        second.close()


def test_invalid_tolerance_rejected_before_deterministic_support_shortcut():
    with GeometrySession() as geometry:
        space = geometry.weight_space((), 3)
        with pytest.raises(ValueError):
            geometry.probabilities(space, Query(0, 1, 0.), tolerance=0.)


def test_mutating_constraint_invalidates_prepared_arrays():
    system = ConstraintSystem()
    system.add_inequality([-1.0, 0.0], 0.0)
    system.add_equality([1.0, 1.0], 1.0)
    before = system.get_solver_matrices()
    system.add_inequality([1.0, 0.0], 0.2)
    after = system.get_solver_matrices()
    assert before[0].shape == (1, 2)
    assert after[0].shape == (2, 2)
    assert np.array_equal(after[0][-1], [1.0, 0.0])
