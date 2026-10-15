"""Analytical probability failure boundaries retain their recovery causes."""
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from otqa.geometry import GeometrySession
from otqa.geometry import session as geometry
from otqa.geometry.rational import RecoveryGeometryError, RecoveryNotApplicable
from otqa.models import Query


class PositiveCorrection(float):
    exact_positive_correction = True


BOUNDARIES = (
    ([0.0], "weight space has no positive intrinsic volume"),
    ([1.0, PositiveCorrection(0.1), 0.8],
     "native volume recovery requires a common exact partition"),
    ([1.0, 0.0, 0.0], "exact query branches have zero total probability"),
)


@pytest.mark.parametrize("volumes,message", BOUNDARIES)
def test_unsupported_probability_recovery_preserves_failure_and_cause(volumes, message):
    # Four simplex weights leave affine dimension three, outside the bounded
    # exact clipping domain. A failed numeric volume must keep its public error.
    with GeometrySession() as session:
        space = session.weight_space((), 4)
        with patch.object(session, "_volume_by_key", side_effect=volumes):
            with pytest.raises(RuntimeError, match=f"^{message}$") as raised:
                session.probabilities(space, Query(0, 1, 1.0))
    assert type(raised.value) is RuntimeError
    assert isinstance(raised.value.__cause__, RecoveryNotApplicable)


@pytest.mark.parametrize("volumes,message", BOUNDARIES)
def test_supported_probability_recovery_uses_complete_exact_partition(volumes, message):
    # Symmetry of a three-weight simplex gives two equal positive halves.
    with GeometrySession() as session:
        space = session.weight_space((), 3)
        with patch.object(session, "_volume_by_key", side_effect=volumes):
            result = session.probabilities(space, Query(0, 1, 1.0))
    assert result == {"<": 0.5, "=": 0.0, ">": 0.5}
    assert result.recovered_exact_partition


@pytest.mark.parametrize("volumes,message", BOUNDARIES)
def test_probability_failure_keeps_recovery_geometry_error_identity(volumes, message):
    original = RecoveryGeometryError("synthetic exact clipping failure")
    with GeometrySession() as session:
        space = session.weight_space((), 3)
        with patch.object(session, "_volume_by_key", side_effect=volumes), patch.object(
            geometry, "recover_probabilities", side_effect=original
        ):
            with pytest.raises(RuntimeError, match=f"^{message}$") as raised:
                session.probabilities(space, Query(0, 1, 1.0))
    assert raised.value.__cause__ is original


def test_ordinary_positive_volumes_never_request_recovery():
    with GeometrySession() as session:
        space = session.weight_space((), 3)
        with patch.object(session, "_volume_by_key", side_effect=[1.0, 0.25, 0.75]), patch.object(
            geometry, "recover_probabilities", side_effect=AssertionError("ordinary path")
        ):
            result = session.probabilities(space, Query(0, 1, 1.0))
    assert result == {"<": 0.25, "=": 0.0, ">": 0.75}
    assert type(result) is dict


def test_positive_native_volume_keeps_existing_nonrecovering_route():
    # This independent volume boundary ensures the probability wrapper does not
    # cause successful geometric volume work to enter the clipping fallback.
    from otqa.geometry.vertices import PolytopeVertices
    import numpy as np

    with GeometrySession() as session:
        space = session.weight_space((), 3)
        vertices = PolytopeVertices("full_dimensional", np.eye(3), 2, 1.0)
        value = float.fromhex("0x1.23456789abcdep-8")
        with patch.object(geometry, "ConvexHull", return_value=SimpleNamespace(volume=value)), patch.object(
            geometry, "recover_volume", side_effect=AssertionError("positive volume")
        ):
            actual = session.volume_from_vertices(space, vertices)
    assert actual.hex() == value.hex()
    assert type(actual) is float
